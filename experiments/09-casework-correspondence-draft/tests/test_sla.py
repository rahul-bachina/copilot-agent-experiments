"""Correspondence clock. Dates are code, and a holding reply does not clear them."""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sla import calculate_casework_sla  # noqa: E402
from working_days import is_working_day, closed_days_covering  # noqa: E402


def _closed(day: date) -> set[date]:
    return closed_days_covering([day, date(day.year + 1, 6, 1)])


def test_england_and_wales_2026_dates_match_the_list_that_was_opened():
    closed = _closed(date(2026, 1, 1))
    assert is_working_day(date(2026, 1, 2), closed) is True
    for holiday in (
        date(2026, 1, 1),
        date(2026, 4, 3),
        date(2026, 4, 6),
        date(2026, 5, 4),
        date(2026, 5, 25),
        date(2026, 8, 31),
        date(2026, 12, 25),
        date(2026, 12, 28),
    ):
        assert is_working_day(holiday, closed) is False
    # Scotland-only on the GOV.UK page retrieved 26 October 2026.
    assert is_working_day(date(2026, 6, 15), closed) is True
    # Coronation bank holiday. Not in the standing pattern.
    coronation = closed_days_covering([date(2023, 5, 8)])
    assert is_working_day(date(2023, 5, 8), coronation) is True


def test_twenty_working_days_from_2_january_2026_is_30_january():
    clock = calculate_casework_sla(
        date(2026, 1, 2),
        regime="central_government",
        target_working_days=20,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=False,
    )
    assert clock["operative"] is True
    assert clock["operative_due_on"] == "2026-01-30"
    assert clock["holding_reply_clears_deadline"] is False
    assert clock["transfer_clocks_calculated"] is False


def test_day_after_receipt_is_day_one_when_that_day_is_open():
    clock = calculate_casework_sla(
        date(2026, 2, 9),
        regime="central_government",
        target_working_days=20,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=False,
    )
    assert clock["operative_due_on"] == "2026-03-09"


def test_christmas_2026_skips_the_substitute_monday():
    clock = calculate_casework_sla(
        date(2026, 12, 24),
        regime="central_government",
        target_working_days=1,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=False,
    )
    assert clock["operative_due_on"] == "2026-12-29"


def test_unconfirmed_target_is_not_operative():
    clock = calculate_casework_sla(
        date(2026, 1, 2),
        regime="central_government",
        target_working_days=20,
        target_confirmed=False,
        channel_confirmed=True,
        information_rights=False,
    )
    assert clock["operative"] is False
    assert clock["operative_due_on"] is None
    assert clock["reference_due_on"] == "2026-01-30"
    assert clock["reason"] == "target_or_channel_not_confirmed"


def test_ceiling_rejects_a_target_over_20_working_days():
    clock = calculate_casework_sla(
        date(2026, 1, 2),
        regime="central_government",
        target_working_days=21,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=False,
    )
    assert clock["operative"] is False
    assert clock["reference_due_on"] is None
    assert clock["reason"] == "exceeds_cabinet_office_ceiling"


def test_council_target_is_not_given_the_cabinet_office_ceiling():
    clock = calculate_casework_sla(
        date(2026, 1, 2),
        regime="council",
        target_working_days=10,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=False,
    )
    assert clock["ceiling_applies"] is False
    assert clock["operative"] is True
    assert clock["operative_due_on"] == "2026-01-16"


def test_council_without_a_target_does_not_borrow_20_days():
    clock = calculate_casework_sla(
        date(2026, 1, 2),
        regime="council",
        target_working_days=None,
        target_confirmed=False,
        channel_confirmed=False,
        information_rights=False,
    )
    assert clock["operative"] is False
    assert clock["reference_due_on"] is None
    assert clock["reason"] == "council_target_not_supplied"


def test_information_rights_clock_is_not_a_correspondence_date():
    clock = calculate_casework_sla(
        date(2026, 1, 2),
        regime="central_government",
        target_working_days=20,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=True,
    )
    assert clock["operative"] is False
    assert clock["operative_due_on"] is None
    assert clock["reference_due_on"] is None
    assert clock["reason"] == "information_rights_clock_is_separate"


def test_extra_closed_day_moves_only_the_count_the_author_passed():
    clock = calculate_casework_sla(
        date(2026, 2, 9),
        regime="central_government",
        target_working_days=1,
        target_confirmed=True,
        channel_confirmed=True,
        information_rights=False,
        extra_closed=(date(2026, 2, 10),),
    )
    assert clock["operative_due_on"] == "2026-02-11"
