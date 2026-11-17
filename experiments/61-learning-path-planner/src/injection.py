"""Course text and goal text are untrusted. Matching uses the cleaned text.

An instruction sentence is removed. It is not followed. Approval words in
that text are not the approval step.
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |previous |prior )?instructions", re.I)),
    ("pretend_approval", re.compile(r"\b(?:the )?(?:manager|employee|hr) has approved\b", re.I)),
    ("pretend_approval", re.compile(r"\bapproval granted\b", re.I)),
    ("enrol", re.compile(r"\benrol|\benroll\b", re.I)),
    ("book", re.compile(r"\bbook (?:the |this |a )?course\b", re.I)),
    ("spend", re.compile(r"\b(?:spend the budget|authorise payment|authorize payment)\b", re.I)),
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


# These signals are instructions. A ranking request is not stripped here:
# the planner has to see it in order to refuse it.
_STRIP = frozenset(
    {
        "ignore_instructions",
        "pretend_approval",
        "enrol",
        "book",
        "spend",
        "strip_label",
    }
)


def without_instruction_sentences(text: str) -> str:
    """Drop a sentence that carries an instruction. Leave the rest.

    A sentence that only ranks people, or only states a clearance, is kept
    so the planner can refuse it. It is still not an approval.
    """

    if not isinstance(text, str) or not text:
        return ""
    kept = []
    for sentence in sentences(text):
        signals = scan_text(sentence)["signals"]
        if any(signal in _STRIP for signal in signals):
            continue
        kept.append(sentence)
    return " ".join(kept)
