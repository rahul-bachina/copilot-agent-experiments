#!/usr/bin/env python3
"""Deterministic smoke test of the ERA 2025 HR checklist.

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

from src.review import LABEL, review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _duty(result: dict, duty_id: str) -> dict:
    return next(row for row in result["duties"] if row["id"] == duty_id)


def _prompt(result: dict, prompt_id: str) -> dict:
    return next(row for row in result["preparation_prompts"] if row["id"] == prompt_id)


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = review(
            case["pack"],
            as_of=date.fromisoformat(case["as_of"]),
            stale_after_days=case.get("stale_after_days", 90),
        )
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

    add("label", result["label"] == expect.get("label", LABEL), result["label"])
    add("compliance_conclusion", result["compliance_conclusion"] is None, "null")
    add("disciplinary_decision", result["disciplinary_decision"] is None, "null")
    add("hr_decision", result["hr_decision"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("message_sent", result["message_sent"] is False, "false")
    add("policy_published", result["policy_published"] is False, "false")
    add("records_changed", result["records_changed"] is False, "false")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("legal_advice", result["legal_advice"] is False, "false")
    if result["label"] == LABEL:
        add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
        add(
            "section_40b_applied",
            result["flags"]["regulations_under_section_40b_applied"] is False,
            "false",
        )
        add("deadline", result["flags"]["tribunal_deadline_calculated"] is False, "false")
        add("dismissal", result["flags"]["dismissal_decided"] is False, "false")
        for duty_id, fields in expect.get("duties", {}).items():
            duty = _duty(result, duty_id)
            for field, expected in fields.items():
                add(f"{duty_id}.{field}", duty[field] == expected, str(duty[field]))
        for prompt_id, fields in expect.get("prompts", {}).items():
            row = _prompt(result, prompt_id)
            for field, expected in fields.items():
                add(f"{prompt_id}.{field}", row[field] == expected, str(row[field]))
        if "rules_current" in expect:
            add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
        if "qa_status" in expect:
            actual = result["employee_qa"]["answer_status"] if result["employee_qa"] else None
            add("qa_status", actual == expect["qa_status"], str(actual))
        if "incident_route" in expect:
            summary = result["incident_summary"] or {}
            add("incident_route", summary.get("route") == expect["incident_route"], str(summary.get("route")))
        if "incident_status" in expect:
            summary = result["incident_summary"] or {}
            add("incident_status", summary.get("status") == expect["incident_status"], str(summary.get("status")))
        if expect.get("all_prompts_not_breaches"):
            breaches = [row["id"] for row in result["preparation_prompts"] if row["legal_breach"]]
            add("no_legal_breach", breaches == [], ",".join(breaches))
    for token in expect.get("absent_tokens", []):
        add(f"absent {token}", token not in json.dumps(result), "hidden")

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the ERA 2025 HR checklist")
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
        "employer_in_fixtures": "Northwharf Community Kitchen CIC (synthetic, invented)",
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
