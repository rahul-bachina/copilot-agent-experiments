"""Commencement is a date comparison. It is not a finding about the employer."""

from datetime import date

import pytest

from src.review import ReviewError, review
from src.sources import LAST_VERIFIED
from tests.support import base_pack


def _duty(result, duty_id):
    return next(row for row in result["duties"] if row["id"] == duty_id)


def _prompt(result, prompt_id):
    return next(row for row in result["preparation_prompts"] if row["id"] == prompt_id)


def _assert_no_decision(result):
    assert result["hr_decision"] is None
    assert result["compliance_conclusion"] is None
    assert result["disciplinary_decision"] is None
    assert result["actions_taken"] == []
    assert result["policy_published"] is False
    assert result["records_changed"] is False
    assert result["message_sent"] is False
    assert result["legal_advice"] is False
    assert result["model_called"] is False
    assert result["network_called"] is False
    assert result["flags"]["compliance_concluded"] is False
    assert result["flags"]["disciplinary_decision_made"] is False
    assert result["flags"]["tribunal_deadline_calculated"] is False
    assert result["flags"]["dismissal_decided"] is False
    assert result["flags"]["acas_contacted"] is False
    assert result["flags"]["regulations_under_section_40b_applied"] is False
    assert result["flags"]["size_used_to_lower_a_duty"] is False
    assert result["risk_assessment"]["likelihood"] is None
    assert result["risk_assessment"]["agent_completed"] is False
    assert all(duty["compliance_conclusion"] is None for duty in result["duties"])
    assert all(row["legal_breach"] is False for row in result["preparation_prompts"])


def test_on_27_october_2026_the_strengthened_duty_is_not_yet_in_force():
    result = review(base_pack(), as_of=date(2026, 10, 27))
    assert result["label"] == "DRAFT FOR HR REVIEW"
    assert result["catalogue_last_verified"] == LAST_VERIFIED
    assert result["rules_current"] is True
    assert result["any_source_stale"] is False
    prevent = _duty(result, "prevent_sexual_harassment")
    assert prevent["in_force"] is True
    assert prevent["wording"] == "reasonable steps"
    assert prevent["all_reasonable_steps_in_force"] is False
    assert _duty(result, "third_party_harassment")["in_force"] is False
    assert _duty(result, "power_to_specify_reasonable_steps")["in_force"] is False
    assert _duty(result, "power_to_specify_reasonable_steps")["specified_steps_regulations_made"] is False
    assert _duty(result, "power_to_specify_reasonable_steps")["regulations_applied"] is False
    assert _duty(result, "whistleblowing_sexual_harassment")["in_force"] is True
    assert _duty(result, "whistleblowing_sexual_harassment")["protected_disclosure_decided"] is False
    assert _duty(result, "tribunal_time_limits")["in_force"] is True
    assert _duty(result, "tribunal_time_limits")["deadline_calculated"] is False
    assert _duty(result, "unfair_dismissal_qualifying_period")["in_force"] is False
    assert _duty(result, "unfair_dismissal_qualifying_period")["qualifying_period_words"] == "two years"
    assert _duty(result, "unfair_dismissal_qualifying_period")["applied_to_a_person"] is False
    assert _duty(result, "nda_misuse_regulations")["in_force"] is False
    assert _duty(result, "nda_misuse_regulations")["scored"] is False
    assert _prompt(result, "third_party_risk_recorded")["status"] == "not_yet_in_force"
    assert _prompt(result, "third_party_risk_recorded")["evidence_gap"] is False
    _assert_no_decision(result)


def test_29_october_is_still_the_existing_reasonable_steps_duty():
    result = review(base_pack(), as_of=date(2026, 10, 29))
    prevent = _duty(result, "prevent_sexual_harassment")
    assert prevent["wording"] == "reasonable steps"
    assert prevent["all_reasonable_steps_in_force"] is False
    assert _duty(result, "third_party_harassment")["in_force"] is False


def test_30_october_2026_changes_the_wording_and_still_decides_nothing():
    result = review(base_pack(), as_of=date(2026, 10, 30))
    prevent = _duty(result, "prevent_sexual_harassment")
    assert prevent["wording"] == "all reasonable steps"
    assert prevent["all_reasonable_steps_in_force"] is True
    assert prevent["compliance_conclusion"] is None
    assert _duty(result, "third_party_harassment")["in_force"] is True
    assert _duty(result, "third_party_harassment")["limbs_decided"] is False
    power = _duty(result, "power_to_specify_reasonable_steps")
    assert power["in_force"] is True
    assert power["specified_steps_regulations_made"] is False
    assert power["regulations_applied"] is False
    assert result["flags"]["regulations_under_section_40b_applied"] is False
    _assert_no_decision(result)


def test_a_fully_evidenced_pack_is_still_not_a_compliance_conclusion():
    pack = base_pack()
    for key in list(pack["evidence"]):
        if key != "policy_review_date":
            pack["evidence"][key] = "evidenced"
    result = review(pack, as_of=date(2026, 10, 30))
    assert result["compliance_conclusion"] is None
    assert all(row["legal_breach"] is False for row in result["preparation_prompts"])
    assert _prompt(result, "policies_reviewed")["status"] == "evidenced"
    assert _prompt(result, "policies_reviewed")["evidence_gap"] is False
    assert _prompt(result, "policies_reviewed")["absence_is_not_a_breach"] is True
    assert result["workforce"]["used_to_lower_a_duty"] is False
    _assert_no_decision(result)


def test_qualifying_period_boundary_does_not_decide_a_dismissal():
    before = review(base_pack(), as_of=date(2026, 12, 31))
    after = review(base_pack(), as_of=date(2027, 1, 1))
    assert _duty(before, "unfair_dismissal_qualifying_period")["in_force"] is False
    assert _duty(before, "unfair_dismissal_qualifying_period")["section_124_omitted"] is False
    assert _duty(before, "unfair_dismissal_qualifying_period")["compensation_figure_stated"] is False
    started = _duty(after, "unfair_dismissal_qualifying_period")
    assert started["in_force"] is True
    assert started["qualifying_period_words"] == "six months"
    assert started["section_124_omitted"] is True
    assert started["applied_to_a_person"] is False
    assert started["effective_date_of_termination_decided"] is False
    assert started["transitional_provision_applied"] is False
    assert started["compensation_figure_stated"] is False
    assert _prompt(after, "probation_wording_reviewed_for_six_month_period")["applied_to_a_person"] is False
    _assert_no_decision(after)


def test_tribunal_limit_is_in_force_from_1_october_and_is_not_counted():
    before = review(base_pack(), as_of=date(2026, 9, 30))
    on_day = review(base_pack(), as_of=date(2026, 10, 1))
    assert _duty(before, "tribunal_time_limits")["in_force"] is False
    row = _duty(on_day, "tribunal_time_limits")
    assert row["in_force"] is True
    assert row["deadline_calculated"] is False
    assert row["relevant_date_identified"] is False
    assert row["scotland_contract_claims"]["applied"] is False
    assert row["scotland_contract_claims"]["instrument_opened"] is False


def test_scotland_timeline_date_is_not_applied_even_on_that_day():
    pack = base_pack()
    pack["employer"]["jurisdiction"] = "scotland"
    result = review(pack, as_of=date(2026, 11, 9))
    claims = _duty(result, "tribunal_time_limits")["scotland_contract_claims"]
    assert claims["applies_to_this_pack"] is True
    assert claims["applied"] is False
    assert claims["instrument_opened"] is False
    assert result["flags"]["tribunal_deadline_calculated"] is False


def test_northern_ireland_is_not_given_great_britain_duties():
    pack = base_pack()
    pack["employer"]["jurisdiction"] = "northern_ireland"
    result = review(pack, as_of=date(2026, 10, 30))
    assert result["jurisdiction_applied"] == "not_applied"
    assert result["northern_ireland_law_stated"] is False
    prevent = _duty(result, "prevent_sexual_harassment")
    assert prevent["applied"] is False
    assert prevent["in_force"] is False
    assert prevent["wording"] is None
    assert _duty(result, "unfair_dismissal_qualifying_period")["qualifying_period_words"] is None
    assert _prompt(result, "policies_reviewed")["status"] == "not_yet_in_force"
    assert _prompt(result, "policies_reviewed")["evidence_gap"] is False
    _assert_no_decision(result)


def test_policy_review_date_is_stale_only_after_the_threshold():
    pack = base_pack()
    pack["evidence"]["policy_review_date"] = "2025-10-27"
    same_day = review(pack, as_of=date(2026, 10, 27))
    assert same_day["policy_currency"]["policy_age_days"] == 365
    assert same_day["policy_currency"]["policy_evidence_stale"] is False
    pack["evidence"]["policy_review_date"] = "2025-10-26"
    older = review(pack, as_of=date(2026, 10, 27))
    assert older["policy_currency"]["policy_age_days"] == 366
    assert older["policy_currency"]["policy_evidence_stale"] is True
    assert older["policy_currency"]["policy_relied_on"] is False
    assert older["compliance_conclusion"] is None


def test_catalogue_equal_to_90_days_is_not_stale_and_the_next_day_is():
    fresh = review(base_pack(), as_of=date(2027, 1, 25))
    stale = review(base_pack(), as_of=date(2027, 1, 26))
    assert fresh["any_source_stale"] is False
    assert fresh["rules_current"] is True
    assert _duty(fresh, "prevent_sexual_harassment")["relied_on"] is True
    assert stale["any_source_stale"] is True
    assert stale["rules_current"] is False
    assert all(row["stale"] is True for row in stale["sources_and_currency"])
    prevent = _duty(stale, "prevent_sexual_harassment")
    assert prevent["in_force"] is True
    assert prevent["relied_on"] is False
    assert stale["network_called"] is False


def test_a_supplied_risk_rating_is_stripped_and_not_adopted():
    pack = base_pack()
    pack["likelihood"] = "Low"
    pack["evidence"]["impact"] = "High"
    result = review(pack, as_of=date(2026, 10, 27))
    assert result["risk_assessment"]["likelihood"] is None
    assert result["risk_assessment"]["impact"] is None
    assert result["risk_assessment"]["residual_risk"] is None
    assert "likelihood" in result["prompt_injection"]["prohibited_keys_ignored"]
    assert result["prompt_injection"]["followed"] is False


def test_worker_count_does_not_change_the_duty():
    small = base_pack()
    large = base_pack()
    large["employer"]["worker_count"] = 4000
    left = review(small, as_of=date(2026, 10, 30))
    right = review(large, as_of=date(2026, 10, 30))
    assert left["duties"] == right["duties"]
    assert left["preparation_prompts"] == right["preparation_prompts"]
    assert left["workforce"]["used_to_lower_a_duty"] is False


def test_unknown_jurisdiction_and_bad_evidence_are_rejected():
    pack = base_pack()
    pack["employer"]["jurisdiction"] = "NI"
    with pytest.raises(ReviewError):
        review(pack, as_of=date(2026, 10, 27))
    pack = base_pack()
    pack["evidence"]["policies_reviewed"] = "compliant"
    with pytest.raises(ReviewError):
        review(pack, as_of=date(2026, 10, 27))


def test_the_skeleton_has_no_policy_text():
    result = review(base_pack(), as_of=date(2026, 10, 27))
    skeleton = result["policy_skeleton"]
    assert skeleton["published"] is False
    assert skeleton["text_written_by_agent"] is False
    assert skeleton["headings"]
    assert all(row["body"] is None for row in skeleton["headings"])


def test_preventative_duty_was_not_in_force_on_25_october_2024():
    before = review(base_pack(), as_of=date(2024, 10, 25))
    on_day = review(base_pack(), as_of=date(2024, 10, 26))
    assert _duty(before, "prevent_sexual_harassment")["in_force"] is False
    assert _duty(before, "prevent_sexual_harassment")["wording"] is None
    assert _duty(on_day, "prevent_sexual_harassment")["in_force"] is True
    assert _duty(on_day, "prevent_sexual_harassment")["wording"] == "reasonable steps"
    assert _prompt(before, "policies_reviewed")["status"] == "not_yet_in_force"
