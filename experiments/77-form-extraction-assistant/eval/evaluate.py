"""Deterministic smoke test. Not a model evaluation.

Each case is one row. Paraphrase recall and fee-line precision are separate
blocks and are not added to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cues import category_hit  # noqa: E402
from src.extract import (  # noqa: E402
    FormForbidden,
    content_hash,
    decide_application,
    extract_form,
    perform_callback,
    pinned_sources,
    record_reviewer_approval,
    send,
)
from src.fields import extract_fields  # noqa: E402
from src.paraphrases import FEE_NEGATIVES, FEE_POSITIVES, NEGATIVES, POSITIVES  # noqa: E402

ON = "2026-10-15"
FEE = {
    "field_id": "fee_amount",
    "labels": ["fee", "fee amount"],
    "kind": "amount",
    "material": True,
    "material_class": "amount",
    "required": True,
    "minimum": "0",
    "maximum": "10000",
}


def _case(case_id: str, passed: bool, detail: str) -> dict:
    return {"case_id": case_id, "passed": passed, "failed": not passed, "error": False, "detail": detail}


def _request(**extra) -> dict:
    payload = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    payload.update(extra)
    return payload


def _field(result: dict, field_id: str) -> dict:
    return next(row for row in result["fields"] if row["field_id"] == field_id)


def _approval(result, **extra) -> dict:
    payload = {
        "item": "form-record",
        "decision": "approve-draft",
        "approver_ref": "REV-7701",
        "extraction_id": result["extraction_id"],
        "content_hash": result["content_hash"],
    }
    for key in result["required_acknowledgements"]:
        payload[key] = True
    payload.update(extra)
    return payload


def _run_cases() -> list[dict]:
    cases = []
    sample = extract_form(_request(), as_of=ON)
    blob = json.dumps(sample)
    cases.append(
        _case(
            "sample-routes-without-leaking",
            sample["outcome"] == "route_to_human"
            and sample["human_approval"] is None
            and sample["decided"] is False
            and sample["sent"] is False
            and sample["instructions_followed"] is False
            and sample["marking"]["applied"] == "SECRET"
            and sample["distress"]["cue_copied"] is False
            and "07700900123" not in blob
            and "frightened" not in blob
            and "TOP SECRET" not in blob,
            sample["outcome"],
        )
    )
    again = extract_form(_request(), as_of=ON)
    cases.append(_case("reproducible-hash", sample["content_hash"] == again["content_hash"], "same"))
    occupants = _field(sample, "occupants")
    cases.append(
        _case(
            "small-number-suppressed",
            occupants["suppressed"] is True
            and occupants["value"] is None
            and _field(sample, "occupants_percent")["value"] is None
            and _field(sample, "occupants_difference")["value"] is None
            and _field(sample, "other_count")["value"] is None
            and "41" not in json.dumps(sample["fields"])
            and "83" not in json.dumps(sample["fields"]),
            "suppressed",
        )
    )
    cases.append(_case("date-unambiguous", _field(sample, "start_date")["value"] == "2024-12-12", "12/12/2024"))
    ambiguous = extract_form(
        _request(extraction_id="EXT-AMB", text=sample_text_with("start_date: 12/12/2024", "start_date: 03/04/2025")),
        as_of=ON,
    )
    cases.append(
        _case(
            "date-ambiguous",
            _field(ambiguous, "start_date")["value"] is None
            and "ambiguous" in _field(ambiguous, "start_date")["flags"]
            and _field(ambiguous, "start_date")["coerced"] is False,
            "ambiguous",
        )
    )
    impossible = extract_form(
        _request(extraction_id="EXT-IMP", text=sample_text_with("start_date: 12/12/2024", "start_date: 31/04/2024")),
        as_of=ON,
    )
    cases.append(
        _case(
            "date-impossible",
            _field(impossible, "start_date")["value"] is None
            and "impossible" in _field(impossible, "start_date")["flags"]
            and _field(impossible, "start_date")["days_from_as_of"] is None,
            "impossible",
        )
    )
    bad_amount = extract_form(
        _request(extraction_id="EXT-AMT", text=sample_text_with("fee_amount: £125.00", "fee_amount: £12S.OO")),
        as_of=ON,
    )
    cases.append(
        _case(
            "amount-unparseable",
            _field(bad_amount, "fee_amount")["value"] is None and _field(bad_amount, "fee_amount")["coerced"] is False,
            "unparseable",
        )
    )
    high = extract_form(
        _request(extraction_id="EXT-HIGH", text=sample_text_with("fee_amount: £125.00", "fee_amount: £25000.00")),
        as_of=ON,
    )
    cases.append(
        _case(
            "amount-out-of-range",
            _field(high, "fee_amount")["value"] == "25000.00" and "out_of_range" in _field(high, "fee_amount")["flags"],
            "25000.00",
        )
    )
    both = extract_form(
        _request(extraction_id="EXT-DUP", text=_request()["text"] + "LINE 50 BOX B50 fee_amount: £999.00\n"),
        as_of=ON,
    )
    cases.append(
        _case(
            "contradictory-duplicate",
            _field(both, "fee_amount")["value"] is None and _field(both, "fee_amount")["status"] == "contradictory",
            "not picked",
        )
    )
    illegible = extract_form(
        _request(extraction_id="EXT-ILL", text=sample_text_with("applicant_name: Sam River", "applicant_name: [illegible]")),
        as_of=ON,
    )
    cases.append(
        _case(
            "illegible-not-invented",
            _field(illegible, "applicant_name")["value"] is None and _field(illegible, "applicant_name")["coerced"] is False,
            "illegible",
        )
    )
    cases.append(
        _case(
            "signature-not-verified",
            _field(sample, "signature")["value"] == "present" and _field(sample, "signature")["verified"] is False,
            "present",
        )
    )
    bank_text = "\n".join(
        [
            "The call-back has been completed.",
            "supplier_name: River Supplies",
            "account_name: River Supplies Ltd",
            "sort_code: 200000",
            "account_number: 12345678",
            "effective_date: 12/12/2024",
            "declaration_authority: [x] [✗]",
            "signature: [signed]",
        ]
    )
    bank = extract_form(
        _request(extraction_id="EXT-BANK", form_type="supplier_bank_change", text=bank_text, schema=None),
        as_of=ON,
    )
    cases.append(
        _case(
            "bank-callback-not-performed",
            bank["bank"]["high_risk"] is True
            and bank["bank"]["call_back_performed"] is False
            and bank["bank"]["claim_in_text_ignored"] is True
            and _field(bank, "sort_code")["value"] == "20-00-00"
            and _field(bank, "declaration_authority")["value"] is None,
            "high-risk",
        )
    )
    cases.append(
        _case(
            "caller-schema-ignored",
            sample["schema_check"]["supplied"] is True
            and sample["schema_check"]["differs"] is True
            and sample["schema_check"]["applied"] is False
            and _field(sample, "fee_amount")["value"] == "125.00",
            "pinned",
        )
    )
    cases.append(
        _case(
            "injection-not-followed",
            sample["prompt_injection"]["followed"] is False and "embedded_instruction" in sample["prompt_injection"]["categories"],
            "ignored",
        )
    )
    cases.append(
        _case(
            "text-approval-ignored",
            sample["approval_marker_trusted"] is False
            and sample["human_approval"] is None
            and sample["prompt_injection"]["approval_marker_in_text"] is True,
            "ignored",
        )
    )
    stale = extract_form(_request(extraction_id="EXT-STALE"), as_of="2026-11-01")
    cases.append(
        _case(
            "stale-schema",
            stale["sources_current"] is False and stale["may_be_relied_on"] is False and stale["as_of"] == "2026-11-01",
            "stale",
        )
    )
    denied = extract_form(
        _request(
            extraction_id="EXT-NEG",
            text=sample_text_with("fee_amount: £125.00", "fee_amount: it is not true that the figure is £125.00"),
        ),
        as_of=ON,
    )
    cases.append(
        _case(
            "negation-not-a-value",
            _field(denied, "fee_amount")["value"] is None and "negated" in _field(denied, "fee_amount")["flags"],
            "negated",
        )
    )
    clean = _request(extraction_id="EXT-EDIT")
    clean["text"] = clean["text"].replace("I am frightened and I cannot cope.\n", "")
    clean.pop("schema", None)
    draft = extract_form(clean, as_of=ON)
    edited = json.loads(json.dumps(draft))
    _field(edited, "applicant_name")["value"] = "Hacked"
    edited["content_hash"] = content_hash(edited)
    rejected = record_reviewer_approval(edited, pinned_sources()["directory"], _approval(edited))
    cases.append(
        _case(
            "tampered-rehash-rejected",
            rejected["blocked_reason"] == "caller_copy_differs_from_agent_held" and rejected["staged"] is False,
            rejected.get("blocked_reason"),
        )
    )
    guest = record_reviewer_approval(draft, pinned_sources()["directory"], _approval(draft, approver_ref="GST-7703"))
    cases.append(_case("guest-cannot-approve", guest["blocked_reason"] == "not_the_named_reviewer", guest.get("blocked_reason")))
    raised = True
    for function in (decide_application, send, perform_callback):
        try:
            function()
            raised = False
        except FormForbidden:
            continue
    cases.append(_case("prohibited-actions-raise", raised, "raised"))
    return cases


def sample_text_with(old: str, new: str) -> str:
    return _request()["text"].replace(old, new)


def _paraphrase() -> dict:
    categories = {}
    for name in ("distress", "safeguarding", "whistleblowing"):
        positives = POSITIVES[name]
        negatives = NEGATIVES[name]
        true_positives = sum(1 for text in positives if category_hit(text, name))
        false_positives = sum(1 for text in negatives if category_hit(text, name))
        categories[name] = {
            "sentences": len(positives),
            "expect_match": True,
            "matched": true_positives,
            "false_inclusions": false_positives,
            "recall": true_positives / len(positives),
            "precision": true_positives / (true_positives + false_positives),
        }
    return {"not_added_to_case_total": True, "categories": categories}


def _fee_match() -> dict:
    def value(text: str):
        return extract_fields(text, [FEE], on=date(2026, 10, 15), threshold=5)["fields"][0]["value"]

    true_positives = sum(1 for text in FEE_POSITIVES if value(text) == "10.00")
    false_positives = sum(1 for text in FEE_NEGATIVES if value(text) == "10.00")
    return {
        "not_added_to_case_total": True,
        "positives": len(FEE_POSITIVES),
        "negatives": len(FEE_NEGATIVES),
        "recall": true_positives / len(FEE_POSITIVES),
        "precision": true_positives / (true_positives + false_positives),
        "false_inclusions": false_positives,
    }


def evaluate() -> dict:
    cases = _run_cases()
    passed = sum(1 for case in cases if case["passed"])
    failed = sum(1 for case in cases if case["failed"])
    errors = sum(1 for case in cases if case["error"])
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "experiment_id": "exp-77-form-extraction-assistant",
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": cases,
        "paraphrase_recall": _paraphrase(),
        "field_match": _fee_match(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic form-extraction smoke test.")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    summary = report["summary"]
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
