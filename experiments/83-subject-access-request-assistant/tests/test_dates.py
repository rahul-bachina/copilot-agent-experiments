"""Date readings. Nothing unreadable is coerced to a default."""

from datetime import date

from src.dates import add_months, as_date, parse_date, shift_weekend, with_question_date

QUESTION = date(2026, 10, 20)

FIXTURES = [
    ("2026-10-03", "2026-10-03", False, False),
    ("2024-12-12", "2024-12-12", False, False),
    ("12/12/2024", "2024-12-12", False, False),
    ("12-12-2024", "2024-12-12", False, False),
    ("2024/02/29", "2024-02-29", False, False),
    ("29 February 2024", "2024-02-29", False, False),
    ("31 January 2024", "2024-01-31", False, False),
    ("31 January 2026", "2026-01-31", False, False),
    ("1st March 2026", "2026-03-01", False, False),
    ("03 October 2026", "2026-10-03", False, False),
    ("2026-02-28", "2026-02-28", False, False),
    ("29/02/2024", "2024-02-29", False, False),
    ("31/01/2028", "2028-01-31", False, False),
    ("7 August 2026", "2026-08-07", False, False),
    ("2020-02-29", "2020-02-29", False, False),
    ("15/08/2026", "2026-08-15", False, False),
    ("2026-11-03", "2026-11-03", False, False),
    ("2 March 2026", "2026-03-02", False, False),
    ("2025-01-31", "2025-01-31", False, False),
    ("9 November 2026", "2026-11-09", False, False),
    ("13 January 2025", "2025-01-13", False, False),
    ("2024-01-01", "2024-01-01", False, False),
]


def test_twenty_unambiguous_dates_parse_and_are_not_coerced():
    assert len(FIXTURES) >= 20
    for raw, iso, ambiguous, unparseable in FIXTURES:
        reading = parse_date(raw)
        assert reading["coerced"] is False, raw
        assert reading["ambiguous"] is ambiguous, raw
        assert reading["unparseable"] is unparseable, raw
        assert reading["iso"] == iso, raw


def test_same_numbers_are_not_ambiguous_and_different_numbers_are():
    same = parse_date("12/12/2024")
    assert same["ambiguous"] is False
    assert same["iso"] == "2024-12-12"
    mixed = parse_date("01/02/2024")
    assert mixed["ambiguous"] is True
    assert mixed["iso"] is None
    assert mixed["coerced"] is False
    assert as_date(mixed) is None


def test_impossible_and_blank_dates_are_not_coerced():
    for raw in ("29/02/2025", "31/02/2024", "00/01/2024", "32/01/2024", "", None, 0, "tomorrow"):
        reading = parse_date(raw)
        assert reading["unparseable"] is True, raw
        assert reading["iso"] is None
        assert reading["coerced"] is False


def test_a_future_date_is_flagged_against_the_question_date():
    reading = with_question_date(parse_date("2026-12-01"), QUESTION)
    assert reading["future"] is True
    assert reading["iso"] == "2026-12-01"
    assert reading["coerced"] is False
    same_day = with_question_date(parse_date("2026-10-20"), QUESTION)
    assert same_day["future"] is False


def test_month_arithmetic_includes_leap_years_and_short_months():
    assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2026, 10, 3), 1) == date(2026, 11, 3)
    assert add_months(date(2026, 8, 7), 3) == date(2026, 11, 7)
    weekend, moved = shift_weekend(date(2026, 2, 28))
    assert moved is True
    assert weekend == date(2026, 3, 2)
    weekday, moved = shift_weekend(date(2026, 11, 3))
    assert moved is False
    assert weekday == date(2026, 11, 3)
