"""Dates are parsed, not coerced. 12/12/2024 is not ambiguous."""

from datetime import date

from src.clocks import foi_clock, read_period, sar_clock
from src.dates import add_months, annotate, as_date, parse_date, twentieth_weekday_following

CASES = [
    ("2024-02-29", {"iso": "2024-02-29", "unparseable": False, "ambiguous": False, "impossible": False}),
    ("2025-02-29", {"iso": None, "unparseable": True, "impossible": True}),
    ("2028-02-29", {"iso": "2028-02-29", "unparseable": False}),
    ("1900-02-29", {"unparseable": True, "impossible": True}),
    ("2000-02-29", {"iso": "2000-02-29", "impossible": False}),
    ("12/12/2024", {"iso": "2024-12-12", "ambiguous": False, "unparseable": False}),
    ("01/02/2024", {"iso": None, "ambiguous": True, "unparseable": False}),
    ("13/01/2024", {"iso": "2024-01-13", "ambiguous": False}),
    ("01/13/2024", {"iso": "2024-01-13", "ambiguous": False}),
    ("32/01/2024", {"iso": None, "unparseable": True}),
    ("2024-13-01", {"iso": None, "unparseable": True, "impossible": True}),
    ("2026-11-31", {"iso": None, "unparseable": True, "impossible": True}),
    ("", {"reason": "missing", "unparseable": True, "coerced": False}),
    (0, {"reason": "not_a_string", "unparseable": True, "coerced": False}),
    ("0", {"unparseable": True, "coerced": False, "iso": None}),
    ("tomorrow", {"reason": "unrecognised_format", "unparseable": True, "coerced": False}),
    ("soon", {"unparseable": True, "coerced": False, "iso": None}),
    ("2 March 2024", {"iso": "2024-03-02", "ambiguous": False}),
    ("29 February 2024", {"iso": "2024-02-29", "impossible": False}),
    ("29 February 2025", {"unparseable": True, "impossible": True}),
    ("05/06/2024", {"ambiguous": True, "iso": None}),
    (True, {"reason": "not_a_string", "coerced": False}),
    ("2024-12-12", {"iso": "2024-12-12", "ambiguous": False}),
    ("29th February 2024", {"iso": "2024-02-29"}),
]


def test_stated_dates_cover_leap_years_and_ambiguous_forms():
    assert len(CASES) >= 20
    for value, expected in CASES:
        reading = parse_date(value)
        for key, wanted in expected.items():
            assert reading[key] == wanted, (value, key, reading)
        assert reading["coerced"] is False


def test_future_dates_are_flagged_against_the_question_date():
    future = annotate(parse_date("2027-01-01"), on=date(2026, 11, 25))
    assert future["future"] is True
    assert future["iso"] == "2027-01-01"
    assert future["coerced"] is False
    same = annotate(parse_date("2026-11-25"), on=date(2026, 11, 25))
    assert same["future"] is False
    assert as_date(parse_date("01/02/2024")) is None
    assert as_date(parse_date("12/12/2024")) == date(2024, 12, 12)


def test_calendar_month_clamps_february_and_does_not_invent_a_day():
    leap = add_months(date(2024, 1, 31), 1)
    assert leap["date"] == "2024-02-29"
    assert leap["day_clamped"] is True
    assert leap["coerced"] is False
    plain = add_months(date(2025, 1, 31), 1)
    assert plain["date"] == "2025-02-28"
    assert add_months(date(2026, 11, 25), "1")["unparseable"] is True


def test_twentieth_weekday_does_not_apply_bank_holidays():
    assert date(2026, 1, 2).weekday() == 4
    assert twentieth_weekday_following(date(2026, 1, 2)).isoformat() == "2026-01-30"
    clock = foi_clock(date(2026, 1, 2), 45)
    assert clock["weekday_count_20"] == "2026-01-30"
    assert clock["bank_holidays_applied"] is False
    assert clock["statutory_due_date"] is None
    assert clock["clock_met"] is False
    assert clock["stated_working_days_above_20"] is True
    assert clock["not_a_finding_of_breach"] is True
    soon = foi_clock(date(2026, 1, 2), "soon")
    assert soon["stated_working_days"]["coerced"] is False
    assert soon["stated_working_days"]["days"] is None
    zero = read_period(0)
    assert zero["days"] is None
    assert zero["coerced"] is False
    assert zero["reason"] == "not_a_positive_period"
    sar = sar_clock(date(2026, 1, 15), 45)
    assert sar["clock_met"] is False
    assert sar["statutory_due_date"] is None
    assert sar["stated_days_above_31"] is True
    assert sar["extension_in_paragraph_3_not_applied"] is True
