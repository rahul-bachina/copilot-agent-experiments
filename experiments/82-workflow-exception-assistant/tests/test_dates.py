"""Date readings. Nothing unreadable is coerced to a default."""

from datetime import date

from src.dates import as_date, calendar_hours, parse_date, parse_timestamp, with_question_date

QUESTION = date(2026, 11, 26)


def _cases():
    return [
        ("2026-11-26", False, False, "2026-11-26"),
        ("2026/11/26", False, False, "2026-11-26"),
        ("12/12/2024", False, False, "2024-12-12"),
        ("29/02/2024", False, False, "2024-02-29"),
        ("29 February 2024", False, False, "2024-02-29"),
        ("01/02/2024", True, False, None),
        ("03/04/2024", True, False, None),
        ("02/30/2024", False, True, None),
        ("29/02/2023", False, True, None),
        ("29 February 2023", False, True, None),
        ("2023-02-29", False, True, None),
        ("2024-02-30", False, True, None),
        ("31/04/2024", False, True, None),
        ("00/01/2024", False, True, None),
        ("32 January 2024", False, True, None),
        ("not-a-date", False, True, None),
        ("", False, True, None),
        ("12/12/24", False, True, None),
        ("2026-11-26T09:30:00Z", False, False, "2026-11-26"),
        ("2024-02-29T00:00:00Z", False, False, "2024-02-29"),
        ("2026-02-29T00:00:00Z", False, True, None),
        ("2026-11-26T25:00:00Z", False, True, None),
        ("20 November 2026 09:00", False, False, "2026-11-20"),
        ("2026-12-01", False, False, "2026-12-01"),
    ]


def test_at_least_twenty_date_fixtures_keep_leap_years_and_ambiguity():
    rows = _cases()
    assert len(rows) >= 20
    for raw, ambiguous, unparseable, iso in rows:
        parser = parse_timestamp if "T" in raw or ":" in raw else parse_date
        reading = parser(raw)
        assert reading["coerced"] is False, raw
        assert reading["ambiguous"] is ambiguous, raw
        assert reading["unparseable"] is unparseable, raw
        assert reading.get("iso") == iso, raw


def test_same_numbers_are_not_ambiguous_and_a_future_date_is_not_rewritten():
    same = parse_date("12/12/2024")
    assert same["ambiguous"] is False
    assert same["iso"] == "2024-12-12"
    future = with_question_date(parse_date("2026-12-01"), QUESTION)
    assert future["future"] is True
    assert future["iso"] == "2026-12-01"
    assert future["coerced"] is False
    same_day = with_question_date(parse_timestamp("2026-11-26T23:59:00Z"), QUESTION)
    assert same_day["future"] is False
    assert same_day["iso"] == "2026-11-26"


def test_calendar_hours_are_not_zero_on_the_question_date():
    same = calendar_hours(parse_date("2026-11-26"), QUESTION)
    assert same["known"] is False
    assert same["hours"] is None
    assert same["coerced"] is False
    earlier = calendar_hours(parse_date("2026-11-25"), QUESTION)
    assert earlier["hours"] == 24
    assert earlier["coerced"] is False
    leap = as_date(parse_date("2024-02-29"))
    assert leap.isoformat() == "2024-02-29"
    assert as_date(parse_date("2023-02-29")) is None


def test_a_boolean_and_a_float_are_not_dates():
    for value in (True, False, 0, 1.5, None):
        reading = parse_timestamp(value)
        assert reading["unparseable"] is True
        assert reading["iso"] is None
        assert reading["coerced"] is False
