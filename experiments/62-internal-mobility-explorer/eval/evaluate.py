#!/usr/bin/env python3
"""Deterministic smoke test of the internal mobility explorer.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from explore import explore  # noqa: E402

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

    relevant = [row["vacancy_id"] for row in result.get("relevant") or []]
    flagged = {row["vacancy_id"]: row for row in result.get("flagged") or []}
    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], "outcome")
    if "not_outcome" in expect:
        need(result.get("outcome") != expect["not_outcome"], "not_outcome")
    if "vacancy_ids" in expect:
        need(relevant == expect["vacancy_ids"], "vacancy_ids")
    if "includes" in expect:
        need(all(vacancy_id in relevant for vacancy_id in expect["includes"]), "includes")
    if "not_relevant" in expect:
        need(all(vacancy_id not in relevant for vacancy_id in expect["not_relevant"]), "not_relevant")
    if "eligibility" in expect:
        by_id = {row["vacancy_id"]: row for row in result.get("relevant") or []}
        for vacancy_id, status in expect["eligibility"].items():
            need(by_id.get(vacancy_id, {}).get("eligibility", {}).get("status") == status, f"eligibility:{vacancy_id}")
    if "flagged" in expect:
        for vacancy_id, reason in expect["flagged"].items():
            need(flagged.get(vacancy_id, {}).get("reason") == reason, f"flagged:{vacancy_id}")
    if "marking" in expect:
        for vacancy_id, marking in expect["marking"].items():
            need(flagged.get(vacancy_id, {}).get("marking") == marking, f"marking:{vacancy_id}")
    if "closing_date_used_null" in expect:
        need(flagged[expect["closing_date_used_null"]]["closing_date_used"] is None, "closing_date_used_null")
    if "hr_seen" in expect:
        need(result["hr_seen"]["recorded"] is expect["hr_seen"], "hr_seen")
    if "coerced" in expect:
        need(result.get("coerced") is expect["coerced"], "coerced")
    if "agent_chose_source" in expect:
        need(result["flags"]["agent_chose_source"] is expect["agent_chose_source"], "agent_chose_source")
    if "directory_proxy_fields_used" in expect:
        need(result["flags"]["directory_proxy_fields_used"] is expect["directory_proxy_fields_used"], "directory_proxy_fields_used")
    if "suitability_inferred" in expect:
        need(result["flags"]["suitability_inferred"] is expect["suitability_inferred"], "suitability_inferred")
    if "adjustment_decided" in expect:
        need(result["flags"]["adjustment_decided"] is expect["adjustment_decided"], "adjustment_decided")
    if "selection_made" in expect:
        need(result["flags"]["selection_made"] is expect["selection_made"], "selection_made")
    if "interest_shared_with_manager" in expect:
        need(result["flags"]["interest_shared_with_manager"] is expect["interest_shared_with_manager"], "interest_shared")
    if "interest_shared_with_recruiters" in expect:
        need(
            result["flags"]["interest_shared_with_recruiters"] is expect["interest_shared_with_recruiters"],
            "interest_shared_recruiters",
        )
    if "contacted" in expect:
        need(result["flags"]["contacted"] is expect["contacted"], "contacted")
    if "sources_current" in expect:
        need(result.get("sources_current") is expect["sources_current"], "sources_current")
    if "may_be_relied_on" in expect:
        need(result.get("may_be_relied_on") is expect["may_be_relied_on"], "may_be_relied_on")
    if "role_id" in expect:
        need(result.get("role_id") == expect["role_id"], "role_id")
    if "experiment_36_called" in expect:
        need(result["experiment_36"]["called"] is expect["experiment_36_called"], "experiment_36_called")
    if "experiment_61_called" in expect:
        need(result["experiment_61"]["called"] is expect["experiment_61_called"], "experiment_61_called")
    if "experiment_61_enrolled" in expect:
        need(result["experiment_61"]["enrolled"] is expect["experiment_61_enrolled"], "experiment_61_enrolled")
    if "experiment_61_selection" in expect:
        need(
            result["experiment_61"]["used_as_a_selection_factor"] is expect["experiment_61_selection"],
            "experiment_61_selection",
        )
    if "cue_absent" in expect:
        need(expect["cue_absent"].lower() not in json.dumps(result).lower(), "cue_absent")
    need(result["flags"]["applied"] is False, "never_applied")
    need(result["flags"]["shortlisted"] is False, "never_shortlisted")
    need(result["flags"]["selection_made"] is False, "never_selected")
    need(result["flags"]["eligibility_decided"] is False, "never_eligibility")
    return failed


def evaluate_case(case: dict, vacancies: dict, rules: dict, framework: dict, directory: dict) -> dict:
    try:
        result = explore(
            {
                "synthetic": True,
                "employee_ref": case["employee_ref"],
                "experience": case["experience"],
            },
            vacancies,
            rules,
            framework,
            directory,
            case.get("as_of", "2026-11-18"),
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
    vacancies = _load("vacancies.json")
    rules = _load("eligibility.json")
    framework = _load("framework.json")
    directory = _load("directory.json")
    results = [evaluate_case(case, vacancies, rules, framework, directory) for case in dataset["cases"]]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_label": dataset.get("label"),
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
