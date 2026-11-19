"""Job text, the person specification, and guide notes are untrusted.

An instruction is recorded and not followed. Approval words, a self-declared
role, and a self-declared clearance are not the approval step and not the directory.
"""

from __future__ import annotations

import re

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |previous |prior )?instructions", re.I)),
    (
        "pretend_approval",
        re.compile(
            r"\b(?:the recruiter has approved|approval granted|questions approved|"
            r"rubric approved|human_approval|pack approved|approved for use)\b",
            re.I,
        ),
    ),
    ("strip_label", re.compile(r"\b(?:strip|drop|ignore|remove) (?:the )?(?:legal hold|retention|marking|classification)\b", re.I)),
    ("self_clearance", re.compile(r"\bmy clearance is\b", re.I)),
    ("self_role", re.compile(r"\b(?:my role is|i am the recruiter|i'm the recruiter|i am hr|i am the guest)\b", re.I)),
    ("decide_occupational", re.compile(r"\boccupational requirement is lawful\b", re.I)),
    ("decide_positive_action", re.compile(r"\bpositive action is lawful\b", re.I)),
    ("decide_health", re.compile(r"\bsection 60 does not apply\b", re.I)),
    ("decide_adjustment", re.compile(r"\bsection 20 (?:is met|does not apply)\b", re.I)),
)


def signals_in(text: str) -> list[str]:
    found: list[str] = []
    if not isinstance(text, str) or not text:
        return found
    for name, pattern in _PATTERNS:
        if pattern.search(text) and name not in found:
            found.append(name)
    return found


def scan(text: str) -> dict:
    return {
        "detected": bool(signals_in(text)),
        "followed": False,
        "signals": signals_in(text),
        "sentences_not_treated_as_approval": True,
    }
