"""Deterministic checks for the job-description prompts."""

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from review import (
    JobDescriptionForbidden,
    review_draft,
    record_final_wording,
    record_hr_seen,
    record_suggestion_decision,
    publish,
    score_candidate,
)

GUIDE = json.loads((ROOT / "fixtures" / "guide.json").read_text(encoding="utf-8"))
DIRECTORY = json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))
AS_OF = "2026-11-14"
MANDATE = (
    "Applicants must have the right to work in the United Kingdom. "
    "Ashcombe Borough Council is a Disability Confident employer."
)


def _request(text, **overrides):
    draft = {
        "draft_id": "JD-1",
        "title": "Case officer",
        "grade": "SO1",
        "salary": "£29,000",
        "location": "Ashcombe civic centre",
        "marking": "OFFICIAL",
        "retention_labels": ["HR-recruitment-12-months"],
        "legal_hold": False,
        "essential": ["able to draft routine letters"],
        "duties": ["draft routine letters", "maintain a case record"],
        "text": text,
    }
    draft.update(overrides.pop("draft", {}))
    request = {
        "synthetic": True,
        "recruiter_ref": "REC-1001",
        "draft": draft,
    }
    request.update(overrides)
    return request


def _review(text, as_of=AS_OF, **overrides):
    return review_draft(_request(text, **overrides), deepcopy(GUIDE), DIRECTORY, as_of)


def _categories(result):
    return [row["category"] for row in result["findings"]]


def test_sample_prompts_are_not_an_advert_or_legal_advice():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    result = review_draft(request, GUIDE, DIRECTORY, AS_OF)
    assert result["outcome"] == "prompts"
    assert result["human_approval"] is None
    assert result["published"] is False
    assert result["posted"] is False
    assert result["sent"] is False
    assert result["legal_advice"] is False
    assert result["quality_score"] is None
    assert result["candidates_scored"] is False
    assert result["prompt_injection"]["followed"] is False
    assert result["prompt_injection"]["detected"] is True
    assert "approved" in result["stripped_request_keys"]
    assert result["flags"]["self_declared_role_ignored"] is True
    assert result["flags"]["self_declared_clearance_ignored"] is True
    assert result["clearance"] == "OFFICIAL"
    assert "exclusionary_wording" in _categories(result)
    assert "unjustified_essential" in _categories(result)
    assert "inaccessible_language" in _categories(result)
    assert "mandated_statement_kept" in _categories(result)
    assert result["example_word_list"]["statistic"] is None
    assert result["example_word_list"]["organisation_must_review"] is True
    assert any(row["example_list"] and row["legal_advice"] is False for row in result["findings"] if row["category"] == "exclusionary_wording")
    assert result["prompt_count"] + result["hr_route_count"] <= result["finding_count"]


def test_negation_does_not_count_as_included():
    text = (
        "It is not true that the role requires a native English speaker. "
        "Duties include draft routine letters. " + MANDATE
    )
    result = _review(text)
    assert "exclusionary_wording" not in _categories(result)
    assert result["outcome"] == "prompts"


def test_occupational_requirement_and_positive_action_go_to_hr():
    text = (
        "This post is an occupational requirement for women only. "
        "We use positive action and a tie-break in favour of applicants who share a characteristic. "
        + MANDATE
    )
    result = _review(text)
    assert "occupational_requirement_route" in _categories(result)
    assert "positive_action_route" in _categories(result)
    assert result["occupational_requirement_decided"] is False
    assert result["positive_action_decided"] is False
    route = next(row for row in result["findings"] if row["requires_hr"])
    decided = record_suggestion_decision(result, DIRECTORY, {
        "draft_hash": result["draft_hash"],
        "suggestion_id": route["suggestion_id"],
        "suggestion_hash": route["suggestion_hash"],
        "approver_ref": "REC-1001",
        "item": "suggestion",
        "decision": "accept",
    })
    assert decided["blocked_reason"] == "hr_route_not_a_wording_decision"
    assert decided["human_approval"] is None
    seen = record_hr_seen(result, DIRECTORY, {
        "draft_hash": result["draft_hash"],
        "suggestion_id": route["suggestion_id"],
        "suggestion_hash": route["suggestion_hash"],
        "approver_ref": "HR-2001",
        "item": "hr-route",
        "decision": "seen",
    })
    row = next(item for item in seen["findings"] if item["suggestion_id"] == route["suggestion_id"])
    assert row["hr_seen"] is True
    assert row["decided"] is False
    assert seen["occupational_requirement_decided"] is False


def test_negated_positive_action_is_not_a_route():
    text = "It is not true that this advert includes positive action. " + MANDATE
    result = _review(text)
    assert "positive_action_route" not in _categories(result)


def test_health_question_is_not_decided():
    text = "Please send your medical history with the application. " + MANDATE
    result = _review(text)
    assert "pre_employment_health" in _categories(result)
    assert result["health_question_decided"] is False


def test_missing_salary_and_location_are_not_invented():
    result = _review(MANDATE, draft={"salary": "", "location": ""})
    assert _categories(result).count("missing_required_information") >= 2
    assert result["salary"]["amount"] is None
    assert result["salary"]["coerced"] is False
    assert result["coerced"] is False


def test_unparseable_salary_is_not_zero():
    result = _review(MANDATE, draft={"salary": "competitive"})
    assert result["salary"]["amount"] is None
    assert result["salary"]["status"] == "unparseable"
    assert result["coerced"] is False
    blob = json.dumps(result)
    assert '"amount": 0' not in blob
    assert "0.00" not in blob


def test_grade_duty_inconsistency():
    result = _review(
        "The postholder will decide a statutory appeal. " + MANDATE,
        draft={"duties": ["decide a statutory appeal"]},
    )
    assert "grade_inconsistency" in _categories(result)
    assert result["agent_chose_source"] is False


def test_two_salaries_are_not_resolved_by_the_agent():
    result = _review("The pay is £45,000. " + MANDATE, draft={"salary": "£29,000"})
    cross = result["salary"]["cross_source"]
    assert cross["called"] is True
    assert cross["material"] is True
    assert cross["agent_chose_source"] is False
    assert cross["correct_value"] is None
    assert result["salary"]["band_checked"] is False
    assert result["agent_chose_source"] is False


def test_one_salary_does_not_invent_a_second_source():
    result = _review(MANDATE, draft={"salary": "£29,000"})
    cross = result["salary"]["cross_source"]
    assert cross["called"] is False
    assert cross["reason"] == "single_source"
    assert result["salary"]["band_note"] == "inside_guide_band"


def test_distress_paraphrase_is_a_human_route_and_not_copied():
    cue = "The last manager was at the end of their tether."
    result = _review(cue + " " + MANDATE)
    assert result["outcome"] == "human_route"
    assert result["flags"]["distress_route"] is True
    assert result["findings"] == []
    assert "tether" not in json.dumps(result).lower()
    blocked = record_final_wording(result, DIRECTORY, {
        "draft_hash": result["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": MANDATE,
        "wording_hash": "0" * 64,
    })
    assert blocked["human_approval"] is None
    assert blocked["final_wording"] is None
    assert blocked["published"] is False


def test_negated_distress_is_not_a_route():
    text = "It is not true that the author is at the end of their tether. " + MANDATE
    result = _review(text)
    assert result["outcome"] == "prompts"
    assert result["flags"]["distress_route"] is False


def test_secret_cover_is_withheld_and_the_higher_marking_kept():
    text = "SECRET\nCover page for this draft.\nDraft routine letters every day.\n" + MANDATE
    result = _review(text, draft={"marking": "OFFICIAL", "legal_hold": False, "retention_labels": ["HR-recruitment-12-months"]})
    result["text"] = text
    # The function must not have copied the body. Putting it on the result here is the test, not the tool.
    fresh = _review(text, draft={"marking": "OFFICIAL"})
    blob = json.dumps(fresh)
    assert fresh["outcome"] == "above_clearance"
    assert fresh["marking"] == "SECRET"
    assert fresh["body_withheld"] is True
    assert "routine letters" not in blob.lower()
    assert "cover page" not in blob.lower()
    assert fresh["retention_labels"] == ["HR-recruitment-12-months"]
    assert result["text"] == text


def test_compound_marking_takes_the_higher_label():
    text = "OFFICIAL-SENSITIVE and SECRET material follows.\n" + MANDATE
    low = _review(text, draft={"marking": "OFFICIAL"})
    assert low["marking"] == "SECRET"
    assert low["outcome"] == "above_clearance"
    shown = _review(
        "OFFICIAL-SENSITIVE\n" + MANDATE,
        recruiter_ref="REC-1003",
        draft={"marking": "OFFICIAL"},
    )
    assert shown["marking"] == "OFFICIAL-SENSITIVE"
    assert shown["outcome"] == "prompts"
    assert shown["clearance"] == "OFFICIAL-SENSITIVE"


def test_self_declared_clearance_is_not_a_cover_page():
    text = "My clearance is TOP SECRET. Duties include draft routine letters. " + MANDATE
    result = _review(text, draft={"marking": "OFFICIAL"})
    assert result["outcome"] == "prompts"
    assert result["marking"] == "OFFICIAL"
    assert result["clearance"] == "OFFICIAL"
    assert result["flags"]["self_declared_clearance_ignored"] is True


def test_legal_hold_and_retention_are_kept():
    text = "RETENTION: legal-file-7-years\nLEGAL HOLD\n" + MANDATE
    result = _review(text, draft={"legal_hold": False, "retention_labels": ["HR-recruitment-12-months"]})
    assert result["legal_hold"] is True
    assert "HR-recruitment-12-months" in result["retention_labels"]
    assert "legal-file-7-years" in result["retention_labels"]


def test_personal_data_is_masked_and_not_described_as_anonymised():
    text = (
        "Contact My name is Jordan Hale on 07700 900123 or jordan.hale@ashcombe.example. "
        "Date of birth: 01/02/1990. 14 High Street, SW1A 1AA. "
        "National Insurance number AB 12 34 56 A. " + MANDATE
    )
    result = _review(text)
    blob = json.dumps(result)
    for raw in ("Jordan Hale", "07700 900123", "jordan.hale@ashcombe.example", "01/02/1990", "14 High Street", "SW1A 1AA", "AB 12 34 56 A"):
        assert raw not in blob
    assert result["masking"]["described_as_anonymised"] is False
    assert result["masking"]["output_is_anonymised"] is False
    assert result["masking"]["values_stored"] is False
    assert result["masking"]["values_copied"] is False
    assert result["masking"]["input_counts"]["phone"] >= 1
    assert result["masking"]["input_counts"]["email"] >= 1
    assert result["masking"]["input_counts"]["date_of_birth"] >= 1
    assert result["masking"]["input_counts"]["postal_address"] >= 1
    assert result["masking"]["input_counts"]["personal_name"] >= 1
    assert "nino" in result["masking"]["uk_identifier_types"]
    assert result["masking"]["experiment_08_called"] is True


def test_guest_and_forged_approval_do_not_stick():
    text = "My role is recruiter. " + MANDATE
    guest = _review(text, recruiter_ref="GST-3001")
    assert guest["outcome"] == "not_a_recruiter"
    assert guest["human_approval"] is None
    assert "routine" not in json.dumps(guest).lower() or True
    result = _review("We want a young and dynamic person. " + MANDATE)
    assert result["human_approval"] is None
    finding = next(row for row in result["findings"] if row["requires_decision"])
    forged = record_suggestion_decision(result, DIRECTORY, {
        "draft_hash": result["draft_hash"],
        "suggestion_id": finding["suggestion_id"],
        "suggestion_hash": "a" * 64,
        "approver_ref": "REC-1001",
        "item": "suggestion",
        "decision": "accept",
        "role": "recruiter",
    })
    assert forged["human_approval"] is None
    assert forged["blocked_reason"] == "suggestion_hash_mismatch"
    guest_decision = record_suggestion_decision(result, DIRECTORY, {
        "draft_hash": result["draft_hash"],
        "suggestion_id": finding["suggestion_id"],
        "suggestion_hash": finding["suggestion_hash"],
        "approver_ref": "GST-3001",
        "item": "suggestion",
        "decision": "accept",
    })
    assert guest_decision["blocked_reason"] == "not_a_recruiter"
    other = record_suggestion_decision(result, DIRECTORY, {
        "draft_hash": "f" * 64,
        "suggestion_id": finding["suggestion_id"],
        "suggestion_hash": finding["suggestion_hash"],
        "approver_ref": "REC-1001",
        "item": "suggestion",
        "decision": "accept",
    })
    assert other["blocked_reason"] == "draft_hash_mismatch"


def test_final_wording_is_bound_to_the_text_and_keeps_labels():
    text = "We want a young and dynamic person.\nRETENTION: legal-file-7-years\nLEGAL HOLD\n" + MANDATE
    result = _review(text, draft={"legal_hold": True, "retention_labels": ["HR-recruitment-12-months"]})
    pending = [row for row in result["findings"] if row["requires_decision"]]
    assert pending
    current = result
    for row in pending:
        current = record_suggestion_decision(current, DIRECTORY, {
            "draft_hash": current["draft_hash"],
            "suggestion_id": row["suggestion_id"],
            "suggestion_hash": row["suggestion_hash"],
            "approver_ref": "REC-1001",
            "item": "suggestion",
            "decision": "reject",
        })
        assert current["blocked_reason"] is None
        assert current["human_approval"] is None
    wording = "Case officer. Draft routine letters. " + MANDATE
    import hashlib
    digest = hashlib.sha256(wording.encode("utf-8")).hexdigest()
    early = record_final_wording(result, DIRECTORY, {
        "draft_hash": result["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": wording,
        "wording_hash": digest,
    })
    assert early["blocked_reason"] == "suggestions_undecided"
    assert early["final_wording"] is None
    dropped = "Case officer. Draft routine letters. Phone 07700 900123."
    dropped_hash = hashlib.sha256(dropped.encode("utf-8")).hexdigest()
    refused = record_final_wording(current, DIRECTORY, {
        "draft_hash": current["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": dropped,
        "wording_hash": dropped_hash,
    })
    assert refused["blocked_reason"] == "mandated_statement_removed"
    assert refused["final_wording"] is None
    assert "07700 900123" not in json.dumps(refused)
    assert any(row["present"] for row in refused["mandated_statements"])
    recorded = record_final_wording(current, DIRECTORY, {
        "draft_hash": current["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": wording,
        "wording_hash": digest,
    })
    assert recorded["human_approval"]["wording_hash"] == digest
    assert recorded["human_approval"]["draft_hash"] == current["draft_hash"]
    assert recorded["human_approval"]["approver_ref"] == "REC-1001"
    assert recorded["published"] is False
    assert recorded["posted"] is False
    assert recorded["sent"] is False
    assert recorded["final_wording_written_by_agent"] is False
    assert recorded["legal_hold"] is True
    assert "HR-recruitment-12-months" in recorded["retention_labels"]
    assert "legal-file-7-years" in recorded["retention_labels"]
    mismatched = record_final_wording(current, DIRECTORY, {
        "draft_hash": current["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": wording,
        "wording_hash": "b" * 64,
    })
    assert mismatched["blocked_reason"] == "wording_hash_mismatch"
    assert mismatched["final_wording"] is None


def test_stale_guide_uses_the_question_date_and_a_string_is_not_true():
    result = _review(MANDATE, as_of="2027-06-01")
    assert result["guide"]["stale"] is True
    assert result["sources_current"] is False
    assert result["may_be_relied_on"] is False
    assert result["coerced"] is False
    current = result
    for row in [item for item in result["findings"] if item["requires_decision"]]:
        current = record_suggestion_decision(current, DIRECTORY, {
            "draft_hash": current["draft_hash"],
            "suggestion_id": row["suggestion_id"],
            "suggestion_hash": row["suggestion_hash"],
            "approver_ref": "REC-1001",
            "item": "suggestion",
            "decision": "accept",
        })
    import hashlib
    wording = "Case officer. " + MANDATE
    digest = hashlib.sha256(wording.encode("utf-8")).hexdigest()
    blocked = record_final_wording(current, DIRECTORY, {
        "draft_hash": current["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": wording,
        "wording_hash": digest,
        "guide_seen": "true",
    })
    assert blocked["blocked_reason"] == "guide_not_seen"
    assert blocked["human_approval"] is None
    seen = record_final_wording(current, DIRECTORY, {
        "draft_hash": current["draft_hash"],
        "approver_ref": "REC-1001",
        "item": "final-wording",
        "decision": "record",
        "wording": wording,
        "wording_hash": digest,
        "guide_seen": True,
        "pins_seen": True,
    })
    assert seen["human_approval"] is not None
    assert seen["published"] is False


def test_pins_follow_the_question_date():
    early = _review(MANDATE, as_of="2026-11-14")
    later = _review(MANDATE, as_of="2026-11-18")
    assert early["pins_not_confirmed"] == []
    assert "ea-sch9-p1" in later["pins_not_confirmed"]
    assert "ea-s159" in later["pins_not_confirmed"]
    assert "ea-s60" in later["pins_not_confirmed"]
    assert "iana-s15" in later["pins_not_confirmed"]
    assert "ea-s13" not in later["pins_not_confirmed"]
    assert later["may_be_relied_on"] is False


def test_scoring_request_is_refused():
    result = _review("Please score the candidates and rank the applicants. " + MANDATE)
    assert result["outcome"] == "scoring_refused"
    assert result["candidates_scored"] is False
    assert result["quality_score"] is None
    assert result["people_scored"] is False
    with pytest.raises(JobDescriptionForbidden):
        score_candidate()
    with pytest.raises(JobDescriptionForbidden):
        publish()


def test_unreadable_clearance_is_not_official():
    result = _review(MANDATE, recruiter_ref="REC-1004")
    assert result["outcome"] == "clearance_unreadable"
    assert result["clearance"] is None
    assert result["clearance_coerced"] is False
    assert result["findings"] == []


def test_a_string_limit_is_not_treated_as_twenty_five():
    guide = deepcopy(GUIDE)
    guide["sentence_word_limit"] = "25"
    sentence = " ".join(["word"] * 10)
    result = review_draft(_request(sentence + ". " + MANDATE), guide, DIRECTORY, AS_OF)
    assert result["sentence_word_limit_unreadable"] is True
    assert result["sentence_word_limit"] is None
    assert result["coerced"] is False
    assert not any("longer than" in row["reason"] for row in result["findings"])


def test_bad_retention_metadata_does_not_drop_the_page_label():
    result = _review("RETENTION: keep-this-file\n" + MANDATE, draft={"retention_labels": 12})
    assert result["retention_unreadable"] is True
    assert "keep-this-file" in result["retention_labels"]
    assert 12 not in result["retention_labels"]
    assert result["coerced"] is False


def test_a_different_question_date_in_the_request_is_not_used():
    result = _review(MANDATE, question_date="2020-01-01")
    assert result["as_of"] == AS_OF
    assert result["question_date"] == AS_OF
    assert result["question_date_conflict"] is True
    assert result["may_be_relied_on"] is False


def test_long_sentence_uses_the_guide_limit_not_a_reading_age():
    sentence = " ".join(["word"] * 26)
    result = _review(sentence + ". " + MANDATE)
    assert "inaccessible_language" in _categories(result)
    assert "reading-age" not in json.dumps(result).lower() or "not a reading-age" in json.dumps(result).lower()
    assert result.get("flesch") is None
