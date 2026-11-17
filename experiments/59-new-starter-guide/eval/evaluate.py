#!/usr/bin/env python3
"""Deterministic smoke test. Not a model score.

Each case is one row. Passed, failed, and errors sum to the case count.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.guide import approve_checklist, draft_guide, share_checklist  # noqa: E402

DATASET = Path(__file__).with_name("synthetic_dataset.json")
PACK = json.loads((ROOT / "fixtures" / "pack.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
SCOPE = json.loads((ROOT / "examples" / "sample_scope.json").read_text(encoding="utf-8"))


def _run(case: dict) -> dict:
    request = {
        "synthetic": True,
        "request_id": case.get("request_id", "SYN-REQ-5901"),
        "person_id": case.get("person_id", "SYN-PERSON-5901"),
        "question": case["question"],
    }
    if "quantity" in case:
        request["quantity"] = case["quantity"]
    if "claimed_role" in case:
        request["claimed_role"] = case["claimed_role"]
    pack = deepcopy(PACK)
    if case.get("pack_synthetic") is False:
        pack["synthetic"] = False
    directory = deepcopy(DIRECTORY)
    if case.get("start_date"):
        for person in directory["people"]:
            if person["person_id"] == request["person_id"]:
                person["start_date"] = case["start_date"]
    scope = deepcopy(SCOPE)
    for document_id in case.get("extra_documents") or []:
        scope["approved_document_ids"].append(document_id)
    result = draft_guide(pack, directory, scope, request, case["as_of"])
    if case.get("approve"):
        approval = {
            "actor_id": case.get("actor_id", "SYN-MGR-5901"),
            "actor_role": case.get("actor_role", "Line manager"),
            "decision": "approve",
            "checklist_id": result.get("checklist_id"),
            "item_digest": result.get("item_digest"),
            "approval_reference": case.get("approval_reference", "RB-NS-5901"),
        }
        if case.get("wrong_digest"):
            approval["item_digest"] = "0" * 16
        result = approve_checklist(result, approval)
    if case.get("share"):
        result = share_checklist(result)
    if case.get("forge_share"):
        forged = deepcopy(result)
        forged["human_approval"] = {
            "source": "deterministic_approval_step",
            "actor_id": result.get("line_manager_id"),
            "actor_role": "Line manager",
            "decision": "approve",
            "checklist_id": result.get("checklist_id"),
            "item_digest": result.get("item_digest"),
            "approval_reference": "RB-NS-7777",
        }
        result = share_checklist(forged)
    return result


def _check(result: dict, expect: dict) -> list[str]:
    failures = []
    if result.get("outcome") != expect.get("outcome"):
        failures.append(f"outcome {result.get('outcome')} != {expect.get('outcome')}")
    if expect.get("shared") is True and result["flags"]["shared_with_starter"] is not True:
        failures.append("checklist was not shared")
    if expect.get("shared") is False and result["flags"]["shared_with_starter"] is not False:
        failures.append("checklist was shared")
    if expect.get("approval") is True and (result.get("human_approval") or {}).get("source") != "deterministic_approval_step":
        failures.append("approval missing")
    if expect.get("approval") is False and result.get("human_approval") is not None:
        failures.append("approval was set")
    for key in (
        "equipment_requested",
        "account_created",
        "access_granted",
        "training_enrolled",
        "provisioned",
        "external_send",
        "hr_system_written",
        "network_called",
        "special_category_collected",
    ):
        if result["flags"][key] is not False:
            failures.append(f"flag {key} was set")
    if result.get("adjustment_decided") is not None or result.get("right_to_work_decided") is not None:
        failures.append("a check was decided")
    if result.get("question_copied") is not False:
        failures.append("question copied flag")
    blob = json.dumps(result)
    for text in expect.get("absent") or []:
        if text in blob:
            failures.append(f"output contains {text!r}")
    if "included" in expect:
        claims = {row["phrase"]: row["included"] for row in result["claims"]}
        for phrase, included in expect["included"].items():
            if claims.get(phrase) is not included:
                failures.append(f"included[{phrase}] is {claims.get(phrase)}")
    if expect.get("route") and (result.get("human_route") or {}).get("reason") != expect["route"]:
        failures.append("route")
    if expect.get("marking"):
        withheld = {row["document_id"]: row for row in result["withheld"]}
        row = withheld.get(expect["marking"]["document_id"])
        if row is None or row["marking"] != expect["marking"]["label"]:
            failures.append("marking")
        if expect["marking"].get("legal_hold") and not row["legal_hold"]:
            failures.append("legal hold dropped")
        if row and row["body_copied"] is not False:
            failures.append("withheld body copied")
    if expect.get("hold_document"):
        citation = next(
            (row for row in result["citations"] if row["document_id"] == expect["hold_document"]),
            None,
        )
        if citation is None or citation["legal_hold"] is not True:
            failures.append("quoted legal hold dropped")
        if citation and "Onboarding-6y" not in citation["retention_labels"]:
            failures.append("retention label dropped")
    if expect.get("rules_current") is False and result["stale"]["rules_current"] is not False:
        failures.append("pins treated as current")
    if expect.get("quantity_applied") is None and "quantity_problem" in expect:
        if result.get("quantity_applied") is not None:
            failures.append("quantity was coerced")
        if result.get("quantity_problem") != expect["quantity_problem"]:
            failures.append("quantity problem")
    if expect.get("role_id") and result.get("role_id") != expect["role_id"]:
        failures.append("role was not taken from the directory")
    if expect.get("experiment_58"):
        block = result["experiment_58"]
        if block.get("called") is not True or "LV-2" not in (block.get("section_ids") or []):
            failures.append("experiment 58")
        if block.get("entitlement_decision") is not None or block.get("user_text_forwarded") is not False:
            failures.append("handbook forwarded the question or decided leave")
    if expect.get("experiment_57"):
        block = result["experiment_57"]
        if block.get("called") is not True or block.get("applied") is not False:
            failures.append("experiment 57")
        if block.get("human_approval") is not None:
            failures.append("space approval")
    if expect.get("experiment_21"):
        block = result["experiment_21"]
        if block.get("called") is not True or block.get("executed") is not False or block.get("grant_access_called") is not False:
            failures.append("experiment 21")
    if expect.get("experiment_11"):
        block = result["experiment_11"]
        if block.get("called") is not True or block.get("compliance_conclusion") is not None:
            failures.append("experiment 11")
        if block.get("reopened_by_this_starter") is not False:
            failures.append("experiment 11 reopened")
    if expect.get("unparseable"):
        if expect["unparseable"] not in (result.get("unparseable_fields") or []):
            failures.append("unparseable field")
    if expect.get("email_counted"):
        if result["masking"]["counts"]["email"] < 1:
            failures.append("email not counted")
        if result["masking"]["described_as_anonymised"] is not False:
            failures.append("described as anonymised")
        if result["masking"]["values_stored"] is not False:
            failures.append("mask values stored")
    return failures


def evaluate() -> dict:
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    rows = []
    passed = failed = errors = 0
    seen = set()
    for case in cases:
        case_id = case["case_id"]
        if case_id in seen:
            errors += 1
            rows.append({"case_id": case_id, "status": "error", "detail": "duplicate case id"})
            continue
        seen.add(case_id)
        try:
            result = _run(case)
            problems = _check(result, case["expect"])
        except Exception as exc:  # noqa: BLE001 — one case must not abort the report
            errors += 1
            rows.append({"case_id": case_id, "status": "error", "detail": type(exc).__name__})
            continue
        if problems:
            failed += 1
            rows.append({"case_id": case_id, "status": "failed", "detail": problems})
        else:
            passed += 1
            rows.append({"case_id": case_id, "status": "passed", "detail": []})
    total = len(cases)
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "pack_is_synthetic": True,
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    counted = summary["passed"] + summary["failed"] + summary["errors"]
    if counted != summary["total_cases"]:
        return 1
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
