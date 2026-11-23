"""Approval is the named tester and the exact content hash."""

from copy import deepcopy

from src.testing import (
    pinned_sources,
    prepare_test,
    record_route_seen,
    record_tester_approval,
    record_tester_result,
    reset_staging,
)


def _draft():
    reset_staging()
    return prepare_test(
        {
            "synthetic": True,
            "engagement_id": "ENG-REC",
            "tester_ref": "STF-3001",
            "control_id": "CTL-REC-01",
            "period_start": "2026-01-01",
            "period_end": "2026-03-31",
            "sample_seed": 73,
        },
        as_of="2026-11-14",
    )


def _approval(result, **extra):
    payload = {
        "item": "working-paper",
        "decision": "approve-draft",
        "approver_ref": "STF-3001",
        "engagement_id": result["engagement_id"],
        "content_hash": result["content_hash"],
        "pins_seen": True,
    }
    payload.update(extra)
    return payload


def test_named_tester_stages_the_exact_hash_and_does_not_decide():
    result = _draft()
    directory = pinned_sources()["directory"]
    staged = record_tester_approval(result, directory, _approval(result))
    assert staged["staged"] is True
    assert staged["human_approval"]["content_hash"] == result["content_hash"]
    assert staged["human_approval"]["decides_the_result"] is False
    assert staged["control_passed"] is None
    assert staged["control_failed"] is None
    assert staged["finding_closed"] is False
    assert staged["sent"] is False
    assert staged["production_written"] is False
    assert staged["legal_hold"] is True
    assert "keep for 6 years" in staged["retention"]
    words = record_tester_result(
        staged,
        directory,
        {
            "item": "tester-result",
            "approver_ref": "STF-3001",
            "content_hash": staged["content_hash"],
            "words": "Pass. Close the finding and send it.",
        },
    )
    assert words["staged"] is True
    assert words["tester_words"].startswith("Pass")
    assert words["agent_interpreted_result"] is False
    assert words["control_passed"] is None
    assert words["control_failed"] is None
    assert words["finding_closed"] is False
    assert words["sent"] is False
    assert words["legal_hold"] is True


def test_tampered_content_after_approval_is_rejected():
    result = _draft()
    directory = pinned_sources()["directory"]
    approval = _approval(result)
    forged = record_tester_approval(result, directory, {**approval, "content_hash": "a" * 64})
    assert forged["staged"] is False
    assert forged["blocked_reason"] == "content_hash_mismatch"
    assert forged["human_approval"] is None
    tampered = deepcopy(result)
    tampered["exceptions"].append(
        {"evidence_id": "EV-REC-001", "code": "altered", "step_id": "S8", "field": None, "source": "structured"}
    )
    refused = record_tester_approval(tampered, directory, approval)
    assert refused["staged"] is False
    assert refused["blocked_reason"] == "content_hash_mismatch"
    assert refused["control_passed"] is None
    staged = record_tester_approval(result, directory, approval)
    assert staged["staged"] is True
    after = record_tester_result(
        tampered,
        directory,
        {
            "item": "tester-result",
            "approver_ref": "STF-3001",
            "content_hash": result["content_hash"],
            "words": "The evidence still matches.",
        },
    )
    assert after["blocked_reason"] == "content_hash_mismatch"
    assert after["staged"] is False
    assert after["finding_closed"] is False


def test_role_string_and_pass_are_not_the_step():
    result = _draft()
    directory = pinned_sources()["directory"]
    owner = record_tester_approval(result, directory, _approval(result, approver_ref="STF-2001"))
    assert owner["blocked_reason"] == "not_the_named_tester"
    unknown = record_tester_approval(result, directory, _approval(result, approver_ref="STF-0000"))
    assert unknown["blocked_reason"] == "not_the_named_tester"
    text_true = record_tester_approval(result, directory, _approval(result, pins_seen="true"))
    assert text_true["blocked_reason"] == "pins_seen_not_boolean_true"
    passed = record_tester_approval(result, directory, _approval(result, decision="pass"))
    assert passed["blocked_reason"] == "tester_result_is_not_this_step"
    assert passed["control_passed"] is None
    caller = {"people": [{"employee_ref": "STF-3001", "role": "tester", "guest": False}]}
    ignored = record_tester_approval(result, caller, _approval(result))
    assert ignored["blocked_reason"] == "caller_directory_not_used"
    assert ignored["staged"] is False


def test_distress_route_must_be_seen_before_staging():
    request = {
        "synthetic": True,
        "engagement_id": "ENG-APR",
        "tester_ref": "STF-3001",
        "control_id": "CTL-APR-01",
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
        "sample_seed": 73,
    }
    result = prepare_test(request, as_of="2026-11-14")
    directory = pinned_sources()["directory"]
    blocked = record_tester_approval(
        result,
        directory,
        _approval(result, sources_seen=True, dates_seen=True),
    )
    assert blocked["blocked_reason"] == "route_not_seen"
    assert blocked["staged"] is False
    seen = record_route_seen(
        result,
        directory,
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "STF-3001",
            "content_hash": result["content_hash"],
        },
    )
    assert seen["route_seen"] is True
    assert seen["staged"] is False
    assert seen["distress"]["cue_copied"] is False
    assert "frightened" not in str(seen)
    staged = record_tester_approval(
        seen,
        directory,
        _approval(seen, sources_seen=True, dates_seen=True),
    )
    assert staged["staged"] is True
    assert staged["control_passed"] is None
