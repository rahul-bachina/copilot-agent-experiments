"""Sentence split and negation.

"It is not true that the pack includes a question about your age" does not
affirm that question. The window is the same shape as Experiment 64.
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_BEFORE = re.compile(
    r"(?:not true that|does not include|doesn't include|do not include|never includes|"
    r"no longer includes|is not included|not included|"
    r"must not|do not require|does not require|is not required|not required|"
    r"do not|does not|don't|doesn't|cannot|can't|never|without|not)\b"
    r"(?:\s+\S+){0,8}\s*$",
    re.IGNORECASE,
)
_AFTER = re.compile(r"^\s+(?:is not|are not|isn't|aren't)\b", re.IGNORECASE)


def sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]


def denied_at(sentence: str, phrase: str, index: int) -> bool:
    folded = sentence.casefold()
    before = folded[:index]
    after = folded[index + len(phrase):]
    if _BEFORE.search(before):
        return True
    if _AFTER.match(after):
        return True
    return False


def affirmed(text: str, phrase: str) -> bool:
    """True when one whole-phrase occurrence sits outside a negation."""

    if not text or not phrase:
        return False
    needle = phrase.casefold()
    for sentence in sentences(text):
        folded = sentence.casefold()
        start = 0
        while True:
            index = folded.find(needle, start)
            if index < 0:
                break
            after = index + len(needle)
            before_ok = index == 0 or not folded[index - 1].isalnum()
            after_ok = after == len(folded) or not folded[after].isalnum()
            if before_ok and after_ok and not denied_at(sentence, phrase, index):
                return True
            start = index + max(len(needle), 1)
    return False
