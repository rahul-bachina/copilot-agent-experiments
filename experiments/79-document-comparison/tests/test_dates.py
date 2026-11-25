"""Date readings. Nothing unreadable becomes today or zero."""

from datetime import date

from src.dates import add_years, parse_date, with_question_date

QUESTION = date(2026, 11, 25)


def _read(value, question=QUESTION):
    return with_question_date(parse_date(value), question)


CASES = [
    ("2024-02-29", "2024-02-29", False, False),
    ("2024/02/29", "2024-02-29", False, False),
    ("29 February 2024", "2024-02-29", False, False),
    ("29th February 2024", "2024-02-29", False, False),
    ("12/12/2024", "2024-12-12", False, False),
    ("02/02/2024", "2024-02-02", False, False),
    ("13/01/2024", "2024-01-13", False, False),
    ("01/13/2024", "2024-01-13", False, False),
    ("2026-11-25", "2026-11-25", False, False),
    ("1 April 2027", "2027-04-01", False, True),
    ("01/02/2024", None, True, False),
    ("05/06/2024", None, True, False),
    ("2023-02-29", None, False, False),
    ("31/02/2024", None, False, False),
    ("2024-04-31", None, False, False),
    ("31 November 2024", None, False, False),
    ("29 February 2025", None, False, False),
    ("00/00/2024", None, False, False),
    ("1600-01-01", None, False, False),
    ("soon", None, False, False),
    ("", None, False, False),
    (None, None, False, False),
    (True, None, False, False),
    (0, None, False, False),
]


def test_at_least_twenty_date_fixtures():
    assert len(CASES) >= 20


def test_date_fixtures_are_not_coerced():
    for value, iso, ambiguous, future in CASES:
        reading = _read(value)
        assert reading["coerced"] is False
        assert reading["iso"] == iso
        assert reading["ambiguous"] is ambiguous
        if iso is None and not ambiguous:
            assert reading["unparseable"] is True
        if future:
            assert reading["future"] is True
        if iso == "2024-12-12":
            assert reading["ambiguous"] is False
            assert reading["reason"] != "ambiguous_day_month"


def test_leap_day_plus_one_year_does_not_invent_29_february():
    result = add_years(date(2024, 2, 29), 1)
    assert result["date"] == "2025-02-28"
    assert result["day_clamped"] is True
    assert result["coerced"] is False


def test_a_string_offset_is_not_zero():
    result = add_years(date(2024, 4, 1), "1")
    assert result["date"] is None
    assert result["unparseable"] is True
    assert result["coerced"] is False
