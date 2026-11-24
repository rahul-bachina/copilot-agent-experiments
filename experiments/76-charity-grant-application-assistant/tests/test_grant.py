"""The draft cites pinned rows and does not paper over a gap."""

import json
from pathlib import Path

from src.grant import NotSynthetic, prepare_application

ROOT = Path(__file__).resolve().parents[1]


def _sample(as_of: str = "2026-11-14"):
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    return prepare_application(request, as_of=as_of)


def test_sample_routes_and_does_not_leak():
    result = _sample()
    blob = json.dumps(result)
    assert result["label"].startswith("GRANT APPLICATION DRAFT FOR THE NAMED APPLICANT")
    assert result["catalogue_id"] == "V007"
    assert result["autonomy"] == "A1"
    assert result["outcome"] == "route_to_human"
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert result["submitted"] is False
    assert result["funder_contacted"] is False
    assert result["sent"] is False
    assert result["instructions_followed"] is False
    assert result["approval_marker_trusted"] is False
    assert result["caller_brief_applied"] is False
    assert result["invented_figures"] is False
    assert result["marked_acceptable"] is False
    assert result["papered_over"] is False
    assert result["coerced"] is False
    assert result["marking"]["applied"] == "SECRET"
    assert result["distress"]["cue_copied"] is False
    assert result["secret_body_copied"] is False
    assert result["legal_hold"] is True
    assert "do not destroy while the hold applies" in result["retention"]
    assert "safeguarding note: do not destroy" in result["retention"]
    for leak in (
        "07700900111",
        "hale@example.test",
        "Mrs Hale",
        "14 Harbour Street",
        "02/03/1954",
        "frightened",
        "kill themselves",
        "TOP SECRET",
        "9999",
        "National High Street Bank",
        "changed my life",
    ):
        assert leak not in blob
    assert result["masking"]["body_copied"] is False
    assert result["masking"]["described_as_anonymised"] is False
    assert result["masking"]["counts"]["phone"] >= 1
    assert result["masking"]["counts"]["email"] >= 1
    assert result["masking"]["counts"]["date_of_birth"] >= 1
    assert result["masking"]["counts"]["postal_address"] >= 1
    assert result["masking"]["counts"]["personal_name"] >= 1
    assert result["intake"]["files_confirmed"] is False
    assert result["intake"]["purpose_confirmed"] is False
    assert result["uk_identifiers"]["output_is_anonymised"] is False
    assert result["uk_identifiers"]["values_stored"] is False


def test_gaps_are_visible_and_figures_are_sourced():
    result = _sample()
    by_id = {row["criterion_id"]: row for row in result["eligibility"]}
    assert by_id["EL-MATCH"]["status"] == "not_met"
    assert by_id["EL-MATCH"]["gap"] is True
    assert by_id["EL-SAFE"]["status"] == "not_met"
    assert by_id["EL-SAFE"]["policy_date"] == "2025-01-15"
    assert by_id["EL-INC"]["status"] == "met"
    assert by_id["EL-INC"]["value"] == 186400
    assert by_id["EL-INC"]["source_ref"] == "charity.income_gbp"
    assert by_id["EL-REG"]["status"] == "met"
    match = next(claim for claim in result["claims"] if claim["claim_id"] == "C-MATCH")
    assert match["status"] == "gap_not_papered"
    meals = next(row for row in result["impact_report"]["figures"] if row["source_ref"] == "ME-OUT-01")
    assert meals["value"] == 14820
    small = next(row for row in result["impact_report"]["figures"] if row["source_ref"] == "ME-BEN-SMALL")
    assert small["value"] is None
    assert small["suppressed"] is True
    assert small["value_copied"] is False
    bad = next(row for row in result["impact_report"]["figures"] if row["source_ref"] == "ME-BEN-BAD")
    assert bad["value"] is None
    assert bad["unparseable"] is True
    assert bad["coerced"] is False
    assert result["impact_report"]["aggregate_includes_suppressed_cells"] is False
    assert result["impact_report"]["figures_invented"] is False
    for answer in result["answers"]:
        assert answer["within_limit"] is True
        assert answer["word_count"] <= answer["word_limit"]
    q5 = next(answer for answer in result["answers"] if answer["question_id"] == "Q5")
    assert "not met" in q5["text"]
    budget = next(item for item in result["attachments"] if item["attachment_id"] == "ATT-BUDGET")
    assert budget["gap"] is True
    assert budget["satisfies_eligibility"] is False
    safe = next(item for item in result["attachments"] if item["attachment_id"] == "ATT-SAFE")
    assert safe["present"] is True
    assert safe["satisfies_eligibility"] is False


def test_caller_brief_is_not_applied():
    result = _sample()
    assert result["deadline_plan"]["deadline"] == "2027-03-31"
    assert result["deadline_plan"]["unparseable_offset"] is True
    assert any(row["field"] == "deadline" and row["applied"] is False for row in result["brief_diff"])
    assert any(row["field"] == "income_under_gbp" and row["applied"] is False for row in result["brief_diff"])
    assert result["criteria_applied"] is False
    assert "biased_criteria" in result["prompt_injection"]["signals"]
    assert result["eligibility_statement_supports_registered_charity"] is False
    assert result["role_in_text_trusted"] is False
    assert "human_approval" in result["ignored_request_keys"]


def test_past_deadline_uses_the_question_date():
    result = _sample("2027-04-01")
    assert result["deadline_plan"]["past"] is True
    assert result["deadline_plan"]["question_date"] == "2027-04-01"
    assert result["as_of"] == "2027-04-01"
    assert result["coerced"] is False
    assert result["sources_current"] is True
    assert "dates_seen" in result["required_acknowledgements"]


def test_stale_review_date_is_not_relied_on():
    result = _sample("2027-10-01")
    assert result["sources_current"] is False
    assert result["may_be_relied_on"] is False
    assert result["deadline_plan"]["past"] is True
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert "sources_seen" in result["required_acknowledgements"]


def test_unreadable_question_date_is_not_coerced():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    result = prepare_application(request, as_of="soon")
    assert result["outcome"] == "unreadable_date"
    assert result["coerced"] is False
    assert result["human_approval"] is None
    ambiguous = prepare_application(request, as_of="03/04/2026")
    assert ambiguous["outcome"] == "unreadable_date"
    assert ambiguous["date_reading"]["ambiguous"] is True
    assert ambiguous["coerced"] is False


def test_same_inputs_produce_the_same_hash():
    first = _sample()
    second = _sample()
    assert first["content_hash"] == second["content_hash"]


def test_not_synthetic_is_refused():
    try:
        prepare_application({"synthetic": False}, as_of="2026-11-14")
    except NotSynthetic:
        return
    raise AssertionError("a live record should be refused")


def test_guest_and_trustee_are_not_the_applicant():
    request = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
    request["applicant_ref"] = "GST-7603"
    guest = prepare_application(request, as_of="2026-11-14")
    assert guest["outcome"] == "needs_named_applicant"
    assert guest["answers"] == []
    assert guest["impact_report"]["figures"] == []
    request["applicant_ref"] = "TRS-7602"
    trustee = prepare_application(request, as_of="2026-11-14")
    assert trustee["applicant_on_directory"] is False
    assert trustee["outcome"] == "needs_named_applicant"


def test_quotes_are_the_opened_sentences():
    result = _sample()
    texts = [quote["text"] for quote in result["uk_context"]["quotes"]]
    assert any(text.startswith("The charity trustees of a charity must have regard") for text in texts)
    assert any("data minimisation" in text for text in texts)
    assert any(text.startswith("You and your co-trustees must make sure") for text in texts)
    assert result["uk_context"]["not_a_legal_opinion"] is True
