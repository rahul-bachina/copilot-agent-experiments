"""Protective markings from metadata and from content.

A compound or conflicting label takes the higher marking. A user's
self-declared clearance is not a marking of the space and is not a clearance.
The rank that places OFFICIAL-SENSITIVE above OFFICIAL is a fixture rule.
"""

from __future__ import annotations

import re

from injection import prepare_text

RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "SECRET": 3,
    "TOP SECRET": 4,
}

ORDERED = (
    ("TOP SECRET", re.compile(r"TOP\s+SECRET")),
    ("OFFICIAL-SENSITIVE", re.compile(r"OFFICIAL\s*-\s*SENSITIVE")),
    ("SECRET", re.compile(r"(?<![A-Z])SECRET(?![A-Z])")),
    ("OFFICIAL", re.compile(r"(?<![A-Z])OFFICIAL(?![A-Z-])")),
)


def highest(names: list[str] | set[str]) -> str | None:
    chosen = [name for name in names if name in RANK]
    if not chosen:
        return None
    return max(chosen, key=lambda name: RANK[name])


def above(left: str | None, right: str | None) -> bool:
    """True when ``left`` is a higher fixture rank than ``right``.

    A missing justified label does not outrank a marking. A missing marking
    does not outrank a justified label.
    """

    if left not in RANK:
        return False
    if right not in RANK:
        return True
    return RANK[left] > RANK[right]


def markings_in(text: str, *, negate: bool) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return []
    scanned = prepare_text(text)[0] if negate else text
    found: list[str] = []
    remaining = scanned
    for name, pattern in ORDERED:
        if pattern.search(remaining):
            found.append(name)
            remaining = pattern.sub(" ", remaining)
    return found


def parse_metadata_label(value) -> tuple[str | None, bool]:
    """Return the higher marking and whether the field is unparseable.

    Empty metadata is not a marking and is not an error. A Purview-style
    name such as Confidential is not mapped onto a tier. It is unparseable
    and is not coerced to OFFICIAL.
    """

    if value is None or value == "":
        return None, False
    if not isinstance(value, str):
        return None, True
    found = markings_in(value, negate=False)
    stripped = value
    for _name, pattern in ORDERED:
        stripped = pattern.sub(" ", stripped)
    stripped = re.sub(r"[\s/|,;:+._-]+", "", stripped)
    if stripped:
        return highest(found), True
    if not found:
        return None, True
    return highest(found), False


def content_marking(text: str) -> str | None:
    return highest(markings_in(text, negate=True))


def combine(*markings: str | None) -> str | None:
    return highest([marking for marking in markings if marking])
