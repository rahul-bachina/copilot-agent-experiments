"""Pinpoint support, number boundaries, gaps, and contradictions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import NOT_STATED, summarise  # noqa: E402
from tests.support import load_sample, submission_with  # noqa: E402

AS_OF = "2026-11-05"
SPAN = {
    "document_id": "schedule",
    "page": 1,
    "paragraph": 1,
    "line_start": 1,
    "line_end": 1,
}


def _proposed(text: str, citation: dict | None = SPAN) -> dict:
    payload = load_sample()
    fact = {"field": "sums_insured", "text": text, "citation": citation}
    return summarise(payload, as_of=AS_OF, proposed_facts=[fact])


def test_a_changed_number_fails_before_the_span_check():
    draft = _proposed("The schedule states a building sum insured of GBP 9999999.")
    fact = draft["facts"][0]
    assert fact["verdict"] == "number_or_date_mismatch"
    assert "span_does_not_support" in fact["other_failures"]
    assert draft["summary"]["failure_count"] == 1
    assert draft["summary"]["verdict_total"] == 1
    assert draft["coverage_decision"] is None


def test_a_paraphrase_with_the_same_number_fails_the_span():
    draft = _proposed("Building sum insured GBP 2500000, in other words.")
    fact = draft["facts"][0]
    assert fact["verdict"] == "span_does_not_support"
    assert fact["other_failures"] == []


def test_a_missing_citation_is_one_verdict():
    draft = _proposed("The schedule states a building sum insured of GBP 2500000.", citation=None)
    assert draft["facts"][0]["verdict"] == "citation_missing"
    assert draft["facts"][0]["other_failures"] == []


def test_an_absent_field_is_not_stated_and_not_inferred():
    payload = submission_with(
        [("risk_description", "The proposal describes a commercial warehouse used to store dry goods.")]
    )
    draft = summarise(payload, as_of=AS_OF)
    assert draft["sections"]["sums_insured"]["status"] == "not_stated"
    assert draft["sections"]["sums_insured"]["items"][0]["value"] == NOT_STATED
    assert draft["sections"]["loss_history"]["items"][0]["inferred"] is False
    assert draft["summary"]["gap_count"] == 7
    assert draft["summary"]["stated_fact_count"] == 1
    assert "grand_total" not in draft["summary"]


def test_two_sums_are_both_shown_and_not_resolved():
    payload = submission_with(
        [("sums_insured", "The schedule states a building sum insured of GBP 2500000.")]
    )
    second = {
        "document_id": "schedule-b",
        "file_id": "schedule-b",
        "title": "Second schedule",
        "status": "current",
        "reviewed_on": "2026-10-21",
        "pages": [
            {
                "page": 1,
                "paragraphs": [
                    {
                        "paragraph": 1,
                        "fact_key": "sums_insured",
                        "lines": [
                            {
                                "line": 1,
                                "text": "The schedule states a building sum insured of GBP 1800000.",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    payload["files"].append(
        {
            "file_id": "schedule-b",
            "filename": "schedule-b.txt",
            "media_type": "text/plain",
            "document_date": "2026-10-21",
            "content": "Policy schedule\nThe schedule states a building sum insured of GBP 1800000.\n",
        }
    )
    payload["documents"].append(second)
    draft = summarise(payload, as_of=AS_OF)
    assert draft["summary"]["contradiction_count"] == 1
    assert draft["contradictions"][0]["resolved"] is False
    assert draft["contradictions"][0]["chosen_value"] is None
    assert draft["summary"]["stated_fact_count"] == 2
    assert draft["price_suggested"] is None


def test_retail_shows_the_consumer_duty_note_and_does_not_decide_it():
    payload = submission_with(
        [("risk_description", "The proposal describes a commercial warehouse used to store dry goods.")]
    )
    payload["market"] = "retail"
    draft = summarise(payload, as_of=AS_OF)
    shown = {note["id"]: note["shown"] for note in draft["regulatory_notes"]}
    assert shown["prin-2a"] is True
    assert shown["ia2015-s3"] is False
    assert shown["prin-2a-not-applied"] is False
    assert draft["coverage_decision"] is None
    assert draft["market_label_decided_by_agent"] is False


def test_an_omitted_market_stays_not_stated():
    payload = submission_with(
        [("risk_description", "The proposal describes a commercial warehouse used to store dry goods.")]
    )
    del payload["market"]
    draft = summarise(payload, as_of=AS_OF)
    assert draft["market_label"] == "not_stated"
    assert "market_not_stated" in draft["do_not_rely_reasons"]
    shown = {note["id"]: note["shown"] for note in draft["regulatory_notes"]}
    assert shown["ia2015-s3"] is False
    assert shown["prin-2a"] is False
    assert shown["prin-2a-not-applied"] is True


def test_an_unrecognised_market_is_not_treated_as_commercial():
    payload = submission_with(
        [("risk_description", "The proposal describes a commercial warehouse used to store dry goods.")]
    )
    payload["market"] = "lloyds"
    draft = summarise(payload, as_of=AS_OF)
    assert draft["market_label"] == "unrecognised"
    assert "market_unrecognised" in draft["do_not_rely_reasons"]
    shown = {note["id"]: note["shown"] for note in draft["regulatory_notes"]}
    assert shown["ia2015-s3"] is False
