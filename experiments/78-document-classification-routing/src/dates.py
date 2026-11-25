"""Parse dates. Do not coerce an unreadable or ambiguous value.

12/12/2024 is not ambiguous: the day and the month are the same number.
01/02/2024 is ambiguous. An impossible calendar day is unparseable.
The question date is the as-of argument. Today is not used.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_NAMED = re.compile(
    r"^(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(\d{4})$",
    re.IGNORECASE,
)
_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_date(value: object) -> dict:
    """Return a reading. coerced is always false. No date is invented."""

    if value is None or value == "":
        return _bad("missing")
    if isinstance(value, bool) or not isinstance(value, str):
        return _bad("not_a_string")
    text = value.strip()
    iso = _ISO.fullmatch(text)
    if iso:
        return _calendar(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)), ambiguous=False)
    slash = _SLASH.fullmatch(text)
    if slash:
        first = int(slash.group(1))
        second = int(slash.group(2))
        year = int(slash.group(3))
        if first == second:
            return _calendar(year, first, second, ambiguous=False)
        if first <= 12 and second <= 12:
            return {
                "iso": None,
                "unparseable": False,
                "ambiguous": True,
                "reason": "ambiguous_day_month",
                "coerced": False,
                "future": False,
                "impossible": False,
            }
        if first > 12 and second <= 12:
            day, month = first, second
        elif second > 12 and first <= 12:
            day, month = second, first
        else:
            return _bad("invalid_calendar_date", impossible=True)
        return _calendar(year, month, day, ambiguous=False)
    named = _NAMED.fullmatch(text)
    if named:
        month = _MONTHS[named.group(2).casefold()]
        return _calendar(int(named.group(3)), month, int(named.group(1)), ambiguous=False)
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


def annotate(parsed: dict, *, on: date | None) -> dict:
    """Flag a future date against the question date. Do not replace it."""

    reading = dict(parsed)
    reading["future"] = False
    parsed_day = as_date(reading)
    if parsed_day is not None and on is not None and parsed_day > on:
        reading["future"] = True
    return reading


def add_months(day: date, months: int) -> dict:
    """Move a whole number of calendar months. Do not invent 29 February."""

    if type(months) is not int:
        return {"date": None, "unparseable": True, "coerced": False, "day_clamped": False}
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    last = calendar.monthrange(year, month)[1]
    clamped = day.day > last
    parsed = date(year, month, min(day.day, last))
    return {
        "date": parsed.isoformat(),
        "unparseable": False,
        "coerced": False,
        "day_clamped": clamped,
    }


def twentieth_weekday_following(day: date) -> date:
    """The 20th Monday-to-Friday after day. Bank holidays are not removed."""

    count = 0
    cursor = day
    while count < 20:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            count += 1
    return cursor


def _calendar(year: int, month: int, day: int, *, ambiguous: bool) -> dict:
    try:
        parsed = date(year, month, day)
    except ValueError:
        return _bad("invalid_calendar_date", impossible=True)
    return {
        "iso": parsed.isoformat(),
        "unparseable": False,
        "ambiguous": ambiguous,
        "reason": None,
        "coerced": False,
        "future": False,
        "impossible": False,
    }


def _bad(reason: str, *, impossible: bool = False) -> dict:
    return {
        "iso": None,
        "unparseable": True,
        "ambiguous": False,
        "reason": reason,
        "coerced": False,
        "future": False,
        "impossible": impossible,
    }
