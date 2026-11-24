"""Approval is the named company secretary and the exact pack hash."""

import json

from src.pack import (
    PackForbidden,
    assemble_pack,
    approve_minutes,
    circulate,
    file_pack,
    pinned_sources,
    publish,
    record_decision,
    record_route_seen,
    record_secretary_approval,
    reset_staging,
    send,
)


def _clean():
    return assemble_pack(
        {
            "synthetic": True,
            "meeting_id": "ARC-2026-11",
            "committee_id": "audit-and-risk",
            "secretary_ref": "STF-4001",
            "include_paper_ids": ["PAP-IA-01"],
        },
        as_of="2026-11-20",
    )


def _approval(result, **extra):
    payload = {
        "item": "board-pack",
        "decision": "approve-draft",
        "approver_ref": "STF-4001",
        "meeting_id": result["meeting_id"],
        "content_hash": result["content_hash"],
        "pins_seen": True,
        "dates_seen": True,
    }
    payload.update(extra)
    return payload


def test_named_secretary_approves_the_exact_hash_only():
    reset_staging()
    directory = pinned_sources()["directory"]
    result = _clean()
    assert result["outcome"] == "draft"
    assert "dates_seen" in result["required_acknowledgements"]
    staged = record_secretary_approval(result, directory, _approval(result))
    assert staged["staged"] is True
    assert staged["human_approval"]["approver_ref"] == "STF-4001"
    assert staged["human_approval"]["content_hash"] == result["content_hash"]
    assert staged["human_approval"]["minutes_approved"] is False
    assert staged["minutes_approved"] is False
    assert staged["decisions_recorded"] is False
    assert staged["circulated"] is False
    assert staged["published"] is False
    assert staged["filed"] is False
    assert staged["sent"] is False
    assert staged["production_written"] is False
    assert staged["legal_hold"] is False or staged["retention"]
    forged = record_secretary_approval(result, directory, _approval(result, content_hash="a" * 64))
    assert forged["staged"] is False
    assert forged["blocked_reason"] == "content_hash_mismatch"
    assert forged["human_approval"] is None


def test_tampered_content_after_approval_is_rejected():
    directory = pinned_sources()["directory"]
    result = _clean()
    tampered = json.loads(json.dumps(result))
    tampered["missing_papers"] = ["PAP-TRE-01", "PAP-INVENTED"]
    refused = record_secretary_approval(tampered, directory, _approval(result))
    assert refused["staged"] is False
    assert refused["blocked_reason"] == "content_hash_mismatch"
    assert refused["circulated"] is False


def test_role_must_be_the_directory_secretary():
    directory = pinned_sources()["directory"]
    result = _clean()
    sponsor = record_secretary_approval(result, directory, _approval(result, approver_ref="STF-4002"))
    assert sponsor["blocked_reason"] == "not_the_named_secretary"
    assert sponsor["staged"] is False
    guest = record_secretary_approval(result, directory, _approval(result, approver_ref="STF-4005"))
    assert guest["staged"] is False
    mutated = json.loads(json.dumps(directory))
    for row in mutated["people"]:
        if row["employee_ref"] == "STF-4005":
            row["role"] = "company_secretary"
            row["guest"] = False
    refused = record_secretary_approval(result, mutated, _approval(result, approver_ref="STF-4005"))
    assert refused["blocked_reason"] == "caller_directory_not_used"
    assert refused["staged"] is False


def test_string_true_is_not_coerced_and_a_route_must_be_seen():
    directory = pinned_sources()["directory"]
    result = _clean()
    string_true = record_secretary_approval(result, directory, _approval(result, pins_seen="true"))
    assert string_true["blocked_reason"] == "pins_seen_not_boolean_true"
    assert string_true["coerced"] is False
    assert string_true["staged"] is False
    sample = assemble_pack(
        {
            "synthetic": True,
            "meeting_id": "ARC-2026-11",
            "committee_id": "audit-and-risk",
            "secretary_ref": "STF-4001",
        },
        as_of="2026-11-20",
    )
    assert sample["outcome"] == "route_to_human"
    early = record_secretary_approval(
        sample,
        directory,
        _approval(sample, sources_seen=True),
    )
    assert early["blocked_reason"] == "route_not_seen"
    assert early["staged"] is False
    seen = record_route_seen(
        sample,
        directory,
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "STF-4001",
            "meeting_id": sample["meeting_id"],
            "content_hash": sample["content_hash"],
        },
    )
    assert seen["route_seen"] is True
    assert seen["staged"] is False
    assert seen["distress"]["cue_copied"] is False
    staged = record_secretary_approval(seen, directory, _approval(seen, sources_seen=True))
    assert staged["staged"] is True
    assert staged["minutes_approved"] is False
    assert staged["sent"] is False


def test_consequential_actions_raise():
    for function in (circulate, publish, file_pack, send, record_decision, approve_minutes):
        try:
            function()
        except PackForbidden:
            pass
        else:
            raise AssertionError(function.__name__)
