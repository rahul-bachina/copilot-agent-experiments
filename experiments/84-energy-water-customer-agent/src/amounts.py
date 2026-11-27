"""Parse a sterling amount. Do not coerce a malformed figure.

£1,25.00 is not one pound and twenty-five pence, and it is not 125.
It is flagged. A missing amount is not turned into 0.
"""

from __future__ import annotations

import re

_MALFORMED = re.compile(
    r"£\s*\d{1,3},\d{1,2}\.\d{2}"
    r"|£\s*\d+\.\d{3,}"
    r"|£\s*\d{1,3}(?:\.\d{3})+,\d{2}"
)
_OK = re.compile(r"^£?\s*(\d{1,3}(?:,\d{3})+|\d+)\.(\d{2})$")
_PLAIN = re.compile(r"^(\d{1,3}(?:,\d{3})+|\d+)\.(\d{2})$")


def parse_amount(value: object) -> dict:
    """Return a reading. coerced is always false. No figure is invented."""

    if value is None or value == "":
        return _bad("missing")
    if isinstance(value, bool) or not isinstance(value, str):
        return _bad("not_a_string")
    text = value.strip()
    if not text:
        return _bad("missing")
    if _MALFORMED.search(text) and _OK.fullmatch(text) is None and _PLAIN.fullmatch(text) is None:
        return _bad("malformed")
    if text.startswith("-") or text.startswith("£-") or text.startswith("-£"):
        return _bad("negative")
    match = _OK.fullmatch(text) or _PLAIN.fullmatch(text)
    if match is None:
        if "£" in text or re.search(r"\d", text):
            return _bad("malformed")
        return _bad("unparseable")
    pounds = match.group(1).replace(",", "")
    pence = match.group(2)
    if len(pounds) > 7:
        return _bad("out_of_range")
    return {
        "unparseable": False,
        "malformed": False,
        "negative": False,
        "coerced": False,
        "amount": f"{int(pounds)}.{pence}",
        "reason": None,
    }


def _bad(reason: str) -> dict:
    return {
        "unparseable": True,
        "malformed": reason == "malformed",
        "negative": reason == "negative",
        "coerced": False,
        "amount": None,
        "reason": reason,
    }


def reading_token(value: object) -> dict:
    """A meter reading is digits. A broken token is not zero."""

    if value is None or value == "":
        return _reading_bad("missing")
    if isinstance(value, bool) or not isinstance(value, str):
        return _reading_bad("not_a_string")
    text = value.strip()
    if re.search(r",\d{1,2}\.", text) or re.search(r"\.\d{1,2},", text):
        return _reading_bad("malformed")
    if not re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d+", text):
        return _reading_bad("malformed")
    digits = text.replace(",", "")
    if not digits.isdigit():
        return _reading_bad("malformed")
    if len(digits) < 1 or len(digits) > 8:
        return _reading_bad("out_of_range")
    return {
        "unparseable": False,
        "malformed": False,
        "coerced": False,
        "reading": digits,
        "reason": None,
    }


def _reading_bad(reason: str) -> dict:
    return {
        "unparseable": True,
        "malformed": reason in {"malformed", "out_of_range"},
        "coerced": False,
        "reading": None,
        "reason": reason,
    }
