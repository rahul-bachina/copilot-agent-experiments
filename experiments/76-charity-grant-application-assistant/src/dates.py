"""Parse dates. Do not coerce an unreadable or ambiguous value.

The question date and the funder deadline come from the caller and the
pinned brief. Today is not used.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")


def parse_date(value: object) -> dict:
    """Return a reading. coerced is always false. No date is invented."""

    if value is None or value == "":
        return _bad("missing")
    if not isinstance(value, str):
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
        if first <= 12 and second <= 12:
            return {
                "iso": None,
                "unparseable": False,
                "ambiguous": True,
                "reason": "ambiguous_day_month",
                "coerced": False,
            }
        if first > 12 and second <= 12:
            day, month = first, second
        elif second > 12 and first <= 12:
            day, month = second, first
        else:
            return _bad("invalid_calendar_date")
        return _calendar(year, month, day, ambiguous=False)
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


def shift_days(day: date, offset: object) -> dict:
    """Add an integer day offset. A string or a boolean is not turned into 0."""

    if type(offset) is not int:
        return {"date": None, "offset_days": None, "unparseable": True, "coerced": False}
    return {
        "date": (day + timedelta(days=offset)).isoformat(),
        "offset_days": offset,
        "unparseable": False,
        "coerced": False,
    }


def subtract_months(day: date, months: object) -> dict:
    """Move back a whole number of calendar months. Do not invent 29 February."""

    if type(months) is not int or months < 0:
        return {"date": None, "unparseable": True, "coerced": False}
    month_index = day.month - 1 - months
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


def _calendar(year: int, month: int, day: int, *, ambiguous: bool) -> dict:
    try:
        parsed = date(year, month, day)
    except ValueError:
        return _bad("invalid_calendar_date")
    return {
        "iso": parsed.isoformat(),
        "unparseable": False,
        "ambiguous": ambiguous,
        "reason": None,
        "coerced": False,
    }


def _bad(reason: str) -> dict:
    return {
        "iso": None,
        "unparseable": True,
        "ambiguous": False,
        "reason": reason,
        "coerced": False,
    }
