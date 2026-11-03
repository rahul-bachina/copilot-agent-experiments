#!/usr/bin/env python3
"""Draft regression cases from one synthetic bundle. Do not merge or push.

The same bundle and the same as-of date produce the same JSON. Text in the
bundle cannot set maintainer_approved, merged, pushed, or the case list.
Autonomy A3 is never the recommendation of this generator.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cases import build_cases, read_manifest
    from injection import scan_strings, strip_prohibited
    from manifest_bridge import draft_skeleton, not_requested
    from render import pr_title, render
    from sources import DEFAULT_STALE_AFTER_DAYS, currency
else:
    from .cases import build_cases, read_manifest
    from .injection import scan_strings, strip_prohibited
    from .manifest_bridge import draft_skeleton, not_requested
    from .render import pr_title, render
    from .sources import DEFAULT_STALE_AFTER_DAYS, currency

LABEL = "DRAFT FOR MAINTAINER REVIEW"
CATALOGUE_ID = "G008"
PROTECTED_BRANCHES = frozenset({"main", "master", "production", "release"})
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,80}$")

LIMITS = (
    "No model was called. A drafted case is not a Foundry score.",
    "The queries file was not uploaded. foundry_evaluation_called stays false.",
    "Trigger phrases are not scored. Generative orchestration on the standard harness selects by description.",
    "Whether the GitHub Copilot harness uses that selection rule was not on the page opened on 3 November 2026. Unverified.",
    "A skipped duplicate is not counted again as a drafted case.",
    "The maintainer approves the tests and any pull request. This generator does not.",
    "Pages were opened on 3 November 2026. A stale pin is not refreshed by the generator.",
)


class ProhibitedAction(RuntimeError):
    """The generator was asked to merge, push, approve, apply, or edit the agent."""


def merge_pull_request(*_args: Any, **_kwargs: Any) -> None:
    raise ProhibitedAction("This generator does not merge a pull request.")


def push_branch(*_args: Any, **_kwargs: Any) -> None:
    raise ProhibitedAction("This generator does not push, including to a protected branch.")


def edit_agent_under_test(*_args: Any, **_kwargs: Any) -> None:
    raise ProhibitedAction("This generator does not edit the agent under test.")


def approve_generated_tests(*_args: Any, **_kwargs: Any) -> None:
    raise ProhibitedAction("The maintainer approves generated tests. This generator does not.")


def open_pull_request(*_args: Any, **_kwargs: Any) -> None:
    raise ProhibitedAction("This generator drafts pull request content. It does not open a pull request.")


def generate(
    bundle: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> dict[str, Any]:
    from datetime import date

    date.fromisoformat(as_of)
    if not isinstance(bundle, dict):
        raise ValueError("The bundle must be a JSON object.")
    cleaned, ignored_keys = strip_prohibited(bundle)
    if not isinstance(cleaned, dict):
        raise ValueError("The bundle must be a JSON object.")
    _guard_paths(cleaned)
    agent = cleaned.get("agent_under_test")
    if not isinstance(agent, dict):
        raise ValueError("agent_under_test must be an object.")
    bundle_id = _require_id(cleaned.get("bundle_id"), "bundle_id")
    agent_id = _require_id(agent.get("id"), "agent_under_test.id")
    agent_path = _relative_path(agent.get("path"), "agent_under_test.path")
    for skill in agent.get("skills") or []:
        if isinstance(skill, dict) and skill.get("path"):
            _relative_path(skill.get("path"), "skill path")
    reading = read_manifest(agent.get("manifest"))
    cases, not_drafted = build_cases(cleaned, reading)
    proposed = render(bundle_id, agent_id, cases, not_drafted)
    drafted = sum(1 for case in cases if case["status"] == "drafted")
    skipped = sum(1 for case in cases if case["status"] == "skipped_duplicate")
    summary = {
        "considered": len(cases),
        "drafted": drafted,
        "skipped_duplicate": skipped,
        "observations_not_drafted": len(not_drafted),
    }
    if summary["drafted"] + summary["skipped_duplicate"] != summary["considered"]:
        raise RuntimeError("Case totals do not add up. drafted + skipped_duplicate must equal considered.")
    _check_foundry_lines(proposed, drafted)
    sources = currency(as_of, stale_after_days)
    hits = scan_strings(cleaned)
    urls = _urls(cleaned)
    skeleton = _skeleton(cleaned, reading, bundle_id, agent_id, as_of)
    push_branch = cleaned.get("requested_push_branch")
    push_refused = isinstance(push_branch, str) and bool(push_branch.strip())
    protected_named = push_refused and push_branch.strip().lower() in PROTECTED_BRANCHES
    title = pr_title(agent_id)
    body = next(item["content"] for item in proposed["files"] if item["role"] == "pull_request")
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "experiments/30-agent-regression-test-generator",
        "autonomy": "A1",
        "document_status": "draft",
        "bundle_id": bundle_id,
        "as_of": as_of,
        "agent_under_test": {"id": agent_id, "path": agent_path, "edited": False},
        "maintainer_approved": False,
        "merged": False,
        "pushed": False,
        "protected_branch_targeted": False,
        "protected_branch_named": protected_named,
        "push_request_refused": push_refused,
        "merge_request_refused": cleaned.get("requested_merge") is True,
        "edit_request_refused": cleaned.get("requested_edit_agent") is True,
        "foundry_request_refused": cleaned.get("requested_foundry_run") is True,
        "agent_under_test_edited": False,
        "pr_opened": False,
        "tests_applied": False,
        "foundry_evaluation_called": False,
        "model_called": False,
        "network_called": False,
        "a3_recommended": False,
        "actions_taken": [],
        "do_not_rely": any(row["stale"] for row in sources),
        "urls_not_fetched": urls,
        "sources": sources,
        "prompt_injection": {
            "detected": bool(hits),
            "followed": False,
            "hits": hits,
            "prohibited_payload_keys_ignored": ignored_keys,
        },
        "manifest_reading": reading,
        "manifest_skeleton": skeleton,
        "summary": summary,
        "cases": cases,
        "not_drafted": not_drafted,
        "proposed_changes": proposed,
        "draft_pr": {
            "title": title,
            "body": body,
            "opened": False,
            "merged": False,
            "pushed": False,
            "base_branch": None,
            "head_branch": None,
        },
        "foundry_option": _foundry_option(bundle_id, drafted),
        "limits": list(LIMITS),
    }


def assert_out_dir_allowed(out_dir: Path, agent_path: str) -> None:
    resolved = out_dir.resolve()
    if ".git" in resolved.parts:
        raise ProhibitedAction("This generator does not write inside a git directory.")
    if resolved.name.lower() in PROTECTED_BRANCHES:
        raise ProhibitedAction("This generator does not write into a path named as a protected branch.")
    normalised = _relative_path(agent_path, "agent_under_test.path")
    text = resolved.as_posix().rstrip("/")
    if text.endswith("/" + normalised) or f"/{normalised}/" in text + "/":
        raise ProhibitedAction("This generator does not write into the agent under test.")


def write_proposed(out_dir: Path, report: dict[str, Any]) -> None:
    assert_out_dir_allowed(out_dir, report["agent_under_test"]["path"])
    for item in report["proposed_changes"]["files"]:
        target = out_dir / item["path"]
        assert_out_dir_allowed(target.parent, report["agent_under_test"]["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item["content"], encoding="utf-8")


def _skeleton(bundle: dict[str, Any], reading: dict[str, Any], bundle_id: str, agent_id: str, as_of: str) -> dict[str, Any]:
    requested = bundle.get("request_manifest_skeleton") is True
    approve = bundle.get("approve_manifest") is True
    level = bundle.get("skeleton_autonomy") if isinstance(bundle.get("skeleton_autonomy"), str) else "A1"
    if not requested:
        if reading["supplied"]:
            return not_requested("The bundle supplied a manifest. Experiment 03 was not called.")
        return not_requested("No skeleton was requested. Experiment 03 was not called.")
    if reading["supplied"]:
        return not_requested("A manifest was supplied. Experiment 03 was not called.")
    return draft_skeleton(
        bundle_id=bundle_id,
        title=agent_id,
        as_of=as_of,
        autonomy_level=level,
        approve=approve,
    )


def _foundry_option(bundle_id: str, drafted: int) -> dict[str, Any]:
    root = f"proposed-changes/{bundle_id}"
    return {
        "called": False,
        "live_run": "not done",
        "threshold_set": False,
        "query_count": drafted,
        "queries_file": f"{root}/foundry-queries.jsonl",
        "trace_file": f"{root}/foundry-trace.json",
        "pages_opened_on": "2026-11-03",
        "item_schema": "The evaluate-agent page requires a query field on each JSONL line. Extra fields are not in that schema. This file has query only. Traceability is in foundry-trace.json.",
        "unverified": [
            "UK region availability for rubric generation, synthetic dataset creation, and risk and safety evaluators. The region page named from the evaluate-agent page was not opened on 3 November 2026.",
            "Whether the GitHub Copilot harness selects skills by description in the same way the standard-harness generative-orchestration page describes. That page says it describes the standard harness.",
            "A live Microsoft Foundry evaluation has not been run for this starter.",
        ],
    }


def _check_foundry_lines(proposed: dict[str, Any], drafted: int) -> None:
    queries = next(item["content"] for item in proposed["files"] if item["role"] == "foundry_queries")
    lines = [line for line in queries.splitlines() if line.strip()]
    if len(lines) != drafted:
        raise RuntimeError("Foundry query lines must equal the drafted count, with no line for a skipped duplicate.")
    case_files = [item for item in proposed["files"] if item["role"] == "case"]
    if len(case_files) != drafted:
        raise RuntimeError("Case files must equal the drafted count.")
    trace = json.loads(next(item["content"] for item in proposed["files"] if item["role"] == "foundry_trace"))
    if len(trace["lines"]) != drafted or trace["called"] is not False or trace["uploaded"] is not False:
        raise RuntimeError("The Foundry trace must list each drafted case once and must not mark a call or an upload.")


def _guard_paths(bundle: dict[str, Any]) -> None:
    agent = bundle.get("agent_under_test")
    if isinstance(agent, dict):
        _relative_path(agent.get("path"), "agent_under_test.path")


def _require_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{label} must be a short identifier.")
    return value


def _relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProhibitedAction(f"Refusing {label}. A relative path is required.")
    text = value.strip().replace("\\", "/")
    if text.startswith("/") or ".." in Path(text).parts:
        raise ProhibitedAction(f"Refusing {label}. Paths stay relative and do not climb.")
    return text.strip("/")


def _urls(value: Any) -> list[str]:
    found: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, str) and ("http://" in item or "https://" in item):
            found.append(item[:180])

    walk(value)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft regression cases. Do not merge, push, or edit the agent.")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--open-pr", action="store_true")
    args = parser.parse_args(argv)
    if args.merge or args.push or args.approve or args.apply or args.open_pr:
        print(
            "Refusing. This generator does not merge, push, approve, apply, or open a pull request.",
            file=sys.stderr,
        )
        return 2
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        report = generate(bundle, args.as_of, args.stale_after_days)
        if args.out_dir is not None:
            write_proposed(args.out_dir, report)
            report["proposed_changes"]["written_to_disk"] = True
            report["proposed_changes"]["written_into_agent_tree"] = False
            report["agent_under_test_edited"] = False
    except (ProhibitedAction, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
