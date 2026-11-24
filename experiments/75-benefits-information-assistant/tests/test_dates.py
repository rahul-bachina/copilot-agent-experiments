"""Date readings. Unreadable and ambiguous values are not coerced."""

from datetime import date

from src.dates import as_date, days_between, parse_date
from src.knowledge import review_status


def test_twenty_date_readings_include_leap_years_and_ambiguous_forms():
    cases = [
        ("2024-02-29", "2024-02-29", False, False),
        ("2023-02-29", None, True, False),
        ("2024-02-30", None, True, False),
        ("2024-04-31", None, True, False),
        ("01/02/2024", None, False, True),
        ("02/01/2024", None, False, True),
        ("13/01/2024", "2024-01-13", False, False),
        ("01/13/2024", "2024-01-13", False, False),
        ("2024/01/13", None, True, False),
        ("", None, True, False),
        (None, None, True, False),
        ("soon", None, True, False),
        ("20261124", None, True, False),
        ("32/01/2024", None, True, False),
        ("29/02/2023", None, True, False),
        ("29/02/2024", "2024-02-29", False, False),
        ("2024-2-29", None, True, False),
        ("00/01/2024", None, True, False),
        (20240113, None, True, False),
        (" 2024-02-29 ", "2024-02-29", False, False),
        ("31/02/2024", None, True, False),
        ("02/30/2024", None, True, False),
    ]
    assert len(cases) >= 20
    for raw, iso, unparseable, ambiguous in cases:
        reading = parse_date(raw)
        assert reading["coerced"] is False
        assert reading["iso"] == iso
        assert reading["unparseable"] is unparseable
        assert reading["ambiguous"] is ambiguous
        if iso:
            assert as_date(reading) == date.fromisoformat(iso)
        else:
            assert as_date(reading) is None


def test_leap_day_interval_is_not_replaced():
    start = parse_date("2023-02-28")
    end = parse_date("2024-02-29")
    assert days_between(start, end) == 366
    assert days_between(parse_date("2024-02-29"), parse_date("2024-03-01")) == 1
    assert days_between(parse_date("01/02/2024"), parse_date("2024-03-01")) is None
    assert days_between(parse_date("soon"), parse_date("2024-03-01")) is None


def test_review_due_date_is_stale_and_an_unreadable_due_date_is_not_quoted():
    current = {"last_reviewed": "2024-02-29", "review_due": "2024-03-01"}
    on_review = review_status(current, date(2024, 2, 29))
    due = review_status(current, date(2024, 3, 1))
    assert on_review["stale"] is False and on_review["quote"] is True and on_review["coerced"] is False
    assert due["stale"] is True and due["quote"] is False
    broken = review_status({"last_reviewed": "2024-02-29", "review_due": "31/02/2024"}, date(2024, 2, 29))
    assert broken["unreadable"] is True and broken["quote"] is False and broken["coerced"] is False
    assert broken["last_reviewed"] is None
