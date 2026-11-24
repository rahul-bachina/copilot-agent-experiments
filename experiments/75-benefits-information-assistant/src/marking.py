"""Protective markings, retention labels, and legal hold.

A label is taken from the metadata and from the page. A compound or
conflicting label takes the higher marking. A sentence that says
"my clearance is" is not a cover page. A hold or a retention label is kept.

The rank order is a starter rule. The Government Security Classifications
Policy was not re-opened for this experiment.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import sentences
else:
    from .negate import sentences

RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
_LABELS = ("TOP SECRET", "OFFICIAL-SENSITIVE", "SECRET", "OFFICIAL")
_RETENTION = re.compile(r"RETENTION:\s*([^\n.;]+)", re.IGNORECASE)
_LEGAL_HOLD = re.compile(r"\bLEGAL HOLD\b", re.IGNORECASE)
_CLEARANCE_CLAIM = re.compile(r"\bmy clearance is\b|\bi have .{0,20}clearance\b", re.IGNORECASE)
_NARROW_DENY = re.compile(
    r"(?:not true that|not the case that|is not|are not|no)\b(?:\s+\S+){0,8}\s*$",
    re.IGNORECASE,
)


def markings_in(text: str) -> list[str]:
    """Longer labels are taken first, so OFFICIAL-SENSITIVE is not read as OFFICIAL."""

    found: list[str] = []
    remaining = text or ""
    for label in _LABELS:
        pattern = re.compile(rf"\b{re.escape(label)}\b")
        if pattern.search(remaining):
            found.append(label)
            remaining = pattern.sub(" ", remaining)
    return found


def _narrowly_denied(sentence: str, phrase: str) -> bool:
    folded = sentence.casefold()
    index = folded.find(phrase.casefold())
    if index < 0:
        return False
    return _NARROW_DENY.search(folded[:index]) is not None


def content_markings(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        if _CLEARANCE_CLAIM.search(sentence):
            continue
        for label in markings_in(sentence):
            if _narrowly_denied(sentence, label):
                continue
            if label not in found:
                found.append(label)
    return found


def higher_marking(labels: list[str]) -> str | None:
    usable = [label for label in labels if label in RANK]
    if not usable:
        return None
    return max(usable, key=lambda label: RANK[label])


def above_ceiling(marking: str | None, ceiling: str | None) -> bool:
    """An unreadable ceiling withholds. No marking is not treated as SECRET."""

    if marking not in RANK:
        return False
    if ceiling not in RANK:
        return True
    return RANK[marking] > RANK[ceiling]


def retention_labels(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        if _narrowly_denied(sentence, "retention"):
            continue
        for match in _RETENTION.finditer(sentence):
            label = " ".join(match.group(1).split())
            if label and label not in found:
                found.append(label)
    return found


def legal_hold_in(text: str) -> bool:
    for sentence in sentences(text or ""):
        if not _LEGAL_HOLD.search(sentence):
            continue
        if _narrowly_denied(sentence, "legal hold"):
            continue
        return True
    return False
