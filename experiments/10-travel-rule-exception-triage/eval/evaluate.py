#!/usr/bin/env python3
"""Deterministic smoke test of the Travel Rule triage.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.triage import LABEL, triage  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _option(result: dict, option_id: str) -> dict:
    return next(item for item in result["options"] if item["id"] == option_id)


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = triage(case["transfer"], as_of=date.fromisoformat(case["as_of"]))
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

    add("label", result["label"] == LABEL, result["label"])
    add("analyst_decision", result["analyst_decision"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("released", result["flags"]["transfer_released_by_agent"] is False, "false")
    add("held", result["flags"]["transfer_held_by_agent"] is False, "false")
    add("returned", result["flags"]["transfer_returned_by_agent"] is False, "false")
    add("sar_filed", result["flags"]["sar_filed"] is False, "false")
    add("contacted", result["flags"]["counterparty_contacted"] is False, "false")
    add("waiver", result["flags"]["fca_statement_treated_as_waiver"] is False, "false")
    add("euro_threshold", result["flags"]["jmlsg_euro_threshold_used"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")

    for category in expect.get("categories_include", []):
        add(f"include {category}", category in result["exception_categories"], category)
    for category in expect.get("categories_exclude", []):
        add(f"exclude {category}", category not in result["exception_categories"], category)
    for option_id, proposed in expect.get("proposed", {}).items():
        actual = _option(result, option_id)["proposed"]
        add(f"proposed {option_id}", actual is proposed, str(actual))
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
    if "sunrise" in expect:
        add(
            "sunrise",
            result["sunrise"]["is_sunrise_on_relied_status"] is expect["sunrise"],
            str(result["sunrise"]["is_sunrise_on_relied_status"]),
        )

    failed = [item for item in checks if not item["passed"]]
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "failed" if failed else "passed",
        "checks": checks,
    }


def summarise(results: list[dict]) -> dict:
    errors = [item for item in results if item["status"] == "error"]
    failed = [item for item in results if item["status"] == "failed"]
    passed = [item for item in results if item["status"] == "passed"]
    total = len(results)
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the Travel Rule triage")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset)
    results = [evaluate_case(case) for case in dataset["cases"]]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_label": dataset.get("label"),
        "firm_in_fixtures": "Harbourline Markets Ltd (synthetic, invented)",
        "summary": summary,
        "cases": results,
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["total_cases"] < 16:
        sys.stderr.write("Fewer than 16 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
