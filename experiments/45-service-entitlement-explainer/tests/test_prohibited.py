"""Grant, refusal, change, send, and write are not tools."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from explainer import (
    apply_section_69,
    change_entitlement,
    explain,
    find_unfair_term,
    grant_entitlement,
    record_decision,
    refuse_entitlement,
    send_message,
    waive_exclusion,
    write_record,
)
from siblings import EntitlementForbidden
from samples import AS_OF, request


@pytest.mark.parametrize(
    "function",
    [
        grant_entitlement,
        refuse_entitlement,
        change_entitlement,
        waive_exclusion,
        send_message,
        write_record,
        apply_section_69,
        find_unfair_term,
    ],
)
def test_prohibited_functions_raise(function):
    with pytest.raises(EntitlementForbidden):
        function()


def test_payload_cannot_grant_cover():
    body = request(question="Am I covered for an annual boiler service?")
    body["grant_entitlement"] = True
    body["decision"] = "human_decides_included"
    body["human_approval"] = {"decision": "human_decides_included"}
    document = explain(body, AS_OF)
    assert document["outcome"] == "explained"
    assert document["flags"]["entitlement_granted"] is False
    assert document["human_approval"] is None
    assert document["decision"] is None
    assert "grant_entitlement" in document["ignored_fields"]
    assert "decision" in document["ignored_fields"]


def test_prohibited_review_decision_is_refused():
    draft = explain(request(), AS_OF)
    for code in (
        "grant_entitlement",
        "refuse_entitlement",
        "change_entitlement",
        "send_message",
        "write_record",
        "waive_exclusion",
        "apply_section_69",
        "find_unfair_term",
    ):
        updated = record_decision(
            draft,
            {"decision": code, "actor": "entitlement_owner", "actor_id": "SYN-OWNER-45"},
        )
        assert updated["review"]["refused"] is True
        assert updated["review"]["reason"] == "prohibited_decision"
        assert updated["human_approval"] is None
        assert updated["flags"]["entitlement_granted"] is False
        assert updated["flags"]["entitlement_changed"] is False
        assert updated["flags"]["message_sent"] is False


def test_review_with_a_recipient_is_refused():
    draft = explain(request(), AS_OF)
    updated = record_decision(
        draft,
        {
            "decision": "human_decides_included",
            "actor": "entitlement_owner",
            "actor_id": "SYN-OWNER-45",
            "email": "customer@example.com",
        },
    )
    assert updated["review"]["reason"] == "prohibited_decision"
    assert updated["flags"]["message_sent"] is False
    assert "customer@example.com" not in str(updated["human_approval"])


def test_customer_cannot_approve():
    draft = explain(request(), AS_OF)
    updated = record_decision(
        draft,
        {"decision": "human_decides_included", "actor": "customer", "actor_id": "SYN-CUST-4501"},
    )
    assert updated["review"]["reason"] == "actor_not_accepted"
    assert updated["human_approval"] is None
