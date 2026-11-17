#!/usr/bin/env python3
"""Deterministic smoke test of the learning path planner.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from plan import draft_plan, record_approval  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def _check(result: dict, expect: dict) -> list[str]:
    failed = []

    def need(condition: bool, name: str) -> None:
        if not condition:
            failed.append(name)

    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], "outcome")
    if "course_ids" in expect:
        need([step["course_id"] for step in result.get("steps") or []] == expect["course_ids"], "course_ids")
    if "within_budget" in expect:
        need(result["budget"]["within_budget"] is expect["within_budget"], "within_budget")
    if "enrolment_request_raised" in expect:
        need(result.get("enrolment_request_raised") is expect["enrolment_request_raised"], "enrolment_request_raised")
    if "human_approval" in expect:
        need(result.get("human_approval") == expect["human_approval"], "human_approval")
    if "enrolled" in expect:
        need(result.get("enrolled") is expect["enrolled"], "enrolled")
    if "spent_gbp" in expect:
        need(result.get("spent_gbp") == expect["spent_gbp"], "spent_gbp")
    if "blocked_reason" in expect:
        need(result.get("blocked_reason") == expect["blocked_reason"], "blocked_reason")
    if "affirmed_skill_ids" in expect:
        need(result.get("affirmed_skill_ids") == expect["affirmed_skill_ids"], "affirmed_skill_ids")
    if "not_affirmed" in expect:
        need(all(skill not in result.get("affirmed_skill_ids", []) for skill in expect["not_affirmed"]), "not_affirmed")
    exclusions = {row["course_id"]: row for row in result.get("exclusions") or []}
    if "exclusion" in expect:
        for course_id, reason in expect["exclusion"].items():
            need(exclusions.get(course_id, {}).get("reason") == reason, f"exclusion:{course_id}")
    if "cost_used_null" in expect:
        need(exclusions[expect["cost_used_null"]]["cost_used"] is None, "cost_used_null")
    if "agent_chose_source" in expect:
        need(result["flags"]["agent_chose_source"] is expect["agent_chose_source"], "agent_chose_source")
    if "marking" in expect:
        for course_id, marking in expect["marking"].items():
            need(exclusions[course_id]["marking"] == marking, f"marking:{course_id}")
    if "legal_hold" in expect:
        for course_id, held in expect["legal_hold"].items():
            need(exclusions[course_id]["legal_hold"] is held, f"legal_hold:{course_id}")
    if "legal_hold_step" in expect:
        step = next(step for step in result["steps"] if step["course_id"] == expect["legal_hold_step"])
        need(step["legal_hold"] is True, "legal_hold_step")
    if "retention_contains" in expect:
        labels = result["steps"][0]["retention_labels"]
        need(expect["retention_contains"] in labels, "retention_contains")
    if "adjustment_decided" in expect:
        need(result["flags"]["adjustment_decided"] is expect["adjustment_decided"], "adjustment_decided")
    if "employees_ranked" in expect:
        need(result["flags"]["employees_ranked"] is expect["employees_ranked"], "employees_ranked")
    if "promotion_use" in expect:
        need(result["flags"]["promotion_use"] is expect["promotion_use"], "promotion_use")
    if "coerced" in expect:
        need(result.get("coerced") is expect["coerced"], "coerced")
    if "sources_current" in expect:
        need(result.get("sources_current") is expect["sources_current"], "sources_current")
    if "may_be_relied_on" in expect:
        need(result.get("may_be_relied_on") is expect["may_be_relied_on"], "may_be_relied_on")
    need(result.get("enrolled") is False, "never_enrolled")
    need(result.get("booked") is False, "never_booked")
    need(result.get("spent_gbp") is None, "never_spent")
    return failed


def evaluate_case(case: dict, catalogue: dict, framework: dict, directory: dict) -> dict:
    try:
        result = draft_plan(
            {
                "synthetic": True,
                "employee_ref": case["employee_ref"],
                "goals": case["goals"],
            },
            catalogue,
            framework,
            directory,
            case.get("as_of", "2026-11-17"),
        )
        mode = case.get("approve")
        if mode in {"employee_only", "both"}:
            result = record_approval(
                result,
                {
                    "plan_id": result["plan_id"],
                    "approver_ref": case["employee_ref"],
                    "decision": "approve",
                    "item": "learning-plan",
                },
            )
        if mode == "both":
            result = record_approval(
                result,
                {
                    "plan_id": result["plan_id"],
                    "approver_ref": result.get("manager_ref") or "EMP-2001",
                    "decision": "approve",
                    "item": "learning-plan",
                },
            )
        failed = _check(result, case["expect"])
        status = "passed" if not failed else "failed"
        return {"case_id": case["id"], "status": status, "checks": failed, "outcome": result.get("outcome")}
    except Exception as exc:  # noqa: BLE001 - one case, one error, not a second failure
        return {"case_id": case["id"], "status": "error", "checks": [type(exc).__name__], "outcome": None}


def summarise(results: list[dict]) -> dict:
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")
    errors = sum(1 for item in results if item["status"] == "error")
    total = len(results)
    if passed + failed + errors != total:
        raise RuntimeError("smoke totals do not add up")
    return {"passed": passed, "failed": failed, "errors": errors, "total_cases": total}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    output = None
    if "--output" in argv:
        index = argv.index("--output")
        output = Path(argv[index + 1])
    dataset = load_dataset()
    ids = [case["id"] for case in dataset["cases"]]
    if len(ids) != len(set(ids)):
        sys.stderr.write("Duplicate case ids\n")
        return 1
    catalogue = _load("catalogue.json")
    framework = _load("framework.json")
    directory = _load("directory.json")
    results = [evaluate_case(case, catalogue, framework, directory) for case in dataset["cases"]]
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
    destination = Path(__file__).parent / "smoke_report.json"
    destination.write_text(text, encoding="utf-8")
    if output is not None:
        output.write_text(text, encoding="utf-8")
    print(
        f"Smoke test: {summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['errors']} errors, {summary['total_cases']} cases"
    )
    if summary["failed"] or summary["errors"]:
        for item in results:
            if item["status"] != "passed":
                print(item["case_id"], item["status"], item["checks"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
