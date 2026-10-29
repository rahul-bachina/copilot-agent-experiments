#!/usr/bin/env python3
"""Deterministic smoke test of the IT service desk.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.desk import LABEL, record_review, triage  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)

PROHIBITED = (
    "password_reset",
    "mfa_changed",
    "access_granted",
    "device_changed",
    "ticket_written",
    "message_sent",
    "licence_purchased",
    "remote_wipe",
    "fix_executed",
    "secrets_collected",
    "stale_article_quoted",
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = triage(case["ticket"], case["as_of"])
        if "review" in case:
            result = record_review(result, case["review"])
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
    add("echoed", result["ticket_text_echoed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("social_followed", result["social_engineering"]["followed"] is False, "false")
    add("disclosure", "automated AI chatbot" in result["ai_disclosure"], "present")
    add("not_anonymised", result["pii_gateway"].get("output_is_anonymised") is False, "false")
    add("not_released", result["pii_gateway"].get("agent_may_release") is False, "false")
    for key in PROHIBITED:
        add(key, result["flags"][key] is False, "false")

    if "review" in case:
        add("review_executed", result["review"]["executed"] is False, "false")
        if expect.get("review_accepted") is True:
            add("review_accepted", result["review"]["accepted"] is True, str(result["review"]["reason"]))
            add("approval_not_execution", result["human_approval"]["executed"] is False, "false")
        else:
            add("review_refused", result["review"]["refused"] is True, result["review"]["reason"])
            add("approval_null", result["human_approval"] is None, "null")
    else:
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
        actual = result["identity"]["trusted"]
        add("identity_trusted", actual is expect["identity_trusted"], str(actual))
    if "social_detected" in expect:
        actual = result["social_engineering"]["detected"]
        add("social_detected", actual is expect["social_detected"], str(actual))
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
    if "gateway_entity" in expect:
        types = result["pii_gateway"].get("entity_types") or []
        add("gateway_entity", expect["gateway_entity"] in types, str(types))
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the IT service desk")
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
        "organisation_in_fixtures": dataset.get("organisation"),
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
