"""Date parsing and period arithmetic. Unreadable values are not coerced."""

from datetime import date

from src.dates import add_period, parse_date


CASES = [
    ("2024-02-29", date(2024, 2, 29), "ok"),
    ("2025-02-29", None, "unparseable"),
    ("2024/03/31", date(2024, 3, 31), "ok"),
    ("01/02/2024", None, "ambiguous"),
    ("02/01/2024", None, "ambiguous"),
    ("13/01/2024", date(2024, 1, 13), "ok"),
    ("01/13/2024", date(2024, 1, 13), "ok"),
    ("31/04/2026", None, "unparseable"),
    ("2024-04-31", None, "unparseable"),
    ("", None, "missing"),
    (None, None, "missing"),
    ("not a date", None, "unparseable"),
    ("29 February 2024", date(2024, 2, 29), "ok"),
    ("29 Feb 2025", None, "unparseable"),
    ("1st March 2024", date(2024, 3, 1), "ok"),
    ("15/15/2024", None, "unparseable"),
    ("0001-01-01", None, "out_of_range"),
    ("9999-01-01", None, "out_of_range"),
    (" 2024-02-29 ", date(2024, 2, 29), "ok"),
    (20240229, None, "unparseable"),
    ("0", None, "unparseable"),
    (True, None, "unparseable"),
    ("32/13/2020", None, "unparseable"),
    ("29 February 2028", date(2028, 2, 29), "ok"),
]


def test_stated_dates_are_not_coerced():
    assert len(CASES) >= 20
    for raw, expected, status in CASES:
        found, found_status = parse_date(raw)
        assert found_status == status, raw
        assert found == expected, raw
        assert found != date(1970, 1, 1) or expected == date(1970, 1, 1)


def test_leap_year_arithmetic():
    start, status = parse_date("2024-02-29")
    assert status == "ok"
    plus_one, one_status = add_period(start, 1, 0)
    assert one_status == "ok"
    assert plus_one == date(2025, 2, 28)
    plus_four, four_status = add_period(start, 4, 0)
    assert four_status == "ok"
    assert plus_four == date(2028, 2, 29)
    january, _ = parse_date("2024-01-31")
    feb, feb_status = add_period(january, 0, 1)
    assert feb_status == "ok"
    assert feb == date(2024, 2, 29)
    january_2025, _ = parse_date("2025-01-31")
    feb_2025, status_2025 = add_period(january_2025, 0, 1)
    assert status_2025 == "ok"
    assert feb_2025 == date(2025, 2, 28)


def test_period_is_not_replaced_with_zero():
    start = date(2024, 3, 31)
    for years, months in (("six", 0), (6, "0"), (-1, 0), (True, 0), (500, 0)):
        found, status = add_period(start, years, months)
        assert found is None
        assert status in {"unparseable", "out_of_range"}
    six, status = add_period(start, 6, 0)
    assert status == "ok"
    assert six == date(2030, 3, 31)
