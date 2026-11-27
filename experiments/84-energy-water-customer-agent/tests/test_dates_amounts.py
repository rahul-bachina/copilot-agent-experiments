"""Dates and amounts. Unreadable values are not coerced."""

from datetime import date

from src.amounts import parse_amount, reading_token
from src.dates import as_date, parse_date, with_question_date

QUESTION = date(2026, 11, 27)


def test_at_least_twenty_dates_including_leap_years_and_ambiguous_forms():
    fixtures = [
        ("2024-02-29", False, False, "2024-02-29"),
        ("2025-02-29", True, False, None),
        ("12/12/2024", False, False, "2024-12-12"),
        ("12-12-2024", False, False, "2024-12-12"),
        ("01/02/2024", False, True, None),
        ("02/03/2024", False, True, None),
        ("2024/12/12", False, False, "2024-12-12"),
        ("29 February 2024", False, False, "2024-02-29"),
        ("29 February 2025", True, False, None),
        ("29th February 2024", False, False, "2024-02-29"),
        ("15 Jan 2024", False, False, "2024-01-15"),
        ("2nd March 2024", False, False, "2024-03-02"),
        ("13/07/2024", False, False, "2024-07-13"),
        ("07/13/2024", False, False, "2024-07-13"),
        ("31/04/2024", True, False, None),
        ("2024-04-31", True, False, None),
        ("00/01/2024", True, False, None),
        ("32/01/2024", True, False, None),
        ("soon", True, False, None),
        ("", True, False, None),
        ("2026-11-27", False, False, "2026-11-27"),
        ("2027-01-01", False, False, "2027-01-01"),
    ]
    assert len(fixtures) >= 20
    for raw, unparseable, ambiguous, iso in fixtures:
        parsed = parse_date(raw)
        assert parsed["coerced"] is False
        assert parsed["unparseable"] is unparseable, (raw, parsed)
        assert parsed.get("ambiguous") is ambiguous, (raw, parsed)
        if iso:
            assert parsed["iso"] == iso
        else:
            assert as_date(parsed) is None
    future = with_question_date(parse_date("2027-01-01"), QUESTION)
    assert future["future"] is True
    assert future["iso"] == "2027-01-01"
    assert future["coerced"] is False
    same_day = with_question_date(parse_date("2026-11-27"), QUESTION)
    assert same_day["future"] is False
    not_a_string = parse_date(0)
    assert not_a_string["unparseable"] is True
    assert not_a_string["coerced"] is False
    assert as_date(not_a_string) is None
    assert parse_date(None)["reason"] == "missing"


def test_malformed_amounts_and_readings_are_not_turned_into_zero():
    broken = parse_amount("£1,25.00")
    assert broken["unparseable"] is True
    assert broken["malformed"] is True
    assert broken["amount"] is None
    assert broken["coerced"] is False
    assert parse_amount("£1,250.00")["amount"] == "1250.00"
    assert parse_amount("£125.00")["amount"] == "125.00"
    assert parse_amount("120.40")["amount"] == "120.40"
    assert parse_amount("")["amount"] is None
    assert parse_amount(None)["reason"] == "missing"
    assert parse_amount(10)["reason"] == "not_a_string"
    assert parse_amount("£-5.00")["negative"] is True
    blank = reading_token("")
    assert blank["reading"] is None
    assert blank["coerced"] is False
    assert reading_token("abc")["reading"] is None
    assert reading_token("12,34.5")["reading"] is None
    assert reading_token("04521")["reading"] == "04521"
    assert reading_token("12,345")["reading"] == "12345"
    assert reading_token(0)["reason"] == "not_a_string"
