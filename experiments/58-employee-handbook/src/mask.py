"""Count extra identifiers. Values are not stored and are not copied into the answer.

Experiment 08 covers UK identifiers such as National Insurance numbers.
This module adds phone numbers, email addresses, dates of birth, postal
addresses, and personal-name cues. A count is not a claim that the text
was anonymised.
"""

from __future__ import annotations

import re

_PHONE = re.compile(
    r"(?:\+44\s?\d{4}\s?\d{6}|\+44\s?\d{10}|07\d{9}|0\d{2,4}\s?\d{3,4}\s?\d{3,4})",
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
    r"\bmy name is\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b"
    r"|\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+[A-Z][a-z]+\b",
    re.IGNORECASE,
)


def mask_counts(text: str) -> dict:
    """Return counts only. Matched substrings are not returned."""

    if not isinstance(text, str) or not text:
        return _empty()
    postal = 0
    if _POSTCODE.search(text) or _STREET.search(text):
        postal = len(_POSTCODE.findall(text)) + len(_STREET.findall(text))
    counts = {
        "phone": len(_PHONE.findall(text)),
        "email": len(_EMAIL.findall(text)),
        "date_of_birth": len(_DOB.findall(text)),
        "postal_address": postal,
        "personal_name": len(_NAME.findall(text)),
    }
    return {
        "counts": counts,
        "any": any(counts.values()),
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
    }


def _empty() -> dict:
    return {
        "counts": {
            "phone": 0,
            "email": 0,
            "date_of_birth": 0,
            "postal_address": 0,
            "personal_name": 0,
        },
        "any": False,
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
    }
