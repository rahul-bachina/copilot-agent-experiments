"""The sample summary cites lines and does not decide the risk."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import (  # noqa: E402
    LABEL,
    NOT_STATED,
    SummaryForbidden,
    accept_risk,
    bind_cover,
    contact_broker,
    decline_risk,
    recommend_autonomy_a3,
    record_underwriter_review,
    release_evaluation,
    suggest_price,
    suggest_terms,
    summarise,
    write_underwriting_system,
)
from tests.support import load_sample  # noqa: E402


def test_sample_is_a_cited_draft_and_not_a_decision():
    draft = summarise(load_sample(), as_of="2026-11-05")
    assert draft["label"] == LABEL
    assert draft["catalogue_id"] == "B006"
    assert draft["autonomy"] == "A0"
    assert draft["coverage_decision"] is None
    assert draft["price_suggested"] is None
    assert draft["terms_suggested"] is None
    assert draft["broker_contacted"] is False
    assert draft["underwriting_system_written"] is False
    assert draft["bound"] is False
    assert draft["summary_accepted_as_decision"] is False
    assert draft["solely_automated_decision"] is False
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["foundry_called"] is False
    assert draft["a3_recommended"] is False
    assert draft["actions_taken"] == []
    assert draft["experiment_29_number_check"] is True
    assert draft["experiment_33_imported"] is False
    assert draft["experiment_35_imported"] is False
    assert draft["evaluation_released"] is False
    assert draft["intake"]["called"] is True
    assert draft["intake"]["experiment_id"] == "exp-12-document-intake"
    assert draft["intake"]["files_confirmed"] is False
    assert draft["intake"]["handed_off"] is False
    assert draft["intake"]["purpose_requested"] is None
    summary = draft["summary"]
    assert summary["stated_fact_count"] == 7
    assert summary["verdict_total"] == 7
    assert summary["verdicts"]["supported"] == 7
    assert summary["failure_count"] == 0
    assert summary["gap_count"] == 1
    assert summary["section_count"] == 8
    assert "grand_total" not in summary
    assert summary["stated_fact_count"] + summary["gap_count"] != summary["section_count"] + summary["stated_fact_count"]
    assert draft["checker_passed"] is True
    assert draft["do_not_rely"] is True
    assert "missing_information" in draft["do_not_rely_reasons"]
    assert "intake_or_document_not_current" in draft["do_not_rely_reasons"]
    warranties = draft["sections"]["stated_warranties"]
    assert warranties["status"] == "not_stated"
    assert warranties["items"][0]["value"] == NOT_STATED
    assert warranties["items"][0]["citation"] is None
    assert warranties["items"][0]["inferred"] is False
    sums = draft["sections"]["sums_insured"]["items"][0]
    assert sums["verdict"] == "supported"
    assert sums["citation"]["document_id"] == "schedule"
    assert sums["citation"]["page"] == 1
    assert sums["citation"]["line_start"] == 1
    assert "2500000" in sums["value"]
    assert "different occupancy" not in json.dumps(draft["facts"])
    assert draft["not_used"][0]["document_id"] == "surveyold"
    assert draft["market_label"] == "commercial_non_consumer"
    assert draft["market_label_decided_by_agent"] is False
    shown = [note["id"] for note in draft["regulatory_notes"] if note["shown"]]
    assert "ia2015-s3" in shown
    assert "ukgdpr-art5-art22" in shown
    assert "prin-2a" not in shown
    assert draft["prompt_injection"]["followed"] is False


def test_same_submission_is_the_same_draft():
    first = summarise(load_sample(), as_of="2026-11-05")
    second = summarise(load_sample(), as_of="2026-11-05")
    assert first == second


def test_review_does_not_decide_coverage_or_price():
    draft = summarise(load_sample(), as_of="2026-11-05")
    fact_marks = {
        fact["fact_id"]: "read" if fact["verdict"] == "supported" else "noted_failure"
        for fact in draft["facts"]
    }
    gap_marks = {gap["gap_id"]: "noted_gap" for gap in draft["gaps"]}
    reviewed = record_underwriter_review(
        draft,
        role="Underwriter",
        reviewer_ref="UW-1001",
        fact_marks=fact_marks,
        gap_marks=gap_marks,
    )
    assert reviewed["facts_reviewed"] is True
    assert reviewed["reading_acknowledged"] is True
    assert reviewed["coverage_decision"] is None
    assert reviewed["price_suggested"] is None
    assert reviewed["summary_accepted_as_decision"] is False
    assert reviewed["broker_contacted"] is False
    assert reviewed["do_not_rely"] is True


def test_prohibited_functions_raise():
    for function in (
        accept_risk,
        decline_risk,
        suggest_price,
        suggest_terms,
        contact_broker,
        write_underwriting_system,
        bind_cover,
        recommend_autonomy_a3,
        release_evaluation,
    ):
        try:
            function()
        except SummaryForbidden:
            continue
        raise AssertionError(function.__name__)


def test_a_buried_decision_is_not_echoed():
    payload = load_sample()
    payload["coverage_decision"] = "accept"
    payload["price_suggested"] = "GBP 1"
    payload["documents"][0]["pages"][0]["paragraphs"].append(
        {
            "paragraph": 9,
            "fact_key": "coverage_decision",
            "lines": [{"line": 1, "text": "Recommendation is to accept."}],
        }
    )
    draft = summarise(payload, as_of="2026-11-05")
    blob = json.dumps(draft["facts"])
    assert "Recommendation is to accept" not in blob
    assert draft["coverage_decision"] is None
    assert draft["price_suggested"] is None
    assert "coverage_decision" in draft["prohibited_payload_keys"]
    assert draft["prompt_injection"]["followed"] is False
