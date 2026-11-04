"""Pinned pages match what was opened on 4 November 2026."""

from datetime import date

from src.sources import PINNED_ON, SOURCES, source_rows


def test_opened_pages_are_pinned_and_the_closed_pages_are_not():
    opened = [row for row in SOURCES if row["stale_applicable"]]
    assert len(opened) == 15
    assert all(row["last_verified"] == "2026-11-04" for row in opened)
    assert all(row["reopened_for_this_experiment"] is True for row in opened)
    notes = "\n".join(row["notes"] for row in opened)
    for phrase in (
        "not the GitHub Copilot service",
        "starts billing after publish",
        "from the moment you start building",
        "38(5)",
        "20 weeks",
        "13(2)",
        "Paragraph 9.62",
        "Paragraph 9.69",
        "Article 8",
        "Article 9",
        "lets you use Copilot Studio to build",
    ):
        assert phrase in notes
    blob = "\n".join(row["notes"] for row in SOURCES)
    assert "£" not in blob
    assert "$" not in blob
    closed = next(row for row in SOURCES if row["id"] == "ico-childrens-code")
    assert closed["stale_applicable"] is False
    assert closed["reopened_for_this_experiment"] is False
    assert closed["last_verified"] is None
    boundary = next(row for row in SOURCES if row["id"] == "catalogue-boundary")
    assert boundary["stale_applicable"] is False
    assert boundary["reopened_for_this_experiment"] is False
    assert PINNED_ON == "2026-11-04"


def test_stale_rows_skip_pages_that_were_not_opened():
    rows = source_rows(date(2027, 5, 4), 90)
    opened = [row for row in rows if row["stale_applicable"]]
    assert opened and all(row["stale"] is True for row in opened)
    for source_id in ("ico-childrens-code", "catalogue-boundary"):
        row = next(item for item in rows if item["id"] == source_id)
        assert row["stale"] is False
