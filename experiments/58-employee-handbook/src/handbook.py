"""Handbook versions, markings, and whether a sentence includes a claim.

A protective marking is taken from the metadata and from the text. The
higher label wins. A legal hold or a retention label in either place is
kept. An approval word inside the document is not HR approval.
"""

from __future__ import annotations

import re
from datetime import date, datetime

RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
_LABELS = ("TOP SECRET", "OFFICIAL-SENSITIVE", "SECRET", "OFFICIAL")

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_RETENTION = re.compile(r"RETENTION:\s*([^\n]+)", re.IGNORECASE)
_LEGAL_HOLD = re.compile(r"\bLEGAL HOLD\b", re.IGNORECASE)


def parse_day(value: object) -> date | None:
    """Return a calendar day, or None. Never substitute today or zero."""

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]


_BEFORE = re.compile(
    r"(?:not true that|does not include|doesn't include|do not include|never includes|"
    r"no longer includes|is not included|not included)\b(?:\s+\S+){0,8}\s*$",
    re.IGNORECASE,
)
_AFTER = re.compile(r"^\s+(?:is|are) not\b", re.IGNORECASE)


def phrase_is_denied(sentence: str, phrase: str) -> bool:
    """A negation that governs this phrase is not an inclusion of it.

    The check is the words around the phrase, not a flag on the whole sentence,
    so a later positive clause in another sentence can still count.
    """

    folded = sentence.casefold()
    needle = phrase.casefold()
    index = folded.find(needle)
    if index < 0:
        return False
    before = folded[:index]
    after = folded[index + len(needle):]
    if _BEFORE.search(before):
        return True
    if _AFTER.match(after):
        return True
    return False


def source_includes(text: str, phrase: str) -> bool:
    """True only when a sentence contains the phrase outside a negation.

    "It is not true that X includes Y" does not count as Y being included.
    """

    if not phrase:
        return False
    for sentence in sentences(text):
        if phrase.casefold() not in sentence.casefold():
            continue
        if phrase_is_denied(sentence, phrase):
            continue
        return True
    return False


def source_denies(text: str, phrase: str) -> bool:
    for sentence in sentences(text):
        if phrase_is_denied(sentence, phrase):
            return True
    return False


def markings_in(metadata: object, text: str) -> list[str]:
    """Longer labels are taken first, so OFFICIAL-SENSITIVE is not read as OFFICIAL."""

    found: list[str] = []
    if isinstance(metadata, str):
        upper = metadata.strip().upper()
        for label in _LABELS:
            if upper == label:
                found.append(label)
                break
    remaining = text
    for label in _LABELS:
        pattern = re.compile(rf"\b{re.escape(label)}\b")
        if pattern.search(remaining):
            if label not in found:
                found.append(label)
            remaining = pattern.sub(" ", remaining)
    return found


def higher_marking(labels: list[str]) -> str | None:
    if not labels:
        return None
    return max(labels, key=lambda label: RANK[label])


def document_text(document: dict) -> str:
    parts = []
    for section in document.get("sections") or []:
        if isinstance(section, dict) and isinstance(section.get("text"), str):
            parts.append(section["text"])
    return "\n".join(parts)


def retention_labels(document: dict, text: str) -> list[str]:
    """Keep every retention label. Do not drop one because another exists."""

    kept: list[str] = []
    raw = document.get("retention_label")
    if isinstance(raw, str) and raw.strip():
        kept.append(raw.strip())
    for match in _RETENTION.findall(text):
        label = match.strip()
        if label and label not in kept:
            kept.append(label)
    return kept


def legal_hold(document: dict, text: str) -> bool:
    """A hold in the metadata or on the page is kept. Neither clears the other."""

    if document.get("legal_hold") is True:
        return True
    return _LEGAL_HOLD.search(text) is not None


def above_ceiling(marking: str | None, ceiling: str) -> bool:
    if marking is None or ceiling not in RANK or marking not in RANK:
        return True
    return RANK[marking] > RANK[ceiling]


def in_force_on(document: dict, day: date) -> bool | None:
    """True, False, or None when a date cannot be parsed. None is not coerced."""

    start = parse_day(document.get("effective_from"))
    if start is None:
        return None
    if day < start:
        return False
    end_raw = document.get("effective_to")
    if end_raw in (None, ""):
        return True
    end = parse_day(end_raw)
    if end is None:
        return None
    return day <= end
