"""Protective markings, retention labels, and legal hold.

A label is taken from the metadata and from the page. A compound or
conflicting label takes the higher marking. "My clearance is" is not a cover
page. A hold or a retention label is kept. "It is not true that the cover is
SECRET" does not remove a SECRET label that is also present. "Do not drop
the legal hold" keeps the hold.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import denial_split, sentences
else:
    from .negate import denial_split, sentences

RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}
_LABELS = ("TOP SECRET", "OFFICIAL-SENSITIVE", "SECRET", "OFFICIAL")
_RETENTION = re.compile(r"RETENTION:\s*([^\n.;]+)", re.IGNORECASE)
_LEGAL_HOLD = re.compile(r"\bLEGAL HOLD\b", re.IGNORECASE)
_KEEP_HOLD = re.compile(
    r"\b(?:do not|don't|must not|shall not)\s+(?:drop|strip|remove|clear) the legal hold\b",
    re.IGNORECASE,
)
_CLEARANCE_CLAIM = re.compile(r"\bmy clearance is\b", re.IGNORECASE)


def markings_in(text: str) -> list[str]:
    found: list[str] = []
    remaining = text or ""
    for label in _LABELS:
        pattern = re.compile(rf"\b{re.escape(label)}\b")
        if pattern.search(remaining):
            found.append(label)
            remaining = pattern.sub(" ", remaining)
    return found


def _denied_label(sentence: str, label: str) -> bool:
    scope, denied = denial_split(sentence)
    if not denied:
        return False
    if label.casefold() not in denied.casefold():
        return False
    if label.casefold() in scope.casefold():
        return False
    return True


def content_markings(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        if _CLEARANCE_CLAIM.search(sentence):
            continue
        for label in markings_in(sentence):
            if _denied_label(sentence, label):
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
    for sentence in sentences(text or ""):
        for match in _RETENTION.findall(sentence):
            scope, denied = denial_split(sentence)
            if match.casefold() in denied.casefold() and match.casefold() not in scope.casefold():
                continue
            for part in re.split(r"\s+and\s+|,\s*", match):
                label = part.strip(" .")
                if label and label not in kept:
                    kept.append(label)
    return kept, unparseable


def legal_hold(metadata: object, text: str) -> tuple[bool, bool]:
    """A hold in either place is kept. A denial on the page does not clear metadata."""

    unparseable = False
    held = False
    if metadata is True:
        held = True
    elif metadata is False or metadata is None:
        held = False
    else:
        unparseable = True
        if isinstance(metadata, str) and _LEGAL_HOLD.search(metadata):
            held = True
    for sentence in sentences(text or ""):
        if _KEEP_HOLD.search(sentence):
            held = True
            continue
        if not _LEGAL_HOLD.search(sentence):
            continue
        scope, denied = denial_split(sentence)
        if "legal hold" in denied.casefold() and "legal hold" not in scope.casefold():
            continue
        held = True
    return held, unparseable
