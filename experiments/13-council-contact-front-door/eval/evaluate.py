#!/usr/bin/env python3
"""Deterministic smoke test of the council front door.

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

from src.front_door import LABEL, triage  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)

PROHIBITED = (
    "eligibility_decided",
    "case_created",
    "message_sent",
    "appointment_booked",
    "payment_taken",
    "enforcement_action",
    "released_to_resident",
    "stale_article_quoted",
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = triage(case["enquiry"], case["as_of"])
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
    add("human_approval", result["human_approval"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("echoed", result["enquiry_text_echoed"] is False, "false")
    add("accepted", result["adviser_accepted_published_text"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("disclosure", "automated AI chatbot" in result["ai_disclosure"], "present")
    for key in PROHIBITED:
        add(key, result["flags"][key] is False, "false")

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "article_id" in expect:
        actual = result["answer"]["verbatim_article_id"]
        add("article_id", actual == expect["article_id"], str(actual))
    if "sufficient" in expect:
        actual = result["answer"]["sufficient"]
        add("sufficient", actual is expect["sufficient"], str(actual))
    if "reason" in expect:
        actual = result["handover"]["reason"]
        add("reason", actual == expect["reason"], actual)
    if "queue" in expect:
        actual = result["handover"]["queue"]
        add("queue", actual == expect["queue"], str(actual))
    if "answer_contains" in expect:
        actual = expect["answer_contains"] in (result["answer"]["text"] or "")
        add("answer_contains", actual, expect["answer_contains"])
    if "citation_ids" in expect:
        actual_ids = [row["article_id"] for row in result["citations"]]
        add("citation_ids", actual_ids == expect["citation_ids"], str(actual_ids))
    for flag in ("emergency", "vulnerability", "eligibility_asked", "any_article_stale", "live_record_refused"):
        if flag in expect:
            add(flag, result["flags"][flag] is expect[flag], str(result["flags"][flag]))
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the council front door")
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
        "council_in_fixtures": dataset.get("council"),
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
