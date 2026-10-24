#!/usr/bin/env python3
"""Smoke-test the mock intake against the synthetic fixtures.

The agreement rate is a pipeline check. The classifier is rule-based and
tuned to this file. It says nothing about a live model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intake import SMOKE_LABEL, intake  # noqa: E402


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    with open(path) as handle:
        return json.load(handle)


def evaluate_case(case: dict) -> dict:
    received = date.fromisoformat(case["received_on"])
    expected = case["expected"]
    try:
        result = intake(case["input_text"], received_on=received)
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": str(exc),
            "checks": [],
        }

    checks = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"field": name, "passed": passed, "detail": detail})

    if "meets_disp_definition" in expected:
        actual = result["complaint"]["meets_disp_definition"]
        check("meets_disp_definition", actual is expected["meets_disp_definition"], f"{actual}")
    if "product" in expected:
        actual = result["product"]["suggested"]
        check("product", actual == expected["product"], f"{actual} == {expected['product']}")
    if "root_cause" in expected:
        actual = result["root_cause"]["suggested"]
        check("root_cause", actual == expected["root_cause"], f"{actual} == {expected['root_cause']}")
    if "outcome" in expected:
        actual = result["consumer_duty"]["outcomes_touched"]
        check("outcome", actual == [expected["outcome"]], f"{actual}")
    if "route" in expected:
        actual = result["route"]["suggested"]
        check("route", actual == expected["route"], f"{actual} == {expected['route']}")
    if "clock_route_without_confirmation" in expected:
        actual = result["route"]["applied_to_clock"]
        check(
            "clock_route",
            actual == expected["clock_route_without_confirmation"] and result["route"]["handler_confirmed"] is False,
            f"applied {actual}, confirmed {result['route']['handler_confirmed']}",
        )
    if "severity" in expected:
        actual = result["severity"]["suggested"]
        check("severity", actual == expected["severity"], f"{actual} == {expected['severity']}")
    if "drivers" in expected:
        actual = [flag["driver"] for flag in result["vulnerability_characteristics"]["flags"]]
        check("drivers", actual == expected["drivers"], f"{actual}")
    if "injection" in expected:
        actual = result["security"]["prompt_injection_detected"]
        check("injection", actual is expected["injection"], f"{actual}")
    if "stale" in expected:
        actual = bool(result["security"]["stale_data_signals"])
        check("stale", actual is expected["stale"], f"{result['security']['stale_data_signals']}")
    if "labelled" in expected:
        actual = result["vulnerability_characteristics"]["customer_labelled_vulnerable"]
        check("labelled", actual is expected["labelled"], f"{actual}")
    if "sent" in expected:
        actual = result["acknowledgement_draft"]["may_be_sent_by_agent"]
        check("sent", actual is expected["sent"], f"{actual}")
    if "breach_found" in expected:
        actual = result["consumer_duty"]["breach_found"]
        check("breach_found", actual is expected["breach_found"], f"{actual}")
    if "harm_empty" in expected:
        actual = result["complaint"]["harm_alleged"] == []
        check("harm_empty", actual is expected["harm_empty"], f"{result['complaint']['harm_alleged']}")
    if "received_on" in expected:
        actual = result["received_on"]
        check("received_on", actual == expected["received_on"], f"{actual}")

    check("actions_empty", result["security"]["actions_taken"] == [], "actions")
    check(
        "smoke_label",
        result["evaluation_label"] == SMOKE_LABEL,
        "label",
    )
    passed = all(item["passed"] for item in checks)
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "passed" if passed else "failed",
        "checks": checks,
    }


def run_evaluation(dataset_path: Path | None = None) -> dict:
    dataset = load_dataset(dataset_path)
    cases = dataset["test_cases"]
    results = [evaluate_case(case) for case in cases]
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")
    errors = sum(1 for item in results if item["status"] == "error")
    total = len(cases)
    print(SMOKE_LABEL)
    print(f"Mode: mock. Cases: {total}")
    for item in results:
        mark = {"passed": "ok", "failed": "FAIL", "error": "ERROR"}[item["status"]]
        print(f"{mark} {item['case_id']} {item['name']}")
        if item["status"] != "passed":
            for check in item.get("checks", []):
                if not check["passed"]:
                    print(f"    {check['field']}: {check['detail']}")
            if item.get("error"):
                print(f"    {item['error']}")
    agreement = round((passed / total) * 100, 1) if total else 0
    print(f"Smoke test: {passed}/{total} ({agreement}% agreement). Errors: {errors}.")
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "mock",
        "not_a_model_evaluation": True,
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "agreement_rate": agreement,
        },
        "cases": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Mock smoke test for the complaint intake")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args()
    report = run_evaluation(args.dataset)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Wrote {args.output}")
    return 0 if report["summary"]["errors"] == 0 and report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
