"""Mask phone numbers, email addresses, dates of birth, postal addresses, and names.

Counts do not store the matched text. A count is not a claim that the pack
was anonymised. UK identifiers are counted by Experiment 08. A headcount
below 5 is not published, and neither is a difference or a percentage of it,
including when those figures sit under another field name.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from sources import SMALL_NUMBER_THRESHOLD
else:
    from .sources import SMALL_NUMBER_THRESHOLD

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
_PEOPLE = re.compile(
    r"\b(\d+|one|two|three|four)\s+"
    r"(employees|people|persons|individuals|residents|beneficiaries|staff|workers|children)\b",
    re.I,
)
_SMALL_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}
_PERCENT_IN_SENTENCE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|per cent)\b", re.I)
_COUNT_FIELDS = (
    "people_affected",
    "headcount",
    "affected_count",
    "count",
    "staff_count",
    "resident_count",
)
_DERIVED_FIELDS = ("difference", "percentage", "percent", "delta", "share", "change_in_headcount")

_TOKENS = {
    "phone": "[phone]",
    "email": "[email]",
    "date_of_birth": "[date of birth]",
    "postal_address": "[address]",
    "personal_name": "[name]",
}


def mask_text(text: str) -> tuple[str, dict]:
    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", empty_mask()
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
    masked, suppression = suppress_small_counts(out)
    report = empty_mask()
    report["counts"] = {kind: int(counts.get(kind, 0)) for kind in _TOKENS}
    report["any"] = any(report["counts"].values())
    report["small_number"] = suppression
    return masked, report


def empty_mask() -> dict:
    return {
        "counts": {kind: 0 for kind in _TOKENS},
        "any": False,
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "masked_text_included": True,
        "small_number": _suppression(False, unreadable=False),
    }


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
        if count is None or count >= SMALL_NUMBER_THRESHOLD:
            continue
        found.append((match.start(1), match.end(1), count))
    return found


def suppress_small_counts(text: str) -> tuple[str, dict]:
    """Replace a headcount below 5, and a percentage in the same sentence."""

    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", _suppression(False, unreadable=False)
    spans = people_count_spans(text)
    if not spans:
        return text, _suppression(False, unreadable=False)
    extra: list[tuple[int, int]] = []
    for sentence_match in re.finditer(r"[^.!?\n]+", text):
        sentence = sentence_match.group(0)
        if not people_count_spans(sentence):
            continue
        for percent in _PERCENT_IN_SENTENCE.finditer(sentence):
            extra.append((sentence_match.start() + percent.start(), sentence_match.start() + percent.end()))
    replacements = [(start, end, "[suppressed count]") for start, end, _count in spans]
    replacements.extend((start, end, "[suppressed percentage]") for start, end in extra)
    replacements.sort(key=lambda item: item[0])
    out = text
    for start, end, token in reversed(replacements):
        out = out[:start] + token + out[end:]
    return out, _suppression(True, unreadable=False)


def suppress_request_fields(payload: dict, texts: list[str]) -> dict:
    """Withhold a small count wherever it was filed, including a difference or a percentage."""

    fields: list[str] = []
    unreadable = False
    applied = False
    for name in _COUNT_FIELDS:
        if name not in payload:
            continue
        reading = _count_reading(payload.get(name))
        if reading["unreadable"]:
            unreadable = True
            fields.append(name)
            continue
        if reading["small"]:
            applied = True
            fields.append(name)
    for text in texts:
        if people_count_spans(text or ""):
            applied = True
            if "text" not in fields:
                fields.append("text")
    if applied:
        for name in _DERIVED_FIELDS:
            if name in payload and name not in fields:
                fields.append(name)
    report = _suppression(applied, unreadable=unreadable)
    report["fields"] = fields
    return report


def _count_reading(value: object) -> dict:
    if value is None or value == "":
        return {"small": False, "unreadable": True}
    if isinstance(value, bool) or isinstance(value, float):
        return {"small": False, "unreadable": True}
    if isinstance(value, int):
        if value < 0:
            return {"small": False, "unreadable": True}
        return {"small": value < SMALL_NUMBER_THRESHOLD, "unreadable": False}
    if isinstance(value, str):
        folded = value.strip().casefold()
        if folded in _SMALL_WORDS:
            return {"small": True, "unreadable": False}
        if folded.isdigit():
            number = int(folded)
            return {"small": number < SMALL_NUMBER_THRESHOLD, "unreadable": False}
        return {"small": False, "unreadable": True}
    return {"small": False, "unreadable": True}


def _suppression(applied: bool, *, unreadable: bool) -> dict:
    return {
        "applied": applied,
        "unreadable": unreadable,
        "threshold": SMALL_NUMBER_THRESHOLD,
        "threshold_is_starter_rule": True,
        "published_values": None,
        "published_difference": None,
        "published_percentage": None,
        "published_count": None,
        "headcount": None,
        "people_affected": None,
        "affected_count": None,
        "delta": None,
        "share": None,
        "coerced": False,
        "described_as_anonymised": False,
    }
