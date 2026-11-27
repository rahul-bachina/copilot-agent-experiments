"""Date readings. Nothing unreadable is stored as zero or as today."""

from datetime import date

from src.dates import add_working_days, deadlines_in, parse_date

QUESTION = date(2026, 11, 20)
VISIT = date(2024, 2, 28)


def _reading(token: str, **expect):
    parsed = parse_date(token)
    for key, value in expect.items():
        assert parsed[key] == value, (token, key, parsed)
    assert parsed["coerced"] is False
    return parsed


def test_twenty_date_fixtures_including_leap_years():
    fixtures = [
        ("2026-11-20", {"iso": "2026-11-20", "unparseable": False, "ambiguous": False}),
        ("2026/11/20", {"iso": "2026-11-20", "unparseable": False, "ambiguous": False}),
        ("12/12/2024", {"iso": "2024-12-12", "ambiguous": False, "unparseable": False}),
        ("12-12-2024", {"iso": "2024-12-12", "ambiguous": False}),
        ("12.12.2024", {"iso": "2024-12-12", "ambiguous": False}),
        ("01/02/2024", {"iso": None, "ambiguous": True, "unparseable": False}),
        ("02/01/2024", {"iso": None, "ambiguous": True}),
        ("31/01/2024", {"iso": "2024-01-31", "ambiguous": False}),
        ("2024-02-29", {"iso": "2024-02-29", "unparseable": False}),
        ("29 February 2024", {"iso": "2024-02-29", "unparseable": False}),
        ("29th February 2024", {"iso": "2024-02-29", "unparseable": False}),
        ("2025-02-29", {"iso": None, "unparseable": True, "reason": "invalid_calendar_date"}),
        ("29 February 2025", {"iso": None, "unparseable": True}),
        ("32/01/2024", {"iso": None, "unparseable": True}),
        ("00/01/2024", {"iso": None, "unparseable": True}),
        ("2026-13-01", {"iso": None, "unparseable": True}),
        ("next Tuesday", {"iso": None, "unparseable": True, "reason": "unrecognised_format"}),
        ("19 November 2026", {"iso": "2026-11-19", "unparseable": False}),
        ("", {"iso": None, "unparseable": True, "reason": "missing"}),
        ("not a date", {"iso": None, "unparseable": True}),
        ("2026-11-31", {"iso": None, "unparseable": True}),
    ]
    assert len(fixtures) >= 20
    for token, expect in fixtures:
        _reading(token, **expect)


def test_future_dates_are_flagged_and_not_rewritten():
    reading = deadlines_in("by 1 December 2026", visit=date(2026, 11, 18), question=QUESTION)
    assert reading["future"] is True
    assert reading["iso"] == "2026-12-01"
    assert reading["coerced"] is False
    same = deadlines_in("by 20 November 2026", visit=date(2026, 11, 18), question=QUESTION)
    assert same["future"] is False
    assert same["iso"] == "2026-11-20"


def test_ambiguous_and_conflicting_dates_are_not_chosen():
    ambiguous = deadlines_in("by 01/02/2024", visit=VISIT, question=QUESTION)
    assert ambiguous["ambiguous"] is True
    assert ambiguous["iso"] is None
    assert ambiguous["chosen"] is False
    assert ambiguous["coerced"] is False
    conflict = deadlines_in(
        "by 19 November 2026 or by 20 November 2026",
        visit=date(2026, 11, 18),
        question=QUESTION,
    )
    assert conflict["conflict"] is True
    assert conflict["iso"] is None
    assert conflict["chosen"] is False


def test_working_days_do_not_coerce_a_bad_count():
    assert add_working_days(VISIT, 5)["iso"] == "2024-03-06"
    leap = add_working_days(date(2024, 2, 28), 1)
    assert leap["iso"] == "2024-02-29"
    bad = add_working_days(VISIT, "five")
    assert bad["iso"] is None
    assert bad["coerced"] is False
    negative = add_working_days(VISIT, -1)
    assert negative["iso"] is None
    prose = deadlines_in("within five working days", visit=VISIT, question=QUESTION)
    assert prose["unparseable"] is True
    assert prose["iso"] is None
    assert prose["coerced"] is False


def test_a_question_date_conflict_does_not_use_today():
    from src.notes import draft_note, reset_state

    reset_state()
    result = draft_note(
        {
            "synthetic": True,
            "visit_id": "VIS-DATE",
            "service": "adult-social-care",
            "practitioner_ref": "PRAC-8501",
            "question_date": "2026-12-01",
            "visit_date": "2026-11-18",
            "lines": [
                {"n": 1, "speaker": "practitioner", "audio": "clear", "text": "We agreed to call by 20 November 2026. Owner: duty team."},
            ],
        },
        as_of="2026-11-20",
    )
    assert result["question_date_conflict"] is True
    assert result["as_of"] is None
    assert result["actions"][0]["date"]["future"] is False
    assert result["coerced"] is False
    assert "dates_seen" in result["required_acknowledgements"]
