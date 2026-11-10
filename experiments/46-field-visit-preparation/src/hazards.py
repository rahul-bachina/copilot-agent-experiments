"""Keyword lists for a field brief. A hit is not a risk assessment.

The words are the ones the tests use. A paraphrase that uses none of them
is not detected. Absence of a hit is not a finding that the site is safe.
"""

from __future__ import annotations

import re

# Narrative holds. A structured defect_open on the same kind is handled in prepare.py.
HOLDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("gas", re.compile(r"\b(?:smell of gas|gas leak)\b", re.IGNORECASE)),
    ("carbon_monoxide", re.compile(r"\b(?:carbon monoxide|co alarm)\b", re.IGNORECASE)),
    ("electrical", re.compile(r"\b(?:exposed live|electric shock|sparking)\b", re.IGNORECASE)),
    ("asbestos", re.compile(r"\b(?:asbestos damaged|damaged asbestos|asbestos disturbed)\b", re.IGNORECASE)),
    ("structural", re.compile(r"\b(?:ceiling coming down|about to collapse)\b", re.IGNORECASE)),
    ("sewage", re.compile(r"\b(?:sewage flooding|sewage coming up)\b", re.IGNORECASE)),
)

HIGHLIGHTS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("damp_mould", re.compile(r"\b(?:mould|mold|damp|black spots)\b", re.IGNORECASE)),
    ("working_at_height", re.compile(r"\b(?:working at height|loft|ladder)\b", re.IGNORECASE)),
    ("confined_space", re.compile(r"\bconfined space\b", re.IGNORECASE)),
    ("lone_working", re.compile(r"\blone working\b", re.IGNORECASE)),
    ("sharps", re.compile(r"\b(?:sharps|needles)\b", re.IGNORECASE)),
    ("dog", re.compile(r"\bdog\b", re.IGNORECASE)),
    ("rotten_structure", re.compile(r"\b(?:rotten joists?|joists? are rotten)\b", re.IGNORECASE)),
)

ACCESS_TEXT: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("do_not_enter", re.compile(r"\bdo not enter\b", re.IGNORECASE)),
    ("key_safe_mentioned", re.compile(r"\bkey safe\b", re.IGNORECASE)),
    ("interpreter_mentioned", re.compile(r"\binterpreter\b", re.IGNORECASE)),
)

# Digits are not returned. The caller records only that a code-shaped phrase was present.
CODE_SHAPE = re.compile(
    r"\b(?:code|pin|password)\s*(?:is|:)?\s*\d{3,8}\b",
    re.IGNORECASE,
)

DESCRIPTIONS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("extract_fan", re.compile(r"extract fan", re.IGNORECASE)),
    ("boiler", re.compile(r"\bboiler\b", re.IGNORECASE)),
    ("gas_meter", re.compile(r"gas meter", re.IGNORECASE)),
    ("consumer_unit", re.compile(r"consumer unit", re.IGNORECASE)),
    ("heat_interface", re.compile(r"heat interface", re.IGNORECASE)),
    ("fire_door", re.compile(r"fire door", re.IGNORECASE)),
    ("street_light", re.compile(r"street light", re.IGNORECASE)),
    ("loft_hatch", re.compile(r"loft hatch", re.IGNORECASE)),
    ("pump", re.compile(r"\bpump\b", re.IGNORECASE)),
    ("radiator", re.compile(r"\bradiator\b", re.IGNORECASE)),
)

HOLD_RECORD_KINDS = frozenset({"gas", "electrical", "carbon_monoxide", "asbestos"})

RECORD_KINDS = frozenset(
    {
        "asbestos",
        "gas",
        "electrical",
        "confined_space",
        "working_at_height",
        "legionella",
        "carbon_monoxide",
        "general",
    }
)

RECORD_STATUSES = frozenset(
    {"current", "survey_missing", "expired", "not_applicable", "defect_open"}
)


def hits(text: str, rules: tuple[tuple[str, re.Pattern[str]], ...]) -> list[str]:
    found: list[str] = []
    for name, pattern in rules:
        if pattern.search(text) and name not in found:
            found.append(name)
    return found


def description_ids(text: str) -> list[str]:
    return [name for name, pattern in DESCRIPTIONS if pattern.search(text)]
