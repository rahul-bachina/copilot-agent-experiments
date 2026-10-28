"""Screening answers are not a decision that a DPIA is required."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from screening import screen

ARTICLE = (
    "article_35_3_a",
    "article_35_3_b",
    "article_35_3_c",
)
ICO = (
    "innovative_technology",
    "denial_of_service",
    "large_scale_profiling",
    "biometric_data",
    "genetic_data",
    "data_matching",
    "invisible_processing",
    "tracking",
    "targeting_children_or_vulnerable",
    "risk_of_physical_harm",
)
WP = (
    "wp248_evaluation_or_scoring",
    "wp248_automated_decision_legal_or_similar",
    "wp248_systematic_monitoring",
    "wp248_sensitive_or_highly_personal",
    "wp248_large_scale",
    "wp248_matching_datasets",
    "wp248_vulnerable_data_subjects",
    "wp248_innovative_use",
    "wp248_prevents_rights_or_service",
)


def answers(**overrides) -> dict:
    base = {key: "no" for key in ARTICLE + ICO + WP}
    base["genetic_data_direct_care_by_individual_professional"] = "no"
    base.update(overrides)
    return base


def test_article_35_3_is_recorded_and_is_not_a_determination():
    for key in ARTICLE:
        result = screen(answers(**{key: "yes"}), article_35_1_view="no")
        assert result["screen_result"] == "article_35_3_recorded"
        assert result["dpia_required"] is None
        assert result["dpia_required_decided_by_this_tool"] is False
        assert result["indicated_on_recorded_answers"] is True
        assert "controller_view_does_not_clear_article_35_3" in result["flags"]


def test_standalone_ico_items_are_recorded():
    for key in (
        "denial_of_service",
        "large_scale_profiling",
        "data_matching",
        "targeting_children_or_vulnerable",
        "risk_of_physical_harm",
    ):
        result = screen(answers(**{key: "yes"}))
        assert result["screen_result"] == "ico_list_recorded"
        assert result["dpia_required"] is None


def test_innovative_technology_alone_is_not_a_completed_trigger():
    result = screen(answers(innovative_technology="yes"))
    assert result["screen_result"] == "ico_list_combination_not_shown"
    assert result["indicated_on_recorded_answers"] is False
    assert result["dpia_required"] is None


def test_innovative_technology_plus_another_criterion_is_recorded():
    result = screen(answers(innovative_technology="yes", wp248_sensitive_or_highly_personal="yes"))
    assert result["screen_result"] == "ico_list_recorded"


def test_the_matching_innovative_criterion_does_not_count_as_the_other_one():
    result = screen(answers(innovative_technology="yes", wp248_innovative_use="yes"))
    assert result["screen_result"] == "ico_list_combination_not_shown"


def test_genetic_direct_care_exception_is_not_applied():
    result = screen(
        answers(
            genetic_data="yes",
            genetic_data_direct_care_by_individual_professional="yes",
        )
    )
    assert result["screen_result"] == "exception_not_decided"
    assert result["dpia_required"] is None


def test_genetic_data_with_another_criterion_is_recorded():
    result = screen(answers(genetic_data="yes", wp248_vulnerable_data_subjects="yes"))
    assert result["screen_result"] == "ico_list_recorded"


def test_two_wp248_factors_are_not_a_strict_rule():
    result = screen(
        answers(
            wp248_evaluation_or_scoring="yes",
            wp248_large_scale="yes",
        )
    )
    assert result["screen_result"] == "wp248_two_factors_recorded"
    assert result["two_factors_usually_indicate"] is True
    assert result["indicated_on_recorded_answers"] is False
    assert "not a strict rule" in result["reading"]


def test_one_wp248_factor_is_not_a_determination():
    result = screen(answers(wp248_systematic_monitoring="yes"))
    assert result["screen_result"] == "single_factor_recorded"
    assert result["dpia_required"] is None


def test_every_no_is_not_a_decision_that_article_35_does_not_apply():
    result = screen(answers(), article_35_1_view="no")
    assert result["screen_result"] == "recorded_answers_do_not_indicate"
    assert result["dpia_required"] is None
    assert "not a decision" in result["reading"]


def test_missing_answers_are_not_treated_as_no():
    result = screen({})
    assert result["screen_result"] == "insufficient_facts"


def test_controller_view_yes_is_recorded_when_nothing_else_is():
    result = screen(answers(), article_35_1_view="yes")
    assert result["screen_result"] == "article_35_1_view_recorded"
    assert result["dpia_required"] is None


def test_a_rejected_answer_is_not_a_yes():
    result = screen(answers(denial_of_service="approve"))
    assert result["screen_result"] == "insufficient_facts"
    assert "denial_of_service" in result["rejected_keys"]
    assert result["dpia_required"] is None
