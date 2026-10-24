"""Stale-data rule: older than the threshold, not equal to it."""

from datetime import date

from src.currency import assess_document_date, assess_source
from src.sources import SOURCES

SOURCE = SOURCES[0]


def test_verified_on_the_as_of_date_is_within_threshold():
    row = assess_source(SOURCE, date(2026, 10, 24), 90)
    assert row["age_days"] == 0
    assert row["currency"] == "within_threshold"
    assert row["last_verified"] == "2026-10-24"


def test_age_equal_to_the_threshold_is_not_stale():
    row = assess_source(SOURCE, date(2027, 1, 22), 90)
    assert row["age_days"] == 90
    assert row["currency"] == "within_threshold"


def test_age_older_than_the_threshold_is_stale():
    row = assess_source(SOURCE, date(2027, 1, 23), 90)
    assert row["age_days"] == 91
    assert row["currency"] == "stale"


def test_as_of_before_verification_is_visible():
    row = assess_source(SOURCE, date(2026, 10, 1), 90)
    assert row["currency"] == "as_of_before_verification"


def test_undated_policy_is_not_called_stale():
    row = assess_document_date(None, date(2026, 10, 24), 365)
    assert row["currency"] == "undated"


def test_old_policy_date_is_stale():
    row = assess_document_date("2024-01-01", date(2026, 10, 24), 365)
    assert row["currency"] == "stale"
