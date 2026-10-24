#!/usr/bin/env python3
"""Smoke-test the phrase matcher and the time-saving scorer.

The report is a mock smoke test. It is not a model score and it is not a
staff study. The median in the time-saving block is fixture arithmetic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from answer import SIGNPOST, answer_question  # noqa: E402
from corpus import load_register, parse_date  # noqa: E402
from time_saving import score_observations  # noqa: E402

DATASET = Path(__file__).with_name("synthetic_dataset.json")
OBSERVATIONS = Path(__file__).with_name("time_observations.json")
LABEL = (
    "MOCK SMOKE TEST. Phrase matcher on synthetic policies. "
    "Not a model score and not a staff study."
)
# Worked example in eval/time_saving_design.md. Seven grounded pairs, median 160.
FIXTURE_MEDIAN_SECONDS = 160


def _check(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def evaluate_case(case: dict, register: dict) -> dict:
    as_of = parse_date(case.get("as_of", "2026-10-24"))
    result = answer_question(case["question"], register, as_of)
    expect = case["expect"]
    errors: list[str] = []
    _check(errors, result["outcome"] == expect["outcome"], f"outcome {result['outcome']}")
    if "policy_ids" in expect:
        got = sorted(item["policy_id"] for item in result["citations"])
        _check(errors, got == sorted(expect["policy_ids"]), f"policies {got}")
    if "clause_ids" in expect:
        got = sorted(item["clause_id"] for item in result["citations"])
        _check(errors, got == sorted(expect["clause_ids"]), f"clauses {got}")
    if "may_be_relied_on" in expect:
        _check(errors, result["may_be_relied_on"] is expect["may_be_relied_on"], "may_be_relied_on")
    if "review_due" in expect:
        dues = {item["review_due"] for item in result["citations"]}
        _check(errors, dues == {expect["review_due"]}, f"review dates {dues}")
    if expect.get("quotes_withheld"):
        _check(errors, all(item["quote"] is None for item in result["citations"]), "quote was returned")
    if "injection_detected" in expect:
        _check(
            errors,
            result["injection_detected"] is expect["injection_detected"],
            "injection_detected",
        )
    for banned in expect.get("answer_must_not_contain", []):
        _check(errors, banned not in result["answer"], f"answer contained {banned!r}")
    blob = json.dumps(result)
    for banned in expect.get("result_must_not_contain", []):
        _check(errors, banned not in blob, f"result contained {banned!r}")
    _check(errors, result["actions_taken"] == [], "actions_taken")
    _check(errors, result["model_called"] is False, "model_called")
    _check(errors, result["may_send"] is False and result["may_publish"] is False, "side effect")
    if expect["outcome"] == "conflict":
        note = (result["change_note"] or [None])[0]
        _check(errors, note is not None and note["published"] is False, "change note published")
        _check(errors, note is not None and note["accepted_by_policy_owner"] is False, "note accepted")
    if expect["outcome"] in {"i_dont_know", "stale_withheld"}:
        entry = result["unanswered_log_entry"]
        _check(errors, entry is not None and entry["persisted"] is False, "log persisted")
    if expect["outcome"] == "refused_clinical":
        _check(errors, result["signpost"] == SIGNPOST, "signpost")
        _check(errors, result["clinical_advice_given"] is False, "clinical_advice_given")
        _check(errors, "antibiotic" not in result["answer"].lower(), "clinical text in the answer")
    return {
        "id": case["id"],
        "as_of": as_of.isoformat(),
        "outcome": result["outcome"],
        "expected_outcome": expect["outcome"],
        "policy_ids": [item["policy_id"] for item in result["citations"]],
        "may_be_relied_on": result["may_be_relied_on"],
        "passed": not errors,
        "errors": errors,
    }


def build_report() -> dict:
    register = load_register()
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    cases = [evaluate_case(case, register) for case in dataset["cases"]]
    failed = [case for case in cases if not case["passed"]]
    error_count = sum(len(case["errors"]) for case in cases)
    total = len(cases)
    observations = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
    if observations.get("observed") is not False:
        raise SystemExit("time_observations.json must stay marked observed: false")
    timed = score_observations(observations["rows"])
    if timed["median_seconds_saved_on_grounded_items"] != FIXTURE_MEDIAN_SECONDS:
        raise SystemExit(
            "Fixture median drifted. The design's worked example is "
            f"{FIXTURE_MEDIAN_SECONDS} seconds, got {timed['median_seconds_saved_on_grounded_items']}."
        )
    if timed["n_rejected_self_report"] != 1 or timed["n_excluded_ungrounded"] != 1:
        raise SystemExit("The fixture must keep one self-report row and one ungrounded row out of the median.")
    agreement = round(100 * (total - len(failed)) / total, 1) if total else 0
    return {
        "evaluation_label": LABEL,
        "mode": "mock",
        "not_a_model_evaluation": True,
        "not_a_staff_study": True,
        "nhs_trial_figure_not_used": True,
        "corpus_id": register["corpus_id"],
        "fictional_organisation": register["organisation"],
        "summary": {
            "total_cases": total,
            "passed": total - len(failed),
            "failed": len(failed),
            "errors": error_count,
            "agreement_rate": agreement,
        },
        "cases": cases,
        "time_saving": {
            "what_this_is": (
                "Synthetic fixture arithmetic from eval/time_observations.json. "
                "Not a measured saving from staff. Not the NHS trial figure of 43 minutes."
            ),
            "design": "eval/time_saving_design.md",
            "observed": False,
            **timed,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Experiment 06.")
    parser.add_argument("--output", default=None, help="Write the report JSON here as well as stdout.")
    args = parser.parse_args(argv)
    report = build_report()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    summary = report["summary"]
    if summary["failed"] or summary["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
