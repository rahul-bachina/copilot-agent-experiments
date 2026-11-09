#!/usr/bin/env python3
"""Deterministic smoke test of the case routing proposal.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.routing import LABEL, propose_route, record_review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    result = propose_route(case["case"], case["as_of"])
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
    add("label", result["label"] == LABEL, result["label"])
    add("catalogue", result["catalogue_id"] == "C003", result["catalogue_id"])
    add("autonomy", result["autonomy"] == "A1", result["autonomy"])
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("executed", result["executed"] is False, "false")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("echoed", result["case_text_echoed"] is False, "false")
    add("followed", result["prompt_injection"]["followed"] is False, "false")
    add("rerouted", result["flags"]["rerouted"] is False, "false")
    add("closed", result["flags"]["closed"] is False, "false")
    add("escalated", result["flags"]["escalated"] is False, "false")
    add("rules_changed", result["flags"]["rules_changed"] is False, "false")
    add("queue_changed", result["flags"]["queue_changed"] is False, "false")
    add("priority_changed", result["flags"]["priority_changed"] is False, "false")
    add("labelled", result["flags"]["person_labelled_vulnerable"] is False, "false")
    add("feature", result["flags"]["protected_characteristic_used_as_a_feature"] is False, "false")
    add("override", result["flags"]["confidence_overrode_human_route"] is False, "false")
    add("clock_route", result["flags"]["clock_applied_as_a_route"] is False, "false")
    add("sent", result["flags"]["message_sent"] is False, "false")
    add("entitlement", result["flags"]["entitlement_decided"] is False, "false")
    add("human_offered", result["human_route"]["offered"] is True, "true")
    add("phone", result["human_route"]["phone_published"] is False, "false")
    add("not_anonymised", result["pii_gateway"]["output_is_anonymised"] is False, "false")
    add("exp01", result["classification"]["experiment_01_model_called"] is False, "false")
    add("date_calculated", result["statutory_clock"]["date_calculated"] is False, "false")
    add("confidence_override", result["confidence"]["overrides_human_route"] is False, "false")

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "queue" in expect:
        add("queue", result["proposed_queue"] == expect["queue"], str(result["proposed_queue"]))
    if "priority" in expect:
        add("priority", result["priority"] == expect["priority"], str(result["priority"]))
    if "band" in expect:
        add("band", result["confidence"]["band"] == expect["band"], result["confidence"]["band"])
    if "injection_detected" in expect:
        add(
            "injection_detected",
            result["prompt_injection"]["detected"] is expect["injection_detected"],
            str(result["prompt_injection"]["detected"]),
        )
    if expect.get("human_approval_null") is True:
        add("human_approval", result["human_approval"] is None, "null")
    if "review_accepted" in expect:
        add("review_accepted", result["review"]["accepted"] is expect["review_accepted"], result["review"]["reason"])
        add("review_executed", result["review"]["executed"] is False, "false")
    if "review_reason" in expect:
        add("review_reason", result["review"]["reason"] == expect["review_reason"], result["review"]["reason"])
    if "primary_type" in expect:
        add("primary_type", result["classification"]["primary_type"] == expect["primary_type"], result["classification"]["primary_type"])
    if "clock_called" in expect:
        clocks = [
            row.get("clock")
            for row in result["statutory_clock"]["citations"]
            if row.get("kind") == "awaabs"
        ]
        called = bool(clocks and clocks[0] and clocks[0]["called"] is True)
        add("clock_called", called is expect["clock_called"], str(called))
        if clocks and clocks[0]:
            add("clock_operative", clocks[0]["any_operative_deadline"] is False, "false")
            add("clock_approval", clocks[0]["officer_approved_category_passed"] is False, "false")
    if "rule_change_status" in expect:
        actual = None if result["rule_change"] is None else result["rule_change"]["status"]
        add("rule_change_status", actual == expect["rule_change_status"], str(actual))
    if "finding_at_least" in expect:
        count = result["vulnerability"].get("finding_count") or 0
        add("finding_at_least", count >= expect["finding_at_least"], str(count))
    if "statutory_present" in expect:
        add(
            "statutory_present",
            result["statutory_clock"]["present"] is expect["statutory_present"],
            str(result["statutory_clock"]["present"]),
        )
    for snippet in expect.get("absent", []):
        add(f"absent {snippet}", snippet not in blob, snippet)
    for snippet in expect.get("present", []):
        add(f"present {snippet}", snippet in blob, snippet)

    failed = [item for item in checks if not item["passed"]]
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "failed" if failed else "passed",
        "checks": checks,
    }


def summarise(results: list[dict]) -> dict:
    """Count each case once. Check rows are not added to the case total."""
    errors = [item for item in results if item["status"] == "error"]
    failed = [item for item in results if item["status"] == "failed"]
    passed = [item for item in results if item["status"] == "passed"]
    total = len(results)
    if len(passed) + len(failed) + len(errors) != total:
        raise RuntimeError("case statuses were counted more than once")
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of case routing")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset)
    ids = [case["id"] for case in dataset["cases"]]
    if len(ids) != len(set(ids)):
        sys.stderr.write("Duplicate case ids\n")
        return 1
    results = [evaluate_case(case) for case in dataset["cases"]]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_label": dataset.get("label"),
        "organisation_in_fixtures": dataset.get("organisation"),
        "summary": summary,
        "cases": results,
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        out = Path(__file__).parent / "smoke_report.json"
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["total_cases"] < 16:
        sys.stderr.write("Fewer than 16 synthetic cases\n")
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        sys.stderr.write("Smoke totals do not add up\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
