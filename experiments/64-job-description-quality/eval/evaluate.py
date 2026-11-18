#!/usr/bin/env python3
"""Deterministic smoke test of the job-description checker.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from review import record_final_wording, record_suggestion_decision, review_draft  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)
MANDATE = (
    "Applicants must have the right to work in the United Kingdom. "
    "Ashcombe Borough Council is a Disability Confident employer."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def _request(case: dict) -> dict:
    if case.get("use_sample"):
        return json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    draft = {
        "draft_id": "JD-1",
        "title": "Case officer",
        "grade": "SO1",
        "salary": "£29,000",
        "location": "Ashcombe civic centre",
        "marking": "OFFICIAL",
        "retention_labels": ["HR-recruitment-12-months"],
        "legal_hold": False,
        "essential": ["able to draft routine letters"],
        "duties": ["draft routine letters", "maintain a case record"],
        "text": case["text"],
    }
    draft.update(case.get("draft") or {})
    request = {
        "synthetic": True,
        "recruiter_ref": case.get("recruiter_ref", "REC-1001"),
        "draft": draft,
    }
    if "question_date" in case:
        request["question_date"] = case["question_date"]
    return request


def _check(result: dict, expect: dict) -> list[str]:
    failed = []

    def need(condition: bool, name: str) -> None:
        if not condition:
            failed.append(name)

    categories = [row["category"] for row in result.get("findings") or []]
    blob = json.dumps(result)
    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], "outcome")
    if "categories_present" in expect:
        for category in expect["categories_present"]:
            need(category in categories, f"present:{category}")
    if "categories_absent" in expect:
        for category in expect["categories_absent"]:
            need(category not in categories, f"absent:{category}")
    for key in (
        "published",
        "posted",
        "sent",
        "legal_advice",
        "candidates_scored",
        "people_scored",
        "coerced",
        "sources_current",
        "may_be_relied_on",
        "occupational_requirement_decided",
        "positive_action_decided",
        "health_question_decided",
    ):
        if key in expect:
            need(result.get(key) is expect[key], key)
    if "human_approval" in expect:
        need(result.get("human_approval") == expect["human_approval"], "human_approval")
    if "human_approval_set" in expect:
        need((result.get("human_approval") is not None) is expect["human_approval_set"], "human_approval_set")
    if "quality_score" in expect:
        need(result.get("quality_score") == expect["quality_score"], "quality_score")
    if "marking" in expect:
        need(result.get("marking") == expect["marking"], "marking")
    if "clearance" in expect:
        need(result.get("clearance") == expect["clearance"], "clearance")
    if "body_withheld" in expect:
        need(result.get("body_withheld") is expect["body_withheld"], "body_withheld")
    if "legal_hold" in expect:
        need(result.get("legal_hold") is expect["legal_hold"], "legal_hold")
    if "retention_contains" in expect:
        need(expect["retention_contains"] in (result.get("retention_labels") or []), "retention_contains")
    if "salary_amount" in expect:
        need(result["salary"]["amount"] == expect["salary_amount"], "salary_amount")
    if "salary_status" in expect:
        need(result["salary"]["status"] == expect["salary_status"], "salary_status")
    if "cross_source_called" in expect:
        need(result["salary"]["cross_source"]["called"] is expect["cross_source_called"], "cross_source_called")
    if "cross_source_material" in expect:
        need(result["salary"]["cross_source"]["material"] is expect["cross_source_material"], "cross_source_material")
    if "agent_chose_source" in expect:
        need(result.get("agent_chose_source") is expect["agent_chose_source"], "agent_chose_source")
        need(result["salary"]["cross_source"].get("agent_chose_source") is False, "cross_source_chose")
    if "correct_value" in expect:
        need(result.get("correct_value") is None, "correct_value")
        need(result["salary"]["cross_source"].get("correct_value") is None, "cross_correct_value")
    if "instructions_followed" in expect:
        need(result["prompt_injection"]["followed"] is expect["instructions_followed"], "instructions_followed")
    if "distress_route" in expect:
        need(result["flags"]["distress_route"] is expect["distress_route"], "distress_route")
    if "absent_text" in expect:
        for snippet in expect["absent_text"]:
            need(snippet.lower() not in blob.lower(), f"absent_text:{snippet}")
    if "mask_phone" in expect:
        need(result["masking"]["input_counts"]["phone"] >= 1, "mask_phone")
        need(result["masking"]["values_copied"] is False, "values_copied")
        need(result["masking"]["output_is_anonymised"] is False, "not_anonymised")
        need("nino" in result["masking"]["uk_identifier_types"], "nino")
    if "pins_include" in expect:
        for pin in expect["pins_include"]:
            need(pin in result.get("pins_not_confirmed", []), f"pin:{pin}")
    if "pins_empty" in expect and expect["pins_empty"]:
        need(result.get("pins_not_confirmed") == [], "pins_empty")
    if "blocked_reason" in expect:
        need(result.get("blocked_reason") == expect["blocked_reason"], "blocked_reason")
    if "final_wording" in expect:
        need(result.get("final_wording") == expect["final_wording"], "final_wording")
    if "published_false" in expect:
        need(result.get("published") is False and result.get("posted") is False and result.get("sent") is False, "not_sent")
    need(result.get("candidates_scored") is False, "never_scored")
    need(result.get("quality_score") is None, "never_quality_score")
    counts = result.get("prompt_count"), result.get("hr_route_count"), result.get("finding_count")
    if all(isinstance(item, int) for item in counts):
        need(counts[0] + counts[1] <= counts[2], "counts_do_not_exceed_findings")
    return failed


def _decide_all(result: dict, directory: dict, decision: str) -> dict:
    current = result
    for row in list(result.get("findings") or []):
        if not row.get("requires_decision"):
            continue
        current = record_suggestion_decision(current, directory, {
            "draft_hash": current["draft_hash"],
            "suggestion_id": row["suggestion_id"],
            "suggestion_hash": row["suggestion_hash"],
            "approver_ref": "REC-1001",
            "item": "suggestion",
            "decision": decision,
        })
    return current


def evaluate_case(case: dict, guide: dict, directory: dict) -> dict:
    try:
        result = review_draft(_request(case), deepcopy(guide), directory, case.get("as_of", "2026-11-14"))
        if case.get("forged"):
            finding = next(row for row in result["findings"] if row["requires_decision"])
            result = record_suggestion_decision(result, directory, {
                "draft_hash": result["draft_hash"],
                "suggestion_id": finding["suggestion_id"],
                "suggestion_hash": "a" * 64,
                "approver_ref": "REC-1001",
                "item": "suggestion",
                "decision": "accept",
            })
        if case.get("record_wording"):
            decided = _decide_all(result, directory, "reject")
            wording = case["record_wording"]
            digest = hashlib.sha256(wording.encode("utf-8")).hexdigest()
            result = record_final_wording(decided, directory, {
                "draft_hash": decided["draft_hash"],
                "approver_ref": "REC-1001",
                "item": "final-wording",
                "decision": "record",
                "wording": wording,
                "wording_hash": digest,
                "guide_seen": True,
                "pins_seen": True,
            })
        if case.get("drop_mandated"):
            decided = _decide_all(result, directory, "reject")
            wording = "Case officer with no mandated statement. 07700 900999."
            digest = hashlib.sha256(wording.encode("utf-8")).hexdigest()
            result = record_final_wording(decided, directory, {
                "draft_hash": decided["draft_hash"],
                "approver_ref": "REC-1001",
                "item": "final-wording",
                "decision": "record",
                "wording": wording,
                "wording_hash": digest,
            })
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
    guide = _load("guide.json")
    directory = _load("directory.json")
    results = [evaluate_case(case, guide, directory) for case in dataset["cases"]]
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
