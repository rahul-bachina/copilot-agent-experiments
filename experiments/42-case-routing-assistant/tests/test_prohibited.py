"""Nothing in the review path reroutes, closes, escalates, or edits a rule."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.routing import (  # noqa: E402
    RoutingForbidden,
    change_routing_rules,
    close_case,
    escalate_case,
    propose_route,
    record_review,
    reroute_case,
)
from tests.conftest import case  # noqa: E402

AS_OF = "2026-11-09"


def _waste():
    return propose_route(case("The bin collection was missed."), AS_OF)


def test_direct_actions_raise():
    for function in (reroute_case, close_case, escalate_case, change_routing_rules):
        with pytest.raises(RoutingForbidden):
            function()


def test_a_confirmation_does_not_reroute():
    reviewed = record_review(
        _waste(),
        {
            "decision": "adviser_confirm_proposed_route",
            "actor": "adviser",
            "actor_id": "SYN-ADVISER-004",
        },
    )
    assert reviewed["review"]["accepted"] is True
    assert reviewed["review"]["executed"] is False
    assert reviewed["flags"]["rerouted"] is False
    assert reviewed["human_approval"]["executed"] is False
    assert reviewed["human_approval"]["rerouted"] is False


def test_a_human_queue_cannot_be_confirmed_as_a_routine_reroute():
    proposal = propose_route(case("I want to kill myself."), AS_OF)
    reviewed = record_review(
        proposal,
        {
            "decision": "adviser_confirm_proposed_route",
            "actor": "adviser",
            "actor_id": "SYN-ADVISER-004",
        },
    )
    assert reviewed["review"]["refused"] is True
    assert reviewed["review"]["reason"] == "human_queue_is_not_a_bot_route"
    assert reviewed["human_approval"] is None
    assert reviewed["flags"]["escalated"] is False


def test_accepting_a_human_queue_does_not_escalate():
    proposal = propose_route(case("This is a freedom of information request."), AS_OF)
    reviewed = record_review(
        proposal,
        {
            "decision": "adviser_accept_human_queue",
            "actor": "adviser",
            "actor_id": "SYN-ADVISER-004",
        },
    )
    assert reviewed["review"]["accepted"] is True
    assert reviewed["flags"]["escalated"] is False
    assert reviewed["flags"]["closed"] is False
    assert reviewed["proposed_queue"] == "q-human-statutory"


def test_a_prohibited_decision_is_refused():
    for decision in ("reroute", "close", "escalate", "change_routing_rules", "send"):
        reviewed = record_review(
            _waste(),
            {"decision": decision, "actor": "adviser", "actor_id": "SYN-ADVISER-004"},
        )
        assert reviewed["review"]["reason"] == "prohibited_decision"
        assert reviewed["flags"]["rerouted"] is False
        assert reviewed["flags"]["rules_changed"] is False
        assert reviewed["human_approval"] is None


def test_queue_owner_approval_does_not_edit_the_rule_file():
    proposal = propose_route(
        case(
            "The bin collection was missed.",
            proposed_rule_change={"rule_id": "rule-extra", "feature": "service_topic"},
        ),
        AS_OF,
    )
    assert proposal["outcome"] == "proposed_route"
    reviewed = record_review(
        proposal,
        {
            "decision": "queue_owner_approve_rule_change",
            "actor": "queue_owner",
            "actor_id": "SYN-OWNER-002",
            "rule_id": "rule-extra",
        },
    )
    assert reviewed["review"]["accepted"] is True
    assert reviewed["review"]["reason"] == "approval_recorded_rule_file_not_changed"
    assert reviewed["flags"]["rules_changed"] is False
    assert reviewed["rule_change"]["rules_file_changed"] is False
    assert reviewed["rule_change"]["applied"] is False


def test_a_protected_characteristic_cannot_be_approved_as_a_feature():
    proposal = propose_route(
        case(
            "The bin collection was missed.",
            proposed_rule_change={"rule_id": "rule-race", "feature": "race"},
        ),
        AS_OF,
    )
    assert proposal["outcome"] == "human_fairness"
    assert proposal["flags"]["protected_characteristic_used_as_a_feature"] is False
    reviewed = record_review(
        proposal,
        {
            "decision": "queue_owner_approve_rule_change",
            "actor": "queue_owner",
            "actor_id": "SYN-OWNER-002",
            "rule_id": "rule-race",
        },
    )
    assert reviewed["review"]["reason"] == "no_approvable_rule_change"
    assert reviewed["flags"]["rules_changed"] is False


def test_an_unapproved_draft_rule_is_not_applied():
    result = propose_route(case("I need a parking permit."), AS_OF)
    assert result["outcome"] == "rule_not_owner_approved"
    assert result["proposed_queue"] is None
    assert "rule-parking-draft" in result["rules"]["unapproved_ids"]
