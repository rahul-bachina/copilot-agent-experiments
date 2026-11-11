#!/usr/bin/env python3
"""Deterministic smoke test of the records classification draft.

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

from classify import LABEL, apply_confirmed_labels, classify_record, record_confirmation  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    result = classify_record(case["document"], case["as_of"])
    if "review" in case:
        result = record_confirmation(result, case["review"])
    if case.get("apply") is True:
        result = apply_confirmed_labels(result)
    return result


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = _run(case)
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
    add("text_recorded", result.get("text_recorded") is False, "false")
    flags = result.get("flags") or {}
    add("deleted", flags.get("deleted") is False, "false")
    add("disposed", flags.get("disposed") is False, "false")
    add("moved", flags.get("moved") is False, "false")
    add("downgraded", flags.get("downgraded") is False, "false")
    add("tenant_label", flags.get("labels_applied_in_tenant") is False, "false")
    route = result.get("human_route") or {}
    add("human_route", route.get("offered") is True, "true")
    add("agent_disposes", route.get("agent_disposes") is False, "false")
    regulatory = result.get("regulatory") or {}
    if regulatory:
        add("public_record", regulatory.get("public_record_decided") is False, "false")
        add("code_complied", regulatory.get("code_complied") is False, "false")
        add("storage_met", regulatory.get("storage_limitation_met") is False, "false")
    screening = ((result.get("reuse") or {}).get("screening") or {})
    if screening.get("called"):
        add("dpia_required", screening.get("dpia_required") is None, "null")
    injection = result.get("prompt_injection") or {}
    if injection:
        add("injection_followed", injection.get("followed") is False, "false")

    if "outcome" in expect:
        add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
    proposals = result.get("proposals") or {}
    if "category" in expect:
        got = (proposals.get("file_plan") or {}).get("category_id")
        add("category", got == expect["category"], str(got))
    if "confidence" in expect:
        got = (proposals.get("file_plan") or {}).get("confidence")
        add("confidence", got == expect["confidence"], str(got))
    if "marking" in expect:
        got = (proposals.get("gsc") or {}).get("suggestion")
        add("marking", got == expect["marking"], str(got))
    if "disposal" in expect:
        got = (proposals.get("disposal") or {}).get("action")
        add("disposal", got == expect["disposal"], str(got))
    if "personal" in expect:
        got = (proposals.get("personal_data") or {}).get("indicated")
        add("personal", got is expect["personal"], str(got))
    if "entity" in expect:
        types = (proposals.get("personal_data") or {}).get("identifier_types") or []
        add("entity", expect["entity"] in types, str(types))
    if "queue_reason" in expect:
        reasons = (result.get("human_queue") or {}).get("reasons") or []
        add("queue_reason", expect["queue_reason"] in reasons, str(reasons))
    if "injection" in expect:
        add("injection", injection.get("detected") is expect["injection"], str(injection.get("detected")))
    if "signal" in expect:
        signals = [row["signal"] for row in injection.get("signals", [])]
        add("signal", expect["signal"] in signals, str(signals))
    if "rules_current" in expect:
        got = (result.get("stale") or {}).get("rules_current")
        add("rules_current", got is expect["rules_current"], str(got))
    if "review_reason" in expect:
        got = (result.get("review") or {}).get("reason")
        add("review_reason", got == expect["review_reason"], str(got))
    if "review_accepted" in expect:
        got = (result.get("review") or {}).get("accepted")
        add("review_accepted", got is expect["review_accepted"], str(got))
    if "labels_stubbed" in expect:
        add("labels_stubbed", flags.get("labels_stubbed") is expect["labels_stubbed"], str(flags.get("labels_stubbed")))
    if "human_approval_null" in expect and expect["human_approval_null"] is True:
        add("human_approval", result.get("human_approval") is None, "null")
    if expect.get("approval_recorded") is True:
        add("approval_recorded", (result.get("human_approval") or {}).get("recorded") is True, "true")
        add("approval_executed", (result.get("human_approval") or {}).get("executed") is False, "false")
    for snippet in expect.get("absent", []):
        add(f"absent {snippet}", snippet not in blob, snippet)

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the classification draft")
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
