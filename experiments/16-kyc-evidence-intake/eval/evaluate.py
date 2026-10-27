#!/usr/bin/env python3
"""Deterministic smoke test of the KYC evidence checklist.

The fixtures are synthetic. The checker is the Python under src/, which calls
Experiment 12, which calls Experiment 08. This is not a model score and it
does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.review import LABEL, NotSynthetic, review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which calls Experiment 12 intake and, through it, Experiment 08. "
    "Not a measure of model accuracy. No model was called."
)

FALSE_FLAGS = (
    "customer_approved",
    "customer_rejected",
    "customer_onboarded",
    "final_risk_rating_assigned",
    "sar_filed",
    "external_sent",
    "production_record_written",
    "customer_text_hints_at_suspicion",
    "purpose_taken_from_document",
    "documents_confirmed_by_document",
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _item(draft: dict, section: str, item_id: str) -> dict:
    return next(item for item in draft["checklist"][section] if item["id"] == item_id)


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
    rules = date.fromisoformat(case["rules_as_of"]) if case.get("rules_as_of") else None

    if expect.get("outcome") == "refused":
        try:
            review(case["customer_file"], as_of=as_of, stale_after_days=window, rules_as_of=rules)
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
        add("refused", False, "review returned a draft")
        return finish("failed")

    try:
        result = review(case["customer_file"], as_of=as_of, stale_after_days=window, rules_as_of=rules)
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
    add("documents_confirmed", result["documents_confirmed"] is False, "false")
    add("purpose_confirmed", result["purpose_confirmed"] is False, "false")
    add("final_risk_rating", result["final_risk_rating"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("fatf_list_downloaded", result["fatf_list_downloaded"] is False, "false")
    add("jmlsg_not_opened", result["jmlsg_part_i_opened"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("intake_followed", result["document_intake"]["prompt_injection"]["followed"] is False, "false")
    add("intake_id", result["document_intake"]["experiment_id"] == "exp-12-document-intake", "exp-12")
    add("intake_not_confirmed", result["document_intake"]["files_confirmed"] is False, "false")
    add("edd_applied", result["checklist"]["edd_applied"] is False, "false")
    add("sufficient", result["checklist"]["sufficient"] is False, "false")
    add("hints", result["customer_facing"]["hints_at_suspicion"] is False, "false")
    add("not_sent", result["customer_facing"]["may_be_sent_by_agent"] is False, "false")
    add("no_deletion", result["record_keeping"]["deletion_performed"] is False, "false")
    for flag in FALSE_FLAGS:
        add(f"flag {flag}", result["flags"][flag] is False, "false")

    status_checks = {
        "identity_status": ("cdd", "reg_28_2_a_identify"),
        "address_status": ("cdd", "intake_address_marker"),
        "verify_status": ("cdd", "reg_28_2_b_verify"),
        "purpose_status": ("cdd", "reg_28_2_c_purpose_and_nature"),
        "beneficial_status": ("cdd", "reg_28_4_beneficial_owner"),
        "pep_status": ("edd_triggers", "reg_33_1_d_pep"),
        "fatf_status": ("edd_triggers", "reg_33_1_b_fatf_call_for_action"),
        "unusual_status": ("edd_triggers", "reg_33_1_f_unusual_transaction"),
    }
    for key, (section, item_id) in status_checks.items():
        if key not in expect:
            continue
        actual = _item(result, section, item_id)["status"]
        add(key, actual == expect[key], actual)

    if "sources_stale" in expect:
        add("sources_stale", result["sources_stale"] is expect["sources_stale"], str(result["sources_stale"]))
    if "any_document_stale" in expect:
        add("any_document_stale", result["any_document_stale"] is expect["any_document_stale"], str(result["any_document_stale"]))
    if "date_status" in expect:
        actual = result["document_intake"]["files"][0]["date_status"]
        add("date_status", actual == expect["date_status"], actual)
    if "read_status" in expect:
        actual = result["document_intake"]["files"][0]["read_status"]
        add("read_status", actual == expect["read_status"], actual)
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "hidden_in" in expect:
        found = {signal["hidden_in"] for signal in result["prompt_injection"]["signals"]}
        add("hidden_in", expect["hidden_in"] in found, ",".join(sorted(found)) or "none")
    if "purpose_conflict" in expect:
        actual = result["purpose_preview"]["conflict"]
        add("purpose_conflict", actual is expect["purpose_conflict"], str(actual))
    if "period_begun" in expect:
        actual = result["record_keeping"]["period_begun"]
        add("period_begun", actual is expect["period_begun"], str(actual))
    if "arithmetic_end" in expect:
        actual = result["record_keeping"]["arithmetic_end"]
        add("arithmetic_end", actual == expect["arithmetic_end"], str(actual))
    if "prohibited_includes" in expect:
        actual = result["prohibited_payload_keys"]
        missing = [item for item in expect["prohibited_includes"] if item not in actual]
        add("prohibited_keys", not missing, ",".join(actual) or "none")
    if "customer_text_excludes" in expect:
        lowered = result["customer_facing"]["text"].lower()
        present = [token for token in expect["customer_text_excludes"] if token.lower() in lowered]
        add("customer_text_excludes", not present, ",".join(present) or "clear")
    if "gateway_called" in expect:
        actual = result["document_intake"]["gateway"]["called"]
        add("gateway_called", actual is expect["gateway_called"], str(actual))
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the KYC checklist")
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
