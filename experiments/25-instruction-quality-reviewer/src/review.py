#!/usr/bin/env python3
"""Score one instruction bundle. Do not edit it and do not deploy it.

The same bundle and the same as-of date produce the same JSON. Instruction
text cannot set owner_approved, diff_applied, or the score. Autonomy A3 is
never the recommendation of this reviewer.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from architecture_bridge import cross_check
    from checklist import CHECKS, evaluate
    from diffing import propose
    from injection import scan_strings, strip_prohibited
    from manifest_bridge import draft_skeleton
    from manifest_yaml import YamlError, load_yaml
    from sources import DEFAULT_STALE_AFTER_DAYS, currency
else:
    from .architecture_bridge import cross_check
    from .checklist import CHECKS, evaluate
    from .diffing import propose
    from .injection import scan_strings, strip_prohibited
    from .manifest_bridge import draft_skeleton
    from .manifest_yaml import YamlError, load_yaml
    from .sources import DEFAULT_STALE_AFTER_DAYS, currency

LABEL = "DRAFT FOR AGENT OWNER REVIEW"
CATALOGUE_ID = "G003"
REPO_ROOT = Path(__file__).resolve().parents[3]


class ProhibitedAction(RuntimeError):
    """The reviewer was asked to approve or apply a change."""


def review(
    bundle: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    approve: bool = False,
    apply: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    if approve or apply:
        raise ProhibitedAction(
            "The reviewer cannot approve a rewrite or apply a diff. The agent owner decides."
        )
    date.fromisoformat(as_of)
    cleaned, ignored_keys = strip_prohibited(bundle)
    if not isinstance(cleaned, dict):
        raise ValueError("The bundle must be a JSON object.")
    documents = _documents(cleaned, base_dir or Path.cwd())
    manifest, manifest_error = _manifest(cleaned, base_dir or Path.cwd())
    checks, actions, view = evaluate(documents, manifest, manifest_error)
    points = sum(check["points"] for check in checks)
    max_points = sum(check["max_points"] for check in checks)
    percent = round(100 * points / max_points, 1) if max_points else 0.0
    blocking = [check["id"] for check in checks if check["result"] == "fail"]
    if blocking:
        band = "blocking"
    elif any(check["result"] == "partial" for check in checks):
        band = "gaps"
    else:
        band = "no_gaps"
    sources = currency(as_of, stale_after_days)
    stale_documents = _document_staleness(documents, as_of, stale_after_days)
    sources_stale = any(row["stale"] for row in sources)
    documents_stale = any(row["stale"] for row in stale_documents)
    do_not_rely = sources_stale or documents_stale
    proposed = propose(documents, checks)
    skeleton = _maybe_skeleton(cleaned, documents, view, as_of, actions)
    architecture = cross_check(cleaned.get("use_case") if isinstance(cleaned.get("use_case"), dict) else None)
    signals = scan_strings(cleaned)
    findings = [check for check in checks if check["result"] != "pass"]
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "25",
        "autonomy": "A0",
        "bundle_id": str(cleaned.get("bundle_id") or ""),
        "title": str(cleaned.get("title") or ""),
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "decision": None,
        "owner_approved": False,
        "diff_applied": False,
        "instructions_edited": False,
        "deployed": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "a3_recommended": False,
        "score": {
            "points": points,
            "max_points": max_points,
            "percent": percent,
            "band": band,
        },
        "blocking": blocking,
        "do_not_rely": do_not_rely,
        "checks": checks,
        "check_ids": [item["id"] for item in CHECKS],
        "findings": findings,
        "actions_seen": actions,
        "proposed_diff": proposed,
        "prompt_injection": {
            "detected": bool(signals),
            "signals": signals,
            "followed": False,
            "prohibited_payload_keys_ignored": ignored_keys,
        },
        "stale": {
            "documents": stale_documents,
            "sources_stale": sources_stale,
            "documents_stale": documents_stale,
            "do_not_rely": do_not_rely,
        },
        "sources": sources,
        "pins_reopened_for_this_experiment": False,
        "manifest_check": view,
        "manifest_skeleton": skeleton,
        "architecture_cross_check": architecture,
        "human_approval": _approval_points(do_not_rely, skeleton),
    }


def _approval_points(do_not_rely: bool, skeleton: dict[str, Any]) -> list[dict[str, Any]]:
    points = [
        {
            "action": "Approve prompt changes",
            "approver": "Agent owner",
            "mandatory": True,
            "rationale": "Catalogue control for G003. The proposed diff stays unapplied.",
        },
        {
            "action": "Accept or reject each finding before a rewrite is kept",
            "approver": "Agent owner",
            "mandatory": True,
            "rationale": "The checklist can miss a paraphrase or flag a line the owner wants to keep.",
        },
    ]
    if skeleton.get("generated"):
        points.append(
            {
                "action": "Rely on the manifest skeleton",
                "approver": "Governance owner",
                "mandatory": True,
                "rationale": "approved is false. The skeleton is not a sign-off.",
            }
        )
    if do_not_rely:
        points.append(
            {
                "action": "Re-open a pinned page or a review date before relying on a citation",
                "approver": "Agent owner",
                "mandatory": True,
                "rationale": "At least one date is older than the threshold, or a review date is missing.",
            }
        )
    return points


def _maybe_skeleton(
    bundle: dict[str, Any],
    documents: list[dict[str, Any]],
    view: dict[str, Any],
    as_of: str,
    actions: list[dict[str, Any]],
) -> dict[str, Any]:
    if view["parsed"]:
        return {
            "generated": False,
            "approved": False,
            "may_be_relied_on": False,
            "reason": "A manifest was supplied. Experiment 03 was not asked to replace it.",
            "experiment_03_called": False,
            "validation_passed": False,
            "autonomy_level": view.get("autonomy"),
            "yaml": None,
            "errors": [],
        }
    requested = "A3" if any(hit["id"] == "autonomy_a3" and hit["polarity"] == "command" for hit in actions) else "A0"
    skeleton = draft_skeleton(
        bundle_id=str(bundle.get("bundle_id") or "bundle"),
        title=str(bundle.get("title") or ""),
        as_of=as_of,
        autonomy_level=requested,
        approve=False,
    )
    skeleton["generated"] = True
    skeleton["approved"] = False
    skeleton["may_be_relied_on"] = False
    return skeleton


def _documents(bundle: dict[str, Any], base_dir: Path) -> list[dict[str, Any]]:
    raw = bundle.get("documents")
    if not isinstance(raw, list) or not raw:
        raise ValueError("The bundle needs a documents list.")
    documents = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Each document must be an object.")
        text = item.get("text")
        if text is None and item.get("text_path"):
            text = _read(base_dir / str(item["text_path"]))
        elif text is None and item.get("repo_path"):
            text = _read(REPO_ROOT / str(item["repo_path"]))
        if not isinstance(text, str):
            raise ValueError("Each document needs text, text_path, or repo_path.")
        documents.append(
            {
                "path": str(item.get("path") or item.get("repo_path") or item.get("text_path") or "instructions.md"),
                "kind": str(item.get("kind") or "system_prompt"),
                "reviewed_on": item.get("reviewed_on"),
                "text": text,
            }
        )
    return documents


def _read(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"Instruction file not found: {path}")
    return path.read_text(encoding="utf-8")


def _manifest(bundle: dict[str, Any], base_dir: Path) -> tuple[dict[str, Any] | None, str | None]:
    raw = bundle.get("manifest")
    if isinstance(raw, dict):
        return raw, None
    path_value = bundle.get("manifest_path") or bundle.get("manifest_repo_path")
    if not path_value:
        return None, None
    if bundle.get("manifest_repo_path"):
        path = REPO_ROOT / str(path_value)
    else:
        path = Path(str(path_value))
        if not path.is_absolute():
            path = base_dir / path
    if not path.is_file():
        return None, f"Manifest file not found: {path}"
    try:
        loaded = load_yaml(path.read_text(encoding="utf-8"))
    except YamlError as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "The manifest did not parse to an object."
    return loaded, None


def _document_staleness(documents: list[dict[str, Any]], as_of: str, stale_after_days: int) -> list[dict[str, Any]]:
    as_of_date = date.fromisoformat(as_of)
    rows = []
    for document in documents:
        reviewed = document.get("reviewed_on")
        row: dict[str, Any] = {"path": document["path"], "reviewed_on": reviewed}
        if not reviewed:
            row["stale"] = True
            row["age_days"] = None
            row["reason"] = "No review date was supplied."
        else:
            reviewed_date = date.fromisoformat(str(reviewed))
            age = (as_of_date - reviewed_date).days
            row["age_days"] = age
            row["stale"] = age > stale_after_days
            row["reason"] = "Older than the threshold." if row["stale"] else "Inside the threshold."
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft an instruction-quality report. Do not apply it.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.approve or args.apply:
        print(
            "The reviewer cannot approve a rewrite or apply a diff. The agent owner decides.",
            file=sys.stderr,
        )
        return 2
    bundle_path = Path(args.bundle)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    report = review(
        bundle,
        args.as_of,
        stale_after_days=args.stale_after_days,
        base_dir=bundle_path.parent,
    )
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
