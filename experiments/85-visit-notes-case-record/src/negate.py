"""Sentence split and negation.

"It is not true that the line includes a diagnosis" does not affirm a
diagnosis. The window is the same sentence, up to eight words before the match.
A safeguarding stem is still routed when the sentence denies it. That route
is not a finding that the concern happened.
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_BEFORE = re.compile(
    r"(?:not true that|not the case that|not correct that|does not include|"
    r"doesn't include|do not include|never includes|no longer includes|"
    r"is not included|not included|must not|do not|does not|"
    r"don't|doesn't|cannot|can't|never|without|nothing|nobody|no one|no-one|no|not)\b"
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


def bounded(text: str, index: int, length: int) -> bool:
    before_ok = index == 0 or not text[index - 1].isalnum()
    after = index + length
    after_ok = after == len(text) or not text[after].isalnum()
    return before_ok and after_ok


def affirmed(text: str, phrase: str) -> bool:
    return bool(affirmed_positions(text, phrase))


def affirmed_positions(text: str, phrase: str) -> list[int]:
    if not text or not phrase:
        return []
    found: list[int] = []
    needle = phrase.casefold()
    for sentence in sentences(text):
        folded = sentence.casefold()
        start = 0
        while True:
            index = folded.find(needle, start)
            if index < 0:
                break
            if bounded(folded, index, len(needle)) and not denied_at(sentence, phrase, index):
                found.append(index)
            start = index + max(len(needle), 1)
    return found


def present(text: str, phrase: str) -> bool:
    """The phrase occurs, including when the sentence denies it."""

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
            if bounded(folded, index, len(needle)):
                return True
            start = index + max(len(needle), 1)
    return False
