"""Mask names, phones, emails, dates of birth, addresses, and NHS numbers.

UK identifiers are also counted by Experiment 08. This module does not copy
that gateway. A count is not a claim that the note was anonymised. Matched
values are not stored.
"""

from __future__ import annotations

import re

_SECRET = re.compile(
    r"(?i)\b(?:client_secret|api[_-]?key|password|secret)\b\s*[:=]\s*\S+"
    r"|Bearer\s+[A-Za-z0-9._\-]{8,}"
    r"|AccountKey=[^;\s]+"
    r"|SharedAccessSignature\s+\S+"
)
_PHONE = re.compile(
    r"(?:\+44[\s-]?\d(?:[\s-]?\d){9,12}|07\d{3}[\s-]?\d{6}|0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4})"
)
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_DOB = re.compile(
    r"\b(?:date of birth|d\.?o\.?b\.?|born on)\b(?:\s+\w+){0,4}\s*[:\-]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    re.I,
)
_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
_STREET = re.compile(
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+"
    r"(?:Street|Road|Avenue|Lane|Close|Drive|Way|Court|Gardens)\b"
)
_NHS = re.compile(
    r"\b(?:NHS\s*(?:numbers?|no\.?)?)\s*[:#-]?\s*(?:\d{3}[\s-]?\d{3}[\s-]?\d{4}|\d{10})\b",
    re.I,
)
_NAME = re.compile(
    r"\bmy name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
    r"|\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+([A-Z][a-z]+)\b"
    r"|\bmy (?:spouse|husband|wife|partner|brother|sister|mother|father|son|daughter|uncle|aunt)(?:'s name)? is\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
    re.I,
)
_PEOPLE = re.compile(
    r"\b(\d+|one|two|three|four)\s+"
    r"(employees|people|persons|individuals|residents|beneficiaries|staff|workers|"
    r"children|adults|neighbours|visitors|attendees)\b",
    re.I,
)
_SMALL_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}
_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|per cent)\b", re.I)
_COUNT_FIELDS = (
    "headcount",
    "difference",
    "percentage",
    "person_count",
    "attendee_count",
    "n_people",
    "visitor_count",
    "resident_count",
)

_TOKENS = {
    "secret": "[secret]",
    "phone": "[phone]",
    "email": "[email]",
    "date_of_birth": "[date of birth]",
    "postal_address": "[address]",
    "personal_name": "[name]",
    "nhs_number": "[NHS number]",
}


def empty_mask() -> dict:
    return {
        "counts": {kind: 0 for kind in _TOKENS},
        "any": False,
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "masked_text_included": False,
    }


def mask_text(text: str, names: list[str] | None = None) -> tuple[str, dict]:
    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", empty_mask()
    matches: list[tuple[int, int, str]] = []
    for kind, pattern in (
        ("secret", _SECRET),
        ("email", _EMAIL),
        ("nhs_number", _NHS),
        ("phone", _PHONE),
        ("date_of_birth", _DOB),
        ("postal_address", _POSTCODE),
        ("postal_address", _STREET),
    ):
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), kind))
    for match in _NAME.finditer(text):
        matches.append((match.start(), match.end(), "personal_name"))
    for name in names or []:
        if not isinstance(name, str) or len(name.strip()) < 3:
            continue
        pattern = re.compile(rf"\b{re.escape(name.strip())}\b", re.IGNORECASE)
        for match in pattern.finditer(text):
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
    report = empty_mask()
    report["counts"] = {kind: int(counts.get(kind, 0)) for kind in _TOKENS}
    report["any"] = any(report["counts"].values())
    report["masked_text_included"] = bool(report["any"])
    return out, report


def add_counts(left: dict, right: dict) -> dict:
    merged = empty_mask()
    for kind in _TOKENS:
        merged["counts"][kind] = int(left.get("counts", {}).get(kind, 0)) + int(right.get("counts", {}).get(kind, 0))
    merged["any"] = any(merged["counts"].values())
    merged["masked_text_included"] = bool(left.get("masked_text_included") or right.get("masked_text_included"))
    return merged


def people_count_spans(text: str) -> list[tuple[int, int, int | None]]:
    """Small headcounts. A number of 5 or more is not in this list."""

    found = []
    if not text:
        return found
    for match in _PEOPLE.finditer(text):
        raw = match.group(1).casefold()
        if raw.isdigit():
            count = int(raw)
        else:
            count = _SMALL_WORDS.get(raw)
        if count is None or count >= 5:
            continue
        found.append((match.start(1), match.end(1), count))
    return found


def suppress_small_counts(text: str) -> tuple[str, dict]:
    """Replace a headcount below 5, and a percentage in the same sentence.

    Published difference, percentage, and count fields stay empty when any
    count is small. Five is this starter's threshold. It is not anonymisation.
    A missing count is not stored as zero.
    """

    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", suppression_fields(False)
    spans = people_count_spans(text)
    if not spans:
        return text, suppression_fields(False)
    extra: list[tuple[int, int]] = []
    for sentence_match in re.finditer(r"[^.!?\n]+", text):
        sentence = sentence_match.group(0)
        if not people_count_spans(sentence):
            continue
        for percent in _PERCENT.finditer(sentence):
            extra.append((sentence_match.start() + percent.start(), sentence_match.start() + percent.end()))
    replacements = [(start, end, "[suppressed count]") for start, end, _count in spans]
    replacements.extend((start, end, "[suppressed percentage]") for start, end in extra)
    replacements.sort(key=lambda item: item[0])
    out = text
    cursor = len(text)
    for start, end, token in reversed(replacements):
        if end > cursor:
            continue
        out = out[:start] + token + out[end:]
        cursor = start
    return out, suppression_fields(True)


def suppression_fields(applied: bool) -> dict:
    fields = {name: None for name in _COUNT_FIELDS}
    fields.update({
        "applied": applied,
        "threshold": 5,
        "values_stored": False,
        "coerced": False,
        "described_as_anonymised": False,
    })
    return fields
