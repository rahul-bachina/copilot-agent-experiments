"""Dates stated in a notice, or computed from a formula the notice states.

An unreadable token stays unreadable. It is not replaced with today, with
zero, or with the last valid day of a month. A missing date is the string
"not stated".
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

MONTHS = {
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

_SPOKEN = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(\d{4})\b",
    re.IGNORECASE,
)
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_EFFECTIVE = re.compile(
    r"(?:effective from|effective on|comes into effect on|comes into force on|"
    r"is effective from)\s+([^.]+)",
    re.IGNORECASE,
)
_CLOSE = re.compile(
    r"(?:consultation closes on|consultation close date is|"
    r"representations may be made until|responses must be received by)\s+([^.]+)",
    re.IGNORECASE,
)
_REL_EFFECTIVE = re.compile(
    r"comes into force\s+(\d+)\s+(day|days|month|months)\s+after publication",
    re.IGNORECASE,
)
_REL_CLOSE = re.compile(
    r"consultation closes\s+(\d+)\s+(day|days|month|months)\s+after publication",
    re.IGNORECASE,
)

NOT_STATED = "not stated"


def parse_as_of(value: object) -> date:
    """The date the question is about. A datetime is not truncated to today."""

    if isinstance(value, datetime):
        raise ValueError("as_of must be a date")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value:
        raise ValueError("as_of must be a date")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _build(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_date_token(token: str) -> tuple[date | None, bool]:
    """Return (date, unparseable). A token that looks like a date and is not one is unparseable."""

    text = (token or "").strip()
    if not text:
        return None, False
    iso = _ISO.search(text)
    spoken = _SPOKEN.search(text)
    if iso is None and spoken is None:
        return None, True
    if iso is not None:
        built = _build(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
        if built is None:
            return None, True
        return built, False
    month = MONTHS[spoken.group(2).lower()]
    built = _build(int(spoken.group(3)), month, int(spoken.group(1)))
    if built is None:
        return None, True
    return built, False


def add_months(value: date, months: int) -> date | None:
    """Add calendar months. A day that does not exist in the target month is not coerced."""

    if months < 0:
        return None
    index = value.month - 1 + months
    year = value.year + index // 12
    month = index % 12 + 1
    return _build(year, month, value.day)


def _shift(published: date | None, count: int, unit: str) -> date | None:
    if published is None or count < 0:
        return None
    unit = unit.lower()
    if unit in {"day", "days"}:
        return published + timedelta(days=count)
    if unit in {"month", "months"}:
        return add_months(published, count)
    return None


def _blank() -> dict:
    return {
        "dates": [],
        "display": NOT_STATED,
        "not_stated": True,
        "unparseable": False,
        "coerced": False,
        "multiple": False,
        "chosen": False,
        "sources": [],
    }


def _finish(found: list[dict]) -> dict:
    if not found:
        return _blank()
    unparseable = any(row["unparseable"] for row in found)
    dates = [row["iso"] for row in found if row["iso"]]
    unique = list(dict.fromkeys(dates))
    if not unique:
        blank = _blank()
        blank["unparseable"] = unparseable
        blank["sources"] = [{"kind": row["kind"], "formula": row["formula"]} for row in found]
        return blank
    return {
        "dates": unique,
        "display": unique[0] if len(unique) == 1 else "; ".join(unique),
        "not_stated": False,
        "unparseable": unparseable,
        "coerced": False,
        "multiple": len(unique) > 1,
        "chosen": False,
        "sources": [{"kind": row["kind"], "formula": row["formula"]} for row in found],
    }


def stated_dates(text: str, published: date | None) -> dict:
    """Effective and consultation-close dates from the notice text only."""

    effective: list[dict] = []
    close: list[dict] = []
    body = text or ""
    for match in _EFFECTIVE.finditer(body):
        parsed, bad = parse_date_token(match.group(1))
        effective.append(
            {
                "iso": parsed.isoformat() if parsed else None,
                "unparseable": bad or parsed is None,
                "kind": "stated",
                "formula": None,
            }
        )
    for match in _REL_EFFECTIVE.finditer(body):
        parsed = _shift(published, int(match.group(1)), match.group(2))
        formula = f"{match.group(1)} {match.group(2).lower()} after publication"
        effective.append(
            {
                "iso": parsed.isoformat() if parsed else None,
                "unparseable": parsed is None,
                "kind": "computed",
                "formula": formula,
            }
        )
    for match in _CLOSE.finditer(body):
        parsed, bad = parse_date_token(match.group(1))
        close.append(
            {
                "iso": parsed.isoformat() if parsed else None,
                "unparseable": bad or parsed is None,
                "kind": "stated",
                "formula": None,
            }
        )
    for match in _REL_CLOSE.finditer(body):
        parsed = _shift(published, int(match.group(1)), match.group(2))
        formula = f"{match.group(1)} {match.group(2).lower()} after publication"
        close.append(
            {
                "iso": parsed.isoformat() if parsed else None,
                "unparseable": parsed is None,
                "kind": "computed",
                "formula": formula,
            }
        )
    return {"effective": _finish(effective), "consultation_close": _finish(close)}


def day_gap(start: date, end: date) -> int:
    """Calendar days from start to end. The caller does not treat this as a statute."""

    return (end - start).days
