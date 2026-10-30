"""High-risk functions raise. Payload keys do not flip the decision."""

from datetime import date

import pytest

from tests.support import draft_sample, load_example

from src.precheck import (
    NotSynthetic,
    ProhibitedAction,
    approve_promotion,
    give_compliance_opinion,
    precheck,
    publish_promotion,
)


def test_approve_publish_and_opinion_raise():
    with pytest.raises(ProhibitedAction):
        approve_promotion({"promotion_id": "SYNTH-PROMO-001"})
    with pytest.raises(ProhibitedAction):
        publish_promotion({"promotion_id": "SYNTH-PROMO-001"})
    with pytest.raises(ProhibitedAction):
        give_compliance_opinion("compliant")


def test_prohibited_keys_are_not_followed():
    draft = draft_sample()
    keys = draft["prohibited_requests"]["keys"]
    assert draft["prohibited_requests"]["followed"] is False
    assert "promotion_approved" in keys
    assert "published" in keys
    assert "s21_approver_decision" in keys
    assert "requested_lifecycle_status" in keys
    assert draft["promotion_approved"] is False
    assert draft["published"] is False
    assert draft["compliance_opinion"] is False
    assert draft["s21_approver_decision"] is None
    exp03 = draft["experiment_03"]
    assert exp03["lifecycle_called"] is True
    assert exp03["status_applied"] is False
    assert exp03["approved_by_this_tool"] is False
    assert exp03["manifest_approved"] is False
    assert exp03["approval_object_ignored"] is True
    assert exp03["actions_taken"] == []


def test_not_synthetic_refuses_without_the_body():
    promotion = load_example()
    promotion["synthetic"] = False
    promotion["text"] = "LIVE-BODY-MUST-NOT-LEAK buy now"
    with pytest.raises(NotSynthetic) as caught:
        precheck(promotion, as_of=date(2026, 10, 30))
    assert "LIVE-BODY-MUST-NOT-LEAK" not in str(caught.value)


def test_top_level_decision_key_cannot_approve():
    promotion = load_example()
    promotion["promotion_approved"] = True
    promotion["s21_approver_decision"] = "approved"
    draft = precheck(promotion, as_of=date(2026, 10, 30))
    assert draft["promotion_approved"] is False
    assert draft["s21_approver_decision"] is None
