"""Render proposed-changes files and draft pull-request content.

Nothing here writes to disk and nothing here opens a pull request.
Skipped duplicates are listed in the index and are not given a case file
or a Foundry query line.
"""

from __future__ import annotations

import json
from typing import Any

LABEL = "DRAFT FOR MAINTAINER REVIEW"


def render(bundle_id: str, agent_id: str, cases: list[dict[str, Any]], not_drafted: list[dict[str, Any]]) -> dict[str, Any]:
    root = f"proposed-changes/{bundle_id}"
    drafted = [case for case in cases if case["status"] == "drafted"]
    skipped = [case for case in cases if case["status"] == "skipped_duplicate"]
    files: list[dict[str, str]] = []
    for case in drafted:
        relative = f"{root}/cases/{case['id']}.json"
        case["file"] = relative
        files.append(
            {
                "path": relative,
                "role": "case",
                "content": _json(
                    {
                        "label": LABEL,
                        "id": case["id"],
                        "kind": case["kind"],
                        "status": "drafted",
                        "input": case["input"],
                        "expected_behaviour": case["expected_behaviour"],
                        "trace": case["trace"],
                        "fingerprint": case["fingerprint"],
                        "agent_under_test_id": agent_id,
                        "applied": False,
                        "note": "Draft content. This file does not call the agent under test.",
                    }
                ),
            }
        )
    index = {
        "label": LABEL,
        "bundle_id": bundle_id,
        "agent_under_test_id": agent_id,
        "considered": len(cases),
        "drafted": len(drafted),
        "skipped_duplicate": len(skipped),
        "observations_not_drafted": len(not_drafted),
        "invariant": (
            "drafted + skipped_duplicate = considered. "
            "observations_not_drafted is not added to considered."
        ),
        "cases": [
            {
                "id": case["id"],
                "kind": case["kind"],
                "status": case["status"],
                "fingerprint": case["fingerprint"],
                "duplicate_of": case["duplicate_of"],
                "trace": case["trace"],
                "file": case["file"],
            }
            for case in cases
        ],
        "not_drafted": not_drafted,
    }
    files.append({"path": f"{root}/index.json", "role": "index", "content": _json(index)})
    query_lines = [json.dumps({"query": case["input"]}, ensure_ascii=True) for case in drafted]
    files.append(
        {
            "path": f"{root}/foundry-queries.jsonl",
            "role": "foundry_queries",
            "content": ("\n".join(query_lines) + "\n") if query_lines else "",
        }
    )
    files.append(
        {
            "path": f"{root}/foundry-trace.json",
            "role": "foundry_trace",
            "content": _json(
                {
                    "called": False,
                    "uploaded": False,
                    "lines": [
                        {
                            "line": index,
                            "case_id": case["id"],
                            "requirement_id": case["trace"].get("requirement_id"),
                            "observation_id": case["trace"].get("observation_id"),
                            "source": case["trace"].get("source"),
                            "rule_id": case["trace"].get("rule_id"),
                        }
                        for index, case in enumerate(drafted, start=1)
                    ],
                }
            ),
        }
    )
    body = draft_pr_body(agent_id, cases, not_drafted, root)
    files.append({"path": f"{root}/draft-pr.md", "role": "pull_request", "content": body})
    return {
        "root": root + "/",
        "written_to_disk": False,
        "written_into_agent_tree": False,
        "files": files,
    }


def draft_pr_body(agent_id: str, cases: list[dict[str, Any]], not_drafted: list[dict[str, Any]], root: str) -> str:
    drafted = [case for case in cases if case["status"] == "drafted"]
    skipped = [case for case in cases if case["status"] == "skipped_duplicate"]
    lines = [
        "# Draft pull request",
        "",
        "Label: DRAFT FOR MAINTAINER REVIEW.",
        "",
        "This file is pull-request content. It has not been opened, pushed, or merged.",
        "The agent under test has not been edited. A maintainer approves the tests",
        "and any later pull request outside this generator.",
        "",
        f"Agent under test: `{agent_id}`.",
        f"Drafted cases: {len(drafted)}.",
        f"Skipped as duplicates: {len(skipped)}.",
        f"Observations not drafted: {len(not_drafted)}.",
        "The duplicate count is not added again on top of the drafted count.",
        f"considered = {len(cases)}. drafted + skipped_duplicate = considered.",
        "",
        "## Files",
        "",
        f"- `{root}/index.json`",
        f"- `{root}/foundry-queries.jsonl` (not uploaded)",
        f"- `{root}/foundry-trace.json`",
    ]
    for case in drafted:
        lines.append(f"- `{case['file']}`")
    lines.extend(["", "## Trace", "", "| Case | Kind | Status | Trace | Requirement | Duplicate of |", "| --- | --- | --- | --- | --- | --- |"])
    for case in cases:
        trace = case["trace"]
        source = trace.get("observation_id") or trace.get("source") or ""
        requirement = trace.get("requirement_id") or ""
        duplicate = case["duplicate_of"] or ""
        lines.append(
            f"| {case['id']} | {case['kind']} | {case['status']} | {source} | {requirement} | {duplicate} |"
        )
    if not_drafted:
        lines.extend(["", "## Not drafted", ""])
        for note in not_drafted:
            lines.append(f"- {note.get('observation_id') or '(none)'}: {note.get('reason')}")
    lines.extend(
        [
            "",
            "## Foundry",
            "",
            "The queries file is a draft mapping. Microsoft Foundry was not called.",
            "No pass rate is claimed.",
            "",
        ]
    )
    return "\n".join(lines)


def pr_title(agent_id: str) -> str:
    return f"Draft regression cases for {agent_id}"


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=True) + "\n"
