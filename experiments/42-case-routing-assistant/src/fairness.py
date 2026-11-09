"""Protected characteristics are not routing features.

The lists are the ones read on 9 November 2026. Section 19(3) includes
marriage and civil partnership. Section 149(7) does not. The refusal list
is the union. Section 4 was not opened.
"""

from __future__ import annotations

import re

# Tokens that name a characteristic as a feature of a rule. Not a finding
# that a person has that characteristic.
CHARACTERISTIC_FEATURES = frozenset(
    {
        "age",
        "disability",
        "disabled",
        "gender reassignment",
        "gender",
        "sex",
        "marriage",
        "civil partnership",
        "race",
        "ethnic",
        "ethnicity",
        "religion",
        "belief",
        "sexual orientation",
        "pregnancy",
        "maternity",
    }
)

_INSTRUCTION = re.compile(
    r"("
    r"\broute(?:d|ing)? (?:them |people |customers |residents )?(?:by|on|using) (?:their )?"
    r"(?:race|age|sex|gender|religion|disability|ethnic\w*|sexual orientation)"
    r"|"
    r"\b(?:deprioritise|deprioritize|lower the priority of|slow queue for|bottom of the queue for)"
    r".{0,60}"
    r"(?:disabled|disability|race|religion|pregnant|sexual orientation|because of (?:their )?age)"
    r"|"
    r"\bsend (?:disabled|older|black|muslim|gay|trans) (?:customers|residents|people) to\b"
    r"|"
    r"\bbecause (?:he|she|they|the customer) (?:is|are) "
    r"(?:black|white|muslim|gay|trans|pregnant|old|disabled)\b"
    r")",
    re.IGNORECASE,
)

_ADJUSTMENT = re.compile(
    r"\b(?:wheelchair|disabled|disability|reasonable adjustment|british sign language|\bBSL\b|interpreter)\b",
    re.IGNORECASE,
)


def characteristic_feature(value: str | None) -> bool:
    if not value or not isinstance(value, str):
        return False
    return value.strip().lower() in CHARACTERISTIC_FEATURES


def fairness_instruction(text: str) -> bool:
    if not text:
        return False
    return _INSTRUCTION.search(text) is not None


def adjustment_mentioned(text: str) -> bool:
    """A resident describing an access need. Not an instruction to discriminate."""
    if not text:
        return False
    return _ADJUSTMENT.search(text) is not None
