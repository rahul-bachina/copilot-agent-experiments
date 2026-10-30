"""A pin older than the threshold is stale. Equal to the threshold is not."""

from datetime import date, timedelta

from tests.support import draft_sample

from src.sources import LAST_VERIFIED


def test_pin_day_is_not_stale():
    draft = draft_sample("2026-10-30")
    assert draft["sources_stale"] is False
    assert draft["rules_current"] is True
    assert draft["promotion_approved"] is False


def test_ninety_days_is_not_stale_and_ninety_one_is():
    pinned = date.fromisoformat(LAST_VERIFIED)
    inside = draft_sample((pinned + timedelta(days=90)).isoformat())
    outside = draft_sample((pinned + timedelta(days=91)).isoformat())
    assert inside["sources_stale"] is False
    assert inside["rules_current"] is True
    assert outside["sources_stale"] is True
    assert outside["rules_current"] is False
    assert outside["promotion_approved"] is False
    assert outside["published"] is False
    assert outside["s21_approver_decision"] is None
    assert all(row["rely_before_reopen"] is False for row in outside["checklist"])


def test_as_of_before_the_pin_is_not_current():
    draft = draft_sample("2026-10-29")
    assert draft["sources_stale"] is True
    assert draft["rules_current"] is False
    assert draft["network_called"] is False
