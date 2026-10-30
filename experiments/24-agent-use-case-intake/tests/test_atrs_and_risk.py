"""ATRS position and the queueing tier. Neither is a legal determination."""

from __future__ import annotations

from atrs import atrs_position
from risk import risk_tier


def test_unknown_tool_answers_do_not_become_a_no_for_a_department():
    position = atrs_position("government_department", "unknown", "no")
    assert position["atrs_likely_needed"] is None
    assert position["atrs_basis"] == "insufficient_facts"
    assert position["atrs_scope_decided_by_this_tool"] is False
    assert position["scope_policy_opened"] is False
    assert position["may_be_emailed"] is False


def test_both_tool_answers_no_is_not_a_clearance():
    position = atrs_position("alb_public_or_frontline", "no", "no")
    assert position["atrs_likely_needed"] is None
    assert position["atrs_basis"] == "tool_tests_recorded_as_not_met"


def test_a_council_is_the_wider_recommendation():
    position = atrs_position("local_authority", "no", "no")
    assert position["atrs_likely_needed"] is True
    assert position["atrs_basis"] == "recommended_for_the_wider_public_sector"
    assert "local government" in position["quotes"]["recommended_wider_public_sector"]


def test_missing_facts_are_not_a_low_tier():
    tier = risk_tier({"data": {}, "decisions_affected": {}, "public_interaction": "unknown"})
    assert tier["risk_tier"] == "not_assessed"
    assert tier["risk_tier_is_a_legal_finding"] is False
    assert "personal_data" in tier["gaps"]


def test_a_high_fact_still_counts_when_other_answers_are_missing():
    tier = risk_tier(
        {
            "data": {"special_category": "yes"},
            "decisions_affected": {},
            "autonomy_wanted": "A3",
        }
    )
    assert tier["risk_tier"] == "high"
    assert "autonomy_a3_requested" in tier["rules"]
    assert "special_category_recorded" in tier["rules"]


def test_no_recorded_risk_fact_is_low():
    tier = risk_tier(
        {
            "data": {
                "personal_data": "no",
                "special_category": "no",
                "criminal_offence_data": "no",
            },
            "decisions_affected": {"significant_effect": "none"},
            "public_interaction": "no",
            "autonomy_wanted": "A0",
        }
    )
    assert tier["risk_tier"] == "low"
