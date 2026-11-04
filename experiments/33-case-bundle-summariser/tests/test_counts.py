"""Sentence totals, gap totals, and contradiction totals stay separate."""

from src.summarise import summarise
from tests.support import bundle, blue_document


AS_OF = "2026-11-04"


def test_gaps_are_not_added_to_the_failure_count():
    draft = summarise(
        bundle([blue_document()], expected=["sighting", "item", "cctv"]),
        AS_OF,
    )
    summary = draft["summary"]
    assert summary["sentence_count"] == 2
    assert summary["failure_count"] == 0
    assert summary["verdict_total"] == 2
    assert sum(summary["verdicts"].values()) == summary["sentence_count"]
    assert summary["gap_count"] == 1
    assert summary["gap_count"] + summary["failure_count"] != summary["verdict_total"]
    assert "gaps" in draft["do_not_rely_reasons"]
    assert draft["checker_passed"] is True


def test_other_failures_are_not_added_to_failure_count():
    from tests.support import cite

    draft = summarise(
        bundle([blue_document()], expected=["sighting"]),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "text": "The witness is credible and the bicycle was red.",
                "citation": cite("SYN-NOTE-01", 1),
            }
        ],
    )
    summary = draft["summary"]
    assert summary["failure_count"] == 1
    assert summary["verdict_total"] == 1
    assert summary["other_failure_mentions"] >= 1
    assert summary["failure_count"] + summary["other_failure_mentions"] != summary["verdict_total"]
    assert summary["sentence_count"] + summary["extractive_sentence_count"] != summary["verdict_total"]
