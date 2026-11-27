"""Mask secrets, phone numbers, email addresses, dates of birth, addresses, and names.

Counts do not store the matched text. A count is not a claim that the run
was anonymised. UK identifiers are counted by Experiment 08. The report says
whether masked text was included.
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
    r"\b(?:date of birth|d\.?o\.?b\.?|born on)\b[:\s-]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    re.I,
)
_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
_STREET = re.compile(
    r"\b\d{1,4}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Street|Road|Avenue|Lane|Close|Drive|Way)\b"
)
_ACCOUNT = re.compile(
    r"\b(?:account(?:\s+(?:number|no\.?|num))?|mpan|mprn)\b[:\s#-]*[A-Z0-9][A-Z0-9-]{5,}",
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
    r"(employees|people|persons|individuals|residents|beneficiaries|staff|workers|children)\b",
    re.I,
)
_SMALL_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}
_PERCENT_IN_SENTENCE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|per cent)\b", re.I)

_TOKENS = {
    "secret": "[secret]",
    "phone": "[phone]",
    "email": "[email]",
    "date_of_birth": "[date of birth]",
    "postal_address": "[address]",
    "personal_name": "[name]",
    "account_number": "[account number]",
}


def mask_text(text: str) -> tuple[str, dict]:
    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", empty_mask()
    matches: list[tuple[int, int, str]] = []
    for kind, pattern in (
        ("secret", _SECRET),
        ("email", _EMAIL),
        ("phone", _PHONE),
        ("date_of_birth", _DOB),
        ("postal_address", _POSTCODE),
        ("postal_address", _STREET),
        ("account_number", _ACCOUNT),
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
    report = empty_mask()
    report["counts"] = {kind: int(counts.get(kind, 0)) for kind in _TOKENS}
    report["any"] = any(report["counts"].values())
    return out, report


def empty_mask() -> dict:
    return {
        "counts": {kind: 0 for kind in _TOKENS},
        "any": False,
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "masked_text_included": False,
    }


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

    The published difference, percentage, and count fields stay empty when
    the count is small. Five is this starter's threshold. It is not a claim
    of anonymisation.
    """

    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else "", _suppression(False)
    spans = people_count_spans(text)
    if not spans:
        return text, _suppression(False)
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
    return out, _suppression(True)


def people_fields(distinct_people: int, text_suppressed: bool) -> dict:
    """A count of people below 5 is not published under any field name."""

    small = text_suppressed or (0 < distinct_people < 5)
    published = None if small else distinct_people
    return {
        "applied": small,
        "threshold": 5,
        "threshold_is_starter_rule": True,
        "published_values": None,
        "published_difference": None,
        "published_percentage": None,
        "published_count": published if not small else None,
        "headcount": None if small else published,
        "delta": None,
        "n": None if small else None,
        "share": None,
        "percentage": None,
        "difference": None,
        "people_affected": None if small else published,
        "named_people_published": False,
        "described_as_anonymised": False,
    }


def _suppression(applied: bool) -> dict:
    return people_fields(0 if not applied else 1, applied)
