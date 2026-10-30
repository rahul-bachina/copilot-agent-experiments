#!/usr/bin/env python3
"""Deterministic smoke test of the promotion checklist.

The fixtures are synthetic. The checker is the Python under src/, which can
call Experiments 08, 04, and 03. This is not a model score and it does not
call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.precheck import LABEL, NotSynthetic, precheck  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which can call Experiments 08, 04, and 03. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _row(checklist: list[dict], row_id: str) -> dict:
    return next(item for item in checklist if item["id"] == row_id)


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    checks: list[dict] = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    def finish(status: str) -> dict:
        if any(not item["passed"] for item in checks):
            status = "failed"
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": status,
            "checks": checks,
        }

    as_of = date.fromisoformat(case["as_of"])
    window = case.get("stale_after_days", 90)

    if expect.get("outcome") == "refused":
        try:
            precheck(case["promotion"], as_of=as_of, stale_after_days=window)
        except NotSynthetic as exc:
            message = str(exc)
            add("refused", True, "NotSynthetic")
            for index, token in enumerate(expect.get("absent", []), start=1):
                add(f"absent planted value {index}", token not in message, "not in the refusal")
            return finish("passed")
        except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
            return {
                "case_id": case["id"],
                "name": case.get("name", ""),
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "checks": checks,
            }
        add("refused", False, "precheck returned a checklist")
        return finish("failed")

    try:
        result = precheck(case["promotion"], as_of=as_of, stale_after_days=window)
    except Exception as exc:  # noqa: BLE001
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "checks": [],
        }

    serialised = json.dumps(result)
    add("label", result["label"] == LABEL, result["label"])
    add("catalogue", result["catalogue_id"] == "UK08", result["catalogue_id"])
    add("autonomy", result["autonomy"] == "A0", result["autonomy"])
    add("promotion_approved", result["promotion_approved"] is False, "false")
    add("published", result["published"] is False, "false")
    add("compliance_opinion", result["compliance_opinion"] is False, "false")
    add("s21_approver_decision", result["s21_approver_decision"] is None, "null")
    add("rewrite_drafted", result["rewrite_drafted"] is False, "false")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("prohibited_followed", result["prohibited_requests"]["followed"] is False, "false")
    for row in result["checklist"]:
        add(
            f"{row['id']}.compliance_finding",
            row["compliance_finding"] is False,
            "false",
        )

    if "sources_stale" in expect:
        add("sources_stale", result["sources_stale"] is expect["sources_stale"], str(result["sources_stale"]))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "quarantine" in expect:
        actual = result["prompt_injection"]["quarantine_document"]
        add("quarantine", actual is expect["quarantine"], str(actual))
    if "signals_include" in expect:
        actual = result["prompt_injection"]["signals"]
        missing = [item for item in expect["signals_include"] if item not in actual]
        add("signals_include", not missing, ",".join(actual) or "none")
    if "prohibited_includes" in expect:
        actual = result["prohibited_requests"]["keys"]
        missing = [item for item in expect["prohibited_includes"] if item not in actual]
        add("prohibited_keys", not missing, ",".join(actual) or "none")
    if "gateway_called" in expect:
        actual = result["identifier_gateway"]["called"]
        add("gateway_called", actual is expect["gateway_called"], str(actual))
    if "lifecycle_called" in expect:
        actual = result["experiment_03"]["lifecycle_called"]
        add("lifecycle_called", actual is expect["lifecycle_called"], str(actual))
    if "status_applied" in expect:
        actual = result["experiment_03"]["status_applied"]
        add("status_applied", actual is expect["status_applied"], str(actual))
    for row_id, status in expect.get("checklist", {}).items():
        row = _row(result["checklist"], row_id)
        add(row_id, row["status"] == status, row["status"])
    for index, token in enumerate(expect.get("absent", []), start=1):
        add(f"absent planted value {index}", token not in serialised, "omitted")

    return finish("passed")


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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the promotion checklist")
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
        "not_a_compliance_score": True,
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
    if summary["total_cases"] < 24:
        sys.stderr.write("Fewer than 24 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
