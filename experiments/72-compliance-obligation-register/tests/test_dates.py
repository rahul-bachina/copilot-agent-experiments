"""Date parsing. Unreadable values stay unreadable."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dates import add_months, parse_as_of, parse_date_token  # noqa: E402
from src.register import _dated  # noqa: E402


CASES = [
    ("2024-02-29", "2024-02-29", False, False),
    ("2025-02-29", None, True, False),
    ("2024-02-30", None, True, False),
    ("32 June 2026", None, True, False),
    ("01/02/2026", None, True, True),
    ("02/01/2026", None, True, True),
    ("2026-13-01", None, True, False),
    ("2026-00-10", None, True, False),
    ("29 February 2024", "2024-02-29", False, False),
    ("29 February 2025", None, True, False),
    ("", None, False, False),
    ("not stated", None, False, False),
    ("2026-11-14", "2026-11-14", False, False),
    ("14 November 2026", "2026-11-14", False, False),
    ("14th November 2026", "2026-11-14", False, False),
    ("November 14, 2026", "2026-11-14", False, False),
    ("2026-11-14T00:00:00", None, True, True),
    ("31 April 2026", None, True, False),
    ("1 May 2026", "2026-05-01", False, False),
    ("soon", None, True, False),
    ("2024/02/29", None, True, True),
    ("14-11-2026", None, True, True),
    ("00", None, True, False),
    ("February 29, 2024", "2024-02-29", False, False),
]


@pytest.mark.parametrize("token, iso, unparseable, ambiguous", CASES)
def test_stated_dates(token, iso, unparseable, ambiguous):
    parsed = parse_date_token(token)
    assert parsed["iso"] == iso
    assert parsed["unparseable"] is unparseable
    assert parsed["ambiguous"] is ambiguous
    assert parsed["coerced"] is False
    assert parsed["chosen"] is False
    if iso is None and token not in {"", "not stated"}:
        assert parsed["display"] == "unparseable"


def test_missing_is_not_stated_and_not_coerced():
    parsed = parse_date_token(None)
    assert parsed["not_stated"] is True
    assert parsed["iso"] is None
    assert parsed["coerced"] is False
    assert parsed["display"] == "not stated"


def test_leap_day_plus_twelve_months_is_not_moved():
    start = parse_date_token("2024-02-29")
    assert start["iso"] == "2024-02-29"
    assert add_months(__import__("datetime").date(2024, 2, 29), 12) is None


def test_as_of_rejects_ambiguous_and_datetime():
    assert parse_as_of("2026-11-14").isoformat() == "2026-11-14"
    with pytest.raises(ValueError):
        parse_as_of("01/02/2026")
    with pytest.raises(ValueError):
        parse_as_of(datetime(2026, 11, 14))
    with pytest.raises(ValueError):
        parse_as_of("2025-02-29")


def test_month_name_disagreement_does_not_drop_the_local_date():
    parsed = _dated("November 14, 2026")
    assert parsed["iso"] == "2026-11-14"
    assert parsed["coerced"] is False
    assert parsed["chosen"] is False
    assert parsed["experiment_68"]["called"] is True
    assert parsed["experiment_68"]["iso"] is None
    assert parsed["disagreement_kind"] == "neighbour_unparseable"


def test_ambiguous_numeric_date_agrees_it_is_unreadable():
    parsed = _dated("01/02/2026")
    assert parsed["iso"] is None
    assert parsed["ambiguous"] is True
    assert parsed["coerced"] is False
    assert parsed["experiment_68"]["iso"] is None
