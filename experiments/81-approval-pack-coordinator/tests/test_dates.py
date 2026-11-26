"""Date parsing and currency arithmetic. Nothing is coerced."""

from datetime import date

from src.dates import add_years, currency_status, extract_dates, parse_date, with_question_date

QUESTION = date(2026, 11, 25)


def test_twenty_readings_include_leap_years_and_an_unambiguous_numeric_date():
    cases = [
        ("2026-11-25", "2026-11-25", False),
        ("2024-02-29", "2024-02-29", False),
        ("2025-02-29", None, True),
        ("12/12/2024", "2024-12-12", False),
        ("12.12.2024", "2024-12-12", False),
        ("01/02/2024", None, False),
        ("02/01/2024", None, False),
        ("13/01/2024", "2024-01-13", False),
        ("01/13/2024", "2024-01-13", False),
        ("31/04/2024", None, True),
        ("29/02/2024", "2024-02-29", False),
        ("29 February 2024", "2024-02-29", False),
        ("31 February 2024", None, True),
        ("2024/12/12", "2024-12-12", False),
        ("", None, True),
        ("soon", None, True),
        ("32/01/2024", None, True),
        ("00/01/2024", None, True),
        ("29/02/2028", "2028-02-29", False),
        ("1900-02-29", None, True),
        ("29th February 2024", "2024-02-29", False),
        ("2026-13-01", None, True),
    ]
    assert len(cases) >= 20
    for raw, iso, unparseable in cases:
        reading = parse_date(raw)
        assert reading["coerced"] is False, raw
        assert reading["iso"] == iso, raw
        assert reading["unparseable"] is unparseable, raw
        if raw in {"01/02/2024", "02/01/2024"}:
            assert reading["ambiguous"] is True
        if raw in {"12/12/2024", "12.12.2024"}:
            assert reading["ambiguous"] is False
    assert parse_date(True)["coerced"] is False
    assert parse_date(True)["unparseable"] is True
    assert parse_date(date(2024, 2, 29))["iso"] == "2024-02-29"
    future = with_question_date(parse_date("2027-01-01"), QUESTION)
    assert future["future"] is True
    assert future["iso"] == "2027-01-01"
    moved = add_years(date(2024, 2, 29), 1)
    assert moved["date"] == "2025-02-28"
    assert moved["day_clamped"] is True
    assert moved["coerced"] is False
    assert add_years(date(2024, 2, 29), "1")["unparseable"] is True


def test_currency_arithmetic_does_not_treat_an_unreadable_date_as_fresh():
    cases = [
        ("2026-10-01", 90, False),
        ("2026-08-01", 90, True),
        ("2026-11-25", 90, False),
        ("2024-02-29", 90, True),
        ("2026-11-24", 0, True),
        ("2026-11-25", 0, False),
        ("01/02/2024", 90, False),
        ("soon", 90, False),
        ("2027-01-01", 90, False),
        ("29 February 2024", 30, True),
        ("12/12/2024", 10, True),
        ("31/04/2024", 10, False),
        ("2026-09-01", 180, False),
        ("2026-01-01", 365, False),
        ("2025-11-01", 365, True),
        ("2026-11-20", 7, False),
        ("2026-11-01", 7, True),
        ("", 90, False),
        ("2024-02-29", 365, True),
        ("2028-02-29", 1, False),
    ]
    assert len(cases) >= 20
    for raw, window, stale in cases:
        status = currency_status(raw, as_of=QUESTION, currency_days=window)
        assert status["coerced"] is False, raw
        assert status["stale"] is stale, raw
        if raw in {"soon", "", "31/04/2024", "01/02/2024"}:
            assert status["age_days"] is None
            assert status["unparseable"] is True
        if raw == "2028-02-29":
            assert status["future"] is True
            assert status["reading"]["iso"] == "2028-02-29"
    stated = extract_dates("The quote is dated 12/12/2024 and also 29 February 2024.")
    assert stated[0]["iso"] == "2024-12-12"
    assert stated[0]["ambiguous"] is False
    assert stated[1]["iso"] == "2024-02-29"
    assert extract_dates("no date here") == []
