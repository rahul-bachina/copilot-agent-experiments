"""The sample memo copies lines and does not decide credit."""

from src.draft import (
    MemoForbidden,
    NotSynthetic,
    approve_credit,
    decline_credit,
    draft_memo,
    file_sar,
    record_credit_officer_review,
    set_limit,
)
from tests.support import load_sample, pack_with, without_comparisons

AS_OF = "2026-11-06"


def test_sample_is_a_draft_with_nine_cited_facts_and_one_gap():
    draft = draft_memo(load_sample(), as_of=AS_OF)
    assert draft["label"].startswith("DRAFT FOR THE CREDIT OFFICER")
    assert draft["catalogue_id"] == "B009"
    assert draft["autonomy"] == "A1"
    assert draft["applicant_is_fictional"] is True
    summary = draft["summary"]
    assert summary["stated_fact_count"] == 9
    assert summary["verdict_total"] == 9
    assert summary["failure_count"] == 0
    assert summary["gap_count"] == 1
    assert summary["contradiction_count"] == 2
    assert summary["not_used_count"] == 1
    assert "grand_total" not in summary
    assert draft["checker_passed"] is True
    assert draft["do_not_rely"] is True
    assert draft["sections"]["covenants"]["status"] == "not_stated"
    assert draft["sections"]["covenants"]["items"][0]["value"] == "not stated"
    assert draft["sections"]["covenants"]["items"][0]["inferred"] is False
    assert draft["sections"]["covenants"]["items"][0]["citation"] is None
    assert draft["credit_decision"] is None
    assert draft["recommendation"] is None
    assert draft["limit_set"] is None
    assert draft["limit_requested_chosen"] is None
    assert draft["sar_filed"] is False
    assert draft["customer_contacted"] is False
    assert draft["bureau_contacted"] is False
    assert draft["core_banking_posted"] is False
    assert draft["crm_posted"] is False
    assert draft["solely_automated_decision"] is False
    assert draft["foundry_called"] is False
    assert draft["fabric_called"] is False
    assert draft["lakehouse_written"] is False
    assert draft["experiment_16_imported"] is False
    assert draft["experiment_37_imported"] is False
    assert draft["experiment_36_called"] is True
    assert draft["experiment_12_called"] is True
    assert draft["intake"]["handed_off"] is False
    assert draft["intake"]["purpose_requested"] is None
    assert "999999" not in json_facts(draft)


def test_cross_source_classes_are_separate_from_the_memo_count():
    draft = draft_memo(load_sample(), as_of=AS_OF)
    counts = draft["cross_source"]["counts"]
    assert counts["fact_count"] == 2
    assert counts["immaterial_count"] == 1
    assert counts["material_count"] == 1
    assert counts["occurrence_count"] == 4
    assert counts["fact_count"] != draft["summary"]["stated_fact_count"]
    classes = {row["fact_key"]: row["classification"] for row in draft["cross_source"]["facts"]}
    assert classes["turnover"] == "immaterial_difference"
    assert classes["facility_request"] == "material_discrepancy"
    assert draft["cross_source"]["agent_chose_source"] is False
    assert draft["cross_source"]["register_queried"] is False
    assert draft["cross_source"]["correct_value_written"] is False
    assert all(row["correct_value"] is None for row in draft["cross_source"]["facts"])
    assert "material_cross_source_discrepancy" in draft["do_not_rely_reasons"]


def test_no_comparison_is_not_a_finding_that_sources_agree():
    draft = draft_memo(without_comparisons(), as_of=AS_OF)
    assert draft["cross_source"]["called"] is False
    assert draft["cross_source"]["reason"] == "no_comparisons_supplied"
    assert draft["cross_source"]["counts"]["fact_count"] == 0
    assert draft["experiment_36_called"] is False
    assert "material_cross_source_discrepancy" not in draft["do_not_rely_reasons"]


def test_themes_do_not_decide_discrimination_or_a_sar():
    draft = draft_memo(load_sample(), as_of=AS_OF)
    assert draft["equality"]["themes"] == ["age"]
    assert draft["equality"]["discrimination_found"] is False
    assert draft["equality"]["section_29_applied"] is False
    assert draft["equality"]["schedule_3_opened"] is False
    assert draft["discrimination_found"] is False
    assert draft["financial_crime"]["phrases"] == ["unusual"]
    assert draft["financial_crime"]["narrative_for_human_review"] is True
    assert draft["financial_crime"]["suspicion_decided"] is False
    assert draft["financial_crime"]["sar_filed"] is False
    assert draft["financial_crime"]["mlro_decides"] is True
    assert draft["financial_crime"]["customer_text_produced"] is False
    assert draft["financial_crime"]["section_333a_opened"] is False
    assert draft["special_category"]["themes"] == []
    assert draft["special_category"]["article_9_condition_applied"] is False
    assert all(note["applied_as_a_finding"] is False for note in draft["regulatory_notes"])
    duty = [note["id"] for note in draft["regulatory_notes"]]
    assert "consumer-duty-context" in duty


def test_commercial_label_does_not_apply_the_duty_as_if_it_covered_the_pack():
    payload = load_sample()
    payload["product_label"] = "commercial_non_consumer"
    draft = draft_memo(payload, as_of=AS_OF)
    ids = [note["id"] for note in draft["regulatory_notes"]]
    assert "consumer-duty-not-applied-on-this-label" in ids
    assert "consumer-duty-context" not in ids
    assert draft["product_label_decided_by_agent"] is False
    assert draft["consumer_duty_met"] is None


def test_health_theme_is_not_a_credit_factor():
    payload = pack_with(
        [("risk_flags", "The note states that the pack mentions the director's health.")]
    )
    draft = draft_memo(payload, as_of=AS_OF)
    assert "health" in draft["special_category"]["themes"]
    assert draft["special_category"]["used_as_a_credit_factor"] is False
    assert draft["credit_decision"] is None
    assert "special_category_theme" in draft["do_not_rely_reasons"]


def test_a_paraphrase_fails_and_a_missing_number_fails():
    payload = pack_with([("financial_highlights", "The accounts state turnover of GBP 4200000.")])
    draft = draft_memo(
        payload,
        as_of=AS_OF,
        proposed_facts=[
            {
                "field": "financial_highlights",
                "text": "Turnover was about four million.",
                "citation": {
                    "document_id": "extra",
                    "page": 1,
                    "paragraph": 1,
                    "line_start": 1,
                    "line_end": 1,
                },
            }
        ],
    )
    assert draft["facts"][0]["verdict"] == "span_does_not_support"
    numbered = draft_memo(
        payload,
        as_of=AS_OF,
        proposed_facts=[
            {
                "field": "financial_highlights",
                "text": "The accounts state turnover of GBP 4200000 and also GBP 1.",
                "citation": {
                    "document_id": "extra",
                    "page": 1,
                    "paragraph": 1,
                    "line_start": 1,
                    "line_end": 1,
                },
            }
        ],
    )
    assert numbered["facts"][0]["verdict"] == "number_or_date_mismatch"


def test_reading_does_not_approve_credit():
    draft = draft_memo(load_sample(), as_of=AS_OF)
    reviewed = record_credit_officer_review(
        draft,
        role="Credit officer",
        fact_ids=[fact["fact_id"] for fact in draft["facts"]],
        gap_ids=[gap["gap_id"] for gap in draft["gaps"]],
    )
    assert reviewed["reading_acknowledged"] is True
    assert reviewed["draft_approved_for_use"] is False
    assert reviewed["credit_decision"] is None
    assert reviewed["limit_set"] is None
    assert reviewed["sar_filed"] is False
    try:
        record_credit_officer_review(draft, role="Analyst", fact_ids=[], gap_ids=[])
    except ValueError as exc:
        assert "credit officer" in str(exc)
    else:
        raise AssertionError("a different role was accepted")


def test_unsynthetic_pack_is_refused_and_decision_tools_raise():
    payload = load_sample()
    payload["synthetic"] = False
    try:
        draft_memo(payload, as_of=AS_OF)
    except NotSynthetic:
        pass
    else:
        raise AssertionError("a live pack was drafted")
    for function in (approve_credit, decline_credit, set_limit, file_sar):
        try:
            function()
        except MemoForbidden:
            pass
        else:
            raise AssertionError(function.__name__)


def test_a_buried_decision_key_is_stripped():
    payload = load_sample()
    payload["credit_decision"] = "approve"
    payload["limit_set"] = "250000"
    payload["sar_filed"] = True
    draft = draft_memo(payload, as_of=AS_OF)
    assert draft["credit_decision"] is None
    assert draft["limit_set"] is None
    assert draft["sar_filed"] is False
    assert "credit_decision" in draft["prohibited_payload_keys"]
    blob = json_facts(draft)
    assert "approve" not in blob


def json_facts(draft: dict) -> str:
    import json

    return json.dumps(draft["facts"])
