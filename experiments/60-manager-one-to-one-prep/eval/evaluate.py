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

from src.prepare import prepare  # noqa: E402

DATASET = Path(__file__).with_name("synthetic_dataset.json")


def _dig(result: dict, path: str):
    current = result
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def check(result: dict, expect: dict) -> list[str]:
    failures: list[str] = []
    for path, value in (expect.get("equals") or {}).items():
        found = _dig(result, path)
        if found != value:
            failures.append(f"{path} is {found!r}, expected {value!r}")
    blob = json.dumps(result)
    points = " ".join(point["text"] for point in result["prep_note"]["points"])
    for text in expect.get("point_includes") or []:
        if text not in points:
            failures.append(f"points omit {text!r}")
    for text in expect.get("excludes") or []:
        if text in blob:
            failures.append(f"output contains {text!r}")
    if expect.get("human_flag"):
        kinds = {flag["kind"] for flag in result["human_flags"]}
        if expect["human_flag"] not in kinds:
            failures.append(f"missing human flag {expect['human_flag']}")
        if any(flag["summarised_as_routine"] or flag["sentence_copied"] for flag in result["human_flags"]):
            failures.append("a human flag was summarised as routine")
    if expect.get("no_human_flag") and result["human_flags"]:
        failures.append("unexpected human flag")
    if expect.get("marking"):
        rows = result["not_read"] + result["source_report"]
        match = next((row for row in rows if row.get("source_id") == expect["marking"]["source_id"]), None)
        if match is None or match.get("marking") != expect["marking"]["label"]:
            failures.append("marking")
        elif expect["marking"].get("legal_hold") and not match.get("legal_hold"):
            failures.append("legal hold dropped")
        elif expect["marking"].get("retention") and expect["marking"]["retention"] not in (match.get("retention_labels") or []):
            failures.append("retention label dropped")
        elif match.get("body_copied"):
            failures.append("withheld body was copied")
    if result["performance_rating"] is not None or result["comparison"] is not None:
        failures.append("a rating or a comparison was set")
    if result["disciplinary_recommendation"] is not None or result["capability_recommendation"] is not None:
        failures.append("a sanction was recommended")
    if result["health_inference"] is not None or result["protected_characteristic_inference"] is not None:
        failures.append("an inference was set")
    if result["employee_profile"] is not None:
        failures.append("a profile was set")
    if result["human_approval"] is not None:
        failures.append("approval was taken from the run")
    if result["mailbox_read"] or result["chat_read"] or result["network_called"]:
        failures.append("a forbidden read was recorded")
    if result["injection_followed"]:
        failures.append("an instruction was followed")
    if result["masking"]["described_as_anonymised"]:
        failures.append("output was described as anonymised")
    return failures


def run(dataset: list[dict]) -> dict:
    rows = []
    for case in dataset:
        case_id = case["case_id"]
        try:
            result = prepare(case["pack"], case.get("as_of"))
            failures = check(result, case["expect"])
            status = "passed" if not failures else "failed"
            error = None
        except Exception as exc:  # noqa: BLE001 — one case must not abort the run
            status = "error"
            failures = []
            error = f"{type(exc).__name__}: {exc}"
        rows.append(
            {
                "case_id": case_id,
                "status": status,
                "failures": failures,
                "error": error,
            }
        )
    passed = sum(row["status"] == "passed" for row in rows)
    failed = sum(row["status"] == "failed" for row in rows)
    errors = sum(row["status"] == "error" for row in rows)
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. NOT A MODEL SCORE.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "summary": {
            "total_cases": len(rows),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the one-to-one prep note.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    report = run(dataset)
    summary = report["summary"]
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        print("Smoke totals do not add up.", file=sys.stderr)
        return 1
    ids = [row["case_id"] for row in report["cases"]]
    if len(ids) != len(set(ids)):
        print("A case id was counted twice.", file=sys.stderr)
        return 1
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    print(
        f"Smoke test {summary['passed']}/{summary['total_cases']} passed",
        file=sys.stderr,
    )
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
