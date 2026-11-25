"""Sentence split and negation.

"It is not true that this includes a subject access request" does not affirm
a subject access request. The window is the same sentence, up to eight words
before the match. A distress stem is not passed through this check.
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


def bounded_at(folded: str, phrase: str) -> list[int]:
    found: list[int] = []
    start = 0
    while True:
        index = folded.find(phrase, start)
        if index < 0:
            break
        after = index + len(phrase)
        before_ok = index == 0 or not folded[index - 1].isalnum()
        after_ok = after == len(folded) or not folded[after].isalnum()
        if before_ok and after_ok:
            found.append(index)
        start = index + max(len(phrase), 1)
    return found


def affirmed(text: str, phrase: str) -> bool:
    return bool(affirmed_positions(text, phrase))


def affirmed_positions(text: str, phrase: str) -> list[int]:
    if not text or not phrase:
        return []
    needle = phrase.casefold()
    found: list[int] = []
    for sentence in sentences(text):
        folded = sentence.casefold()
        for index in bounded_at(folded, needle):
            if not denied_at(sentence, phrase, index):
                found.append(index)
    return found
