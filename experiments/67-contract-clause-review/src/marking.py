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
    from cues import phrase_is_denied, sentences
else:
    from .cues import phrase_is_denied, sentences

RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
_LABELS = ("TOP SECRET", "OFFICIAL-SENSITIVE", "SECRET", "OFFICIAL")
_RETENTION = re.compile(r"RETENTION:\s*([^\n.;]+)", re.IGNORECASE)
_LEGAL_HOLD = re.compile(r"\bLEGAL HOLD\b", re.IGNORECASE)
_CLEARANCE_CLAIM = re.compile(r"\bmy clearance is\b", re.IGNORECASE)


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


def content_markings(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        if _CLEARANCE_CLAIM.search(sentence):
            continue
        for label in markings_in(sentence):
            if phrase_is_denied(sentence, label):
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

    if ceiling not in RANK:
        return True
    if marking is None:
        return False
    if marking not in RANK:
        return True
    return RANK[marking] > RANK[ceiling]


def metadata_markings(value: object) -> tuple[list[str], bool]:
    """Labels, and whether the metadata value could not be read. Nothing is coerced."""

    if value is None or value == "" or value == []:
        return [], False
    if isinstance(value, str):
        return markings_in(value), False
    if isinstance(value, list):
        found: list[str] = []
        bad = False
        for item in value:
            if isinstance(item, str):
                for label in markings_in(item):
                    if label not in found:
                        found.append(label)
            elif item not in (None, ""):
                bad = True
        return found, bad
    return [], True


def retention_labels(metadata: object, text: str) -> tuple[list[str], bool]:
    kept: list[str] = []
    unparseable = False
    if isinstance(metadata, str) and metadata.strip():
        kept.append(metadata.strip())
    elif isinstance(metadata, list):
        for item in metadata:
            if isinstance(item, str) and item.strip() and item.strip() not in kept:
                kept.append(item.strip())
            elif item not in (None, "") and not isinstance(item, str):
                unparseable = True
    elif metadata not in (None, "", []):
        unparseable = True
    for match in _RETENTION.findall(text or ""):
        for part in re.split(r"\s+and\s+|,\s*", match):
            label = part.strip(" .")
            if label and label not in kept and not phrase_is_denied(match, label):
                kept.append(label)
    return kept, unparseable


def legal_hold(metadata: object, text: str) -> tuple[bool, bool]:
    """A hold in either place is kept. A denial on the page does not clear metadata.

    Returns (held, metadata_unparseable). A string is not coerced to true.
    """

    unparseable = False
    held = False
    if metadata is True:
        held = True
    elif metadata is False or metadata is None:
        held = False
    else:
        unparseable = True
    for sentence in sentences(text or ""):
        if not _LEGAL_HOLD.search(sentence):
            continue
        if phrase_is_denied(sentence, "LEGAL HOLD"):
            continue
        held = True
    return held, unparseable
