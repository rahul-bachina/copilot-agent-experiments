"""Parse dates. Do not coerce an unreadable, ambiguous, or impossible value.

12/12/2024 is one calendar day: the day and the month are the same number,
so it is not ambiguous. 01/02/2024 is ambiguous because the numbers differ
and both are 1 to 12. A future date, compared with the question date, is
flagged. It is not rewritten as today. This module does not read today's date.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, timedelta

MIN_YEAR = 1800
MAX_YEAR = 2200

_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_ISO_SLASH = re.compile(r"^(\d{4})/(\d{2})/(\d{2})$")
_NUMERIC = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$")
_LONG = re.compile(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})$", re.IGNORECASE)
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_date(value: object) -> dict:
    """Return a reading. coerced is always false. No date is invented."""

    if value is None or value == "":
        return _bad("missing")
    if isinstance(value, datetime):
        return _bad("not_a_calendar_date")
    if isinstance(value, date):
        return _from_parts(value.year, value.month, value.day, ambiguous=False)
    if isinstance(value, bool) or not isinstance(value, str):
        return _bad("not_a_string")
    text = value.strip()
    if not text:
        return _bad("missing")
    iso = _ISO.fullmatch(text) or _ISO_SLASH.fullmatch(text)
    if iso:
        return _from_parts(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)), ambiguous=False)
    numeric = _NUMERIC.fullmatch(text)
    if numeric:
        first = int(numeric.group(1))
        second = int(numeric.group(2))
        year = int(numeric.group(3))
        if first == 0 or second == 0 or first > 31 or second > 31:
            return _bad("invalid_calendar_date")
        if first == second and first <= 12:
            return _from_parts(year, first, first, ambiguous=False)
        if first <= 12 and second <= 12:
            return {
                "iso": None,
                "unparseable": False,
                "ambiguous": True,
                "future": False,
                "reason": "ambiguous_day_month",
                "coerced": False,
            }
        if first > 12 and second > 12:
            return _bad("invalid_calendar_date")
        if first > 12:
            return _from_parts(year, second, first, ambiguous=False)
        return _from_parts(year, first, second, ambiguous=False)
    long = _LONG.fullmatch(text)
    if long:
        month = _MONTHS.get(long.group(2).casefold())
        if month is None:
            return _bad("unrecognised_format")
        return _from_parts(int(long.group(3)), month, int(long.group(1)), ambiguous=False)
    return _bad("unrecognised_format")


def as_date(parsed: dict) -> date | None:
    if not isinstance(parsed, dict):
        return None
    if parsed.get("unparseable") or parsed.get("ambiguous") or not parsed.get("iso"):
        return None
    try:
        return date.fromisoformat(parsed["iso"])
    except ValueError:
        return None


def with_question_date(parsed: dict, question: date | None) -> dict:
    """Flag a date after the question date. Do not replace it."""

    reading = dict(parsed)
    reading["future"] = False
    reading["coerced"] = False
    parsed_day = as_date(reading)
    if parsed_day is not None and isinstance(question, date) and not isinstance(question, datetime):
        if parsed_day > question:
            reading["future"] = True
            reading["reason"] = "future"
    return reading


def add_years(day: date, years: object) -> dict:
    """Move a whole number of years. 29 February does not become 29 February."""

    if type(years) is not int:
        return {"date": None, "unparseable": True, "coerced": False, "day_clamped": False}
    year = day.year + years
    last = calendar.monthrange(year, day.month)[1]
    clamped = day.day > last
    parsed = date(year, day.month, min(day.day, last))
    return {
        "date": parsed.isoformat(),
        "unparseable": False,
        "coerced": False,
        "day_clamped": clamped,
    }


def add_days(day: date, offset: object) -> dict:
    if type(offset) is not int:
        return {"date": None, "unparseable": True, "coerced": False}
    return {
        "date": (day + timedelta(days=offset)).isoformat(),
        "unparseable": False,
        "coerced": False,
    }


def _from_parts(year: int, month: int, day: int, *, ambiguous: bool) -> dict:
    if year < MIN_YEAR or year > MAX_YEAR:
        return _bad("out_of_range")
    try:
        parsed = date(year, month, day)
    except ValueError:
        return _bad("invalid_calendar_date")
    return {
        "iso": parsed.isoformat(),
        "unparseable": False,
        "ambiguous": ambiguous,
        "future": False,
        "reason": None,
        "coerced": False,
    }


def _bad(reason: str) -> dict:
    return {
        "iso": None,
        "unparseable": True,
        "ambiguous": False,
        "future": False,
        "reason": reason,
        "coerced": False,
    }
