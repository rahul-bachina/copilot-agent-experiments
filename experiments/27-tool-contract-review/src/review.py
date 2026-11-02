#!/usr/bin/env python3
"""Score one tool contract. Do not modify it, publish a policy, or deploy it.

The same contract and the same as-of date produce the same JSON. Contract
text cannot set contract_approved, diff_applied, policy_published, or the
score. Autonomy A3 is never the recommendation of this reviewer.
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
    from architecture_bridge import cross_check as architecture_cross_check
    from checklist import CHECKS, evaluate
    from diffing import propose
    from injection import scan_strings, strip_prohibited
    from instruction_bridge import cross_check as instruction_cross_check
    from manifest_bridge import draft_skeleton
    from normalise import normalise
    from prohibited import ProhibitedAction
    from sources import DEFAULT_STALE_AFTER_DAYS, currency
    from yaml_reader import YamlError, load_yaml
else:
    from .architecture_bridge import cross_check as architecture_cross_check
    from .checklist import CHECKS, evaluate
    from .diffing import propose
    from .injection import scan_strings, strip_prohibited
    from .instruction_bridge import cross_check as instruction_cross_check
    from .manifest_bridge import draft_skeleton
    from .normalise import normalise
    from .prohibited import ProhibitedAction
    from .sources import DEFAULT_STALE_AFTER_DAYS, currency
    from .yaml_reader import YamlError, load_yaml

LABEL = "DRAFT FOR SECURITY/API OWNER REVIEW"
CATALOGUE_ID = "G005"
REPO_ROOT = Path(__file__).resolve().parents[3]


def review(
    bundle: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    approve: bool = False,
    apply: bool = False,
    publish: bool = False,
    deploy: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    if approve or apply or publish or deploy:
        raise ProhibitedAction(
            "The reviewer cannot approve a contract, apply a diff, publish a policy, or deploy. "
            "The security/API owner decides."
        )
    date.fromisoformat(as_of)
    cleaned, ignored_keys = strip_prohibited(bundle)
    if not isinstance(cleaned, dict):
        raise ValueError("The bundle must be a JSON object.")
    root = base_dir or Path.cwd()
    document, kind = _contract(cleaned, root)
    normalised = normalise(document, kind)
    manifest, manifest_error = _manifest(cleaned, root)
    checks, view = evaluate(normalised, manifest, manifest_error)
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
    contract_stale = _contract_staleness(cleaned, as_of, stale_after_days)
    sources_stale = any(row["stale"] for row in sources)
    do_not_rely = sources_stale or contract_stale["stale"]
    proposed = propose(checks)
    skeleton = _maybe_skeleton(cleaned, view, as_of)
    architecture = architecture_cross_check(
        cleaned.get("use_case") if isinstance(cleaned.get("use_case"), dict) else None,
        normalised["operations"],
    )
    instructions = instruction_cross_check(
        cleaned.get("instructions") if isinstance(cleaned.get("instructions"), str) else None,
        manifest,
        as_of,
        str(cleaned.get("bundle_id") or ""),
    )
    signals = scan_strings(cleaned)
    findings = [check for check in checks if check["result"] != "pass"]
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "27",
        "autonomy": "A0",
        "bundle_id": str(cleaned.get("bundle_id") or ""),
        "title": str(cleaned.get("title") or ""),
        "contract_kind": normalised["kind"],
        "http_contract": normalised["http_contract"],
        "reading_shape_note": (
            None
            if normalised["kind"] == "openapi"
            else "This kind is a reading shape for this reviewer, not a verified vendor export."
        ),
        "operation_ids": [operation["operation_id"] for operation in normalised["operations"]],
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "decision": None,
        "owner_approved": False,
        "contract_approved": False,
        "diff_applied": False,
        "contract_modified": False,
        "policy_published": False,
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
        "proposed_diff": proposed,
        "prompt_injection": {
            "detected": bool(signals),
            "signals": signals,
            "followed": False,
            "prohibited_payload_keys_ignored": ignored_keys,
        },
        "stale": {
            "contract": contract_stale,
            "sources_stale": sources_stale,
            "do_not_rely": do_not_rely,
        },
        "sources": sources,
        "pins_reopened_for_this_experiment": True,
        "manifest_check": view,
        "manifest_skeleton": skeleton,
        "architecture_cross_check": architecture,
        "instruction_review": instructions,
        "human_approval": _approval_points(do_not_rely, skeleton),
    }


def _approval_points(do_not_rely: bool, skeleton: dict[str, Any]) -> list[dict[str, Any]]:
    points = [
        {
            "action": "Approve the contract",
            "approver": "Security/API owner",
            "mandatory": True,
            "rationale": "Catalogue control for G005. The proposed diff stays unapplied.",
        },
        {
            "action": "Approve an API Management policy change before it is published",
            "approver": "Security/API owner",
            "mandatory": True,
            "rationale": "policy_published is false. Placeholders are not a call volume.",
        },
        {
            "action": "Accept or reject each finding before a contract change is kept",
            "approver": "Security/API owner",
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
                "approver": "Security/API owner",
                "mandatory": True,
                "rationale": "At least one date is older than the threshold, or a review date is missing.",
            }
        )
    return points


def _maybe_skeleton(bundle: dict[str, Any], view: dict[str, Any], as_of: str) -> dict[str, Any]:
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
    requested = "A3" if str(bundle.get("requested_autonomy") or "") == "A3" else "A0"
    skeleton = draft_skeleton(
        bundle_id=str(bundle.get("bundle_id") or "bundle"),
        title=str(bundle.get("title") or ""),
        as_of=as_of,
        autonomy_level=requested,
        approve=False,
    )
    skeleton["generated"] = skeleton.get("generator") != "refused"
    skeleton["approved"] = False
    skeleton["may_be_relied_on"] = False
    return skeleton


def _contract(bundle: dict[str, Any], base_dir: Path) -> tuple[dict[str, Any], str | None]:
    kind = bundle.get("contract_kind")
    if kind is not None and not isinstance(kind, str):
        raise ValueError("contract_kind must be a string.")
    raw = bundle.get("contract")
    if isinstance(raw, dict):
        return raw, kind
    path_value = bundle.get("contract_path") or bundle.get("contract_repo_path")
    if not path_value:
        raise ValueError("The bundle needs a contract object, contract_path, or contract_repo_path.")
    if bundle.get("contract_repo_path"):
        path = REPO_ROOT / str(path_value)
    else:
        path = Path(str(path_value))
        if not path.is_absolute():
            path = base_dir / path
    if not path.is_file():
        raise ValueError(f"Contract file not found: {path}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("The contract file did not parse to an object.")
    return loaded, kind


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


def _contract_staleness(bundle: dict[str, Any], as_of: str, stale_after_days: int) -> dict[str, Any]:
    reviewed = bundle.get("reviewed_on")
    row: dict[str, Any] = {"reviewed_on": reviewed}
    as_of_date = date.fromisoformat(as_of)
    if not reviewed:
        row["stale"] = True
        row["age_days"] = None
        row["reason"] = "No review date was supplied."
        return row
    reviewed_date = date.fromisoformat(str(reviewed))
    age = (as_of_date - reviewed_date).days
    row["age_days"] = age
    row["stale"] = age > stale_after_days
    row["reason"] = "Older than the threshold." if row["stale"] else "Inside the threshold."
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a tool-contract review. Do not apply it.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args(argv)
    if args.approve or args.apply or args.publish or args.deploy:
        print(
            "The reviewer cannot approve a contract, apply a diff, publish a policy, or deploy. "
            "The security/API owner decides.",
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
