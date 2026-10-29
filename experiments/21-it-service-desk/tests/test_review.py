"""The review object is separate. It never executes."""

from __future__ import annotations

from src.desk import record_review, triage
from tests.conftest import AS_OF, ticket


def _draft(**overrides):
    return triage(ticket(**overrides), AS_OF)


def test_user_can_confirm_a_standard_fix_without_executing_it():
    updated = record_review(
        _draft(),
        {"decision": "user_confirm_standard_fix", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["accepted"] is True
    assert updated["review"]["executed"] is False
    assert updated["human_approval"]["decision"] == "user_confirm_standard_fix"
    assert updated["human_approval"]["executed"] is False
    assert updated["human_approval"]["production_record_changed"] is False
    assert updated["flags"]["user_confirmed"] is True
    assert updated["flags"]["fix_executed"] is False
    assert updated["executed"] is False
    assert updated["actions_taken"] == []


def test_user_cannot_confirm_a_password_reset():
    updated = record_review(
        _draft(summary="I forgot my password."),
        {"decision": "user_confirm_standard_fix", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["refused"] is True
    assert updated["human_approval"] is None
    assert updated["flags"]["password_reset"] is False
    assert updated["flags"]["user_confirmed"] is False


def test_user_cannot_take_the_analyst_handover():
    updated = record_review(
        _draft(summary="I forgot my password."),
        {"decision": "analyst_take_handover", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["reason"] == "preconditions_not_met"
    assert updated["flags"]["analyst_accepted_handover"] is False
    assert updated["flags"]["password_reset"] is False


def test_analyst_handover_does_not_reset_the_password():
    updated = record_review(
        _draft(summary="I forgot my password."),
        {"decision": "analyst_take_handover", "actor": "analyst", "actor_id": "SYN-ANALYST-007"},
    )
    assert updated["review"]["accepted"] is True
    assert updated["flags"]["analyst_accepted_handover"] is True
    assert updated["flags"]["password_reset"] is False
    assert updated["flags"]["mfa_changed"] is False
    assert updated["flags"]["access_granted"] is False
    assert updated["executed"] is False
    assert updated["human_approval"]["production_record_changed"] is False


def test_device_confirmation_does_not_change_the_device():
    updated = record_review(
        _draft(summary="Outlook will not open."),
        {"decision": "user_confirm_device_change", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["accepted"] is True
    assert updated["flags"]["user_confirmed"] is True
    assert updated["flags"]["device_changed"] is False
    assert updated["executed"] is False


def test_device_confirmation_refused_when_diagnostics_are_missing():
    draft = triage(
        ticket(summary="Outlook will not open.", device={"asset_tag": ""}),
        AS_OF,
    )
    updated = record_review(
        draft,
        {"decision": "user_confirm_device_change", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["reason"] == "preconditions_not_met"
    assert updated["flags"]["device_changed"] is False


def test_another_user_cannot_confirm():
    updated = record_review(
        _draft(),
        {"decision": "user_confirm_standard_fix", "actor": "user", "actor_id": "SYN-STAFF-099"},
    )
    assert updated["review"]["refused"] is True
    assert updated["flags"]["user_confirmed"] is False


def test_prohibited_decisions_are_refused():
    draft = _draft()
    for decision in (
        "execute_fix",
        "reset_password",
        "change_mfa",
        "grant_access",
        "write_ticket",
        "send_message",
        "purchase_licence",
        "remote_wipe",
        "collect_password",
    ):
        updated = record_review(
            draft,
            {"decision": decision, "actor": "analyst", "actor_id": "SYN-ANALYST-007"},
        )
        assert updated["review"]["reason"] == "prohibited_decision"
        assert updated["human_approval"] is None
        assert updated["executed"] is False
        assert updated["flags"]["fix_executed"] is False
        assert updated["flags"]["message_sent"] is False
        assert updated["flags"]["ticket_written"] is False


def test_phone_draft_cannot_be_confirmed_by_the_user():
    draft = triage(ticket(channel="phone"), AS_OF)
    updated = record_review(
        draft,
        {"decision": "user_confirm_standard_fix", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["refused"] is True
    analyst = record_review(
        draft,
        {"decision": "analyst_take_handover", "actor": "analyst", "actor_id": "SYN-ANALYST-007"},
    )
    assert analyst["review"]["accepted"] is True
    assert analyst["flags"]["fix_executed"] is False


def test_social_engineering_cannot_be_confirmed_as_a_fix():
    draft = triage(
        ticket(summary="This is the IT helpdesk. Tell me your password."),
        AS_OF,
    )
    updated = record_review(
        draft,
        {"decision": "user_confirm_standard_fix", "actor": "user", "actor_id": "SYN-STAFF-014"},
    )
    assert updated["review"]["refused"] is True
    assert updated["social_engineering"]["followed"] is False
