"""Date parsing and deadline arithmetic. Nothing unreadable becomes zero or today."""

from datetime import date

from src.dates import as_date, parse_date, shift_days, subtract_months

FIXTURES = [
    ("2024-02-29", "2024-02-29", False, False),
    ("2028-02-29", "2028-02-29", False, False),
    ("2000-02-29", "2000-02-29", False, False),
    ("2025-02-29", None, True, False),
    ("1900-02-29", None, True, False),
    ("2026-02-29", None, True, False),
    ("2024-02-30", None, True, False),
    ("2026-11-14", "2026-11-14", False, False),
    ("2027-03-31", "2027-03-31", False, False),
    ("03/04/2026", None, False, True),
    ("04/03/2026", None, False, True),
    ("13/04/2026", "2026-04-13", False, False),
    ("04/13/2026", "2026-04-13", False, False),
    ("29/02/2024", "2024-02-29", False, False),
    ("32/01/2026", None, True, False),
    ("2026-13-01", None, True, False),
    ("2026-00-10", None, True, False),
    ("31/04/2026", None, True, False),
    ("soon", None, True, False),
    ("", None, True, False),
    ("2026/03/31", None, True, False),
    ("14 November 2026", None, True, False),
    ("2026-11-14T00:00:00", None, True, False),
    ("29/02/2025", None, True, False),
]


def test_at_least_twenty_date_fixtures():
    assert len(FIXTURES) >= 20


def test_stated_dates_are_not_coerced():
    for raw, iso, unparseable, ambiguous in FIXTURES:
        reading = parse_date(raw)
        assert reading["coerced"] is False
        assert reading["unparseable"] is unparseable
        assert reading["ambiguous"] is ambiguous
        assert reading["iso"] == iso
        if iso:
            assert as_date(reading) == date.fromisoformat(iso)
        else:
            assert as_date(reading) is None


def test_non_string_is_not_coerced():
    reading = parse_date(20261114)
    assert reading["unparseable"] is True
    assert reading["reason"] == "not_a_string"
    assert reading["coerced"] is False
    assert parse_date(None)["reason"] == "missing"


def test_leap_day_arithmetic():
    leap = date(2024, 3, 1)
    back = shift_days(leap, -1)
    assert back["date"] == "2024-02-29"
    assert back["coerced"] is False
    assert shift_days(leap, "soon")["date"] is None
    assert shift_days(leap, "soon")["coerced"] is False
    assert shift_days(leap, True)["unparseable"] is True
    earlier = subtract_months(date(2024, 2, 29), 12)
    assert earlier["date"] == "2023-02-28"
    assert earlier["day_clamped"] is True
    assert earlier["coerced"] is False
    assert subtract_months(date(2027, 3, 31), "12")["unparseable"] is True


def test_deadline_offsets_from_the_pinned_brief():
    deadline = date(2027, 3, 31)
    assert shift_days(deadline, -28)["date"] == "2027-03-03"
    assert shift_days(deadline, -14)["date"] == "2027-03-17"
    assert shift_days(deadline, -7)["date"] == "2027-03-24"
    assert shift_days(deadline, 0)["date"] == "2027-03-31"
    assert shift_days(deadline, 0)["offset_days"] == 0
