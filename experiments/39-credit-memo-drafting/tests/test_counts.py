"""Smoke totals count each figure once. Fact counts are not added to case counts."""

from src.draft import draft_memo
from tests.support import load_sample


def test_two_runs_do_not_become_one_total():
    first = draft_memo(load_sample(), as_of="2026-11-06")
    second = draft_memo(load_sample(), as_of="2026-11-06")
    assert first["summary"]["stated_fact_count"] == 9
    assert second["summary"]["stated_fact_count"] == 9
    assert "grand_total" not in first["summary"]
    assert first["summary"]["verdict_total"] == first["summary"]["stated_fact_count"]
    added = (
        first["summary"]["stated_fact_count"]
        + first["summary"]["gap_count"]
        + first["summary"]["contradiction_count"]
        + first["summary"]["not_used_count"]
        + first["cross_source"]["counts"]["fact_count"]
        + first["cross_source"]["counts"]["occurrence_count"]
    )
    assert added not in first["summary"].values()
    assert 18 not in first["summary"].values()
    assert first["summary"]["failure_count"] == 0
    assert sum(first["summary"]["verdicts"].values()) == 9
