"""Enquiry text is data. Instructions inside it are recorded and not followed."""

from __future__ import annotations

import re

# Order is stable so the signal list does not depend on dict ordering.
PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (all |any )?(previous |prior |above |your )?instructions"),
    ("disregard_rules", r"disregard (the )?(catalogue|catalog|rules|pages)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("reveal_prompt", r"reveal (the |your )?prompt"),
    ("mark_eligible", r"mark me eligible"),
    ("create_case", r"create (a |the )?case"),
    ("send_email", r"send (an |the )?e-?mail"),
    ("override_stale", r"override (the )?stale"),
    ("do_not_handover", r"do not hand ?over"),
    ("role_jailbreak", r"\bDAN\b"),
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)


def signals_in(text: str) -> list[str]:
    if not text:
        return []
    found = [name for name, pattern in _COMPILED if pattern.search(text)]
    return found


def sentence_is_instruction(sentence: str) -> bool:
    return bool(signals_in(sentence))


def strip_instruction_sentences(text: str) -> str:
    """Drop sentences that are themselves instructions. Leave the rest."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    kept = [part for part in parts if part and not sentence_is_instruction(part)]
    return " ".join(kept).strip()
