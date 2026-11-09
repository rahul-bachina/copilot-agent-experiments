"""Sentence verdicts are not added to gap counts or to a case total."""

from src.summarise import summarise
from tests.support import case, event, four_events

AS_OF = "2026-11-09"


def test_failure_count_does_not_include_gaps_or_withheld_lines():
    events = [
        event("E1", "2026-10-20", "what_happened", "The tenant reported a leaking kitchen tap."),
        event("E2", "2026-10-21", "customer_ask", "The tenant asked for the tap to be repaired this week."),
    ]
    draft = summarise(case(events), AS_OF)
    summary = draft["summary"]
    assert summary["sentence_count"] == 2
    assert summary["verdict_total"] == summary["sentence_count"]
    assert summary["failure_count"] == 0
    assert summary["gap_count"] == 2
    assert summary["failure_count"] != summary["sentence_count"] + summary["gap_count"]
    assert "total" not in summary
    assert "total_cases" not in summary
    combined = summary["sentence_count"] + summary["extractive_sentence_count"] + summary["gap_count"]
    assert summary.get("total") != combined


def test_one_failed_sentence_is_counted_once_when_other_failures_exist():
    stale = event("E9", "2026-01-02", "what_happened", "The tenant reported a leaking kitchen tap.")
    draft = summarise(
        case(four_events() + [stale]),
        AS_OF,
        proposed_sentences=[
            {
                "sentence_id": "P1",
                "fact_key": "what_happened",
                "text": "This is not what the note says.",
                "citation": {"event_id": "E9", "paragraph": 1, "line_start": 1, "line_end": 1},
            }
        ],
    )
    sentence = draft["sentences"][0]
    assert sentence["verdict"] == "stale_or_superseded"
    assert "span_does_not_support" in sentence["other_failures"]
    assert draft["summary"]["failure_count"] == 1
    assert draft["summary"]["verdict_total"] == 1
