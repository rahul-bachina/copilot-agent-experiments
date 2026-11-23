"""Schedule support and caller-source comparison.

A sentence supports the pinned invoice line only when that sentence affirms
invoices, a six-year period, and closure. A different period, a different
line id, a negation, or a carve-out does not support the line and is not
marked acceptable. "It is not true that invoices are kept for six years
after closure" is not support.

The caller schedule, inventory, and directory are not the pinned sources.
"""

from __future__ import annotations

import hashlib
import json
import re

if __package__ in {None, ""}:
    from negate import affirmed, denied_at, sentences
else:
    from .negate import affirmed, denied_at, sentences

_INVOICE = re.compile(r"\binvoices?\b", re.IGNORECASE)
_SIX = re.compile(r"\b(?:six years|6 years)\b", re.IGNORECASE)
_CLOSED = re.compile(r"\b(?:closed|closure)\b", re.IGNORECASE)
_OTHER_PERIOD = re.compile(
    r"\b(?:seven years|7 years|five years|5 years|one year|1 year|6 months)\b",
    re.IGNORECASE,
)
_LINE = re.compile(r"\bSCH-[A-Z0-9-]+\b")
_CARVE = re.compile(
    r"\b(?:except|unless|provided that|save where|subject to|apart from|other than|but only if)\b",
    re.IGNORECASE,
)
INVOICE_LINE = "SCH-FIN-01"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def differs(pinned: object, supplied: object) -> bool:
    if supplied is None:
        return False
    return canonical(pinned) != canonical(supplied)


def sentence_supports(text: str, line_id: str = INVOICE_LINE) -> dict:
    """Whether text supports the six-year paid-invoice line. The sentence is not stored."""

    supported = False
    carve = False
    denied = False
    for sentence in sentences(text or ""):
        row = _one(sentence, line_id)
        carve = carve or row["carve_out"]
        denied = denied or row["denied"]
        if row["supports"]:
            supported = True
    return {
        "line_id": line_id,
        "supports": supported,
        "carve_out": carve,
        "denied": denied,
        "marked_acceptable": False,
        "sentence_stored": False,
    }


def _one(sentence: str, line_id: str) -> dict:
    has_parts = bool(_INVOICE.search(sentence) and _SIX.search(sentence) and _CLOSED.search(sentence))
    carve = bool(_CARVE.search(sentence))
    other_period = bool(_OTHER_PERIOD.search(sentence))
    other_line = any(match.group(0) != line_id for match in _LINE.finditer(sentence))
    denied = False
    if has_parts:
        match = _SIX.search(sentence)
        if match is not None and denied_at(sentence, match.group(0), match.start()):
            denied = True
        if not affirmed(sentence, "invoices") and not affirmed(sentence, "invoice"):
            denied = True
    supports = has_parts and not carve and not other_period and not other_line and not denied
    return {"supports": supports, "carve_out": carve and has_parts, "denied": denied}


def period_months(years: object, months: object) -> tuple[int | None, str]:
    if type(years) is not int or type(months) is not int:
        return None, "unparseable"
    if years < 0 or months < 0 or years > 200 or months > 240:
        return None, "out_of_range"
    return years * 12 + months, "ok"
