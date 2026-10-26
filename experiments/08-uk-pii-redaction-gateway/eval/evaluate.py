#!/usr/bin/env python3
"""Smoke-test the deterministic detectors against the synthetic fixtures.

The agreement rate checks that the gateway did what these fixtures specify,
including the misses they deliberately contain. The recall figure is the
share of planted identifier types those fixtures also record. Neither number
is a model score or a live recall rate.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gateway import propose  # noqa: E402

SMOKE_LABEL = (
    "SMOKE TEST of deterministic rules on synthetic fixtures. "
    "Not a model evaluation. Not a live false-negative rate. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def evaluate_case(case: dict) -> dict:
    kwargs = {"caller": "eval-08"}
    if case.get("rules_as_of"):
        kwargs["rules_as_of"] = date.fromisoformat(case["rules_as_of"])
    try:
        result = propose(case["text"], **kwargs)
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": str(exc),
            "checks": [],
            "detected": [],
            "planted": case.get("planted", []),
        }

    detected = sorted({item["entity_type"] for item in result["audit_log"]["findings"]})
    checks = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"field": name, "passed": passed, "detail": detail})

    check("types", detected == sorted(case["expect_detected"]), f"{detected}")
    redacted = result["redacted_text"]
    for raw in case.get("must_remove", []):
        check("removed", raw not in redacted, "removed" if raw not in redacted else "still present")
    for raw in case.get("must_keep", []):
        check("kept", raw in redacted, "kept" if raw in redacted else "missing")
    check("not_anonymised", result["anonymisation"]["output_is_anonymised"] is False, "flag")
    check("not_released", result["release"]["agent_may_release"] is False, "flag")
    check("not_sent", result["release"]["agent_may_send"] is False, "flag")
    check("no_actions", result["security"]["actions_taken"] == [], "actions")
    check("banner", redacted.startswith("[REDACTION PROPOSAL. Not anonymised."), "banner")
    check("raw_values_logged", result["audit_log"]["raw_values_logged"] is False, "audit")
    if case.get("injection"):
        check("injection", bool(result["security"]["prompt_injection_signals"]), "signals")
    if case.get("stale"):
        check("stale_rules", result["audit_log"]["rules_stale"] is True, "rules")
    passed = all(item["passed"] for item in checks)
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "passed" if passed else "failed",
        "known_miss": bool(case.get("known_miss")),
        "planted": case.get("planted", []),
        "detected": detected,
        "checks": checks,
    }


def _rates(results: list[dict]) -> dict:
    true_positive = 0
    false_negative = 0
    false_positive = 0
    for item in results:
        planted = set(item["planted"])
        detected = set(item["detected"])
        true_positive += len(planted & detected)
        false_negative += len(planted - detected)
        false_positive += len(detected - planted)
    recall_denominator = true_positive + false_negative
    precision_denominator = true_positive + false_positive
    recall = round(100 * true_positive / recall_denominator, 1) if recall_denominator else 0
    precision = round(100 * true_positive / precision_denominator, 1) if precision_denominator else 0
    return {
        "planted_type_hits": true_positive,
        "planted_type_misses": false_negative,
        "unplanted_type_hits": false_positive,
        "recall_on_planted_types_percent": recall,
        "precision_on_detected_types_percent": precision,
        "note": (
            "Counted by identifier type on these synthetic fixtures, not by span "
            "and not on live text. A known miss is still a miss in the recall figure."
        ),
    }


def run_evaluation(dataset_path: Path | None = None) -> dict:
    dataset = load_dataset(dataset_path)
    cases = dataset["test_cases"]
    results = [evaluate_case(case) for case in cases]
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")
    errors = sum(1 for item in results if item["status"] == "error")
    total = len(cases)
    rates = _rates(results)
    print(SMOKE_LABEL)
    print(f"Cases: {total}")
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
    print(
        f"Smoke test: {passed}/{total} fixtures behaved as specified ({agreement}%). "
        f"Planted-type recall on this file: {rates['recall_on_planted_types_percent']}% "
        f"({rates['planted_type_hits']} hit, {rates['planted_type_misses']} miss). "
        f"Unplanted types detected: {rates['unplanted_type_hits']}."
    )
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic_rules",
        "not_a_model_evaluation": True,
        "not_a_live_recall_rate": True,
        "output_is_anonymised": False,
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "agreement_rate": agreement,
            "known_miss_cases": sum(1 for item in results if item.get("known_miss")),
            **rates,
        },
        "cases": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke test for the UK identifier gateway")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args(argv)
    report = run_evaluation(args.dataset)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    summary = report["summary"]
    return 0 if summary["errors"] == 0 and summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
