"""Lifecycle status changes only when a governance owner has already decided."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from support import load_record  # noqa: E402
from lifecycle import ProhibitedAction, apply_status_change, propose_status_change  # noqa: E402


def _approval(record, target, **overrides):
    approval = {
        "source": "external",
        "approval_id": "GOV-2026-0001",
        "approver_role": "Governance owner",
        "decision": "approve",
        "decided_on": "2026-10-24",
        "inventory_id": record["inventory_id"],
        "to_status": target,
        "approved_by_this_tool": False,
    }
    approval.update(overrides)
    return approval


def test_propose_does_not_change_status():
    record = load_record("exp-01-foi-triage")
    original = record["lifecycle_status"]
    proposal = propose_status_change(record, "in_design", "Move the draft on", "Inventory drafter")
    assert record["lifecycle_status"] == original
    assert proposal["applied"] is False
    assert proposal["approved"] is False
    assert proposal["approved_by_this_tool"] is False
    assert proposal["actions_taken"] == []


def test_apply_without_decision_leaves_status():
    record = load_record("exp-01-foi-triage")
    proposal = propose_status_change(record, "in_design", "Move the draft on", "Inventory drafter")
    updated, event = apply_status_change(record, proposal, None)
    assert updated["lifecycle_status"] == "proposed"
    assert event["applied"] is False
    assert event["approved"] is False
    assert event["approved_by_this_tool"] is False


def test_wrong_role_is_rejected():
    record = load_record("exp-01-foi-triage")
    proposal = propose_status_change(record, "pilot", "Start a pilot", "Inventory drafter")
    updated, event = apply_status_change(
        record, proposal, _approval(record, "pilot", approver_role="Information rights lead")
    )
    assert updated is record
    assert event["applied"] is False
    assert "Governance owner" in event["rejection"]


def test_generated_approval_id_is_rejected():
    record = load_record("exp-02-consumer-duty-complaint-intake")
    proposal = propose_status_change(record, "in_design", "Draft only", "Inventory drafter")
    updated, event = apply_status_change(
        record,
        proposal,
        _approval(record, "in_design", approval_id="g010-generated-99"),
    )
    assert updated["lifecycle_status"] == "proposed"
    assert event["applied"] is False


def test_reject_decision_does_not_change_status():
    record = load_record("exp-01-foi-triage")
    proposal = propose_status_change(record, "suspended", "Pause", "Inventory drafter")
    updated, event = apply_status_change(
        record, proposal, _approval(record, "suspended", decision="reject")
    )
    assert updated["lifecycle_status"] == "proposed"
    assert event["external_decision"] == "reject"
    assert event["applied"] is False
    assert event["approved_by_this_tool"] is False


def test_external_approval_changes_status_and_still_is_not_this_tool():
    record = load_record("exp-01-foi-triage")
    proposal = propose_status_change(record, "in_design", "Owner has decided outside this tool", "Inventory drafter")
    updated, event = apply_status_change(record, proposal, _approval(record, "in_design"))
    assert updated["lifecycle_status"] == "in_design"
    assert record["lifecycle_status"] == "proposed"
    assert event["applied"] is True
    assert event["external_decision"] == "approve"
    assert event["approved"] is False
    assert event["approved_by_this_tool"] is False
    assert updated["lifecycle_change_approved_by_this_tool"] is False


def test_tool_refuses_to_mint_an_approval():
    record = load_record("exp-01-foi-triage")
    proposal = propose_status_change(record, "in_design", "No", "Inventory drafter")
    with pytest.raises(ProhibitedAction):
        apply_status_change(record, proposal, {"minted_by": "g010", "source": "external"})


def test_every_status_requires_the_governance_owner():
    record = load_record("exp-01-foi-triage")
    current = record
    for target in ("in_design", "pilot", "assurance_drafted", "awaiting_governance_owner", "approved_for_limited_use"):
        proposal = propose_status_change(current, target, f"Step to {target}", "Inventory drafter")
        refused, event = apply_status_change(copy.deepcopy(current), proposal, None)
        assert refused["lifecycle_status"] == current["lifecycle_status"]
        assert event["approved_by_this_tool"] is False
        current, event = apply_status_change(current, proposal, _approval(current, target))
        assert current["lifecycle_status"] == target
        assert event["approved"] is False
