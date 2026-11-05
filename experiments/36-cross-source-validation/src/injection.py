"""Instructions inside a source document are data. They are not followed.

A line that already refuses the action is not treated as an instruction.
Experiment 12 still scans the same text for its own phrase list. A phrase
on neither list is not detected. That gap is a limitation.
"""

from __future__ import annotations

import re

PHRASES = (
    ("ignore-instructions", ("ignore previous instructions", "ignore all instructions", "ignore the above")),
    ("treat-as-match", ("treat the amount as a match", "treat this as a match", "classify this as a match")),
    ("choose-source", ("the form is correct", "the invoice is correct", "choose the invoice", "choose the form", "the register is right")),
    ("edit-record", ("update the register", "edit the record", "correct the record", "overwrite the record")),
    ("contact", ("email the supplier", "email the customer", "contact the supplier", "contact the customer")),
    ("role-play", ("you are now", "system prompt")),
    ("mark-resolved", ("mark as resolved", "mark this resolved")),
)

_NEGATION = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.IGNORECASE)


def codes_in(text: str) -> list[str]:
    """Return pattern ids found in one string. A negation in the same string is skipped.

    The skip can hide an instruction that shares a sentence with "do not".
    Experiment 12's scan does not use this skip. Callers should run both.
    """
    if not isinstance(text, str) or not text:
        return []
    if _NEGATION.search(text):
        return []
    lower = text.casefold()
    found = [code for code, phrases in PHRASES if any(phrase in lower for phrase in phrases)]
    return found
