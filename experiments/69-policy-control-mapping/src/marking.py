"""Protective markings, retention labels, and legal hold.

A label is taken from the metadata and from the page. A compound or
conflicting label takes the higher marking. A sentence that says
"my clearance is" is not a cover page. A hold or a retention label is kept.
The rank order is a starter rule. The Government Security Classifications
Policy was not re-opened for this experiment.
"""

from __future__ import annotations

import re

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
_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")


def sentences(text: str) -> list[str]:
    parts = [part.strip() for part in _SENTENCE.split(text or "") if part.strip()]
    return parts or ([text.strip()] if text and text.strip() else [])


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
    values: list[object] = []
    if isinstance(metadata, str):
        values.append(metadata)
    elif isinstance(metadata, list):
        values.extend(metadata)
    elif metadata not in (None, ""):
        unparseable = True
    blob = "\n".join(item for item in values if isinstance(item, str))
    blob = f"{blob}\n{text or ''}"
    for match in _RETENTION.finditer(blob):
        label = "RETENTION: " + " ".join(match.group(1).split())
        if label not in kept:
            kept.append(label)
    for item in values:
        if isinstance(item, str) and item.strip() and not _RETENTION.search(item) and "RETENTION" in item.upper():
            if item.strip() not in kept:
                kept.append(item.strip())
        elif item not in (None, "") and not isinstance(item, str):
            unparseable = True
    return kept, unparseable


def legal_hold(metadata: object, text: str) -> tuple[bool, bool]:
    """Return (held, unparseable). A string is not coerced to false."""

    unparseable = False
    held = bool(_LEGAL_HOLD.search(text or ""))
    if metadata is True:
        held = True
    elif metadata is False or metadata in (None, ""):
        pass
    elif isinstance(metadata, str) and _LEGAL_HOLD.search(metadata):
        held = True
    elif isinstance(metadata, str) and metadata.strip().casefold() in {"true", "yes", "y"}:
        unparseable = True
        held = True
    elif metadata not in (None, ""):
        unparseable = True
    return held, unparseable
