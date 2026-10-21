#!/usr/bin/env python3
"""
Evaluation script for FOI Complaint Triage Agent.

Runs the triage agent against the synthetic dataset and reports per-field accuracy.

Usage:
    python evaluate.py                    # Run evaluation in mock mode
    python evaluate.py --live             # Run with Azure AI (requires credentials)
    python evaluate.py --output report.json  # Save detailed report
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from triage_agent import triage


def load_dataset(path: Path = None) -> dict:
    """Load the synthetic evaluation dataset."""
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    
    with open(path) as f:
        return json.load(f)


def check_field(actual: Any, expected: Any, path: str = "") -> tuple[bool, str]:
    """
    Check if actual value matches expected.
    
    Supports:
    - Exact match for strings/bools
    - Minimum value for integers with _min suffix
    - Contains check for strings with _contains suffix
    - Nested dict checking
    """
    if expected is None:
        return True, f"{path}: skipped (no expected value)"
    
    if isinstance(expected, dict):
        results = []
        for key, exp_value in expected.items():
            if key.endswith("_min"):
                base_key = key[:-4]
                act_value = actual.get(base_key) if isinstance(actual, dict) else None
                if act_value is None:
                    act_value = actual if isinstance(actual, (int, list)) else 0
                if isinstance(act_value, list):
                    act_value = len(act_value)
                passed = act_value >= exp_value
                results.append((passed, f"{path}.{base_key}: {act_value} >= {exp_value} = {passed}"))
            elif key.endswith("_contains"):
                base_key = key[:-9]
                act_value = actual.get(base_key, "") if isinstance(actual, dict) else str(actual)
                if act_value is None:
                    act_value = ""
                passed = exp_value.lower() in str(act_value).lower()
                results.append((passed, f"{path}.{base_key}: '{act_value}' contains '{exp_value}' = {passed}"))
            else:
                act_value = actual.get(key) if isinstance(actual, dict) else None
                sub_passed, sub_msg = check_field(act_value, exp_value, f"{path}.{key}")
                results.append((sub_passed, sub_msg))
        
        all_passed = all(r[0] for r in results)
        return all_passed, "; ".join(r[1] for r in results)
    
    elif isinstance(expected, bool):
        passed = actual == expected
        return passed, f"{path}: {actual} == {expected} = {passed}"
    
    elif isinstance(expected, str):
        passed = str(actual).lower() == expected.lower()
        return passed, f"{path}: '{actual}' == '{expected}' = {passed}"
    
    elif isinstance(expected, (int, float)):
        passed = actual == expected
        return passed, f"{path}: {actual} == {expected} = {passed}"
    
    else:
        return False, f"{path}: unknown expected type {type(expected)}"


def evaluate_case(case: dict, mock: bool = True) -> dict:
    """Evaluate a single test case."""
    case_id = case["id"]
    input_text = case["input_text"]
    expected = case["expected"]
    
    try:
        result = triage(input_text, mock=mock)
    except Exception as e:
        return {
            "case_id": case_id,
            "name": case.get("name", ""),
            "status": "error",
            "error": str(e),
            "checks": []
        }
    
    checks = []
    all_passed = True
    
    for field, exp_value in expected.items():
        if field.endswith("_min") or field.endswith("_contains"):
            continue
        
        actual = result.get(field)
        
        if field == "ask_count_min":
            actual = len(result.get("extracted_asks", []))
            passed = actual >= exp_value
            msg = f"ask_count: {actual} >= {exp_value} = {passed}"
            checks.append({"field": "ask_count", "passed": passed, "detail": msg})
            if not passed:
                all_passed = False
        else:
            passed, msg = check_field(actual, exp_value, field)
            checks.append({"field": field, "passed": passed, "detail": msg})
            if not passed:
                all_passed = False
    
    return {
        "case_id": case_id,
        "name": case.get("name", ""),
        "status": "passed" if all_passed else "failed",
        "checks": checks,
        "result_summary": {
            "classification": result.get("classification", {}).get("primary_type"),
            "urgency": result.get("flags", {}).get("urgency_level"),
            "safeguarding": result.get("flags", {}).get("safeguarding_concern"),
            "exceeds_cost": result.get("cost_limit_assessment", {}).get("likely_exceeds_limit"),
            "bulk_detected": result.get("bulk_submission_signals", {}).get("detected"),
            "ask_count": len(result.get("extracted_asks", []))
        }
    }


def run_evaluation(mock: bool = True, dataset_path: Path = None) -> dict:
    """Run full evaluation and return report."""
    dataset = load_dataset(dataset_path)
    test_cases = dataset["test_cases"]
    
    results = []
    passed = 0
    failed = 0
    errors = 0
    
    print(f"Running evaluation on {len(test_cases)} test cases...")
    print(f"Mode: {'mock' if mock else 'live'}")
    print("-" * 60)
    
    for case in test_cases:
        result = evaluate_case(case, mock=mock)
        results.append(result)
        
        status_icon = "✓" if result["status"] == "passed" else ("✗" if result["status"] == "failed" else "!")
        print(f"{status_icon} {result['case_id']}: {result['name']}")
        
        if result["status"] == "passed":
            passed += 1
        elif result["status"] == "failed":
            failed += 1
            for check in result["checks"]:
                if not check["passed"]:
                    print(f"    - {check['detail']}")
        else:
            errors += 1
            print(f"    Error: {result.get('error', 'unknown')}")
    
    print("-" * 60)
    
    total = len(test_cases)
    accuracy = passed / total if total > 0 else 0
    
    field_stats = calculate_field_accuracy(results)
    
    report = {
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "overall_accuracy": round(accuracy * 100, 1)
        },
        "field_accuracy": field_stats,
        "mode": "mock" if mock else "live",
        "cases": results
    }
    
    print(f"\nResults: {passed}/{total} passed ({report['summary']['overall_accuracy']}%)")
    print(f"Errors: {errors}")
    print("\nPer-field accuracy:")
    for field, stats in field_stats.items():
        print(f"  {field}: {stats['accuracy']}% ({stats['passed']}/{stats['total']})")
    
    return report


def calculate_field_accuracy(results: list[dict]) -> dict:
    """Calculate per-field accuracy from results."""
    field_counts = {}
    
    for result in results:
        for check in result.get("checks", []):
            field = check["field"]
            if field not in field_counts:
                field_counts[field] = {"passed": 0, "total": 0}
            field_counts[field]["total"] += 1
            if check["passed"]:
                field_counts[field]["passed"] += 1
    
    field_stats = {}
    for field, counts in field_counts.items():
        accuracy = (counts["passed"] / counts["total"] * 100) if counts["total"] > 0 else 0
        field_stats[field] = {
            "passed": counts["passed"],
            "total": counts["total"],
            "accuracy": round(accuracy, 1)
        }
    
    return field_stats


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate FOI Triage Agent against synthetic dataset"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use live Azure AI instead of mock mode"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        help="Path to dataset JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Path to save detailed report JSON"
    )
    
    args = parser.parse_args()
    
    mock = not args.live
    report = run_evaluation(mock=mock, dataset_path=args.dataset)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {args.output}")
    
    return 0 if report["summary"]["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
