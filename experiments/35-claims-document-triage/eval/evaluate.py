#!/usr/bin/env python3
"""Deterministic smoke test of the claims document triage.

The fixtures are synthetic. The checker is the Python under src/, which calls
Experiment 12, Experiment 08, and Experiment 29. This is not a model score,
not an LLM-as-a-judge result, and not a Microsoft Foundry score.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.triage import NotSynthetic, score_supplied_summary, triage  # noqa: E402
from tests.support import (  # noqa: E402
    COVERED_CANDIDATE,
    INCOMPLETE_CANDIDATE,
    INVENTED_AMOUNT,
    amount_pack,
    base_pack,
    injection_pack,
    invoice_before_loss_pack,
    name_pack,
    nino_pack,
    not_synthetic_pack,
    period_pack,
    stale_pack,
    two_peril_pack,
)

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which calls Experiment 12 intake, Experiment 08 through that intake, "
    "and Experiment 29 score_claim. Not a measure of model accuracy. "
    "Not an LLM-as-a-judge result. No model was called."
)

AS_OF = "2026-11-05"


def _cases() -> list[dict]:
    return [
        {
            "id": "reedmarsh-consistent",
            "name": "Consistent escape-of-water pack",
            "as_of": AS_OF,
            "pack": base_pack(),
            "expect": {
                "outcome": "draft",
                "proposed_class": "escape_of_water",
                "below_threshold": False,
                "do_not_rely": False,
                "injection_detected": False,
                "prompt_prefix": None,
            },
        },
        {
            "id": "reedmarsh-amount",
            "name": "Stated amount and invoice total differ",
            "as_of": AS_OF,
            "pack": amount_pack(),
            "expect": {
                "outcome": "draft",
                "proposed_class": "escape_of_water",
                "below_threshold": False,
                "prompt_prefix": "amount_check:",
            },
        },
        {
            "id": "reedmarsh-period",
            "name": "Date of loss outside the printed period",
            "as_of": AS_OF,
            "pack": period_pack(),
            "expect": {
                "outcome": "draft",
                "below_threshold": False,
                "do_not_rely": False,
                "prompt_prefix": "period_check:",
            },
        },
        {
            "id": "reedmarsh-invoice-before-loss",
            "name": "Invoice date before the date of loss",
            "as_of": AS_OF,
            "pack": invoice_before_loss_pack(),
            "expect": {
                "outcome": "draft",
                "below_threshold": False,
                "prompt_prefix": "invoice_date_before_loss:",
            },
        },
        {
            "id": "reedmarsh-injection",
            "name": "Hidden instruction to decline",
            "as_of": AS_OF,
            "pack": injection_pack(),
            "expect": {
                "outcome": "draft",
                "injection_detected": True,
                "injection_followed": False,
                "below_threshold": False,
            },
        },
        {
            "id": "reedmarsh-stale",
            "name": "Invoice document date outside the freshness window",
            "as_of": AS_OF,
            "pack": stale_pack(),
            "expect": {
                "outcome": "draft",
                "do_not_rely": True,
                "below_threshold": False,
                "prompt_prefix": "date_not_current:",
            },
        },
        {
            "id": "reedmarsh-nino",
            "name": "Invoice carries a non-allocatable National Insurance fixture",
            "as_of": AS_OF,
            "pack": nino_pack(),
            "expect": {
                "outcome": "draft",
                "withheld_file": "invoice",
                "absent": ["QQ 12 34 56 A", "QQ123456A"],
                "output_is_anonymised": False,
            },
        },
        {
            "id": "reedmarsh-two-perils",
            "name": "Two peril lines",
            "as_of": AS_OF,
            "pack": two_peril_pack(),
            "expect": {
                "outcome": "draft",
                "proposed_class": "not_proposed",
                "prompt_id": "class_not_single",
            },
        },
        {
            "id": "reedmarsh-name",
            "name": "Policyholder line and invoice addressee differ",
            "as_of": AS_OF,
            "pack": name_pack(),
            "expect": {
                "outcome": "draft",
                "below_threshold": False,
                "prompt_prefix": "name_check:",
            },
        },
        {
            "id": "reedmarsh-not-synthetic",
            "name": "Pack is not marked synthetic",
            "as_of": AS_OF,
            "pack": not_synthetic_pack(),
            "expect": {"outcome": "refused", "absent": ["TOKEN-NOT-IN-THE-REFUSAL"]},
        },
        {
            "id": "reedmarsh-covered-sentence",
            "name": "Supplied summary states a coverage outcome",
            "as_of": AS_OF,
            "pack": base_pack(),
            "candidate": COVERED_CANDIDATE,
            "expect": {
                "outcome": "candidate",
                "human_escalation_required": True,
                "criterion": "unsupported_coverage",
            },
        },
        {
            "id": "reedmarsh-invented-amount",
            "name": "Supplied summary uses a figure that is not in the cited line",
            "as_of": AS_OF,
            "pack": base_pack(),
            "candidate": INVENTED_AMOUNT,
            "expect": {
                "outcome": "candidate",
                "human_escalation_required": True,
                "criterion": "faithfulness",
            },
        },
        {
            "id": "reedmarsh-incomplete",
            "name": "Supplied summary omits the date of loss",
            "as_of": AS_OF,
            "pack": base_pack(),
            "candidate": INCOMPLETE_CANDIDATE,
            "expect": {
                "outcome": "candidate",
                "human_escalation_required": True,
                "criterion": "completeness",
                "faithfulness_rate": 1.0,
            },
        },
    ]


def _add(checks: list[dict], field: str, passed: bool, detail: str) -> None:
    checks.append({"field": field, "passed": passed, "detail": detail})


def _outcome_flags(draft: dict, checks: list[dict]) -> None:
    for flag in (
        "claim_accepted",
        "claim_declined",
        "claim_settled",
        "customer_told",
        "claims_system_written",
        "fraud_indicated",
        "coverage_decided",
        "a3_recommended",
    ):
        _add(checks, flag, draft[flag] is False, "stays false")
    _add(checks, "customer_message", draft["customer_message"] is None, "no customer message")
    _add(checks, "model_called", draft["model_called"] is False, "no model")
    _add(checks, "classification_approved", draft["classification_approved_by_handler"] is False, "handler has not recorded a class")
    _add(checks, "llm_as_judge", draft["scorecard"]["llm_as_judge"] is False, "deterministic checker")


def evaluate_case(case: dict) -> dict:
    checks: list[dict] = []
    expect = case["expect"]
    as_of = date.fromisoformat(case["as_of"])

    def finish(status: str, extra: dict | None = None) -> dict:
        if any(not item["passed"] for item in checks):
            status = "failed"
        row = {
            "case_id": case["id"],
            "name": case["name"],
            "status": status,
            "checks": checks,
            "human_escalation_required": False,
        }
        if extra:
            row.update(extra)
        return row

    if expect.get("outcome") == "refused":
        try:
            triage(case["pack"], as_of=as_of)
        except NotSynthetic as exc:
            message = str(exc)
            _add(checks, "refused", True, "NotSynthetic")
            for index, token in enumerate(expect.get("absent", []), start=1):
                _add(checks, f"absent {index}", token not in message, "not in the refusal")
            return finish("passed")
        except Exception as exc:  # noqa: BLE001
            return {
                "case_id": case["id"],
                "name": case["name"],
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "checks": checks,
                "human_escalation_required": False,
            }
        _add(checks, "refused", False, "triage returned a draft")
        return finish("failed")

    try:
        draft = triage(case["pack"], as_of=as_of)
    except Exception as exc:  # noqa: BLE001
        return {
            "case_id": case["id"],
            "name": case["name"],
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "checks": checks,
            "human_escalation_required": False,
        }

    _outcome_flags(draft, checks)
    if "proposed_class" in expect:
        _add(
            checks,
            "proposed_class",
            draft["classification"]["proposed_class"] == expect["proposed_class"],
            draft["classification"]["proposed_class"],
        )
    if "below_threshold" in expect:
        _add(
            checks,
            "below_threshold",
            draft["scorecard"]["below_threshold"] is expect["below_threshold"],
            str(draft["scorecard"]["criteria_below_threshold"]),
        )
    if "do_not_rely" in expect:
        _add(checks, "do_not_rely", draft["do_not_rely"] is expect["do_not_rely"], str(draft["do_not_rely"]))
    if "injection_detected" in expect:
        _add(
            checks,
            "injection_detected",
            draft["prompt_injection"]["detected"] is expect["injection_detected"],
            str(draft["prompt_injection"]["detected"]),
        )
    if "injection_followed" in expect:
        _add(
            checks,
            "injection_followed",
            draft["prompt_injection"]["followed"] is expect["injection_followed"],
            str(draft["prompt_injection"]["followed"]),
        )
    if expect.get("prompt_prefix"):
        found = any(item["id"].startswith(expect["prompt_prefix"]) for item in draft["inconsistency_prompts"])
        _add(checks, "prompt", found, expect["prompt_prefix"])
    if expect.get("prompt_id"):
        found = any(item["id"] == expect["prompt_id"] for item in draft["inconsistency_prompts"])
        _add(checks, "prompt", found, expect["prompt_id"])
    if expect.get("withheld_file"):
        file_id = expect["withheld_file"]
        row = next(item for item in draft["files"] if item["file_id"] == file_id)
        _add(checks, "withheld", row["withheld_for_identifier"] is True, file_id)
    if "output_is_anonymised" in expect:
        _add(
            checks,
            "output_is_anonymised",
            draft["output_is_anonymised"] is expect["output_is_anonymised"],
            str(draft["output_is_anonymised"]),
        )
    blob = json.dumps(draft)
    for index, token in enumerate(expect.get("absent", []), start=1):
        _add(checks, f"absent {index}", token not in blob, "not in the draft")
    for prompt in draft["inconsistency_prompts"]:
        _add(checks, f"prompt {prompt['id']} is not a finding", prompt["is_a_finding"] is False, "prompt")

    escalated = bool(draft["scorecard"]["human_escalation_required"])
    extra = {"human_escalation_required": escalated}

    if expect.get("outcome") == "candidate":
        card = score_supplied_summary(case["pack"], case["candidate"], as_of=as_of)
        _add(checks, "candidate_declined", card["claim_declined"] is False, "a score does not decline")
        _add(
            checks,
            "candidate_escalation",
            card["human_escalation_required"] is expect["human_escalation_required"],
            str(card["criteria_below_threshold"]),
        )
        if expect.get("criterion"):
            _add(
                checks,
                "criterion",
                expect["criterion"] in card["criteria_below_threshold"],
                str(card["criteria_below_threshold"]),
            )
        if "faithfulness_rate" in expect:
            _add(
                checks,
                "faithfulness_rate",
                card["faithfulness"]["supported_rate"] == expect["faithfulness_rate"],
                str(card["faithfulness"]["supported_rate"]),
            )
        extra["human_escalation_required"] = bool(card["human_escalation_required"])
        extra["criteria_below_threshold"] = card["criteria_below_threshold"]

    return finish("passed", extra)


def evaluate(cases: list[dict] | None = None) -> dict:
    rows = [evaluate_case(case) for case in (cases if cases is not None else _cases())]
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    errors = sum(1 for row in rows if row["status"] == "error")
    escalated = sum(1 for row in rows if row.get("human_escalation_required"))
    summary = {
        "case_count": len(rows),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "cases_escalated": escalated,
        "scores_are_not_summed_across_criteria": True,
        "case_count_is_not_added_to_escalated": True,
        "escalated_is_a_case_count": True,
    }
    if summary["case_count"] + summary["cases_escalated"] in summary.values():
        raise RuntimeError("Smoke summary would store a sum of the case count and the escalation count.")
    return {
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_an_llm_judge": True,
        "not_a_foundry_score": True,
        "evaluation_label": SMOKE_LABEL,
        "summary": summary,
        "cases": rows,
    }


def write_dataset(path: Path) -> None:
    """Publish the fixture list without the Python builders."""

    payload = {
        "label": SMOKE_LABEL,
        "note": "Synthetic fixtures for the fictional firm Reedmarsh General. Not a model evaluation.",
        "cases": [
            {
                "id": case["id"],
                "name": case["name"],
                "as_of": case["as_of"],
                "pack": case["pack"],
                "candidate": case.get("candidate"),
                "expect": case["expect"],
            }
            for case in _cases()
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic claims-triage smoke test.")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    if summary["failed"] or summary["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
