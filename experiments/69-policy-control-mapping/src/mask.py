"""Mask phone numbers, email addresses, dates of birth, postal addresses, and names.

Counts do not store the matched text. A count is not a claim that the policy
was anonymised. A category count below the suppression threshold is not published.
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
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+"
    r"(?:Street|Road|Avenue|Lane|Close|Drive|Way)\b"
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

SUPPRESS_BELOW = 5


def mask_text(text: str) -> tuple[str, dict]:
    """Return masked text and counts. Matched substrings are not in the counts."""

    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", _report({})
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
    return out, _report(counts)


def publish_counts(counts: dict[str, int]) -> dict:
    """Publish a count only when it is zero or at least the threshold.

    A count of one, two, three, or four people is not published. Five is this
    starter's threshold. A statistics authority page was not opened for it.
    """

    published: dict[str, int | None] = {}
    suppressed: list[str] = []
    for kind in _TOKENS:
        count = int(counts.get(kind, 0))
        if 0 < count < SUPPRESS_BELOW:
            published[kind] = None
            suppressed.append(kind)
        else:
            published[kind] = count
    return {
        "counts": published,
        "suppressed_categories": suppressed,
        "threshold": SUPPRESS_BELOW,
        "threshold_source": "this starter, not a statistics authority page",
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
    }


def _report(found: dict[str, int]) -> dict:
    raw = {kind: int(found.get(kind, 0)) for kind in _TOKENS}
    published = publish_counts(raw)
    published["categories_masked"] = [kind for kind, count in raw.items() if count]
    published["any"] = bool(published["categories_masked"])
    return published
