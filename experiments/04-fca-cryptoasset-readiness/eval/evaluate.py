#!/usr/bin/env python3
"""Deterministic smoke test of the gap register.

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

from src.gap_register import FORBIDDEN_CONCLUSION_PHRASES, LABEL, build_register  # noqa: E402
from src.checklist import REQUIREMENTS  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _row(register: dict, requirement_id: str) -> dict:
    return next(item for item in register["observations"] if item["requirement_id"] == requirement_id)


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    as_of = date.fromisoformat(case.get("as_of", "2026-10-24"))
    try:
        register = build_register(
            case["pack"],
            as_of=as_of,
            stale_after_days=case.get("stale_after_days", 90),
            document_stale_after_days=case.get("document_stale_after_days", 365),
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

    add("label", register["label"] == LABEL, register["label"])
    add("readiness_conclusion", register["readiness_conclusion"] is None, "null")
    add("firm_ready", register["firm_ready"] is None, "null")
    add("firm_not_ready", register["firm_not_ready"] is None, "null")
    add("regulatory_advice", register["regulatory_advice"] is None, "null")
    add("legal_advice", register["legal_advice"] is None, "null")
    add("actions_taken", register["actions_taken"] == [], "[]")
    add("model_called", register["model_called"] is False, "false")
    add("network_called", register["network_called"] is False, "false")
    add("injection_followed", register["prompt_injection"]["followed"] is False, "false")
    add("agent_accepted_any_gap", register["human_review"]["agent_accepted_any_gap"] is False, "false")
    add("row_count", len(register["observations"]) == len(REQUIREMENTS), str(len(register["observations"])))
    blob = json.dumps(register).lower()
    forbidden = [phrase for phrase in FORBIDDEN_CONCLUSION_PHRASES if phrase in blob]
    add("forbidden_conclusion_phrases", not forbidden, ", ".join(forbidden) or "none")

    if "injection_detected" in expect:
        actual = register["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "any_source_stale" in expect:
        actual = register["any_source_stale"]
        add("any_source_stale", actual is expect["any_source_stale"], str(actual))
    if "synthetic" in expect:
        add("synthetic", register["synthetic"] is expect["synthetic"], str(register["synthetic"]))

    for requirement_id, status in expect.get("observations", {}).items():
        row = _row(register, requirement_id)
        add(requirement_id, row["text_observation"] == status, row["text_observation"])
        add(f"{requirement_id}.accepted_as_gap", row["accepted_as_gap"] is False, "false")

    for requirement_id, stage in expect.get("rule_stages", {}).items():
        row = _row(register, requirement_id)
        add(f"{requirement_id}.rule_stage", row["rule_stage"] == stage, row["rule_stage"])

    if "mentioned" in expect:
        for requirement_id, mentioned in expect["mentioned"].items():
            row = _row(register, requirement_id)
            add(f"{requirement_id}.mentioned", row.get("mentioned_in_pack") is mentioned, str(row.get("mentioned_in_pack")))

    if "date_observation_dates" in expect:
        actual = sorted(item["date_in_text"] for item in register["date_observations"])
        expected_dates = sorted(expect["date_observation_dates"])
        add("date_observations", actual == expected_dates, ", ".join(actual) or "none")

    if "document_currency" in expect:
        for document_id, currency in expect["document_currency"].items():
            document = next(item for item in register["documents"] if item["id"] == document_id)
            actual = document["document_currency"]["currency"]
            add(f"{document_id}.document_currency", actual == currency, actual)

    if "doc_type" in expect:
        for document_id, doc_type in expect["doc_type"].items():
            document = next(item for item in register["documents"] if item["id"] == document_id)
            add(f"{document_id}.doc_type", document["doc_type"] == doc_type, document["doc_type"])

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the gap register")
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
    if summary["total_cases"] < 12:
        sys.stderr.write("Fewer than 12 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
