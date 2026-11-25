"""Mask phone numbers, email addresses, dates of birth, postal addresses, and names.

Counts do not store the matched text. A count is not a claim that the
document was anonymised. Experiment 08 covers UK identifiers.
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
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Street|Road|Avenue|Lane|Close|Drive|Way)\b"
)
_NAME = re.compile(
    r"\bmy name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
    r"|\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+([A-Z][a-z]+)\b"
    r"|\bmy (?:spouse|husband|wife|partner|brother|sister|mother|father|son|daughter|uncle|aunt)(?:'s name)? is\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
    re.I,
)

_KINDS = ("phone", "email", "date_of_birth", "postal_address", "personal_name")


def mask_counts(text: str) -> dict:
    if not isinstance(text, str) or not text:
        return _report({})
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
        matches.append((match.start(), match.end(), "personal_name"))
    matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    counts: dict[str, int] = {}
    cursor = -1
    for start, end, kind in matches:
        if start < cursor:
            continue
        counts[kind] = counts.get(kind, 0) + 1
        cursor = end
    return _report(counts)


def _report(found: dict[str, int]) -> dict:
    counts = {kind: int(found.get(kind, 0)) for kind in _KINDS}
    return {
        "counts": counts,
        "any": any(counts.values()),
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "masked_text_included": False,
    }
