"""Dates are parsed and not coerced. 12/12/2024 is one day."""

from datetime import date

from src.checks import read_date

QUESTION = date(2026, 11, 26)

CASES = [
    ("2024-12-12", {"iso": "2024-12-12", "ambiguous": False, "unparseable": False}),
    ("12/12/2024", {"iso": "2024-12-12", "ambiguous": False, "unparseable": False}),
    ("2024/12/12", {"iso": "2024-12-12", "ambiguous": False, "unparseable": False}),
    ("01/02/2024", {"iso": None, "ambiguous": True, "unparseable": False}),
    ("02/01/2024", {"iso": None, "ambiguous": True, "unparseable": False}),
    ("13/01/2024", {"iso": "2024-01-13", "ambiguous": False, "unparseable": False}),
    ("12/13/2024", {"iso": "2024-12-13", "ambiguous": False, "unparseable": False}),
    ("2024-02-29", {"iso": "2024-02-29", "ambiguous": False, "unparseable": False}),
    ("29/02/2024", {"iso": "2024-02-29", "ambiguous": False, "unparseable": False}),
    ("29 February 2024", {"iso": "2024-02-29", "ambiguous": False, "unparseable": False}),
    ("2023-02-29", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("29/02/2023", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("31/02/2024", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("31/04/2024", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("32 January 2024", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("not-a-date", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("2024-13-01", {"iso": None, "ambiguous": False, "unparseable": True}),
    ("1st March 2024", {"iso": "2024-03-01", "ambiguous": False, "unparseable": False}),
    ("12 May 2024", {"iso": "2024-05-12", "ambiguous": False, "unparseable": False}),
    ("2020-01-01", {"iso": "2020-01-01", "ambiguous": False, "unparseable": False, "future": False}),
    ("2027-01-01", {"iso": "2027-01-01", "ambiguous": False, "unparseable": False, "future": True}),
]


def test_at_least_twenty_date_fixtures_and_no_coercion():
    assert len(CASES) >= 20
    for value, expect in CASES:
        reading = read_date(value, QUESTION)
        assert reading["coerced"] is False, value
        for key, wanted in expect.items():
            assert reading.get(key) == wanted, (value, key, reading)
            if wanted is None or isinstance(wanted, bool):
                assert reading.get(key) is wanted, (value, key, reading)


def test_a_future_flag_uses_the_question_date_not_today():
    early = read_date("2026-12-01", date(2026, 11, 26))
    later = read_date("2026-12-01", date(2026, 12, 1))
    assert early["future"] is True
    assert later["future"] is False
    assert later["coerced"] is False


def test_none_and_a_boolean_are_not_turned_into_a_date():
    for value in (None, True, False, 0):
        reading = read_date(value, QUESTION)
        assert reading["unparseable"] is True
        assert reading["iso"] is None
        assert reading["coerced"] is False
