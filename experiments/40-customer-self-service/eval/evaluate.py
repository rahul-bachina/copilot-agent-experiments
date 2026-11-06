#!/usr/bin/env python3
"""Deterministic smoke test of the customer self-service draft.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.service import LABEL, draft_reply, record_review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)

PROHIBITED = (
    "password_reset",
    "payment_taken",
    "complaint_closed",
    "tariff_changed",
    "contract_changed",
    "record_changed",
    "appointment_booked",
    "message_sent",
    "customer_labelled_vulnerable",
    "secrets_collected",
    "stale_article_quoted",
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    result = draft_reply(case["enquiry"], case["as_of"])
    if "review" in case:
        result = record_review(result, case["review"])
    for review in case.get("reviews") or []:
        result = record_review(result, review)
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
    add("label", result["label"] == LABEL, result["label"])
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("executed", result["executed"] is False, "false")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("echoed", result["enquiry_text_echoed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("disclosure", "automated AI chatbot" in result["ai_disclosure"], "present")
    add("human_route", result["human_route"]["offered"] is True, "true")
    add("not_anonymised", result["pii_gateway"].get("output_is_anonymised") is False, "false")
    add("not_released", result["pii_gateway"].get("agent_may_release") is False, "false")
    for key in PROHIBITED:
        if key in expect and expect[key] is False:
            add(key, result["flags"][key] is False, "false")
        elif key not in expect:
            add(key, result["flags"][key] is False, "false")

    reviewed = "review" in case or "reviews" in case
    if reviewed:
        add("review_executed", result["review"]["executed"] is False, "false")
        if expect.get("review_accepted") is True:
            add("review_accepted", result["review"]["accepted"] is True, str(result["review"]["reason"]))
            add("approval_not_execution", result["human_approval"]["executed"] is False, "false")
        else:
            add("review_refused", result["review"]["refused"] is True, result["review"]["reason"])
    if expect.get("human_approval_null") is True:
        add("human_approval", result["human_approval"] is None, "null")
    elif not reviewed:
        add("human_approval", result["human_approval"] is None, "null")

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "article_id" in expect:
        actual = None if result["article"] is None else result["article"]["id"]
        add("article_id", actual == expect["article_id"], str(actual))
    if "body_quoted" in expect:
        actual = False if result["article"] is None else result["article"]["body_quoted"]
        add("body_quoted", actual is expect["body_quoted"], str(actual))
    if "identity_trusted" in expect:
        add("identity_trusted", result["identity"]["trusted"] is expect["identity_trusted"], str(result["identity"]["trusted"]))
    if "action_kind" in expect:
        actual = None if result["proposed_action"] is None else result["proposed_action"]["kind"]
        add("action_kind", actual == expect["action_kind"], str(actual))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
    if "injection_detected" in expect:
        add("injection_detected", result["prompt_injection"]["detected"] is expect["injection_detected"], str(result["prompt_injection"]["detected"]))
    if "analyse_called" in expect:
        add("analyse_called", result["complaint_gate"]["called"] is expect["analyse_called"], str(result["complaint_gate"]["called"]))
    if "clock" in expect:
        add("clock", result["complaint_gate"]["clock_calculated"] is expect["clock"], str(result["complaint_gate"]["clock_calculated"]))
    if "labelled" in expect:
        add("labelled", result["complaint_gate"]["customer_labelled_vulnerable"] is expect["labelled"], "false")
    if "ofgem" in expect:
        add("ofgem", result["regulatory"]["ofgem"]["scenario_is_energy_retail"] is expect["ofgem"], str(expect["ofgem"]))
    if "section_149" in expect:
        add("section_149", result["regulatory"]["equality_act"]["section_149_noted"] is expect["section_149"], "noted")
    if "duty_met" in expect:
        add("duty_met", result["regulatory"]["equality_act"]["duty_met"] is expect["duty_met"], "false")
    if "gateway_entity" in expect:
        types = result["pii_gateway"].get("entity_types") or []
        add("gateway_entity", expect["gateway_entity"] in types, str(types))
    if "customer_confirmed" in expect:
        add("customer_confirmed", result["flags"]["customer_confirmed"] is expect["customer_confirmed"], str(result["flags"]["customer_confirmed"]))
    if "handler_approved_own_send" in expect:
        add(
            "handler_approved_own_send",
            result["flags"]["handler_approved_own_send"] is expect["handler_approved_own_send"],
            str(result["flags"]["handler_approved_own_send"]),
        )
    if "review_reason" in expect:
        add("review_reason", result["review"]["reason"] == expect["review_reason"], result["review"]["reason"])
    if "prior_confirmation" in expect:
        actual = (result.get("human_approval") or {}).get("prior_customer_confirmation")
        add("prior_confirmation", actual == expect["prior_confirmation"], str(actual))
    if "appointment_booked" in expect:
        add("appointment_booked", result["flags"]["appointment_booked"] is expect["appointment_booked"], "false")
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of customer self-service")
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
    sys.stdout.write(text)
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["total_cases"] < 16:
        sys.stderr.write("Fewer than 16 synthetic cases\n")
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        sys.stderr.write("Smoke totals do not add up\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
