"""Date parsing, leap years, ambiguous formats, and arithmetic."""

import pytest

from src.dates import as_date, days_between, parse_date, within_period


CASES = [
    ("2024-02-29", "2024-02-29", False, False),
    ("2025-02-29", None, True, False),
    ("2023-02-29", None, True, False),
    ("2000-02-29", "2000-02-29", False, False),
    ("1900-02-29", None, True, False),
    ("2026-04-31", None, True, False),
    ("2026-02-29", None, True, False),
    ("2026-01-01", "2026-01-01", False, False),
    ("2026-12-31", "2026-12-31", False, False),
    ("01/02/2026", None, False, True),
    ("02/01/2026", None, False, True),
    ("12/11/2026", None, False, True),
    ("29/02/2024", "2024-02-29", False, False),
    ("02/29/2024", "2024-02-29", False, False),
    ("31/01/2026", "2026-01-31", False, False),
    ("31/04/2026", None, True, False),
    ("32/01/2026", None, True, False),
    ("15/13/2026", None, True, False),
    ("next week", None, True, False),
    ("", None, True, False),
    (None, None, True, False),
    (73, None, True, False),
    ("2026-02-30", None, True, False),
    ("2024-02-28", "2024-02-28", False, False),
]


def test_at_least_twenty_date_fixtures():
    assert len(CASES) >= 20


@pytest.mark.parametrize("raw, iso, unparseable, ambiguous", CASES)
def test_stated_dates(raw, iso, unparseable, ambiguous):
    reading = parse_date(raw)
    assert reading["coerced"] is False
    assert reading["unparseable"] is unparseable
    assert reading["ambiguous"] is ambiguous
    assert reading["iso"] == iso
    if unparseable or ambiguous:
        assert as_date(reading) is None


def test_leap_day_arithmetic_and_period():
    start = parse_date("2024-02-29")
    end = parse_date("2024-03-01")
    assert days_between(start, end) == 1
    quarter = (as_date(parse_date("2026-01-01")), as_date(parse_date("2026-03-31")))
    assert days_between(parse_date("2026-01-01"), parse_date("2026-03-31")) == 89
    assert within_period(parse_date("2026-02-03"), *quarter) is True
    assert within_period(parse_date("2025-12-15"), *quarter) is False
    assert within_period(parse_date("2024-02-29"), as_date(parse_date("2024-01-01")), as_date(parse_date("2024-03-31"))) is True
    assert within_period(parse_date("01/02/2026"), *quarter) is None
    assert within_period(parse_date("next week"), *quarter) is None
    assert days_between(parse_date("next week"), parse_date("2026-03-31")) is None
    assert days_between(parse_date("01/02/2026"), parse_date("2026-03-31")) is None
