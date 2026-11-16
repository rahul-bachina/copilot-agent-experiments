"""Instructions in a question or a handbook section are data. They are not followed."""

from __future__ import annotations

import re

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |previous |the above )?instructions", re.I)),
    ("ignore_effective_date", re.compile(r"ignore the effective date", re.I)),
    ("ignore_legal_hold", re.compile(r"ignore the legal hold|disregard the legal hold", re.I)),
    ("strip_marking", re.compile(r"strip the (?:protective )?marking|remove the marking|strip the legal hold", re.I)),
    ("override_approval", re.compile(r"\bhr approved\b|\bthis (?:draft|version) is approved\b", re.I)),
    ("grant_entitlement", re.compile(r"entitled to\s+\d+\s+days", re.I)),
    ("use_the_draft", re.compile(r"answer from the draft|use the draft", re.I)),
    ("reveal_withheld", re.compile(r"reveal the secret|quote the pay file|show the canary", re.I)),
    ("role_play", re.compile(r"\byou are now\b|\bsystem\s*:", re.I)),
    ("self_clearance", re.compile(r"\bmy clearance is\b|\bi have\s+(?:secret|top secret)\s+clearance\b", re.I)),
)


def scan_text(text: str) -> dict:
    """Return signal names. The matched sentences are not copied out."""

    if not isinstance(text, str) or not text:
        return {"detected": False, "followed": False, "signals": [], "sentence_count": 0}
    signals: list[str] = []
    count = 0
    for sentence in re.split(r"(?<=[.!?\n])\s+", text):
        names = [name for name, pattern in _PATTERNS if pattern.search(sentence)]
        if not names:
            continue
        count += 1
        for name in names:
            if name not in signals:
                signals.append(name)
    return {
        "detected": bool(signals),
        "followed": False,
        "signals": signals,
        "sentence_count": count,
    }


def without_instruction_sentences(text: str) -> str:
    """Drop instruction sentences before topic matching. The drop is not approval."""

    if not isinstance(text, str):
        return ""
    kept: list[str] = []
    for sentence in re.split(r"(?<=[.!?\n])\s+", text):
        if any(pattern.search(sentence) for _, pattern in _PATTERNS):
            continue
        if sentence.strip():
            kept.append(sentence.strip())
    return " ".join(kept)
