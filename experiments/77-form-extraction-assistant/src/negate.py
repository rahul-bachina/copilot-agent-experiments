"""Sentence split and negation.

"It is not true that the fee includes £100" does not affirm £100.
The window is the same sentence, up to eight words before the match.
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
_AFTER = re.compile(
    r"^\s+(?:is not|are not|isn't|aren't|does not|doesn't|do not|don't)\b",
    re.IGNORECASE,
)


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
            after = index + len(needle)
            before_ok = index == 0 or not folded[index - 1].isalnum()
            after_ok = after == len(folded) or not folded[after].isalnum()
            if before_ok and after_ok and not denied_at(sentence, phrase, index):
                found.append(index)
            start = index + max(len(needle), 1)
    return found


def regex_affirmed(text: str, pattern: re.Pattern[str]) -> bool:
    if not text:
        return False
    for sentence in sentences(text):
        for match in pattern.finditer(sentence):
            if not denied_at(sentence, match.group(0), match.start()):
                return True
    return False
