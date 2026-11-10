#!/usr/bin/env python3
"""Deterministic smoke test of the field brief.

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

from prepare import LABEL, prepare_brief, record_review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    result = prepare_brief(case["pack"], case["as_of"])
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
    add("echoed", result["narrative_echoed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("human_route", result["human_route"]["offered"] is True, "true")
    add("agent_dispatches", result["human_route"]["agent_dispatches"] is False, "false")
    add("scheduled", result["flags"]["scheduled"] is False, "false")
    add("dispatched", result["flags"]["dispatched"] is False, "false")
    add("closed", result["flags"]["closed"] is False, "false")
    add("entry", result["flags"]["entry_authorised"] is False, "false")
    add("labelled", result["flags"]["person_labelled_vulnerable"] is False, "false")
    add("code_copied", result["flags"]["code_copied"] is False, "false")
    add("duty", result["regulatory"]["hswa_duty_met"] is False, "false")
    add("risk_assessment", result["regulatory"]["risk_assessment_is_this_brief"] is False, "false")
    add("covenant", result["regulatory"]["awaabs_covenant_decided"] is False, "false")

    reviewed = "review" in case
    if reviewed:
        add("review_executed", result["review"]["executed"] is False, "false")
        if expect.get("review_accepted") is True:
            add("review_accepted", result["review"]["accepted"] is True, result["review"]["reason"])
        elif expect.get("review_accepted") is False:
            add("review_refused", result["review"]["refused"] is True, result["review"]["reason"])
            add("approval_null", result["human_approval"] is None, "null")
    elif expect.get("human_approval_null", True) is True:
        add("human_approval", result["human_approval"] is None, "null")

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "highlight" in expect:
        add("highlight", expect["highlight"] in result["safety_highlights"], str(result["safety_highlights"]))
    if "hold" in expect:
        add("hold", expect["hold"] in result["safety_holds"], str(result["safety_holds"]))
    if "access" in expect:
        add("access", expect["access"] in result["access_flags"], str(result["access_flags"]))
    if "gap" in expect:
        add("gap", expect["gap"] in result["gaps"], str(result["gaps"]))
    if "injection" in expect:
        add("injection", result["prompt_injection"]["detected"] is expect["injection"], str(result["prompt_injection"]["detected"]))
    if "signal" in expect:
        signals = [row["signal"] for row in result["prompt_injection"]["signals"]]
        add("signal", expect["signal"] in signals, str(signals))
    if "hidden_in" in expect:
        carriers = [row["hidden_in"] for row in result["prompt_injection"]["signals"]]
        add("hidden_in", expect["hidden_in"] in carriers, str(carriers))
    if "awaabs_called" in expect:
        add("awaabs_called", result["awaabs"]["called"] is expect["awaabs_called"], str(result["awaabs"]["called"]))
    if "operative" in expect:
        add("operative", result["awaabs"]["any_operative_deadline"] is expect["operative"], str(result["awaabs"]["any_operative_deadline"]))
    if "category" in expect:
        add("category", expect["category"] in result["vulnerability"]["categories"], str(result["vulnerability"]["categories"]))
    if "description" in expect:
        add("description", expect["description"] in result["asset"]["description_catalogue_ids"], str(result["asset"]["description_catalogue_ids"]))
    if "code" in expect:
        add("code", result["possible_code_in_notes"] is expect["code"], str(result["possible_code_in_notes"]))
    if "rules_current" in expect:
        add("rules_current", result["stale"]["rules_current"] is expect["rules_current"], str(result["stale"]["rules_current"]))
        if expect["rules_current"] is False:
            add("quotes_withheld", all(row["taken"] is None for row in result["sources"]), "withheld")
    if "context_confirmed" in expect:
        add("context_confirmed", result["flags"]["context_confirmed"] is expect["context_confirmed"], str(result["flags"]["context_confirmed"]))
    if "hold_cleared" in expect:
        add("hold_cleared", result["flags"]["hold_cleared"] is expect["hold_cleared"], str(result["flags"]["hold_cleared"]))
    if "review_reason" in expect:
        add("review_reason", result["review"]["reason"] == expect["review_reason"], result["review"]["reason"])
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the field brief")
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
