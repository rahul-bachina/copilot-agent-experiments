#!/usr/bin/env python3
"""Deterministic smoke test of the interview pack builder.

The fixtures are synthetic. This is not a model score. Each case is counted
once. Paraphrase recall is a separate block and is not added to the case total.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pack import (  # noqa: E402
    draft_pack,
    record_hr_seen,
    record_pack_approval,
    record_questions_approval,
    record_rubric_approval,
    route_hash,
)

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def recall_report_safe() -> dict:
    sys.path.insert(0, str(ROOT / "tests"))
    from test_recall import recall_report as report

    return report()


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def _request(case: dict) -> dict:
    if case.get("use_sample") and not any(
        key in case for key in ("notes", "job_text", "essential", "proposed_questions", "invitation")
    ):
        return json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    request["notes"] = case.get("notes", "")
    request["proposed_questions"] = case.get("proposed_questions", [])
    request.pop("invitation", None)
    if "job_text" in case:
        request["job"]["text"] = case["job_text"]
        request["job"]["marking"] = case.get("marking", "OFFICIAL")
        request["job"]["legal_hold"] = case.get("legal_hold", False)
    if "essential" in case:
        request["person_specification"]["essential"] = case["essential"]
    if "invitation" in case:
        request["invitation"] = case["invitation"]
    if case.get("not_synthetic"):
        request["synthetic"] = False
    return request


def _approve(pack: dict, directory: dict) -> dict:
    current = record_questions_approval(
        pack,
        directory,
        {
            "item": "questions",
            "decision": "accept",
            "approver_ref": "REC-1001",
            "pack_hash": pack["pack_hash"],
            "questions_hash": pack["questions_hash"],
        },
    )
    current = record_rubric_approval(
        current,
        directory,
        {
            "item": "rubric",
            "decision": "accept",
            "approver_ref": "REC-1001",
            "pack_hash": current["pack_hash"],
            "rubric_hash": current["rubric_hash"],
        },
    )
    for route in list(current.get("hr_routes") or []):
        current = record_hr_seen(
            current,
            directory,
            {
                "item": "hr-route",
                "decision": "seen",
                "approver_ref": "HR-2001",
                "pack_hash": current["pack_hash"],
                "route_id": route["route_id"],
                "route_hash": route_hash(route),
            },
        )
    return record_pack_approval(
        current,
        directory,
        {
            "item": "pack",
            "decision": "approve",
            "approver_ref": "REC-1001",
            "pack_hash": current["pack_hash"],
        },
    )


def _check(result: dict, expect: dict) -> list[str]:
    failed = []

    def need(condition: bool, name: str) -> None:
        if not condition:
            failed.append(name)

    blob = json.dumps(result)
    for key in (
        "outcome",
        "question_count",
        "approved_for_use",
        "marking",
        "legal_hold",
        "body_copied",
        "coerced",
        "health_question_decided",
        "section_20_decided",
        "section_20_met",
        "positive_action_decided",
        "right_to_work_statement_present",
        "right_to_work_checked",
        "invented_criteria",
        "cue_copied",
        "scored",
        "ranked",
        "contacted",
        "hiring_decision",
        "sources_current",
        "may_be_relied_on",
        "as_of",
    ):
        if key in expect:
            need(result.get(key) == expect[key], key)
    if "human_approval" in expect:
        need(result.get("human_approval") == expect["human_approval"], "human_approval")
    if expect.get("human_approval_set"):
        need(isinstance(result.get("human_approval"), dict), "human_approval_set")
    if "probe_present" in expect:
        need(expect["probe_present"] in (result.get("input_probe_categories") or []), "probe_present")
    if "probe_absent" in expect:
        need(expect["probe_absent"] not in (result.get("input_probe_categories") or []), "probe_absent")
    kinds = {row.get("kind") for row in result.get("hr_routes") or []}
    if "route_present" in expect:
        need(expect["route_present"] in kinds, "route_present")
    if "route_present_also" in expect:
        need(expect["route_present_also"] in kinds, "route_present_also")
    if result.get("hr_routes"):
        need(all(row.get("decided") is False for row in result["hr_routes"]), "routes_not_decided")
    if expect.get("guide_stale"):
        need((result.get("guide") or {}).get("stale") is True, "guide_stale")
    if expect.get("below_opened_rule"):
        need((result.get("adjustment") or {}).get("below_opened_rule") is True, "below_opened_rule")
    if expect.get("prohibited_empty"):
        need(result.get("prohibited_requests") == [], "prohibited_empty")
    if "wording_phrase" in expect:
        phrases = [row.get("phrase") for row in result.get("wording_flags") or []]
        need(expect["wording_phrase"] in phrases, "wording_phrase")
    if "absent_text" in expect:
        need(expect["absent_text"].casefold() not in blob.casefold(), "absent_text")
    need(result.get("contacted") is False, "never_contacted")
    need(result.get("scheduled") is False, "never_scheduled")
    need(result.get("scored") is False, "never_scored")
    need(result.get("ranked") is False, "never_ranked")
    need(result.get("hiring_decision") is False, "never_hired")
    need(result.get("discrimination_decided") is False, "never_discrimination")
    need(result.get("legal_advice") is False, "never_advice")
    need(result.get("coerced") is False, "never_coerced")
    return failed


def evaluate_case(case: dict, guide: dict, directory: dict) -> dict:
    try:
        result = draft_pack(_request(case), guide, directory, case.get("as_of", "2026-11-14"))
        if case.get("approve"):
            result = _approve(result, directory)
        failed = _check(result, case["expect"])
        status = "passed" if not failed else "failed"
        return {"case_id": case["id"], "status": status, "checks": failed, "outcome": result.get("outcome")}
    except Exception as exc:  # noqa: BLE001 - one case, one error
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
    guide = _load("guide.json")
    directory = _load("directory.json")
    results = [evaluate_case(case, guide, directory) for case in dataset["cases"]]
    summary = summarise(results)
    recall = recall_report_safe()
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_label": dataset.get("label"),
        "organisation_in_fixtures": dataset.get("organisation"),
        "summary": summary,
        "cases": results,
        "paraphrase_recall": recall,
        "recall_not_added_to_case_total": True,
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
    for name, row in recall["categories"].items():
        print(f"Recall {name}: {row['caught']}/{row['variants']} ({row['recall']})")
    if summary["failed"] or summary["errors"]:
        for item in results:
            if item["status"] != "passed":
                print(item["case_id"], item["status"], item["checks"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
