"""Parse a date and add a period. Nothing unreadable becomes today or zero.

Year-first dates (2024-02-29, 2024/02/29) are unambiguous. A numeric
day/month pair is ambiguous when both numbers are 1 to 12, and it is not
resolved. When one number is greater than 12, that number is the day.
29 February plus one year lands on 28 February in a non-leap year. That
clamp is a starter rule. It is not a statute.

The question date is the date the caller names. This module does not read
today's date.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime

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


def _make(year: int, month: int, day: int) -> tuple[date | None, str]:
    if year < MIN_YEAR or year > MAX_YEAR:
        return None, "out_of_range"
    try:
        return date(year, month, day), "ok"
    except ValueError:
        return None, "unparseable"


def parse_date(value: object) -> tuple[date | None, str]:
    """Return (date, status). Status is ok, missing, ambiguous, unparseable, or out_of_range."""

    if value is None or value == "":
        return None, "missing"
    if isinstance(value, datetime):
        return None, "unparseable"
    if isinstance(value, date):
        return _make(value.year, value.month, value.day)
    if isinstance(value, bool) or not isinstance(value, str):
        return None, "unparseable"
    text = value.strip()
    if not text:
        return None, "missing"
    matched = _ISO.match(text) or _ISO_SLASH.match(text)
    if matched:
        return _make(int(matched.group(1)), int(matched.group(2)), int(matched.group(3)))
    matched = _NUMERIC.match(text)
    if matched:
        first = int(matched.group(1))
        second = int(matched.group(2))
        year = int(matched.group(3))
        if first == 0 or second == 0 or first > 31 or second > 31:
            return None, "unparseable"
        if first <= 12 and second <= 12:
            return None, "ambiguous"
        if first > 12 and second > 12:
            return None, "unparseable"
        if first > 12:
            return _make(year, second, first)
        return _make(year, first, second)
    matched = _LONG.match(text)
    if matched:
        month = _MONTHS.get(matched.group(2).casefold())
        if month is None:
            return None, "unparseable"
        return _make(int(matched.group(3)), month, int(matched.group(1)))
    return None, "unparseable"


def add_period(start: date, years: object, months: object) -> tuple[date | None, str]:
    """Add whole years and months. A bad period is not replaced with zero."""

    if type(years) is not int or type(months) is not int:
        return None, "unparseable"
    if years < 0 or months < 0 or years > 200 or months > 240:
        return None, "out_of_range"
    index = start.month - 1 + months
    year = start.year + years + index // 12
    month = index % 12 + 1
    if year < MIN_YEAR or year > MAX_YEAR:
        return None, "out_of_range"
    last = calendar.monthrange(year, month)[1]
    day = min(start.day, last)
    return date(year, month, day), "ok"


def iso(value: date | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
