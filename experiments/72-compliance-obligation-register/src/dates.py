"""Dates on an obligation. Nothing unreadable is turned into today or into zero.

A numeric date such as 01/02/2026 is ambiguous and stays unreadable. A day
that does not exist, including 29 February in a year that is not a leap year,
stays unreadable. Adding months does not move the day to the last valid day.
"""

from __future__ import annotations

import re
from datetime import date, datetime

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
_MONTH = (
    "January|February|March|April|May|June|July|August|September|"
    "October|November|December"
)
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_DMY_NAME = re.compile(
    rf"^(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH})\s+(\d{{4}})$",
    re.IGNORECASE,
)
_MDY_NAME = re.compile(
    rf"^({_MONTH})\s+(\d{{1,2}})(?:st|nd|rd|th)?[,]?\s+(\d{{4}})$",
    re.IGNORECASE,
)
_AMBIGUOUS = re.compile(
    r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$"
    r"|^\d{4}/\d{1,2}/\d{1,2}$"
    r"|^\d{1,2}-\d{1,2}-\d{4}$"
)
_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]")
NOT_STATED = "not stated"


def parse_as_of(value: object) -> date:
    """The date the question is about. A datetime is not truncated."""

    if isinstance(value, datetime):
        raise ValueError("as_of must be a date")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value:
        raise ValueError("as_of must be a date")
    if not _ISO.fullmatch(value):
        raise ValueError("as_of must be YYYY-MM-DD")
    try:
        return date(int(value[0:4]), int(value[5:7]), int(value[8:10]))
    except ValueError as exc:
        raise ValueError("as_of must be a real date") from exc


def _blank(*, unparseable: bool = False, ambiguous: bool = False, not_stated: bool = False) -> dict:
    return {
        "iso": None,
        "display": NOT_STATED if not_stated else "unparseable",
        "unparseable": unparseable,
        "ambiguous": ambiguous,
        "not_stated": not_stated,
        "coerced": False,
        "chosen": False,
    }


def _from_parts(year: int, month: int, day: int) -> dict:
    try:
        built = date(year, month, day)
    except ValueError:
        return _blank(unparseable=True)
    return {
        "iso": built.isoformat(),
        "display": built.isoformat(),
        "unparseable": False,
        "ambiguous": False,
        "not_stated": False,
        "coerced": False,
        "chosen": False,
    }


def parse_date_token(value: object) -> dict:
    """One supplied date. Two readings are not reduced to one."""

    if value is None or value == "":
        return _blank(not_stated=True)
    if isinstance(value, datetime):
        return _blank(unparseable=True)
    if isinstance(value, date):
        return _from_parts(value.year, value.month, value.day)
    if not isinstance(value, str):
        return _blank(unparseable=True)
    text = value.strip()
    if text.casefold() == NOT_STATED:
        return _blank(not_stated=True)
    if not text:
        return _blank(not_stated=True)
    if _DATETIME.match(text) or _AMBIGUOUS.fullmatch(text):
        return _blank(unparseable=True, ambiguous=True)
    iso = _ISO.fullmatch(text)
    dmy = _DMY_NAME.fullmatch(text)
    mdy = _MDY_NAME.fullmatch(text)
    readings = []
    if iso is not None:
        readings.append((int(iso.group(1)), int(iso.group(2)), int(iso.group(3))))
    if dmy is not None:
        readings.append((int(dmy.group(3)), MONTHS[dmy.group(2).lower()], int(dmy.group(1))))
    if mdy is not None:
        readings.append((int(mdy.group(3)), MONTHS[mdy.group(1).lower()], int(mdy.group(2))))
    if not readings:
        return _blank(unparseable=True)
    unique = list(dict.fromkeys(readings))
    if len(unique) != 1:
        row = _blank(unparseable=True, ambiguous=True)
        row["chosen"] = False
        return row
    return _from_parts(*unique[0])


def add_months(value: date, months: int) -> date | None:
    """A day that does not exist in the target month is not moved."""

    if isinstance(months, bool) or not isinstance(months, int) or months < 0:
        return None
    index = value.month - 1 + months
    year = value.year + index // 12
    month = index % 12 + 1
    try:
        return date(year, month, value.day)
    except ValueError:
        return None


def in_force(effective_from: dict, effective_to: dict, status: str, as_of: date) -> dict:
    """Pin status and the two dates. A denial in the text is not an input."""

    problems = []
    if effective_from["unparseable"] or effective_to["unparseable"]:
        problems.append("unparseable_date")
    start = effective_from["iso"]
    end = effective_to["iso"]
    if status == "superseded":
        return {"in_force": False, "reason": "superseded", "problems": problems, "coerced": False}
    if start is None and effective_from["not_stated"] and end is None and effective_to["not_stated"]:
        if problems:
            return {"in_force": None, "reason": "unparseable_date", "problems": problems, "coerced": False}
        return {"in_force": None, "reason": "dates_not_stated", "problems": problems, "coerced": False}
    if problems and (start is None or (effective_to["unparseable"] and end is None and not effective_to["not_stated"])):
        return {"in_force": None, "reason": "unparseable_date", "problems": problems, "coerced": False}
    if start is not None and start > as_of.isoformat():
        return {"in_force": False, "reason": "not_yet_in_force", "problems": problems, "coerced": False}
    if end is not None and end < as_of.isoformat():
        return {"in_force": False, "reason": "effective_to_passed", "problems": problems, "coerced": False}
    if start is None and not effective_from["not_stated"]:
        return {"in_force": None, "reason": "unparseable_date", "problems": problems, "coerced": False}
    return {"in_force": True, "reason": "in_force_on_question_date", "problems": problems, "coerced": False}


def review_stale(review: dict, as_of: date) -> dict:
    """A review date on the question date is stale. That is this starter's rule."""

    if review["not_stated"]:
        return {"stale": None, "reason": "not_stated", "coerced": False}
    if review["unparseable"] or review["iso"] is None:
        return {"stale": None, "reason": "unparseable", "coerced": False}
    stale = review["iso"] <= as_of.isoformat()
    return {
        "stale": stale,
        "reason": "on_or_before_question_date" if stale else "after_question_date",
        "coerced": False,
        "rule": "A review date on the question date is stale. This is the starter's rule, not a statute.",
    }
