"""Supplied summaries are scored. A miss escalates. It does not decline."""

from datetime import date

from src.triage import score_supplied_summary, triage
from tests.support import COVERED_CANDIDATE, INCOMPLETE_CANDIDATE, INVENTED_AMOUNT, base_pack

AS_OF = date(2026, 11, 5)


def test_agent_summary_meets_the_draft_bar():
    draft = triage(base_pack(), as_of=AS_OF)
    card = draft["scorecard"]
    assert card["faithfulness"]["method"] == "experiment_29_score_claim"
    assert card["faithfulness"]["supported_rate"] == 1.0
    assert card["faithfulness"]["stale_claim_count_is_separate"] is True
    assert card["completeness"]["rate"] == 1.0
    assert card["unsupported_coverage"]["count"] == 0
    assert card["scores_are_not_summed_across_criteria"] is True
    assert card["threshold_approved_by_evaluation_owner"] is False
    assert "total" not in card
    assert "grand_total" not in card


def test_unsupported_coverage_escalates_without_declining():
    card = score_supplied_summary(base_pack(), COVERED_CANDIDATE, as_of=AS_OF)
    assert card["unsupported_coverage"]["count"] >= 1
    assert "unsupported_coverage" in card["criteria_below_threshold"]
    assert card["human_escalation_required"] is True
    assert card["claim_declined"] is False
    assert card["llm_as_judge"] is False
    assert card["foundry_evaluator_called"] is False


def test_invented_amount_fails_faithfulness_only_as_a_flag():
    card = score_supplied_summary(base_pack(), INVENTED_AMOUNT, as_of=AS_OF)
    assert card["faithfulness"]["supported_rate"] < 1
    assert "faithfulness" in card["criteria_below_threshold"]
    assert card["human_escalation_required"] is True
    assert card["claim_declined"] is False
    verdicts = {row["verdict"] for row in card["faithfulness"]["claims"]}
    assert "number_mismatch" in verdicts


def test_incomplete_summary_fails_completeness_without_a_summed_score():
    card = score_supplied_summary(base_pack(), INCOMPLETE_CANDIDATE, as_of=AS_OF)
    assert card["completeness"]["rate"] < 1
    assert "completeness" in card["criteria_below_threshold"]
    assert card["faithfulness"]["supported_rate"] == 1.0
    assert card["human_escalation_required"] is True
    assert card["claim_declined"] is False
    assert "grand_total" not in card
    combined = (card["faithfulness"]["supported_rate"] or 0) + (card["completeness"]["rate"] or 0)
    assert combined not in card.values()
    assert combined not in card["faithfulness"].values()
    assert combined not in card["completeness"].values()
