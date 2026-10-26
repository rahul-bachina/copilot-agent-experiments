#!/usr/bin/env python3
"""Mock smoke test for the correspondence drafter.

The fixtures are synthetic. The drafter is a keyword stand-in. This is not a
model evaluation. A Microsoft Foundry run has not been done.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from draft import draft_correspondence, validate_draft  # noqa: E402

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "synthetic_dataset.json"
SMOKE_LABEL = (
    "MOCK SMOKE TEST. Rule-based stand-in tuned to the synthetic fixtures. "
    "Not a measure of model accuracy. No model was called."
)


def _check(case: dict, result: dict) -> list[str]:
    errors = []
    expect = case["expect"]
    validate_draft(result)

    def need(name: str, actual, expected) -> None:
        if actual != expected:
            errors.append(f"{name}: expected {expected!r}, got {actual!r}")

    need("channel", result["classification"]["channel"], expect["channel"])
    need("cited", [line["id"] for line in result["lines_cited"]], expect["cited_line_ids"])
    need("specialist_route", result["classification"]["specialist_route"], expect["specialist_route"])
    need("gaps", [gap["topic"] for gap in result["gaps"]], expect["gap_topics"])
    need("injection", result["security"]["prompt_injection_detected"], expect["injection"])
    need("stale", bool(result["security"]["stale_data_signals"]), expect["stale"])
    need("vulnerability", bool(result["vulnerability"]["flags"]), expect["vulnerability"])
    need("immediate_review", result["vulnerability"]["requires_immediate_human_review"], expect["immediate_review"])
    need("may_be_sent", result["draft"]["may_be_sent_by_agent"], False)
    need("recipient_approved", result["recipient"]["approved"], False)
    need("actions", result["security"]["actions_taken"], [])
    need("labelled", result["vulnerability"]["person_labelled_vulnerable"], False)
    need("auto_closed", result["vulnerability"]["case_auto_closed"], False)
    need("atrs_submitted", result["atrs_draft"]["not_submitted"], True)
    need("scope_decided", result["atrs_draft"]["mandatory_scope_decided"], False)
    need("holding_clears", result["sla"]["holding_reply_clears_deadline"], False)
    need("sla_operative", result["sla"]["operative"], expect["sla_operative"])
    need("due_on", result["sla"]["operative_due_on"], expect["due_on"])
    need("sla_reason", result["sla"]["reason"], expect["sla_reason"])
    if "complaints" in expect:
        need("complaints", result["classification"]["complaints_process_flag"], expect["complaints"])
    if "media" in expect:
        need("media", result["classification"]["media_flag"], expect["media"])
    if "welsh" in expect:
        need("welsh", result["classification"]["welsh_language_review"], expect["welsh"])
    if "refused_contains" in expect:
        refused = [line["id"] for line in result["lines_refused"]]
        for line_id in expect["refused_contains"]:
            if line_id not in refused:
                errors.append(f"refused missing {line_id}")
    forbidden = expect.get("draft_must_not_contain", "")
    if forbidden and forbidden.lower() in result["draft"]["text"].lower():
        errors.append(f"draft contained forbidden text: {forbidden}")
    if "vulnerable" in result["draft"]["text"].lower():
        errors.append("draft used the word vulnerable")
    return errors


def evaluate(dataset_path: Path = DATASET) -> dict:
    cases = json.loads(dataset_path.read_text(encoding="utf-8"))
    results = []
    failed = 0
    for case in cases:
        try:
            draft = draft_correspondence(
                case["text"],
                date.fromisoformat(case["received_on"]),
                date.fromisoformat(case["as_of"]),
                regime=case.get("regime", "central_government"),
                target_working_days=case.get("target_working_days", 20),
                confirm_target=case.get("confirm_target", False),
                confirm_channel=case.get("confirm_channel", False),
            )
            errors = _check(case, draft)
        except Exception as exc:  # noqa: BLE001 — a smoke run should record the failure, not hide it.
            errors = [f"exception: {exc}"]
            draft = None
        if errors:
            failed += 1
        results.append(
            {
                "id": case["id"],
                "passed": not errors,
                "errors": errors,
                "channel": None if draft is None else draft["classification"]["channel"],
            }
        )
    total = len(cases)
    return {
        "mode": "mock",
        "not_a_model_evaluation": True,
        "evaluation_label": SMOKE_LABEL,
        "dataset": dataset_path.name,
        "summary": {
            "total_cases": total,
            "passed": total - failed,
            "failed": failed,
            "errors": failed,
            "agreement_rate": 0 if total == 0 else round(100 * (total - failed) / total, 1),
        },
        "cases": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the mock correspondence smoke test.")
    parser.add_argument("--dataset", default=str(DATASET))
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    report = evaluate(Path(args.dataset))
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
