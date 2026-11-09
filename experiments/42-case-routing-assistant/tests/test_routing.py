"""Queue proposals stay explanatory, and a human queue cannot be downgraded."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.routing import propose_route  # noqa: E402
from tests.conftest import case  # noqa: E402

AS_OF = "2026-11-09"


def test_a_single_approved_rule_proposes_a_queue_and_does_not_apply_it():
    result = propose_route(case("The bin collection was missed on Tuesday."), AS_OF)
    assert result["outcome"] == "proposed_route"
    assert result["proposed_queue"] == "q-waste"
    assert result["priority"] == "routine"
    assert result["confidence"]["band"] == "high"
    assert result["confidence"]["basis"] == "deterministic_rule_match"
    assert result["human_approval"] is None
    assert result["flags"]["rerouted"] is False
    assert result["rules"]["applied"] is True
    assert result["rules"]["applied_means_rerouted"] is False
    assert result["confirmation_required_before_reroute"] is True


def test_vulnerability_and_a_statutory_clock_both_stay_with_a_person():
    result = propose_route(
        case("I can't afford food and there is mould in the bathroom."),
        AS_OF,
    )
    assert result["outcome"] == "human_vulnerability"
    assert result["proposed_queue"] == "q-human-vulnerability"
    assert result["confidence"]["band"] == "not_used"
    assert result["confidence"]["overrides_human_route"] is False
    assert result["statutory_clock"]["present"] is True
    assert result["flags"]["person_labelled_vulnerable"] is False
    assert "awaabs" in result["statutory_clock"]["kinds"]


def test_classification_names_follow_experiment_01_without_calling_it():
    result = propose_route(
        case("This is a freedom of information request for the pest control contract."),
        AS_OF,
    )
    assert result["classification"]["primary_type"] == "foi_request"
    assert result["classification"]["experiment_01_model_called"] is False
    assert result["outcome"] == "human_statutory"
    assert result["statutory_clock"]["date_calculated"] is False


def test_a_subject_access_period_is_not_invented():
    result = propose_route(case("This is a subject access request for my file."), AS_OF)
    blob = __import__("json").dumps(result)
    assert "one month" not in blob.lower()
    assert "Article 12A" in blob
    assert result["classification"]["primary_type"] == "subject_access_request"


def test_conflicting_rules_choose_neither_queue():
    result = propose_route(
        case("The bin collection was missed and the kitchen tap is leaking."),
        AS_OF,
    )
    assert result["outcome"] == "human_review"
    assert result["proposed_queue"] is None
    assert result["confidence"]["band"] == "low"
    assert result["confidence"]["conflict"] is True
