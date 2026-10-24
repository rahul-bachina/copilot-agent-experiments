#!/usr/bin/env python3
"""Smoke-test the mock triage against the synthetic fixtures.

The agreement rate is a pipeline check. The classifier is rule-based and
tuned to this file. It says nothing about a live model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage import SMOKE_LABEL, triage  # noqa: E402


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    with open(path) as handle:
        return json.load(handle)


def _by_id(result: dict) -> dict:
    return {item["id"]: item for item in result["statutory_clock"]["deadlines"]}


def evaluate_case(case: dict) -> dict:
    aware = datetime.fromisoformat(case["aware_at"])
    expected = case["expected"]
    officer = case.get("officer") or {}
    try:
        result = triage(case["input_text"], aware, **officer)
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

    if "category" in expected:
        actual = result["proposed"]["category"]
        check("category", actual == expected["category"], f"{actual} == {expected['category']}")
    if "hazard_family" in expected:
        actual = result["proposed"]["hazard_family"]
        check("hazard_family", actual == expected["hazard_family"], f"{actual} == {expected['hazard_family']}")
    if "injection" in expected:
        actual = result["security"]["prompt_injection_detected"]
        check("injection", actual is expected["injection"], f"{actual}")
    if "stale" in expected:
        actual = bool(result["security"]["stale_data_signals"])
        check("stale", actual is expected["stale"], f"{result['security']['stale_data_signals']}")
    if "downgrade_refused" in expected:
        actual = result["proposed"]["downgrade_refused"]
        check("downgrade_refused", actual is expected["downgrade_refused"], f"{actual}")
    if "in_force" in expected:
        actual = result["statutory_clock"]["in_force"]
        check("in_force", actual is expected["in_force"], f"{actual}")
    if "clock_operative" in expected:
        actual = result["statutory_clock"]["operative"]
        check("clock_operative", actual is expected["clock_operative"], f"{actual}")
    if "investigation_on" in expected:
        actual = _by_id(result).get("standard_investigation", {}).get("on")
        check("investigation_on", actual == expected["investigation_on"], f"{actual}")
    if "drivers" in expected:
        actual = [flag["characteristic"] for flag in result["vulnerability_flags"]["flags"]]
        check("drivers", actual == expected["drivers"], f"{actual}")
    if "not_social" in expected:
        actual = result["text_suggests_not_social_housing"]
        check("not_social", actual is expected["not_social"], f"{actual}")
    if "lower_category" in expected:
        actual = result["officer"]["recorded_a_lower_category_than_proposed"]
        check("lower_category", actual is expected["lower_category"], f"{actual}")

    check("labelled", result["vulnerability_flags"]["tenant_labelled_vulnerable"] is False, "label")
    check("sent", result["tenant_summary"]["may_be_sent_by_agent"] is False, "sent")
    check("defence", result["reasonable_endeavours"]["defence_made_out"] is False, "defence")
    check("referral", result["housing_ombudsman"]["referral_made_by_agent"] is False, "referral")
    check("actions_empty", result["security"]["actions_taken"] == [], "actions")
    check("smoke_label", result["evaluation_label"] == SMOKE_LABEL, "label")
    check("synthetic", result["synthetic_data"] is True, "synthetic")

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
    parser = argparse.ArgumentParser(description="Mock smoke test for Awaab's Law hazard triage")
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
