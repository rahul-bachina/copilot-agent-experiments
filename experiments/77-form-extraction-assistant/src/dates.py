"""Parse a stated date. An unreadable date stays unreadable.

12/12/2024 is one date, because the two numbers are the same.
03/04/2025 is ambiguous and is not given either reading.
01/13/2024 is not read as a US date. A future or impossible date is flagged.
Nothing here becomes today, and nothing becomes zero.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime

_MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_NAMED = re.compile(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})$", re.IGNORECASE)
_NUMERIC = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$")


def _row(stated: str | None) -> dict:
    return {
        "stated": stated,
        "iso": None,
        "ambiguous": False,
        "impossible": False,
        "unparseable": False,
        "future": False,
        "leap_day": False,
        "days_from_as_of": None,
        "coerced": False,
    }


def _valid(year: int, month: int, day: int) -> date | None:
    if month < 1 or month > 12 or day < 1 or year < 1:
        return None
    if day > calendar.monthrange(year, month)[1]:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _finish(
    parsed: date | None,
    *,
    on: date,
    stated: str,
    ambiguous: bool = False,
    impossible: bool = False,
    unparseable: bool = False,
) -> dict:
    row = _row(stated)
    row["ambiguous"] = ambiguous
    row["impossible"] = impossible
    row["unparseable"] = unparseable
    if parsed is None:
        return row
    row["iso"] = parsed.isoformat()
    row["leap_day"] = parsed.month == 2 and parsed.day == 29
    row["future"] = parsed > on
    row["days_from_as_of"] = (parsed - on).days
    return row


def parse_date(raw: object, *, on: date) -> dict:
    if not isinstance(on, date) or isinstance(on, datetime):
        raise TypeError("on must be a date")
    if not isinstance(raw, str):
        row = _row(None)
        row["unparseable"] = True
        return row
    text = raw.strip()
    if not text:
        row = _row(raw)
        row["unparseable"] = True
        return row

    iso = _ISO.fullmatch(text)
    if iso:
        parsed = _valid(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
        if parsed is None:
            return _finish(None, on=on, stated=text, impossible=True)
        return _finish(parsed, on=on, stated=text)

    named = _NAMED.fullmatch(text)
    if named:
        month = _MONTHS.get(named.group(2).casefold())
        if month is None:
            return _finish(None, on=on, stated=text, unparseable=True)
        parsed = _valid(int(named.group(3)), month, int(named.group(1)))
        if parsed is None:
            return _finish(None, on=on, stated=text, impossible=True)
        return _finish(parsed, on=on, stated=text)

    numeric = _NUMERIC.fullmatch(text)
    if numeric:
        first = int(numeric.group(1))
        second = int(numeric.group(2))
        year = int(numeric.group(3))
        if first < 1 or second < 1 or first > 31 or second > 31:
            return _finish(None, on=on, stated=text, impossible=True)
        if first == second:
            parsed = _valid(year, second, first)
            if parsed is None:
                return _finish(None, on=on, stated=text, impossible=True)
            return _finish(parsed, on=on, stated=text)
        if first > 12 and 1 <= second <= 12:
            parsed = _valid(year, second, first)
            if parsed is None:
                return _finish(None, on=on, stated=text, impossible=True)
            return _finish(parsed, on=on, stated=text)
        if second > 12 and first <= 12:
            return _finish(None, on=on, stated=text, impossible=True)
        if first <= 12 and second <= 12:
            return _finish(None, on=on, stated=text, ambiguous=True)
        return _finish(None, on=on, stated=text, impossible=True)

    return _finish(None, on=on, stated=text, unparseable=True)


def as_date(value: object) -> date:
    """The question date. Only an ISO calendar date is accepted."""

    if isinstance(value, datetime):
        raise ValueError("as_of must be an ISO date")
    if isinstance(value, date):
        return value
    if isinstance(value, str) and _ISO.fullmatch(value.strip()):
        parsed = parse_date(value.strip(), on=date(2000, 1, 1))
        if parsed["iso"] and not parsed["impossible"]:
            return date.fromisoformat(parsed["iso"])
    raise ValueError("as_of must be an ISO date")
