"""Article 22A to 22D is a screen, not a clearance."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from automated import screen_automated

AS_OF = date(2026, 10, 28)


def test_restriction_when_special_category_and_no_human():
    result = screen_automated(
        {
            "processing_regime": "uk_gdpr",
            "processes_personal_data": "yes",
            "meaningful_human_involvement": "no",
            "significant_effect": "legal",
            "special_category_data": "yes",
            "explicit_consent": "no",
            "contract_or_authorised_by_law": "no",
            "article_9_2_g": "no",
            "profiling": "yes",
            "lawful_basis": "Article 6(1)(ea)",
            "decision_taken_before_5_february_2026": "no",
        },
        as_of=AS_OF,
    )
    assert result["screen_result"] == "restriction_may_apply"
    assert result["lawful"] is None
    assert "article_22B_1_restriction_may_apply" in result["flags"]
    assert "article_22B_4_restriction_may_apply" in result["flags"]
    assert "article_22D_regulations_not_read" in result["flags"]


def test_safeguards_recorded_are_not_a_clearance():
    result = screen_automated(
        {
            "processing_regime": "uk_gdpr",
            "processes_personal_data": "yes",
            "meaningful_human_involvement": "no",
            "significant_effect": "similarly_significant",
            "special_category_data": "no",
            "profiling": "no",
            "lawful_basis": "Article 6(1)(e)",
            "safeguard_information": "yes",
            "safeguard_representations": "yes",
            "safeguard_human_intervention": "yes",
            "safeguard_contest": "yes",
            "decision_taken_before_5_february_2026": "no",
        },
        as_of=AS_OF,
    )
    assert result["screen_result"] == "safeguards_recorded_not_a_clearance"
    assert result["lawful"] is None


def test_human_involvement_recorded_is_not_article_22a_met():
    result = screen_automated(
        {
            "processing_regime": "uk_gdpr",
            "processes_personal_data": "yes",
            "meaningful_human_involvement": "yes",
            "significant_effect": "none",
            "decision_taken_before_5_february_2026": "no",
        },
        as_of=AS_OF,
    )
    assert result["screen_result"] == "significant_decision_not_recorded"
    assert "not a finding" in result["reading"] or "does not cover" in result["reading"]


def test_law_enforcement_is_a_different_regime():
    result = screen_automated(
        {"processing_regime": "law_enforcement"},
        as_of=AS_OF,
    )
    assert result["screen_result"] == "different_regime"
    assert "adverse" in result["reading"]
    assert result["lawful"] is None


def test_a_decision_before_commencement_is_not_run_through_the_new_test():
    result = screen_automated(
        {
            "processing_regime": "uk_gdpr",
            "processes_personal_data": "yes",
            "meaningful_human_involvement": "no",
            "significant_effect": "legal",
            "special_category_data": "yes",
            "decision_date": "2026-01-15",
        },
        as_of=AS_OF,
    )
    assert result["screen_result"] == "saving_provision_may_apply"
    assert "not interpreted" in result["reading"].lower() or "has not interpreted" in result["reading"]
    assert result["lawful"] is None


def test_missing_facts_stay_missing():
    result = screen_automated({"processing_regime": "uk_gdpr"}, as_of=AS_OF)
    assert result["screen_result"] == "insufficient_facts"
    assert result["lawful"] is None
