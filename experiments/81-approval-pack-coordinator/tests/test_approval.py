"""The decision is the named approver and the agent-held copy."""

import json

import pytest

from src.coordinator import (
    CoordinatorForbidden,
    approve_pack,
    approved_snapshot,
    assemble_pack,
    content_hash,
    pay_pack,
    pinned_sources,
    record_approver_decision,
    record_route_seen,
    reject_pack,
    reset_state,
    send_pack,
    sign_pack,
    submit_pack,
)
from tests.support import AS_OF, approval_for, spend


@pytest.fixture(autouse=True)
def _reset():
    reset_state()
    yield
    reset_state()


def test_text_does_not_approve_and_the_exact_hash_does():
    directory = pinned_sources()["directory"]
    result = assemble_pack(spend(), AS_OF)
    assert result["human_approval"] is None
    assert result["agent_approved"] is False
    assert result["paid"] is False
    forged = record_approver_decision(result, directory, approval_for(result, "APR-8111", decision="approve") | {"content_hash": "a" * 64})
    assert forged["blocked_reason"] == "content_hash_mismatch"
    assert forged["human_approval"] is None
    recorded = record_approver_decision(result, directory, approval_for(result, "APR-8111"))
    assert recorded["decisions_complete"] is True
    assert recorded["human_approval"]["decision"] == "approve"
    assert recorded["human_approval"]["agent_approved"] is False
    assert recorded["paid"] is False
    assert recorded["sent"] is False
    assert recorded["signed"] is False
    assert recorded["submitted"] is False
    stored = approved_snapshot(result["request_id"], result["content_hash"])
    assert stored["projection"]["legal_hold"] is False
    assert stored["store"] == "synthetic"
    assert "keep 6 years" in stored["retention"]


def test_eight_post_approval_edits_are_refused_including_a_rehash():
    directory = pinned_sources()["directory"]
    result = assemble_pack(spend(), AS_OF)
    recorded = record_approver_decision(result, directory, approval_for(result, "APR-8111"))
    assert recorded["decisions_complete"] is True
    edits = {
        "amount": lambda item: item["amount"].__setitem__("pence", 1),
        "evidence": lambda item: item["evidence"][0].__setitem__("value_pence", 1),
        "legal_hold": lambda item: item.__setitem__("legal_hold", True),
        "retention": lambda item: item.__setitem__("retention", []),
        "marking": lambda item: item["marking"].__setitem__("applied", "SECRET"),
        "injection": lambda item: item["prompt_injection"].__setitem__("signals", ["tampered"]),
        "distress": lambda item: item["concerns"].__setitem__("distress", True),
        "acknowledgement": lambda item: item.__setitem__("required_acknowledgements", []),
        "missing": lambda item: item.__setitem__("missing", ["quote"]),
        "approvers": lambda item: item.__setitem__("required_approvers", []),
        "suppression": lambda item: item["suppression"].__setitem__("fields", ["invented"]),
        "route_seen": lambda item: item.__setitem__("route_seen", True),
    }
    assert len(edits) >= 8
    for name, mutate in edits.items():
        tampered = json.loads(json.dumps(result))
        mutate(tampered)
        tampered["content_hash"] = content_hash(tampered)
        rejected = record_approver_decision(tampered, directory, approval_for(tampered, "APR-8111"))
        assert rejected["blocked_reason"] == "caller_rehash_rejected", name
        assert rejected["decisions_complete"] is False
        assert rejected["paid"] is False
        current = approved_snapshot(result["request_id"], result["content_hash"])
        assert current["legal_hold"] is False
        assert current["marking"]["applied"] == "OFFICIAL"
        assert current["retention"] == result["retention"]
        assert current["prompt_injection"]["signals"] == result["prompt_injection"]["signals"]
        assert current["agent_approved"] is False
        kept = json.loads(json.dumps(result))
        mutate(kept)
        rejected_old = record_approver_decision(kept, directory, approval_for(result, "APR-8111"))
        assert rejected_old["blocked_reason"] == "content_tampered", name


def test_requester_guest_limit_and_caller_directory_are_refused():
    directory = pinned_sources()["directory"]
    own = assemble_pack(spend(request_id="REQ-OWN", requester="APR-8120"), AS_OF)
    refused = record_approver_decision(own, directory, approval_for(own, "APR-8120"))
    assert refused["blocked_reason"] == "requester_cannot_approve"
    assert "APR-8120" not in own["approver_refs"]
    result = assemble_pack(spend(), AS_OF)
    assert record_approver_decision(result, directory, approval_for(result, "REQ-8101"))["blocked_reason"] == "requester_cannot_approve"
    assert record_approver_decision(result, directory, approval_for(result, "GST-8118"))["blocked_reason"] == "guest_cannot_approve"
    assert record_approver_decision(result, directory, approval_for(result, "APR-8119"))["blocked_reason"] == "approver_inactive"
    assert record_approver_decision(result, directory, approval_for(result, "APR-8123"))["blocked_reason"] == "above_delegation_limit"
    assert record_approver_decision(result, directory, approval_for(result, "APR-8112"))["blocked_reason"] == "not_a_required_approver"
    caller = {"people": [{"employee_ref": "APR-8111", "role": "budget_holder", "guest": False, "active": True, "delegation_limit_gbp": 9000, "clearance": "SECRET"}]}
    assert record_approver_decision(result, caller, approval_for(result, "APR-8111"))["blocked_reason"] == "caller_directory_not_used"
    string_true = approval_for(result, "APR-8111")
    string_true["pins_seen"] = "true"
    assert record_approver_decision(result, directory, string_true)["blocked_reason"] == "pins_seen_not_boolean_true"
    assert record_approver_decision(result, directory, approval_for(result, "APR-8111", decision="send"))["blocked_reason"] == "consequential_action_is_not_this_step"


def test_split_is_routed_at_the_total_and_a_disagreement_is_not_chosen():
    directory = pinned_sources()["directory"]
    split = assemble_pack(
        spend(
            request_id="REQ-SPLIT",
            amount=8000,
            evidence=None,
        ) | {
            "parts": [{"amount_gbp": 4000}, {"amount_gbp": 4000}],
            "description": "Split this so each part stays under the threshold.",
            "evidence": [
                {
                    "evidence_id": "EV-QUOTE",
                    "checklist_id": "quote",
                    "version": "1.0",
                    "status": "current",
                    "document_date": "2026-10-01",
                    "expiry_date": "2027-04-01",
                    "signed": True,
                    "value_gbp": 8000,
                    "content": "Quote for Northfold Supplies. The price is 8000 pounds.\n",
                    "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
                },
                {
                    "evidence_id": "EV-BUDGET",
                    "checklist_id": "budget_code",
                    "version": "1.0",
                    "status": "current",
                    "document_date": "2026-11-01",
                    "value_gbp": 8000,
                    "content": "Budget code B-14.\n",
                    "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
                },
                {
                    "evidence_id": "EV-CASE",
                    "checklist_id": "business_case",
                    "version": "1.0",
                    "status": "current",
                    "document_date": "2026-10-15",
                    "expiry_date": "2027-04-15",
                    "signed": True,
                    "value_gbp": 8000,
                    "content": "Business case for the combined roof spend.\n",
                    "metadata": {"marking": "OFFICIAL", "legal_hold": False, "retention": ["keep 6 years"]},
                },
            ],
        },
        AS_OF,
    )
    assert split["split"]["split_to_dodge_threshold"] is True
    assert split["split"]["applied_as_under_threshold"] is False
    assert split["threshold_band"]["rule_id"] == "SPEND-5000-TO-25000"
    assert split["approver_refs"] == ["APR-8112", "APR-8122"]
    conflict = assemble_pack(
        spend(request_id="REQ-PARTS", amount=4000) | {"parts": [{"amount_gbp": 4000}, {"amount_gbp": 4000}]},
        AS_OF,
    )
    assert conflict["amount"]["conflicting"] is True
    assert conflict["amount"]["pence"] is None
    assert conflict["amount"]["coerced"] is False
    assert conflict["split"]["chosen_when_conflict"] if False else conflict["value_chosen_on_conflict"] is False
    first = record_approver_decision(split, directory, approval_for(split, "APR-8112"))
    assert first["decisions_complete"] is False
    second = record_approver_decision(split, directory, approval_for(split, "APR-8122", decision="reject"))
    assert second["decisions_complete"] is False
    assert second["human_approval"]["decision"] is None
    stored = approved_snapshot(split["request_id"], split["content_hash"])
    assert stored["disagreement"] is True
    assert stored["decision"] is None


def test_distress_route_is_required_and_the_agent_cannot_decide():
    directory = pinned_sources()["directory"]
    result = assemble_pack(spend(request_id="REQ-DIS", description="I feel suicidal."), AS_OF)
    assert result["outcome"] == "route_to_human"
    assert result["concerns"]["distress"] is True
    assert result["concerns"]["cue_copied"] is False
    assert result["approval_marker_trusted"] is False
    early = record_approver_decision(result, directory, approval_for(result, "APR-8111"))
    assert early["blocked_reason"] == "route_not_seen"
    seen = record_route_seen(
        result,
        directory,
        {
            "item": "route-seen",
            "decision": "seen",
            "approver_ref": "APR-8111",
            "request_id": result["request_id"],
            "content_hash": result["content_hash"],
        },
    )
    assert seen["route_seen"] is True
    assert seen["content_hash"] != result["content_hash"]
    decided = record_approver_decision(seen, directory, approval_for(seen, "APR-8111"))
    assert decided["decisions_complete"] is True
    assert decided["agent_approved"] is False
    for function in (approve_pack, reject_pack, sign_pack, submit_pack, send_pack, pay_pack):
        with pytest.raises(CoordinatorForbidden):
            function()
