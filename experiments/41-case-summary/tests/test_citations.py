"""Pinpoint support is a contiguous copy of the cited lines."""

from src.summarise import summarise
from tests.support import case, event, four_events

AS_OF = "2026-11-09"


def test_extracted_sentences_are_supported_copies():
    draft = summarise(case(four_events()), AS_OF)
    assert draft["checker_passed"] is True
    assert draft["do_not_rely"] is False
    assert draft["summary"]["sentence_count"] == 4
    assert draft["summary"]["failure_count"] == 0
    assert draft["sentences"][0]["citation"]["event_id"] == "E1"
    assert draft["sentences"][0]["citation"]["paragraph"] == 1
    assert draft["sentences"][0]["citation"]["line_start"] == 1
    assert draft["sentences"][0]["text"] == "The tenant reported a leaking kitchen tap."
    assert draft["case_outcome"] is None
    assert draft["accuracy_checked"] is False
    assert draft["human_approval"] is None


def test_a_paraphrase_fails_even_when_it_is_about_the_same_event():
    draft = summarise(
        case(four_events()),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "fact_key": "what_happened",
                "text": "The tenant mentioned a problem with the tap.",
                "citation": {"event_id": "E1", "paragraph": 1, "line_start": 1, "line_end": 1},
            }
        ],
    )
    assert draft["sentences"][0]["verdict"] == "span_does_not_support"
    assert draft["checker_passed"] is False
    assert draft["summary"]["failure_count"] == 1


def test_missing_citation_is_one_failure_and_later_failures_are_not_added():
    draft = summarise(
        case(four_events()),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "fact_key": "what_happened",
                "text": "Contact the customer.",
                "citation": None,
            }
        ],
    )
    sentence = draft["sentences"][0]
    assert sentence["verdict"] == "citation_missing"
    assert "prohibited_action" in sentence["other_failures"]
    assert draft["summary"]["sentence_count"] == 1
    assert draft["summary"]["verdict_total"] == 1
    assert draft["summary"]["failure_count"] == 1
    assert sum(draft["summary"]["verdicts"].values()) == 1


def test_incomplete_pinpoint_and_unknown_event():
    incomplete = summarise(
        case(four_events()),
        AS_OF,
        proposed_sentences=[
            {
                "text": "The tenant reported a leaking kitchen tap.",
                "fact_key": "what_happened",
                "citation": {"event_id": "E1", "paragraph": 1},
            }
        ],
    )
    assert incomplete["sentences"][0]["verdict"] == "pinpoint_incomplete"
    missing = summarise(
        case(four_events()),
        AS_OF,
        proposed_sentences=[
            {
                "text": "The tenant reported a leaking kitchen tap.",
                "fact_key": "what_happened",
                "citation": {"event_id": "E9", "paragraph": 1, "line_start": 1, "line_end": 1},
            }
        ],
    )
    assert missing["sentences"][0]["verdict"] == "citation_not_in_case"


def test_two_lines_are_one_contiguous_sentence():
    events = four_events()
    events[0] = event(
        "E1",
        "2026-10-20",
        "what_happened",
        "unused",
        paragraphs=[
            {
                "paragraph": 1,
                "fact_key": "what_happened",
                "lines": [
                    "The tenant reported a leaking kitchen tap.",
                    "The leak is on the ground floor.",
                ],
            }
        ],
    )
    del events[0]["text"]
    draft = summarise(case(events), AS_OF)
    matched = next(row for row in draft["sentences"] if row["fact_key"] == "what_happened")
    assert matched["verdict"] == "supported"
    assert matched["text"] == "The tenant reported a leaking kitchen tap. The leak is on the ground floor."
    assert matched["citation"]["line_end"] == 2
