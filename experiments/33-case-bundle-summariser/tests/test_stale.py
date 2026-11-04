"""Superseded and stale documents are not the reading, even when the quote is exact."""

from src.summarise import summarise
from tests.support import (
    BLUE,
    GREEN,
    LOCATION,
    RED,
    bundle,
    blue_document,
    cite,
    document,
    paragraph,
)


AS_OF = "2026-11-04"


def test_superseded_document_is_not_extracted_and_an_exact_quote_still_fails():
    old = document(
        "SYN-NOTE-02",
        [paragraph(1, RED, "sighting")],
        status="superseded",
        reviewed_on="2026-07-01",
        document_date="2026-07-01",
        superseded_by="SYN-NOTE-01",
    )
    draft = summarise(
        bundle([blue_document(), old], expected=["sighting", "item"]),
        AS_OF,
        proposed_sentences=[
            {"sentence_id": "P1", "text": RED, "fact_key": "sighting", "citation": cite("SYN-NOTE-02", 1)}
        ],
    )
    assert all(row["citation"]["document_id"] != "SYN-NOTE-02" for row in draft["extractive_sentences"])
    assert any(row["document_id"] == "SYN-NOTE-02" and row["reason"] == "superseded" for row in draft["not_used"])
    assert draft["sentences"][0]["verdict"] == "stale_or_superseded"
    assert "span_does_not_support" not in draft["sentences"][0]["other_failures"]
    assert draft["checker_passed"] is False
    assert draft["contradiction_resolved"] is False


def test_a_current_document_that_names_a_successor_is_treated_as_superseded():
    labelled_current = document(
        "SYN-NOTE-02",
        [paragraph(1, RED, "sighting")],
        status="current",
        reviewed_on="2026-09-01",
        document_date="2026-07-01",
        superseded_by="SYN-NOTE-01",
    )
    draft = summarise(bundle([labelled_current], expected=["sighting"]), AS_OF)
    assert draft["summary"]["sentence_count"] == 0
    assert draft["not_used"][0]["reason"] == "superseded"


def test_stale_review_date_is_not_used_and_a_quote_of_it_fails():
    stale = document(
        "SYN-NOTE-03",
        [paragraph(1, LOCATION, "location")],
        reviewed_on="2025-06-01",
        document_date="2025-06-01",
    )
    draft = summarise(
        bundle([stale], expected=["location"]),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "text": LOCATION,
                "fact_key": "location",
                "citation": cite("SYN-NOTE-03", 1),
            }
        ],
    )
    assert draft["extractive_sentences"] == []
    assert draft["not_used"][0]["reason"] == "stale"
    assert draft["sentences"][0]["verdict"] == "stale_or_superseded"
    assert "stale_or_superseded_documents_in_bundle" in draft["do_not_rely_reasons"]


def test_the_day_the_window_ends_is_not_stale():
    note = document(
        "SYN-NOTE-EDGE",
        [paragraph(1, BLUE, "sighting")],
        reviewed_on="2026-08-06",
        document_date="2026-08-06",
    )
    draft = summarise(bundle([note], expected=["sighting"]), AS_OF, 90)
    assert draft["checker_passed"] is True
    assert draft["not_used"] == []
    older = document(
        "SYN-NOTE-OLD",
        [paragraph(1, BLUE, "sighting")],
        reviewed_on="2026-08-05",
        document_date="2026-08-05",
    )
    stale = summarise(bundle([older], expected=["sighting"]), AS_OF, 90)
    assert stale["not_used"][0]["reason"] == "stale"


def test_a_later_as_of_date_marks_the_pinned_pages_stale_without_dropping_a_fresh_note():
    note = document(
        "SYN-NOTE-FRESH",
        [paragraph(1, BLUE, "sighting")],
        reviewed_on="2027-02-01",
        document_date="2027-02-01",
    )
    draft = summarise(bundle([note], expected=["sighting"]), "2027-03-01", 90)
    assert draft["pins_stale"] is True
    assert draft["sentences"][0]["verdict"] == "supported"
    assert draft["checker_passed"] is True
    assert "pins_stale" in draft["do_not_rely_reasons"]
    boundary = next(row for row in draft["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert boundary["reopened_for_this_experiment"] is False
    opened = [row for row in draft["sources"] if row["stale_applicable"]]
    assert opened and all(row["stale"] is True for row in opened)


def test_contradiction_is_listed_once_and_not_resolved():
    green = document(
        "SYN-NOTE-05",
        [paragraph(1, GREEN, "sighting")],
        reviewed_on="2026-09-20",
        document_date="2026-09-01",
    )
    draft = summarise(
        bundle([blue_document(), green], expected=["sighting"]),
        AS_OF,
    )
    assert draft["summary"]["sentence_count"] == 2
    assert draft["summary"]["contradiction_count"] == 1
    assert draft["summary"]["failure_count"] == 0
    assert draft["checker_passed"] is True
    assert draft["contradictions"][0]["resolved"] is False
    assert draft["contradictions"][0]["credibility_finding"] is None
    assert draft["contradiction_resolved"] is False
    assert "contradictions" in draft["do_not_rely_reasons"]
    assert draft["summary"]["failure_count"] + draft["summary"]["contradiction_count"] != draft["summary"]["verdict_total"] or draft["summary"]["sentence_count"] == 2
