#!/usr/bin/env python3
"""Deterministic smoke test of the document intake.

The fixtures are synthetic. The checker is the Python under src/, which calls
Experiment 08 in-process. This is not a model score and it does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.intake import LABEL, NotSynthetic, intake  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which calls Experiment 08 for UK identifier spans. "
    "Not a measure of model accuracy. No model was called."
)

FALSE_FLAGS = (
    "accepted_into_queue",
    "production_record_written",
    "external_sent",
    "underlying_matter_approved",
    "underlying_matter_rejected",
    "redacted_text_released",
    "output_is_anonymised",
    "purpose_taken_from_document",
    "files_confirmed_by_document",
    "handed_off",
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


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
    rules = date.fromisoformat(case["rules_as_of"]) if case.get("rules_as_of") else None
    window = case.get("stale_after_days", 90)

    if expect.get("outcome") == "refused":
        try:
            intake(case["batch"], as_of=as_of, stale_after_days=window, rules_as_of=rules)
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
        add("refused", False, "intake returned a draft")
        return finish("failed")

    try:
        result = intake(case["batch"], as_of=as_of, stale_after_days=window, rules_as_of=rules)
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
    add("files_confirmed", result["files_confirmed"] is False, "false")
    add("purpose_confirmed", result["purpose_confirmed"] is False, "false")
    add("reviewer_decision", result["reviewer_decision"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("anonymised", result["gateway"]["output_is_anonymised"] is False, "false")
    add("may_release", result["gateway"]["agent_may_release"] is False, "false")
    add("handed_off", result["routing"]["handed_off"] is False, "false")
    for flag in FALSE_FLAGS:
        add(f"flag {flag}", result["flags"][flag] is False, "false")

    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "hidden_in" in expect:
        found = {signal["hidden_in"] for signal in result["prompt_injection"]["signals"]}
        add("hidden_in", expect["hidden_in"] in found, ",".join(sorted(found)) or "none")
    if "any_document_stale" in expect:
        add("any_document_stale", result["any_document_stale"] is expect["any_document_stale"], str(result["any_document_stale"]))
    if "any_document_not_current" in expect:
        actual = result["any_document_not_current"]
        add("any_document_not_current", actual is expect["any_document_not_current"], str(actual))
    if "date_status" in expect:
        actual = result["files"][0]["date_status"]
        add("date_status", actual == expect["date_status"], actual)
    if "catalogue_stale" in expect:
        add("catalogue_stale", result["catalogue_stale"] is expect["catalogue_stale"], str(result["catalogue_stale"]))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
    if "gateway_rules_stale" in expect:
        actual = result["gateway_rules_stale"]
        add("gateway_rules_stale", actual is expect["gateway_rules_stale"], str(actual))
    if "suggested_class" in expect:
        actual = result["files"][0]["suggested_class"]
        add("suggested_class", actual == expect["suggested_class"], str(actual))
    if "read_status" in expect:
        actual = result["files"][0]["read_status"]
        add("read_status", actual == expect["read_status"], actual)
    if "pii_called" in expect:
        actual = result["files"][0]["pii"]["called"]
        add("pii_called", actual is expect["pii_called"], str(actual))
    if "injection_scanned" in expect:
        actual = result["files"][0]["injection_scanned"]
        add("injection_scanned", actual is expect["injection_scanned"], str(actual))
    if "entity_types_include" in expect:
        actual = result["files"][0]["pii"]["entity_types"]
        missing = [item for item in expect["entity_types_include"] if item not in actual]
        add("entity_types", not missing, ",".join(actual) or "none")
    if "checklist_complete" in expect:
        preview = result["checklist_preview"]
        actual = None if preview is None else preview["complete"]
        add("checklist_complete", actual is expect["checklist_complete"], str(actual))
        if preview is not None:
            add("checklist_sufficient", preview["sufficient"] is False, "false")
            add("checklist_preview_only", preview["preview_only"] is True, "true")
    if "downstream" in expect:
        preview = result["checklist_preview"] or {}
        actual = preview.get("downstream_catalogue_id")
        add("downstream", actual == expect["downstream"], str(actual))
    if "checksum_matches" in expect:
        actual = result["files"][0]["checksum_matches"]
        add("checksum_matches", actual is expect["checksum_matches"], str(actual))
    if "duplicate_of" in expect:
        actual = result["files"][1]["duplicate_of"]
        add("duplicate_of", actual == expect["duplicate_of"], str(actual))
    if "prohibited_includes" in expect:
        actual = result["prohibited_payload_keys"]
        missing = [item for item in expect["prohibited_includes"] if item not in actual]
        add("prohibited_keys", not missing, ",".join(actual) or "none")
    for index, token in enumerate(expect.get("absent", []), start=1):
        omitted = token not in serialised and token.replace(" ", "") not in serialised
        add(f"absent planted value {index}", omitted, "omitted")

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the document intake")
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
        "not_a_live_recall_rate": True,
        "dataset_label": dataset.get("label"),
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
