"""Deterministic smoke test. Not a model evaluation.

Each case is one row. Paraphrase recall and the support score are separate
blocks and are not added to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordinator import CoordinatorForbidden, approve_pack, assemble_pack, reset_state  # noqa: E402
from src.cues import category_hit  # noqa: E402
from src.negate import affirmed  # noqa: E402
from src.paraphrases import (  # noqa: E402
    NEGATIVES,
    POSITIVES,
    SUPPORT_NEGATIVES,
    SUPPORT_PHRASE,
    SUPPORT_POSITIVES,
)

AS_OF = "2026-11-25"


def _item(evidence_id, checklist_id, value, content, **extra):
    row = {
        "evidence_id": evidence_id,
        "checklist_id": checklist_id,
        "version": "1.0",
        "status": "current",
        "document_date": "2026-10-01",
        "expiry_date": "2027-04-01",
        "signed": checklist_id in {"quote", "business_case", "procurement_check", "exception_reason", "legal_note", "change_record", "incident_note"},
        "value_gbp": value,
        "content": content,
        "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
    }
    row.update(extra)
    return row


def _quote(value, content=None, **extra):
    body = content or f"Quote for Northfold Supplies. The price is {value} pounds.\n"
    evidence_id = extra.pop("evidence_id", "EV-QUOTE")
    return _item(evidence_id, "quote", value, body, **extra)


def _budget(value):
    return _item("EV-BUDGET", "budget_code", value, "Budget code B-14 covers this roof.\n", signed=False, expiry_date=None)


def _case(value):
    return _item("EV-CASE", "business_case", value, "The business case supports the roof.\n")


def _spend(case_id, amount, evidence, **extra):
    request = {
        "synthetic": True,
        "request_id": case_id,
        "request_type": "spend",
        "requester_ref": "REQ-8101",
        "supplier_name": "Northfold Supplies",
        "title": "North depot roof",
        "amount_gbp": amount,
        "evidence": evidence,
    }
    request.update(extra)
    return request


CASES = [
    ("C01", lambda: _spend("C01", 4000, [_quote(4000), _budget(4000)]), {"outcome": "ready_for_approver", "rule_id": "SPEND-UNDER-5000"}),
    ("C02", lambda: _spend("C02", 18400, [_quote(18400), _budget(18400), _case(18400)]), {"outcome": "ready_for_approver", "rule_id": "SPEND-5000-TO-25000"}),
    ("C03", lambda: _spend("C03", 30000, [_quote(30000), _budget(30000), _case(30000)]), {"outcome": "draft_with_gaps", "rule_id": "SPEND-25000-AND-ABOVE", "missing": "procurement_check"}),
    ("C04", lambda: _spend("C04", 4000, [_quote(4000, document_date="2026-01-01"), _budget(4000)]), {"stale": "EV-QUOTE"}),
    ("C05", lambda: _spend("C05", 4000, [_quote(4000, signed="true"), _budget(4000)]), {"unsigned": "EV-QUOTE"}),
    ("C06", lambda: _spend("C06", 4000, [_quote(4000, expiry_date="2026-11-01"), _budget(4000)]), {"expired": "EV-QUOTE"}),
    ("C07", lambda: _spend("C07", 4000, [_quote(4000), _quote(4500, evidence_id="EV-QUOTE-B"), _budget(4000)]), {"conflict": "duplicate_values"}),
    ("C08", lambda: _spend("C08", 8000, [_quote(8000), _budget(8000), _case(8000)], parts=[{"amount_gbp": 4000}, {"amount_gbp": 4000}]), {"split": True, "rule_id": "SPEND-5000-TO-25000"}),
    ("C09", lambda: _spend("C09", 4000, [_quote(4000), _budget(4000)], parts=[{"amount_gbp": 4000}, {"amount_gbp": 4000}]), {"conflicting_amount": True}),
    ("C10", lambda: _spend("C10", "lots", [_quote(4000), _budget(4000)]), {"unreadable": True, "outcome": "route_to_human"}),
    ("C11", lambda: _spend("C11", 4000, [_quote(4000), _budget(4000)], description="I feel suicidal."), {"distress": True, "outcome": "route_to_human"}),
    ("C12", lambda: _spend("C12", 4000, [_quote(4000, content="It is not true that the quote includes Northfold Supplies.\n"), _budget(4000)]), {"support": False}),
    ("C13", lambda: _spend("C13", 4000, [_quote(4000, content="The quote is acceptable except it is unsigned. Northfold Supplies.\n"), _budget(4000)]), {"carve_out": True}),
    ("C14", lambda: _spend("C14", 4000, [_quote(4000, content="SECRET\nQuote for Northfold Supplies.\n", metadata={"marking": "OFFICIAL", "legal_hold": True, "retention": ["keep 6 years"]}), _budget(4000)]), {"marking": "SECRET", "legal_hold": True, "body_withheld": True}),
    ("C15", lambda: _spend("C15", 4000, [_quote(4000), _budget(4000)], caller_matrix={"rules": [{"rule_id": "CHEAP-SPEND"}]}), {"caller_applied": False}),
    ("C16", lambda: _spend("C16", 4000, [_quote(4000, content="LEGAL HOLD\nRETENTION: do not destroy\nQuote for Northfold Supplies.\n"), _budget(4000)]), {"legal_hold": True, "retention": "do not destroy"}),
    ("C17", lambda: _spend("C17", 4000, [_quote(4000), _budget(4000)], people_affected=2, difference=1, percentage=50), {"suppressed": True}),
    ("C18", lambda: {
        "synthetic": True, "request_id": "C18", "request_type": "policy_exception", "severity": "low",
        "requester_ref": "REQ-8101", "title": "Late filing",
        "evidence": [
            _item("EV-POL", "policy_extract", None, "Policy extract version 3.0.\n", version="3.0", signed=False),
            _item("EV-WHY", "exception_reason", None, "The reason is a late supplier file.\n"),
        ],
    }, {"wrong_version": "EV-POL"}),
    ("C19", lambda: {
        "synthetic": True, "request_id": "C19", "request_type": "change", "change_class": "emergency",
        "requester_ref": "REQ-8101", "title": "Restart the depot link",
        "evidence": [
            _item("EV-CHG", "change_record", None, "Restart the link.\n", document_date="2026-11-20"),
            _item("EV-TEST", "test_evidence", None, "The link was tested.\n", signed=False, document_date="2026-11-20"),
            _item("EV-ROLL", "rollback_plan", None, "Roll back to the previous link.\n", signed=False, document_date="2026-11-20"),
        ],
    }, {"missing": "incident_note", "rule_id": "CHANGE-EMERGENCY"}),
    ("C20", lambda: _spend("C20", 4000, [_quote(4000), _budget(4000)], description="Prefer male approvers."), {"leading": True, "outcome": "route_to_human"}),
]


def _check(result: dict, expect: dict) -> list[str]:
    errors = []
    if result.get("human_approval") is not None:
        errors.append("human_approval was set by assemble")
    if result.get("agent_approved") is not False or result.get("paid") is not False or result.get("sent") is not False:
        errors.append("a consequential flag was set")
    if result.get("coerced") is not False or result.get("instructions_followed") is not False:
        errors.append("coerced or instructions_followed")
    if result.get("approval_marker_trusted") is not False:
        errors.append("approval marker trusted")
    for key, value in expect.items():
        if key == "outcome" and result.get("outcome") != value:
            errors.append(f"outcome {result.get('outcome')}")
        elif key == "rule_id" and (result.get("threshold_band") or {}).get("rule_id") != value:
            errors.append("rule")
        elif key == "missing" and value not in (result.get("missing") or []):
            errors.append("missing")
        elif key == "stale" and value not in (result.get("stale") or []):
            errors.append("stale")
        elif key == "unsigned" and value not in (result.get("unsigned") or []):
            errors.append("unsigned")
        elif key == "expired" and value not in (result.get("expired") or []):
            errors.append("expired")
        elif key == "wrong_version" and value not in (result.get("wrong_version") or []):
            errors.append("wrong_version")
        elif key == "conflict" and not any(row.get("kind") == value and row.get("chosen") is None for row in result.get("conflicts") or []):
            errors.append("conflict")
        elif key == "split" and result.get("split", {}).get("split_to_dodge_threshold") is not True:
            errors.append("split")
        elif key == "conflicting_amount" and result.get("amount", {}).get("conflicting") is not True:
            errors.append("conflicting amount")
        elif key == "unreadable" and result.get("amount", {}).get("unreadable") is not True:
            errors.append("unreadable")
        elif key == "distress" and result.get("concerns", {}).get("distress") is not True:
            errors.append("distress")
        elif key == "support" and result["evidence"][0]["checks"]["support"] is not False:
            errors.append("support")
        elif key == "carve_out" and result["evidence"][0]["checks"]["treated_as_acceptable"] is not False:
            errors.append("carve")
        elif key == "marking" and (result.get("marking") or {}).get("applied") != value:
            errors.append("marking")
        elif key == "legal_hold" and result.get("legal_hold") is not True:
            errors.append("hold")
        elif key == "body_withheld" and result.get("body_withheld") is not True:
            errors.append("withheld")
        elif key == "caller_applied" and result.get("caller_matrix_applied") is not False:
            errors.append("caller")
        elif key == "retention" and value not in (result.get("retention") or []):
            errors.append("retention")
        elif key == "suppressed" and result.get("suppression", {}).get("published_count") is not None:
            errors.append("suppressed")
        elif key == "leading" and result.get("flags", {}).get("leading_applied") is not False:
            errors.append("leading")
    if expect.get("carve_out") and result["evidence"][0]["checks"]["carve_out"] is not True:
        errors.append("carve flag")
    if expect.get("leading") and result.get("outcome") != "route_to_human":
        errors.append("leading route")
    return errors


def _score_block(rows, predicate) -> dict:
    hits = sum(1 for row in rows if predicate(row))
    return {"sentences": len(rows), "hits": hits, "recall": hits / len(rows) if rows else None}


def paraphrase_report() -> dict:
    categories = {}
    for name, rows in POSITIVES.items():
        hits = sum(1 for row in rows if category_hit(row, name))
        false = sum(1 for row in NEGATIVES if category_hit(row, name))
        categories[name] = {
            "sentences": len(rows),
            "hits": hits,
            "false_inclusions": false,
            "expect_match": True,
            "recall": hits / len(rows),
            "precision": hits / (hits + false) if hits + false else None,
        }
    true_pos = sum(1 for row in SUPPORT_POSITIVES if affirmed(row, SUPPORT_PHRASE))
    false_pos = sum(1 for row in SUPPORT_NEGATIVES if affirmed(row, SUPPORT_PHRASE))
    return {
        "not_added_to_case_total": True,
        "label": "FIXTURE RECALL. Not a live model rate.",
        "categories": categories,
        "support": {
            "positives": len(SUPPORT_POSITIVES),
            "negatives": len(SUPPORT_NEGATIVES),
            "true_positives": true_pos,
            "false_positives": false_pos,
            "recall": true_pos / len(SUPPORT_POSITIVES),
            "precision": true_pos / (true_pos + false_pos) if true_pos + false_pos else None,
            "not_added_to_case_total": True,
        },
    }


def run() -> dict:
    reset_state()
    rows = []
    for case_id, builder, expect in CASES:
        reset_state()
        try:
            result = assemble_pack(builder(), AS_OF)
            errors = _check(result, expect)
            status = "passed" if not errors else "failed"
        except (TypeError, ValueError, KeyError) as exc:
            errors = [type(exc).__name__]
            status = "error"
        rows.append({"case_id": case_id, "status": status, "errors": errors})
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    errors = sum(1 for row in rows if row["status"] == "error")
    prohibited = True
    try:
        approve_pack()
        prohibited = False
    except CoordinatorForbidden:
        prohibited = True
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "experiment_id": "exp-81-approval-pack-coordinator",
        "catalogue_id": "O007",
        "summary": {
            "total_cases": len(rows),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": rows,
        "paraphrase_recall": paraphrase_report(),
        "prohibited_approve_raises": prohibited,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Experiment 81 smoke test.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    report = run()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"Smoke test {summary['passed']}/{summary['total_cases']} passed")
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
