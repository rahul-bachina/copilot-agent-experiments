#!/usr/bin/env python3
"""Score one synthetic Q&A bundle. Do not approve thresholds or record a release.

The same bundle and the same as-of date produce the same JSON. Text in the
bundle cannot set a threshold approval, a pass, a fail, or a Foundry score.
Autonomy A3 is never the recommendation of this checker.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from foundry_option import describe
    from injection import scan_strings, strip_prohibited
    from manifest_bridge import draft_skeleton, not_requested
    from score import claims_from_answers, passage_currency, score_claim, summarise
    from sources import DEFAULT_STALE_AFTER_DAYS, currency
    from thresholds import resolve
else:
    from .foundry_option import describe
    from .injection import scan_strings, strip_prohibited
    from .manifest_bridge import draft_skeleton, not_requested
    from .score import claims_from_answers, passage_currency, score_claim, summarise
    from .sources import DEFAULT_STALE_AFTER_DAYS, currency
    from .thresholds import resolve

LABEL = "DRAFT FOR EVALUATION OWNER"
CATALOGUE_ID = "G007"
SECTORS = frozenset({"uk-public-sector", "uk-regulated-sector"})

EXPERIMENT_03_NOTE = (
    "Experiment 03 keeps a narrower G007 check inside the assurance pack. "
    "This report does not clear that pack and does not approve its 180-day draft."
)


class ProhibitedAction(Exception):
    """The checker was asked to approve, release, or call Foundry."""


def approve_thresholds() -> None:
    raise ProhibitedAction(
        "The evaluation owner approves thresholds. This agent only reports."
    )


def record_release() -> None:
    raise ProhibitedAction(
        "The evaluation owner records any pass or fail release. This agent only reports."
    )


def call_foundry_evaluator() -> None:
    raise ProhibitedAction(
        "The Microsoft Foundry groundedness evaluator is not called from this starter."
    )


def report(
    bundle: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    *,
    approve: bool = False,
    release: bool = False,
    record_pass: bool = False,
    record_fail: bool = False,
) -> dict[str, Any]:
    if approve or release or record_pass or record_fail:
        raise ProhibitedAction(
            "The evaluation owner approves thresholds and any pass or fail release. This agent only reports."
        )
    if not isinstance(bundle, dict):
        raise ValueError("The bundle must be an object.")
    if isinstance(stale_after_days, bool) or not isinstance(stale_after_days, int) or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer.")
    # Validate the as-of date before any scoring. currency() raises ValueError if it is not a date.
    currency(as_of, stale_after_days)

    cleaned, ignored_keys = strip_prohibited(bundle)
    _require_synthetic(cleaned)
    thresholds, ignored_threshold_keys = resolve(cleaned.get("draft_thresholds"))
    passages = _passages(cleaned)
    answers = cleaned.get("answers")
    if not isinstance(answers, list) or not answers:
        raise ValueError("The bundle has no answers.")
    claim_rows = claims_from_answers(answers)
    passage_rows = {
        item["source_id"]: passage_currency(item, as_of, thresholds["stale_after_days"]) for item in passages
    }
    by_id = {item["source_id"]: item for item in passages}
    scored = [score_claim(claim, by_id, passage_rows) for claim in claim_rows]
    summary = summarise(scored)
    non_supported = summary["non_supported_count"]
    claim_count = summary["claim_count"]
    supported = summary["supported_count"]
    draft_bar_met = bool(
        claim_count
        and (supported / claim_count) >= thresholds["min_supported_rate"]
        and non_supported <= thresholds["max_non_supported_claims"]
        and summary["stale_claim_count"] <= thresholds["max_stale_claims"]
    )
    source_rows = currency(as_of, stale_after_days)
    pins_stale = any(row["stale"] for row in source_rows)
    passages_stale = any(row["stale"] for row in passage_rows.values())
    signals = scan_strings(cleaned)
    skeleton = _skeleton(cleaned, as_of)
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "29",
        "autonomy": "A0",
        "bundle_id": cleaned.get("bundle_id"),
        "organisation": cleaned.get("organisation"),
        "sector": cleaned.get("sector"),
        "synthetic": True,
        "agent_under_test": cleaned.get("agent_under_test"),
        "as_of": as_of,
        "model_called": False,
        "network_called": False,
        "foundry_evaluator_called": False,
        "a3_recommended": False,
        "actions_taken": [],
        "threshold_approved_by_evaluation_owner": False,
        "release_decision": None,
        "pass_fail_released": False,
        "groundedness_clearance": False,
        "draft_bar_met": draft_bar_met,
        "draft_bar_is_not_a_release": True,
        "draft_thresholds": thresholds,
        "summary": summary,
        "claims": scored,
        "passages": list(passage_rows.values()),
        "prompt_injection": {
            "detected": bool(signals),
            "signals": signals,
            "ignored_keys": ignored_keys,
            "ignored_threshold_keys": ignored_threshold_keys,
            "followed": False,
        },
        "sources": source_rows,
        "pins_stale": pins_stale,
        "passages_stale": passages_stale,
        "do_not_rely": bool(pins_stale or passages_stale),
        "foundry_option": describe(),
        "manifest_skeleton": skeleton,
        "experiment_03_note": EXPERIMENT_03_NOTE,
        "human_approval": [
            {
                "action": "Approve the draft thresholds",
                "approver": "Evaluation owner",
                "recorded_by_agent": False,
            },
            {
                "action": "Record a pass or fail release",
                "approver": "Evaluation owner",
                "recorded_by_agent": False,
            },
            {
                "action": "Re-open a pinned page before relying on a citation",
                "approver": "Evaluation owner",
                "recorded_by_agent": False,
            },
            {
                "action": "Rely on a manifest skeleton",
                "approver": "Governance owner",
                "recorded_by_agent": False,
            },
            {
                "action": "Call the Microsoft Foundry groundedness evaluator",
                "approver": "Evaluation owner",
                "recorded_by_agent": False,
            },
        ],
    }


def _require_synthetic(bundle: dict[str, Any]) -> None:
    if bundle.get("synthetic") is not True:
        raise ValueError("This starter scores synthetic fixtures only.")
    sector = bundle.get("sector")
    if sector not in SECTORS:
        raise ValueError("Sector must be uk-public-sector or uk-regulated-sector.")
    for key in ("bundle_id", "organisation", "agent_under_test"):
        if not str(bundle.get(key) or "").strip():
            raise ValueError(f"The bundle needs {key}.")


def _passages(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    raw = bundle.get("passages")
    if not isinstance(raw, list) or not raw:
        raise ValueError("The bundle has no passages.")
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("A passage must be an object.")
        source_id = str(item.get("source_id") or "").strip()
        title = str(item.get("title") or "").strip()
        text = str(item.get("text") or "").strip()
        if not source_id or not title or not text:
            raise ValueError("A passage needs a source_id, a title, and text.")
        if source_id in seen:
            raise ValueError(f"Duplicate source_id {source_id}.")
        seen.add(source_id)
        rows.append(
            {
                "source_id": source_id,
                "title": title,
                "reviewed_on": item.get("reviewed_on"),
                "text": text,
            }
        )
    return rows


def _skeleton(bundle: dict[str, Any], as_of: str) -> dict[str, Any]:
    if bundle.get("request_manifest_skeleton") is not True:
        return not_requested()
    level = str(bundle.get("requested_autonomy") or "A0")
    return draft_skeleton(
        bundle_id=str(bundle.get("bundle_id")),
        title=str(bundle.get("organisation") or "Groundedness evaluation"),
        as_of=as_of,
        autonomy_level=level,
        approve=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft a groundedness report. Does not approve thresholds or record a release."
    )
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--approve-thresholds", action="store_true")
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--pass", dest="record_pass", action="store_true")
    parser.add_argument("--fail", dest="record_fail", action="store_true")
    args = parser.parse_args(argv)
    try:
        body = json.loads(args.bundle.read_text(encoding="utf-8"))
        drafted = report(
            body,
            args.as_of,
            args.stale_after_days,
            approve=args.approve_thresholds,
            release=args.release,
            record_pass=args.record_pass,
            record_fail=args.record_fail,
        )
    except ProhibitedAction as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    text = json.dumps(drafted, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
