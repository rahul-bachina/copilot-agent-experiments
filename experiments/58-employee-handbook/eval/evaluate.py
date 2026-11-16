#!/usr/bin/env python3
"""Deterministic smoke test. Not a model score.

Each case is one row. Passed, failed, and errors sum to the case count.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.answer import answer_handbook  # noqa: E402

DATASET = Path(__file__).with_name("synthetic_dataset.json")
HANDBOOK = json.loads((ROOT / "fixtures" / "handbook.json").read_text(encoding="utf-8"))
SCOPE = json.loads((ROOT / "examples" / "sample_scope.json").read_text(encoding="utf-8"))


def _scope(extra: list[str]) -> dict:
    scope = json.loads(json.dumps(SCOPE))
    if extra:
        scope["approved_document_ids"] = list(scope["approved_document_ids"]) + extra
    return scope


def _check(result: dict, expect: dict) -> list[str]:
    failures = []
    if result["outcome"] != expect["outcome"]:
        failures.append(f"outcome {result['outcome']} != {expect['outcome']}")
    if result["entitlement_decision"] is not None:
        failures.append("entitlement was set")
    if result["human_approval"] is not None:
        failures.append("approval was taken from the run")
    if result["legal_advice"] or result["medical_advice"] or result["tax_advice"]:
        failures.append("advice flag was set")
    if result["network_called"] or result["model_called"]:
        failures.append("network or model was called")
    section = expect.get("section_id")
    if section is not None:
        found = [row["section_id"] for row in result["citations"]]
        if section not in found:
            failures.append(f"missing section {section}")
    for text in expect.get("answer_contains") or []:
        if text not in result["answer"]:
            failures.append(f"answer missing {text!r}")
    blob = json.dumps(result)
    for text in expect.get("answer_excludes") or []:
        if text in result["answer"] or text in blob:
            failures.append(f"output contains {text!r}")
    if "included" in expect:
        claims = {row["phrase"]: row["included"] for row in result["claims"]}
        for phrase, included in expect["included"].items():
            if claims.get(phrase) is not included:
                failures.append(f"included[{phrase}] is {claims.get(phrase)}")
    if expect.get("route"):
        if result["human_route"]["named"] != expect["route"]:
            failures.append("route name")
    if expect.get("reason") and result["human_route"]["reason"] != expect["reason"]:
        failures.append("route reason")
    if expect.get("rules_current") is False and result["stale"]["rules_current"] is not False:
        failures.append("pin was treated as current")
    if expect.get("marking"):
        withheld = {row["document_id"]: row for row in result["withheld"]}
        row = withheld.get(expect["marking"]["document_id"])
        if row is None or row["marking"] != expect["marking"]["label"]:
            failures.append("marking")
        if expect["marking"].get("legal_hold") and not row["legal_hold"]:
            failures.append("legal hold dropped")
    if expect.get("experiment_11"):
        era = result["experiment_11"]
        if era.get("called") is not True or era.get("reopened_by_this_starter") is not False:
            failures.append("experiment 11")
        if era.get("compliance_conclusion") is not None:
            failures.append("compliance conclusion")
        if era.get("all_reasonable_steps_in_force_on_as_of") is not expect["experiment_11"]:
            failures.append("in-force flag")
    return failures


def evaluate() -> dict:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    rows = []
    passed = failed = errors = 0
    for case in cases:
        try:
            result = answer_handbook(
                case["question"],
                HANDBOOK,
                _scope(case.get("extra_documents") or []),
                case["as_of"],
                case.get("about_date"),
            )
            problems = _check(result, case["expect"])
        except Exception as exc:  # noqa: BLE001 — one case must not abort the report
            errors += 1
            rows.append({"case_id": case["case_id"], "status": "error", "detail": type(exc).__name__})
            continue
        if problems:
            failed += 1
            rows.append({"case_id": case["case_id"], "status": "failed", "detail": problems})
        else:
            passed += 1
            rows.append({"case_id": case["case_id"], "status": "passed", "detail": []})
    total = len(cases)
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "handbook_is_synthetic": True,
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).with_name("smoke_report.json")))
    args = parser.parse_args()
    report = evaluate()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"Smoke test {summary['passed']}/{summary['total_cases']} passed. "
        "This is not a model score."
    )
    if summary["failed"] or summary["errors"]:
        print(json.dumps(report["cases"], indent=2))
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        print("totals do not add up")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
