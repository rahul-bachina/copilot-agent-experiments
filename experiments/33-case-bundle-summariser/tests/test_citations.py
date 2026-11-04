"""Pinpoint support. A sentence stands only if the cited lines contain it."""

from src.summarise import summarise
from tests.support import BLUE, BELL, bundle, blue_document, cite, paragraph, document


AS_OF = "2026-11-04"


def test_extractive_sentences_quote_the_span_and_carry_a_pinpoint():
    draft = summarise(
        bundle([blue_document()], expected=["sighting", "item"]),
        AS_OF,
    )
    assert draft["shown_source"] == "extractive"
    assert draft["checker_passed"] is True
    assert draft["summary"]["sentence_count"] == 2
    assert draft["summary"]["failure_count"] == 0
    assert draft["summary"]["verdict_total"] == 2
    by_key = {row["fact_key"]: row for row in draft["sentences"]}
    assert by_key["sighting"]["text"] == BLUE
    assert by_key["sighting"]["citation"] == cite("SYN-NOTE-01", 1)
    assert by_key["item"]["text"] == BELL
    assert by_key["item"]["citation"]["paragraph"] == 2
    assert draft["case_outcome"] is None
    assert draft["disclosure_decision"] is None
    assert draft["credibility_finding"] is None
    assert draft["summary_accepted_as_reading_aid"] is False
    assert draft["outcome_recommended"] is False


def test_hallucinated_document_id_fails():
    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "text": BLUE,
                "fact_key": "sighting",
                "citation": cite("SYN-GHOST-99", 1),
            }
        ],
    )
    assert draft["sentences"][0]["verdict"] == "citation_not_in_bundle"
    assert draft["checker_passed"] is False
    assert draft["summary"]["failure_count"] == 1
    assert draft["summary"]["verdict_total"] == 1
    assert draft["case_outcome"] is None


def test_hallucinated_page_fails_even_when_the_words_exist_elsewhere():
    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "text": BLUE,
                "fact_key": "sighting",
                "citation": cite("SYN-NOTE-01", 1, page=9),
            }
        ],
    )
    assert draft["sentences"][0]["verdict"] == "pinpoint_not_in_document"
    assert draft["checker_passed"] is False


def test_changed_colour_is_not_supported_by_the_cited_span():
    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "text": BLUE.replace("blue", "red"),
                "fact_key": "sighting",
                "citation": cite("SYN-NOTE-01", 1),
            }
        ],
    )
    row = draft["sentences"][0]
    assert row["verdict"] == "span_does_not_support"
    assert row["other_failures"] == []
    assert draft["summary"]["failure_count"] == 1


def test_missing_citation_fails_and_is_not_counted_twice():
    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[{"sentence_id": "P1", "text": BLUE, "fact_key": "sighting"}],
    )
    row = draft["sentences"][0]
    assert row["verdict"] == "citation_missing"
    assert row["other_failures"] == []
    assert draft["summary"]["failure_count"] == 1
    assert draft["summary"]["other_failure_mentions"] == 0


def test_incomplete_pinpoint_fails():
    citation = cite("SYN-NOTE-01", 1)
    del citation["line_end"]
    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[{"sentence_id": "P1", "text": BLUE, "citation": citation}],
    )
    assert draft["sentences"][0]["verdict"] == "pinpoint_incomplete"


def test_a_verbatim_proposed_sentence_passes_and_is_still_not_accepted():
    draft = summarise(
        bundle([blue_document()], expected=["sighting", "item"]),
        AS_OF,
        proposed_sentences=[
            {"sentence_id": "P1", "text": BLUE, "fact_key": "sighting", "citation": cite("SYN-NOTE-01", 1)}
        ],
    )
    assert draft["shown_source"] == "proposed"
    assert draft["checker_passed"] is True
    assert draft["summary"]["sentence_count"] == 1
    assert draft["summary"]["extractive_sentence_count"] == 2
    assert draft["summary"]["sentence_count"] != draft["summary"]["extractive_sentence_count"]
    assert draft["summary"]["gap_count"] == 1
    assert draft["summary_accepted_as_reading_aid"] is False
    assert draft["do_not_rely"] is True


def test_multi_line_span_is_quoted_in_full():
    note = document(
        "SYN-NOTE-LINES",
        [
            paragraph(
                1,
                "On 12 August 2026 synthetic witness W-01 saw a blue bicycle.",
                "sighting",
                extra_lines=[line_two()],
            )
        ],
    )
    draft = summarise(bundle([note], expected=["sighting"]), AS_OF)
    text = draft["sentences"][0]["text"]
    assert text == (
        "On 12 August 2026 synthetic witness W-01 saw a blue bicycle. "
        "The fictional shop is Reed Wharf Cycles."
    )
    assert draft["sentences"][0]["citation"]["line_start"] == 1
    assert draft["sentences"][0]["citation"]["line_end"] == 2
    assert draft["checker_passed"] is True


def line_two() -> dict:
    return {"line": 2, "text": "The fictional shop is Reed Wharf Cycles."}


def test_non_contiguous_lines_are_not_summarised():
    note = document(
        "SYN-NOTE-GAP",
        [
            {
                "paragraph": 1,
                "fact_key": "sighting",
                "lines": [
                    {"line": 1, "text": BLUE},
                    {"line": 3, "text": "A later line."},
                ],
            }
        ],
    )
    draft = summarise(bundle([note], expected=["sighting"]), AS_OF)
    assert draft["summary"]["sentence_count"] == 0
    assert draft["not_used"][0]["reason"] == "non_contiguous_lines"
    assert draft["summary"]["gap_count"] == 1
    assert draft["do_not_rely"] is True
