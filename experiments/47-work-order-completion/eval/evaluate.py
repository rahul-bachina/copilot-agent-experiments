#!/usr/bin/env python3
"""Deterministic smoke test of the completion draft.

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

from complete import LABEL, draft_completion, record_review  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    result = draft_completion(case["pack"], case["as_of"])
    reviews = case.get("reviews") or []
    for review in reviews:
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
    add("echoed", result["narrative_echoed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("human_route", result["human_route"]["offered"] is True, "true")
    add("agent_closes", result["human_route"]["agent_closes_the_job"] is False, "false")
    add("job_closed", result["flags"]["job_closed"] is False, "false")
    add("charges", result["flags"]["charges_raised"] is False, "false")
    add("ordered", result["flags"]["parts_ordered"] is False, "false")
    add("contacted", result["flags"]["customer_contacted"] is False, "false")
    add("labelled", result["flags"]["person_labelled_vulnerable"] is False, "false")
    add("production", result["flags"]["production_system_written"] is False, "false")
    add("duty", result["regulatory"]["hswa_duty_met"] is False, "false")
    add("accuracy", result["regulatory"]["accuracy_principle_decided"] is False, "false")
    add("summary_sent", result["regulatory"]["written_summary_sent"] is False, "false")

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if expect.get("human_approval_null") is True:
        add("human_approval", result["human_approval"] is None, "null")
    if "follow_up_job" in expect:
        add("follow_up_job", result["flags"]["follow_up_job"] is expect["follow_up_job"], str(result["flags"]["follow_up_job"]))
    if "safety" in expect:
        add("safety", result["flags"]["safety_escalation"] is expect["safety"], str(result["flags"]["safety_escalation"]))
    if "awaabs_follow" in expect:
        add("awaabs_follow", result["flags"]["awaabs_follow_up_for_a_person"] is expect["awaabs_follow"], str(result["flags"]["awaabs_follow_up_for_a_person"]))
    if "awaabs_called" in expect:
        add("awaabs_called", result["awaabs"]["called"] is expect["awaabs_called"], str(result["awaabs"]["called"]))
    if "operative" in expect:
        add("operative", result["awaabs"]["any_operative_deadline"] is expect["operative"], str(result["awaabs"]["any_operative_deadline"]))
    if "category" in expect:
        add("category", result["awaabs"]["proposed_category"] == expect["category"], str(result["awaabs"]["proposed_category"]))
    if "vulnerability" in expect:
        categories = result["vulnerability"]["categories"]
        add("vulnerability", expect["vulnerability"] in categories, str(categories))
    if "work_done" in expect:
        proposed = next(field["proposed"] for field in result["fields"] if field["field_id"] == "work_done")
        add("work_done", proposed == expect["work_done"], str(proposed))
    if "outstanding" in expect:
        proposed = next(field["proposed"] for field in result["fields"] if field["field_id"] == "outstanding_hazards")
        add("outstanding", expect["outstanding"] in (proposed or []), str(proposed))
    if "inconsistency" in expect:
        add("inconsistency", expect["inconsistency"] in result["inconsistencies"], str(result["inconsistencies"]))
    if "gap" in expect:
        add("gap", expect["gap"] in result["gaps"], str(result["gaps"]))
    if "signal" in expect:
        signals = [row["signal"] for row in result["prompt_injection"]["signals"]]
        add("signal", expect["signal"] in signals, str(signals))
    if "hidden_in" in expect:
        carriers = [row["hidden_in"] for row in result["prompt_injection"]["signals"]]
        add("hidden_in", expect["hidden_in"] in carriers, str(carriers))
    if "access" in expect:
        proposed = next(field["proposed"] for field in result["fields"] if field["field_id"] == "vulnerability_or_access")
        add("access", expect["access"] in proposed["access_flags"], str(proposed["access_flags"]))
    if "rules_current" in expect:
        add("rules_current", result["stale"]["rules_current"] is expect["rules_current"], str(result["stale"]["rules_current"]))
        if expect["rules_current"] is False:
            add("quotes_withheld", all(row["taken"] is None for row in result["sources"]), "withheld")
    if "review_reason" in expect:
        add("review_reason", result["review"]["reason"] == expect["review_reason"], str(result["review"]["reason"]))
    if "review_accepted" in expect:
        add("review_accepted", result["review"]["accepted"] is expect["review_accepted"], str(result["review"]["accepted"]))
    if "written" in expect:
        add("written", result["stub_write"]["fields_written"] == expect["written"], str(result["stub_write"]["fields_written"]))
    if "stub_executed" in expect:
        add("stub_executed", result["stub_write"]["executed"] is expect["stub_executed"], str(result["stub_write"]["executed"]))
    if "approved_fields" in expect:
        approved = None if result["human_approval"] is None else result["human_approval"]["approved_fields"]
        add("approved_fields", approved == expect["approved_fields"], str(approved))
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the completion draft")
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
