"""Stated dates, including leap years, ambiguous numbers, and arithmetic."""

from datetime import date

from src.dates import as_date, parse_date

ON = date(2026, 10, 15)


def test_twenty_stated_dates_and_arithmetic():
    cases = [
        ("12/12/2024", {"iso": "2024-12-12", "ambiguous": False, "impossible": False, "unparseable": False}),
        ("03/04/2025", {"iso": None, "ambiguous": True, "impossible": False, "unparseable": False}),
        ("2024-02-29", {"iso": "2024-02-29", "leap_day": True, "impossible": False}),
        ("2025-02-29", {"iso": None, "impossible": True}),
        ("29/02/2024", {"iso": "2024-02-29", "leap_day": True}),
        ("29/02/2023", {"iso": None, "impossible": True}),
        ("31/04/2024", {"iso": None, "impossible": True}),
        ("13/01/2024", {"iso": "2024-01-13", "ambiguous": False}),
        ("01/13/2024", {"iso": None, "impossible": True, "ambiguous": False}),
        ("12 December 2024", {"iso": "2024-12-12"}),
        ("12 Dec 2024", {"iso": "2024-12-12"}),
        ("12th December 2024", {"iso": "2024-12-12"}),
        ("2024-12-12", {"iso": "2024-12-12"}),
        ("soon", {"iso": None, "unparseable": True, "coerced": False}),
        ("", {"iso": None, "unparseable": True}),
        ("12/12/24", {"iso": None, "unparseable": True}),
        ("01/01/2099", {"iso": "2099-01-01", "future": True}),
        ("32/01/2024", {"iso": None, "impossible": True}),
        ("00/01/2024", {"iso": None, "impossible": True}),
        ("2024-13-01", {"iso": None, "impossible": True}),
        ("1/1/2024", {"iso": "2024-01-01", "ambiguous": False}),
        ("15/08/2024", {"iso": "2024-08-15", "ambiguous": False}),
    ]
    assert len(cases) >= 20
    for raw, expect in cases:
        parsed = parse_date(raw, on=ON)
        for key, value in expect.items():
            assert parsed[key] == value, (raw, key, parsed)
        assert parsed["coerced"] is False
        if parsed["iso"] is None:
            assert parsed["days_from_as_of"] is None
        else:
            assert parsed["days_from_as_of"] == (date.fromisoformat(parsed["iso"]) - ON).days
            assert parsed["days_from_as_of"] != 0 or parsed["iso"] == ON.isoformat()


def test_leap_day_arithmetic_is_one_day():
    parsed = parse_date("2024-03-01", on=date(2024, 2, 29))
    assert parsed["days_from_as_of"] == 1
    assert parsed["coerced"] is False


def test_question_date_must_be_iso():
    assert as_date("2026-10-15") == ON
    try:
        as_date("15/10/2026")
    except ValueError:
        return
    raise AssertionError("ambiguous question date")
