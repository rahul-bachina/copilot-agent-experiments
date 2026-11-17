"""Mask phone numbers, email addresses, dates of birth, postal addresses, and personal names.

Matched values are not returned. A count is not a claim that the text was anonymised.
Names of the manager and the employee, taken from the directory, are left in place.
"""

from __future__ import annotations

import re

_PHONE = re.compile(
    r"(?:\+44[\s-]?\d(?:[\s-]?\d){9,12}|07\d{3}[\s-]?\d{6}|0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4})"
)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_DOB = re.compile(
    r"\b(?:date of birth|d\.?o\.?b\.?|born on)\b[:\s-]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    re.I,
)
_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
_STREET = re.compile(
    r"\b\d{1,4}\s+[A-Z][a-z]+\s+(?:Street|Road|Avenue|Lane|Close|Drive|Way)\b",
)
_NAME = re.compile(
    r"\bmy name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
    r"|\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+([A-Z][a-z]+)\b",
    re.I,
)

_TOKENS = {
    "phone": "[phone]",
    "email": "[email]",
    "date_of_birth": "[date of birth]",
    "postal_address": "[address]",
    "personal_name": "[name]",
}


def _keep(name: str, keep_names: set[str]) -> bool:
    words = {word.casefold() for word in name.split() if word}
    if not words:
        return False
    for phrase in keep_names:
        kept = {word.casefold() for word in phrase.split() if word}
        if words <= kept:
            return True
    return False


def mask_text(text: str, keep_names: set[str] | None = None) -> tuple[str, dict]:
    """Return masked text and counts. The matched substrings are not in the counts."""
    keep = keep_names or set()
    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", _counts({})
    matches: list[tuple[int, int, str]] = []
    for kind, pattern in (
        ("email", _EMAIL),
        ("phone", _PHONE),
        ("date_of_birth", _DOB),
        ("postal_address", _POSTCODE),
        ("postal_address", _STREET),
    ):
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), kind))
    for match in _NAME.finditer(text):
        name = match.group(1) or match.group(2) or ""
        if _keep(name, keep):
            continue
        matches.append((match.start(), match.end(), "personal_name"))
    matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    chosen: list[tuple[int, int, str]] = []
    cursor = -1
    for start, end, kind in matches:
        if start < cursor:
            continue
        chosen.append((start, end, kind))
        cursor = end
    counts: dict[str, int] = {}
    out = text
    for start, end, kind in reversed(chosen):
        out = out[:start] + _TOKENS[kind] + out[end:]
        counts[kind] = counts.get(kind, 0) + 1
    return out, _counts(counts)


def _counts(found: dict[str, int]) -> dict:
    counts = {kind: int(found.get(kind, 0)) for kind in _TOKENS}
    return {
        "counts": counts,
        "any": any(counts.values()),
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
    }


def merge_counts(rows: list[dict]) -> dict:
    totals = {kind: 0 for kind in _TOKENS}
    for row in rows:
        for kind, count in (row.get("counts") or {}).items():
            if kind in totals and isinstance(count, int):
                totals[kind] += count
    return {
        "counts": totals,
        "any": any(totals.values()),
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
    }
