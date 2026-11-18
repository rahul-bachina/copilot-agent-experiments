"""Experience text and vacancy text are untrusted.

An instruction sentence is removed from matching text. It is not followed.
Eligibility words in that text are not HR's decision, and they are not the
seen-step.
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |previous |prior )?instructions", re.I)),
    ("pretend_approval", re.compile(r"\b(?:the )?(?:manager|employee|hr|recruiter) has approved\b", re.I)),
    ("pretend_approval", re.compile(r"\bapproval granted\b", re.I)),
    ("pretend_approval", re.compile(r"\bhr has seen\b", re.I)),
    ("pretend_eligible", re.compile(r"\b(?:you are|the reader is|the candidate is|this person is) eligible\b", re.I)),
    ("shortlist", re.compile(r"\bshort-?list\b", re.I)),
    ("apply", re.compile(r"\b(?:apply for|submit an application|nominate)\b", re.I)),
    ("contact", re.compile(r"\b(?:tell the manager|tell my manager|notify the recruiter|notify recruiters|contact the recruiter)\b", re.I)),
    ("strip_label", re.compile(r"\b(?:strip|drop|ignore) (?:the )?(?:legal hold|retention|marking|classification)\b", re.I)),
    ("rank_people", re.compile(r"\brank (?:the )?(?:employees|staff|team)\b", re.I)),
    ("self_clearance", re.compile(r"\bmy clearance is\b", re.I)),
    ("self_role", re.compile(r"\bmy role is\b", re.I)),
)


def sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]


def scan_text(text: str) -> dict:
    signals: list[str] = []
    if not isinstance(text, str) or not text:
        return {"detected": False, "followed": False, "signals": signals}
    for name, pattern in _PATTERNS:
        if pattern.search(text) and name not in signals:
            signals.append(name)
    return {"detected": bool(signals), "followed": False, "signals": signals}


# Jailbreak sentences are removed from matching text. A request to
# shortlist, apply, or contact is kept so the explorer can refuse it.
_STRIP = frozenset(
    {
        "ignore_instructions",
        "pretend_approval",
        "pretend_eligible",
        "strip_label",
    }
)


def without_instruction_sentences(text: str) -> str:
    """Drop a sentence that carries an instruction. Leave the rest."""

    if not isinstance(text, str) or not text:
        return ""
    kept = []
    for sentence in sentences(text):
        signals = scan_text(sentence)["signals"]
        if any(signal in _STRIP for signal in signals):
            continue
        kept.append(sentence)
    return " ".join(kept)
