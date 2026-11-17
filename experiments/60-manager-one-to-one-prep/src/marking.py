"""Protective markings, legal holds, and retention labels.

The label is taken from the metadata and from the text. The higher label wins.
A clearance boast in the text is not a marking and is not a clearance.
A negation does not create a label. An instruction to strip a label does not
remove one that the metadata or another part of the text already states.
"""

from __future__ import annotations

import re

RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
CEILING = "OFFICIAL-SENSITIVE"
QUOTE_MAX = RANK[CEILING]

_CLEARANCE_BOAST = re.compile(
    r"\b(?:my|our|the user'?s?) clearance is\s+"
    r"(?:top secret|secret|official-sensitive|official sensitive|official)\b",
    re.I,
)
_NEGATION = re.compile(
    r"\b(?:it is not true that|it's not true that|it isn't true that|"
    r"not true that|it is not the case that|it isn't the case that|"
    r"does not include|does not mention|did not mention|did not include|"
    r"no sign of|there is no mention of|there was no|there is no)\b",
    re.I,
)
_BUT = re.compile(r"\b(?:but|however)\b", re.I)
_HOLD = re.compile(r"\b(?:legal hold|litigation hold|do not destroy)\b", re.I)
_RETENTION = re.compile(
    r"\bretention(?:\s+label)?\s*[:\-]\s*([A-Za-z0-9][A-Za-z0-9-]{1,40})",
    re.I,
)
_COVER_LINE = re.compile(
    r"(?im)^(?:protective marking|classification|handling)\s*[:\-]\s*(.+)$"
)


def negation_spans(text: str) -> list[tuple[int, int]]:
    """Spans governed by a denial, up to 'but' or 'however' or the end."""
    spans: list[tuple[int, int]] = []
    for match in _NEGATION.finditer(text):
        rest = text[match.end() :]
        stop = _BUT.search(rest)
        end = match.end() + (stop.start() if stop else len(rest))
        spans.append((match.start(), end))
    return spans


def in_negation(start: int, spans: list[tuple[int, int]]) -> bool:
    return any(begin <= start < end for begin, end in spans)


def strip_clearance_boasts(text: str) -> str:
    """Remove self-declared clearance. The directory is the clearance."""
    return _CLEARANCE_BOAST.sub(" ", text)


def labels_in_text(text: str) -> list[str]:
    """Labels that are not inside a denial. Higher handling is done by the caller."""
    if not text:
        return []
    spans = negation_spans(text)
    found: list[str] = []
    upper = text.upper()
    for label in ("TOP SECRET", "OFFICIAL-SENSITIVE", "OFFICIAL SENSITIVE", "SECRET", "OFFICIAL"):
        needle = label
        start = 0
        while True:
            at = upper.find(needle, start)
            if at < 0:
                break
            if not in_negation(at, spans):
                canonical = "OFFICIAL-SENSITIVE" if "SENSITIVE" in label else label
                if canonical == "SECRET" and upper[max(0, at - 4) : at].endswith("TOP "):
                    start = at + len(needle)
                    continue
                if canonical not in found:
                    found.append(canonical)
            start = at + len(needle)
    for match in _COVER_LINE.finditer(text):
        if in_negation(match.start(), spans):
            continue
        for label in labels_in_text(match.group(1)):
            if label not in found:
                found.append(label)
    return found


def highest(labels: list[str]) -> str | None:
    known = [label for label in labels if label in RANK]
    if not known:
        return None
    return max(known, key=lambda label: RANK[label])


def readable_marking(value) -> tuple[list[str], bool]:
    """Return labels and whether the metadata value could be read.

    An absent value is readable and unlabeled. A number, a bool, or a string
    with no known label is not readable. It is not treated as OFFICIAL.
    """
    if value is None or value == "":
        return [], True
    if isinstance(value, list):
        labels: list[str] = []
        for item in value:
            item_labels, ok = readable_marking(item)
            if not ok:
                return [], False
            labels.extend(item_labels)
        return labels, True
    if not isinstance(value, str):
        return [], False
    labels = labels_in_text(value)
    if not labels:
        return [], False
    return labels, True


def hold_indicated(text: str, metadata) -> bool:
    if metadata is True:
        return True
    if not isinstance(text, str) or not text:
        return False
    spans = negation_spans(text)
    for match in _HOLD.finditer(text):
        if not in_negation(match.start(), spans):
            return True
    return False


def retention_labels(text: str, metadata) -> list[str]:
    found: list[str] = []

    def add(value) -> None:
        if not isinstance(value, str):
            return
        token = value.strip()
        if token and token not in found:
            found.append(token)

    if isinstance(metadata, str):
        add(metadata)
    elif isinstance(metadata, list):
        for item in metadata:
            add(item)
    if isinstance(text, str):
        spans = negation_spans(text)
        for match in _RETENTION.finditer(text):
            if not in_negation(match.start(), spans):
                add(match.group(1))
    return found


def above_ceiling(label: str | None) -> bool:
    if label is None:
        return False
    return RANK.get(label, 0) > QUOTE_MAX


def clearance_rank(value) -> tuple[int | None, bool]:
    """Directory clearance. Unreadable is not raised to TOP SECRET."""
    if value is None or value == "":
        return RANK["OFFICIAL"], True
    if not isinstance(value, str):
        return None, False
    label = highest(labels_in_text(value))
    if label is None:
        return None, False
    return RANK[label], True
