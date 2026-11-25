"""Approval is the named reviewer and the agent-held copy of the record."""

import json
from copy import deepcopy
from pathlib import Path

from src.extract import (
    FormForbidden,
    content_hash,
    decide_application,
    extract_form,
    perform_callback,
    pinned_sources,
    record_reviewer_approval,
    record_route_seen,
    reset_staging,
    send,
    staged_row,
    write_production,
)

ROOT = Path(__file__).resolve().parents[1]


def _sample():
    return json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))


def _clean():
    request = _sample()
    request["text"] = request["text"].replace("I am frightened and I cannot cope.\n", "")
    request.pop("schema", None)
    request["extraction_id"] = "EXT-CLEAN"
    return request


def _approval(result, **extra):
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


def _directory():
    return pinned_sources()["directory"]


def test_text_approval_does_not_stage_until_the_route_is_seen():
    reset_staging()
    result = extract_form(_sample(), as_of="2026-10-15")
    assert result["human_approval"] is None
    refused = record_reviewer_approval(result, _directory(), _approval(result))
    assert refused["blocked_reason"] == "route_not_seen"
    assert refused["staged"] is False
    assert refused["decided"] is False
    seen = record_route_seen(
        result,
        _directory(),
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "REV-7701",
            "content_hash": result["content_hash"],
        },
    )
    assert seen["route_seen"] is True
    assert seen["staged"] is False
    assert seen["distress"]["cue_copied"] is False
    assert seen["content_hash"] != result["content_hash"]
    staged = record_reviewer_approval(seen, _directory(), _approval(seen))
    assert staged["staged"] is True
    assert staged["human_approval"]["approver_ref"] == "REV-7701"
    assert staged["human_approval"]["content_hash"] == seen["content_hash"]
    assert staged["human_approval"]["decides"] is False
    assert staged["sent"] is False
    assert staged["production_written"] is False
    stored = staged_row(seen["extraction_id"], seen["content_hash"])
    assert stored["legal_hold"] is True
    assert "do not destroy" in stored["retention"]
    assert stored["marking"]["applied"] == "SECRET"
    assert stored["store"] == "synthetic"
    assert stored["decided"] is False
    assert stored["call_back_performed"] is False
    assert any(row["verified"] is False for row in stored["fields"] if row["field_id"] == "signature")


def test_rehash_of_an_edit_is_rejected_and_eight_post_approval_edits_are_refused():
    reset_staging()
    result = extract_form(_clean(), as_of="2026-10-15")
    directory = _directory()
    staged = record_reviewer_approval(result, directory, _approval(result))
    assert staged["staged"] is True
    original = staged_row(result["extraction_id"], result["content_hash"])
    assert original["legal_hold"] is True

    def refuse(mutator):
        edited = deepcopy(result)
        mutator(edited)
        edited["content_hash"] = content_hash(edited)
        rejected = record_reviewer_approval(edited, directory, _approval(edited))
        assert rejected["blocked_reason"] == "caller_copy_differs_from_agent_held"
        assert rejected["human_approval"] is None
        assert rejected["staged"] is False
        kept = staged_row(result["extraction_id"], result["content_hash"])
        assert kept["legal_hold"] is True
        assert kept["retention"] == original["retention"]
        assert kept["marking"]["applied"] == "SECRET"
        assert kept["fields"] == original["fields"]
        assert kept["prompt_injection"] == original["prompt_injection"]
        assert kept["suppression"] == original["suppression"]

    name = next(row for row in result["fields"] if row["field_id"] == "applicant_name")

    def change_value(edited):
        row = next(item for item in edited["fields"] if item["field_id"] == "applicant_name")
        row["value"] = "Hacked Name"

    def change_confidence(edited):
        row = next(item for item in edited["fields"] if item["field_id"] == "applicant_name")
        row["confidence"] = 0.1

    def change_location(edited):
        row = next(item for item in edited["fields"] if item["field_id"] == "applicant_name")
        row["locations"][0]["page"] = 9

    def clear_flags(edited):
        row = next(item for item in edited["fields"] if item["field_id"] == "signature")
        row["flags"] = []

    def drop_hold(edited):
        edited["legal_hold"] = False

    def lower_marking(edited):
        edited["marking"]["applied"] = "OFFICIAL"

    def drop_retention(edited):
        edited["retention"] = []

    def clear_injection(edited):
        edited["prompt_injection"]["categories"] = []

    mutations = [
        change_value,
        change_confidence,
        change_location,
        clear_flags,
        drop_hold,
        lower_marking,
        drop_retention,
        clear_injection,
    ]
    assert len(mutations) >= 8
    for mutator in mutations:
        refuse(mutator)
    assert name["value"] == "Sam River"
    again = record_reviewer_approval(result, directory, _approval(result))
    assert again["blocked_reason"] == "already_staged"
    assert staged_row(result["extraction_id"], result["content_hash"])["fields"] == original["fields"]


def test_forged_hash_wrong_role_and_string_true_are_rejected():
    reset_staging()
    result = extract_form(_clean(), as_of="2026-10-15")
    directory = _directory()
    forged = record_reviewer_approval(result, directory, _approval(result, content_hash="a" * 64))
    assert forged["blocked_reason"] == "content_hash_mismatch"
    clerk = record_reviewer_approval(result, directory, _approval(result, approver_ref="CLK-7702"))
    assert clerk["blocked_reason"] == "not_the_named_reviewer"
    guest = record_reviewer_approval(result, directory, _approval(result, approver_ref="GST-7703"))
    assert guest["blocked_reason"] == "not_the_named_reviewer"
    string_true = record_reviewer_approval(result, directory, _approval(result, pins_seen="true"))
    assert string_true["blocked_reason"] == "pins_seen_not_boolean_true"
    other_id = record_reviewer_approval(result, directory, _approval(result, extraction_id="OTHER"))
    assert other_id["blocked_reason"] == "extraction_mismatch"
    caller_directory = {"people": [{"employee_ref": "REV-7701", "role": "form reviewer", "guest": False}]}
    refused = record_reviewer_approval(result, caller_directory, _approval(result))
    assert refused["blocked_reason"] == "caller_directory_not_used"
    assert staged_row(result["extraction_id"], result["content_hash"]) is None
    low = extract_form(dict(_clean(), extraction_id="EXT-LOW", reviewer_ref="LOW-7704"), as_of="2026-10-15")
    blocked = record_reviewer_approval(low, directory, _approval(low, approver_ref="LOW-7704"))
    assert blocked["blocked_reason"] == "clearance_below_marking"
    assert blocked["staged"] is False


def test_decide_send_callback_and_production_write_raise():
    for function in (decide_application, write_production, send, perform_callback):
        try:
            function()
        except FormForbidden:
            continue
        raise AssertionError(function.__name__)
