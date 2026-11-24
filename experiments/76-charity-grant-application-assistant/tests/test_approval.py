"""Approval is the named applicant and the exact package hash."""

import json
from pathlib import Path

from src.grant import (
    GrantForbidden,
    contact_funder,
    pinned_sources,
    prepare_application,
    record_applicant_approval,
    record_route_seen,
    reset_staging,
    send,
    staged_row,
    submit_application,
)

ROOT = Path(__file__).resolve().parents[1]


def _draft():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    return prepare_application(request, as_of="2026-11-14")


def _approval(result, **extra):
    payload = {
        "item": "grant-package",
        "decision": "approve-draft",
        "approver_ref": "APP-7601",
        "application_id": result["application_id"],
        "content_hash": result["content_hash"],
        "pins_seen": True,
        "sources_seen": True,
        "dates_seen": True,
        "criteria_seen": True,
    }
    payload.update(extra)
    return payload


def test_text_approval_does_not_stage():
    result = _draft()
    assert result["human_approval"] is None
    assert result["staged"] is False
    refused = record_applicant_approval(result, pinned_sources()["directory"], _approval(result))
    assert refused["blocked_reason"] == "route_not_seen"
    assert refused["staged"] is False
    assert refused["submitted"] is False


def test_exact_hash_stages_and_tamper_is_rejected():
    reset_staging()
    directory = pinned_sources()["directory"]
    result = _draft()
    seen = record_route_seen(
        result,
        directory,
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "APP-7601",
            "content_hash": result["content_hash"],
        },
    )
    assert seen["route_seen"] is True
    assert seen["staged"] is False
    assert seen["content_hash"] != result["content_hash"]
    staged = record_applicant_approval(seen, directory, _approval(seen))
    assert staged["staged"] is True
    assert staged["human_approval"]["approver_ref"] == "APP-7601"
    assert staged["human_approval"]["content_hash"] == seen["content_hash"]
    assert staged["submitted"] is False
    assert staged["funder_contacted"] is False
    assert staged["sent"] is False
    stored = staged_row(seen["application_id"], seen["content_hash"])
    assert stored["legal_hold"] is True
    assert "safeguarding note: do not destroy" in stored["retention"]
    assert stored["store"] == "synthetic"
    tampered = json.loads(json.dumps(seen))
    tampered["answers"][0]["text"] = "We served 99999 meals."
    rejected = record_applicant_approval(tampered, directory, _approval(seen))
    assert rejected["blocked_reason"] == "content_hash_mismatch"
    assert rejected["human_approval"] is None
    assert rejected["staged"] is False
    assert staged_row(seen["application_id"], seen["content_hash"])["answers"][0]["text"].startswith(
        "Harbour Lane Community Kitchen served 14820"
    )


def test_forged_hash_trustee_guest_and_string_true_are_rejected():
    reset_staging()
    directory = pinned_sources()["directory"]
    result = _draft()
    seen = record_route_seen(
        result,
        directory,
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "APP-7601",
            "content_hash": result["content_hash"],
        },
    )
    forged = record_applicant_approval(seen, directory, _approval(seen, content_hash="a" * 64))
    assert forged["blocked_reason"] == "content_hash_mismatch"
    trustee = record_applicant_approval(seen, directory, _approval(seen, approver_ref="TRS-7602"))
    assert trustee["blocked_reason"] == "not_the_named_applicant"
    guest = record_applicant_approval(seen, directory, _approval(seen, approver_ref="GST-7603"))
    assert guest["blocked_reason"] == "not_the_named_applicant"
    string_true = record_applicant_approval(seen, directory, _approval(seen, pins_seen="true"))
    assert string_true["blocked_reason"] == "pins_seen_not_boolean_true"
    other_id = record_applicant_approval(seen, directory, _approval(seen, application_id="OTHER"))
    assert other_id["blocked_reason"] == "application_mismatch"
    caller_directory = record_applicant_approval(seen, {"people": [{"employee_ref": "APP-7601", "role": "applicant"}]}, _approval(seen))
    assert caller_directory["blocked_reason"] == "caller_directory_not_used"
    assert staged_row(seen["application_id"], seen["content_hash"]) is None


def test_submit_contact_and_send_raise():
    for function in (submit_application, contact_funder, send):
        try:
            function()
        except GrantForbidden:
            continue
        raise AssertionError(function.__name__)
