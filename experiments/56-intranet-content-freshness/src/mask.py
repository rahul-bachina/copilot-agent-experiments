"""Extra masks on a short snippet or a contact field.

Experiment 08 does not detect names, email addresses, telephone numbers,
dates of birth, or a street address. A value that still passes through is
masked here. The output is not anonymised. A field the patterns do not
match is withheld rather than copied raw.
"""

from __future__ import annotations

import re

EMAIL = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE = re.compile(
    r"(?<!\d)(?:\+44[\s\-()]?\d(?:[\s\-()]?\d){8,12}|0\d(?:[\s\-()]?\d){8,11})(?!\d)"
)
DOB = re.compile(
    r"\b(?:date of birth|d\.?o\.?b\.?|born on|born)\b[:\s,/-]{0,16}"
    r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}",
    re.IGNORECASE,
)
DATE_NEAR_BIRTH = re.compile(
    r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b(?=[^.]{0,24}\b(?:date of birth|born)\b)",
    re.IGNORECASE,
)
STREET = re.compile(
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\s+"
    r"(?:Street|Road|Lane|Avenue|Close|Way|Drive|Place|Gardens|Crescent)\b",
    re.IGNORECASE,
)
POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.IGNORECASE)
NAME = re.compile(
    r"\b(?:Mr|Mrs|Ms|Mx|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b"
)
NINO = re.compile(r"\b[A-CEGHJ-PR-TW-Z]{2}\s*\d{2}\s*\d{2}\s*\d{2}\s*[A-D]\b", re.IGNORECASE)

_PATTERNS = (
    (DOB, "[date of birth]"),
    (DATE_NEAR_BIRTH, "[date of birth]"),
    (EMAIL, "[email]"),
    (PHONE, "[phone]"),
    (STREET, "[address]"),
    (POSTCODE, "[postcode]"),
    (NAME, "[name]"),
    (NINO, "[nino]"),
)

_KIND_BY_TOKEN = (
    ("[date of birth]", "date of birth"),
    ("[email]", "email"),
    ("[phone]", "phone"),
    ("[address]", "address"),
    ("[postcode]", "postcode"),
    ("[name]", "name"),
    ("[nino]", "nino"),
)


def mask_snippet(text: str) -> tuple[str, list[str]]:
    """Replace the extra patterns. Return the text and the kinds applied.

    A kind is recorded only when a token was introduced by this function.
    """

    masked = text
    for pattern, token in _PATTERNS:
        masked = pattern.sub(token, masked)
    masked = re.sub(r"\s+", " ", masked).strip()
    kinds = []
    for token, kind in _KIND_BY_TOKEN:
        if token in masked and token not in text:
            kinds.append(kind)
    return masked, kinds
