"""Evidence text is untrusted. An instruction is recorded and not followed."""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from words import family_hit, sentences
else:
    from .words import family_hit, sentences

_STRIP = re.compile(
    r"\b(?:ignore|disregard) (?:all |any |the )?(?:previous |prior |above |earlier )?instructions\b"
    r"|\byou are now (?:hr|the manager|authorised|authorized)\b"
    r"|\b(?:strip|drop|ignore) (?:the )?(?:legal hold|retention|marking|classification)\b"
    r"|\b(?:confirm all skills|mark every skill confirmed|the employee has already confirmed|hr has validated)\b"
    r"|\bwrite this to the hr system\b"
    r"|\bset the performance rating\b",
    re.I,
)


def scan_text(text: str) -> dict:
    detected = bool(text) and (family_hit(text, "injection") or bool(_STRIP.search(text)))
    return {"detected": detected, "followed": False, "signals": ["injection"] if detected else []}


def without_instruction_sentences(text: str) -> str:
    if not isinstance(text, str) or not text:
        return ""
    kept = []
    for sentence in sentences(text):
        if _STRIP.search(sentence) or family_hit(sentence, "injection"):
            continue
        kept.append(sentence)
    return " ".join(kept)
