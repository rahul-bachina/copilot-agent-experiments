#!/usr/bin/env python3
"""Deterministic smoke test of the sentiment evidence pack.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence import LABEL_DRAFT, LABEL_READY, LABEL_REFUSED, prepare_pack, record_review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    result = prepare_pack(case["batch"], case["as_of"])
    if "review" in case:
        result = record_review(result, case["review"])
    return result


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = _run(case)
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": str(exc),
            "checks": [],
        }

    checks: list[dict] = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    blob = json.dumps(result)
    add("catalogue", result["catalogue_id"] == "C010", result["catalogue_id"])
    add("autonomy", result["autonomy"] == "A0", result["autonomy"])
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("executed", result["executed"] is False, "false")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("text_echoed", result["text_echoed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("human_route", result["human_route"]["offered"] is True, "true")
    add("agent_publishes", result["human_route"]["agent_publishes"] is False, "false")
    add("agent_contacts", result["human_route"]["agent_contacts"] is False, "false")
    flags = result["flags"]
    for key in (
        "published",
        "contacted_customer",
        "individual_conclusion",
        "board_report_approved",
        "duty_met",
        "outcome_tested",
        "quotes_meet_article_4_1_5",
        "output_is_anonymised",
    ):
        add(key, flags[key] is False, "false")
    testing = result.get("outcome_testing") or {}
    if testing:
        add("not_the_board_report", testing.get("is_the_prin_2a_8_report") is False, "false")
        add("no_finding", testing.get("finding") is None, "null")

    distribution = result.get("distribution")
    if isinstance(distribution, dict) and distribution.get("overall"):
        overall = distribution["overall"]
        add("counts_sum", sum(overall["counts"].values()) == overall["n"], str(overall["n"]))
        add("channel_n", distribution["channel_n_equals_overall"] is True, "true")
        add("period_n", distribution["period_n_equals_overall"] is True, "true")
        add(
            "voice_n",
            result["counts"]["unique_voices"] == overall["n"] == len(result["voices"]),
            str(result["counts"]["unique_voices"]),
        )
        add(
            "in_frame_split",
            result["counts"]["in_frame_records"]
            == len(result["voices"]) + len(result["not_counted_as_extra_voices"]),
            str(result["counts"]["in_frame_records"]),
        )

    reviewed = "review" in case
    if reviewed:
        add("review_executed", result["review"]["executed"] is False, "false")
        if expect.get("review_accepted") is True:
            add("review_accepted", result["review"]["accepted"] is True, result["review"]["reason"])
        elif expect.get("review_accepted") is False:
            add("review_refused", result["review"]["refused"] is True, result["review"]["reason"])
    if "review_reason" in expect:
        add("review_reason", result["review"]["reason"] == expect["review_reason"], result["review"]["reason"])
    if "ready" in expect:
        add("ready", result["ready"] is expect["ready"], str(result["ready"]))
    if expect.get("human_approval_null") is True:
        add("human_approval", result["human_approval"] is None, "null")
    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "label" in expect:
        expected_label = {"draft": LABEL_DRAFT, "ready": LABEL_READY, "refused": LABEL_REFUSED}[expect["label"]]
        add("label", result["label"] == expected_label, result["label"][:48])
    if "unique_voices" in expect:
        add("unique_voices", result["counts"]["unique_voices"] == expect["unique_voices"], str(result["counts"]["unique_voices"]))
    if "signal" in expect:
        signals = [row["signal"] for row in result["prompt_injection"]["signals"]]
        add("signal", expect["signal"] in signals, str(signals))
    if "hidden_in" in expect:
        carriers = [row["hidden_in"] for row in result["prompt_injection"]["signals"]]
        add("hidden_in", expect["hidden_in"] in carriers, str(carriers))
    if "absent" in expect:
        add("absent", expect["absent"] not in blob, "absent")
    if "present" in expect:
        add("present", expect["present"] in blob, "present")
    if "rules_current" in expect:
        add("rules_current", result["stale"]["rules_current"] is expect["rules_current"], str(result["stale"]["rules_current"]))
    if expect.get("quotes_withheld") is True:
        add("quotes_withheld", all(row["taken"] is None for row in result["sources"]), "withheld")
    if "prin_applied" in expect:
        add("prin_applied", result["outcome_testing"]["applied"] is expect["prin_applied"], str(result["outcome_testing"]["applied"]))
    if "complaints_called" in expect:
        add(
            "complaints_called",
            result["complaints_root_cause"]["called"] is expect["complaints_called"],
            str(result["complaints_root_cause"]["called"]),
        )
    if "complaint_theme" in expect:
        rows = {row["record_id"]: row["theme"] for row in result["complaints_root_cause"]["rows"]}
        add("complaint_theme", rows.get(expect["complaint_record"]) == expect["complaint_theme"], str(rows))
    if "sampling_bias" in expect:
        row = next(item for item in result["limitations"] if item["id"] == "sampling_bias")
        add("sampling_bias", row["applies"] is expect["sampling_bias"], str(row["applies"]))
    if "small_numbers" in expect:
        row = next(item for item in result["limitations"] if item["id"] == "small_numbers")
        add("small_numbers", row["applies"] is expect["small_numbers"], str(row["applies"]))
    if "number_verified" in expect:
        source = next(item for item in result["sources"] if item["id"] == expect["number_verified"]["id"])
        add(
            "number_verified",
            source["number_verified"] is expect["number_verified"]["value"],
            str(source["number_verified"]),
        )

    failed = [check for check in checks if not check["passed"]]
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "passed" if not failed else "failed",
        "checks": checks,
        "failed": [check["field"] for check in failed],
    }


def evaluate(dataset: dict | None = None) -> dict:
    if dataset is None:
        dataset = load_dataset()
    cases = [evaluate_case(case) for case in dataset["cases"]]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = sum(1 for case in cases if case["status"] == "failed")
    errors = sum(1 for case in cases if case["status"] == "error")
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "model_called": False,
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "agreement_rate": round(100 * passed / len(cases), 2) if cases else 0,
        },
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test. Not a model score.")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
