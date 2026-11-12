#!/usr/bin/env python3
"""Deterministic smoke test of the proposal draft.

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

from proposal import LABEL, draft_proposal, record_acceptance  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = draft_proposal(case["pack"], case["as_of"])
        if "review" in case:
            result = record_acceptance(result, case["review"])
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
    add("label", result.get("label") == LABEL, str(result.get("label")))
    add("actions_taken", result.get("actions_taken") == [], "[]")
    add("executed", result.get("executed") is False, "false")
    add("model_called", result.get("model_called") is False, "false")
    add("network_called", result.get("network_called") is False, "false")
    add("text_recorded", result.get("requirement_text_recorded") is False, "false")
    flags = result.get("flags") or {}
    add("submitted", flags.get("submitted") is False, "false")
    add("sent", flags.get("sent") is False, "false")
    add("uploaded", flags.get("uploaded") is False, "false")
    add("used", flags.get("used_anywhere") is False, "false")
    add("graph", flags.get("graph_called") is False, "false")
    route = result.get("human_route") or {}
    add("human_route", route.get("offered") is True, "true")
    add("agent_submits", route.get("agent_submits") is False, "false")
    regulatory = result.get("regulatory") or {}
    add("assessment", regulatory.get("assessment_summary_produced") is False, "false")
    add("basis", regulatory.get("lawful_basis_decided") is False, "false")
    injection = result.get("prompt_injection") or {}
    add("followed", injection.get("followed") is False, "false")

    if "outcome" in expect:
        add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
    rows = {row["requirement_id"]: row for row in result.get("compliance_matrix") or []}
    if "status" in expect:
        got = (rows.get(expect.get("requirement_id", "R1")) or {}).get("status")
        add("status", got == expect["status"], str(got))
    if "met" in expect:
        got = (rows.get(expect.get("requirement_id", "R1")) or {}).get("requirement_met")
        add("met", got is expect["met"], str(got))
    if "sources" in expect:
        got = (rows.get(expect.get("requirement_id", "R1")) or {}).get("source_ids")
        add("sources", got == expect["sources"], str(got))
    if "classification" in expect:
        got = (result.get("reuse") or {}).get("cross_source", {}).get("classification")
        add("classification", got == expect["classification"], str(got))
    if "injection" in expect:
        add("injection", injection.get("detected") is expect["injection"], str(injection.get("detected")))
    if "rules_current" in expect:
        got = (result.get("stale") or {}).get("rules_current")
        add("rules_current", got is expect["rules_current"], str(got))
    if "review_reason" in expect:
        got = (result.get("review") or {}).get("reason")
        add("review_reason", got == expect["review_reason"], str(got))
    if "review_accepted" in expect:
        got = (result.get("review") or {}).get("accepted")
        add("review_accepted", got is expect["review_accepted"], str(got))
    if expect.get("approval_recorded") is True:
        approval = result.get("human_approval") or {}
        add("approval_recorded", approval.get("recorded") is True, "true")
        add("approval_submitted", approval.get("submitted") is False, "false")
    if expect.get("approval_null") is True:
        add("approval_null", result.get("human_approval") is None, "null")
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the proposal draft")
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
    print(SMOKE_LABEL)
    print(
        f"{summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['errors']} errors, {summary['total_cases']} cases"
    )
    if summary["failed"] or summary["errors"]:
        for row in results:
            if row["status"] != "passed":
                print(row["case_id"], row["status"], row.get("error", ""))
                for check in row.get("checks", []):
                    if not check["passed"]:
                        print(" ", check["field"], check["detail"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
