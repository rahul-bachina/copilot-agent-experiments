#!/usr/bin/env python3
"""Deterministic smoke test of the response drafter.

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

from response import LABEL, draft_response, record_review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    library = case.get("library")
    result = draft_response(case["case"], case["as_of"], library=library)
    if "review" in case:
        result = record_review(result, case["review"])
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
    add("echoed", result["case_text_echoed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("human_route", result["human_route"]["offered"] is True, "true")
    add("agent_sends", result["human_route"]["agent_sends"] is False, "false")
    add("may_send", result["draft"]["may_be_sent_by_agent"] is False, "false")
    add("message_sent", result["flags"]["message_sent"] is False, "false")
    add("case_written", result["flags"]["case_written"] is False, "false")
    add("redress", result["flags"]["redress_offered"] is False, "false")
    add("closed", result["flags"]["complaint_closed"] is False, "false")
    add("promised", result["flags"]["outcome_promised"] is False, "false")
    add("labelled", result["flags"]["customer_labelled_vulnerable"] is False, "false")
    add("outcome_met", result["regulatory"]["consumer_duty"]["outcome_met"] is False, "false")
    add("duty_met", result["regulatory"]["equality_act"]["duty_met"] is False, "false")
    add("article_12_met", result["regulatory"]["article_12"]["article_12_met"] is False, "false")
    add("not_anonymised", result["pii_gateway"].get("output_is_anonymised") is False, "false")
    add("not_released", result["pii_gateway"].get("agent_may_release") is not True, "false")
    if case["case"].get("text") and len(case["case"]["text"]) > 24:
        add("source_not_in_output", case["case"]["text"] not in blob, "absent")

    reviewed = "review" in case
    if reviewed:
        add("review_executed", result["review"]["executed"] is False, "false")
        if expect.get("review_accepted") is True:
            add("review_accepted", result["review"]["accepted"] is True, result["review"]["reason"])
            if result.get("human_approval"):
                add("approval_not_execution", result["human_approval"]["executed"] is False, "false")
                add("approval_not_send", result["human_approval"]["message_sent"] is False, "false")
            else:
                add("approval_null", result["human_approval"] is None, "null")
        else:
            add("review_refused", result["review"]["refused"] is True, result["review"]["reason"])
            add("approval_null", result["human_approval"] is None, "null")
    elif expect.get("human_approval_null", True) is True:
        add("human_approval", result["human_approval"] is None, "null")

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "cited_ids" in expect:
        actual = [item["id"] for item in result["sources_cited"]]
        add("cited_ids", actual == expect["cited_ids"], str(actual))
    if "refused" in expect:
        actual = {item["id"]: item["reason"] for item in result["snippets_refused"]}
        for item in expect["refused"]:
            add(
                f"refused {item['id']}",
                actual.get(item["id"]) == item["reason"],
                str(actual.get(item["id"])),
            )
    if "rules_current" in expect:
        add("rules_current", result["stale"]["rules_current"] is expect["rules_current"], str(result["stale"]["rules_current"]))
    if "injection_detected" in expect:
        add(
            "injection_detected",
            result["prompt_injection"]["detected"] is expect["injection_detected"],
            str(result["prompt_injection"]["detected"]),
        )
    if "consumer_duty_applied" in expect:
        add(
            "consumer_duty_applied",
            result["regulatory"]["consumer_duty"]["applied"] is expect["consumer_duty_applied"],
            str(result["regulatory"]["consumer_duty"]["applied"]),
        )
    if "plain_passed" in expect:
        add("plain_passed", result["plain_english"]["passed"] is expect["plain_passed"], str(result["plain_english"]["passed"]))
    if "tone_passed" in expect:
        add("tone_passed", result["tone"]["passed"] is expect["tone_passed"], str(result["tone"]["passed"]))
    if "gateway_called" in expect:
        add("gateway_called", result["pii_gateway"]["called"] is expect["gateway_called"], str(result["pii_gateway"]["called"]))
    if "gateway_entity" in expect:
        types = result["pii_gateway"].get("entity_types") or []
        add("gateway_entity", expect["gateway_entity"] in types, str(types))
    if "approved_flag" in expect:
        add(
            "approved_flag",
            result["flags"]["representative_approved_own_send"] is expect["approved_flag"],
            str(result["flags"]["representative_approved_own_send"]),
        )
    if "review_reason" in expect:
        add("review_reason", result["review"]["reason"] == expect["review_reason"], result["review"]["reason"])
    if "recipient_approved" in expect:
        add(
            "recipient_approved",
            result["recipient"]["approved"] is expect["recipient_approved"],
            str(result["recipient"]["approved"]),
        )
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of response drafting")
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
