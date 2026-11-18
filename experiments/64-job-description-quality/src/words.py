"""Example phrases. Not a statistic. The organisation must review the list.

A phrase counts only when a sentence contains it outside a negation.
"It is not true that X includes Y" is not an inclusion of Y.
"""

from __future__ import annotations

import re

EXAMPLE_NOTE = (
    "This is an example list. It is not a measure of biased wording and it is "
    "not a statistic. The organisation must review the list before relying on it."
)

EXAMPLE_TERMS: tuple[dict, ...] = (
    {"phrase": "chairman", "group": "gendered", "alternative": "chair"},
    {"phrase": "chairwoman", "group": "gendered", "alternative": "chair"},
    {"phrase": "manpower", "group": "gendered", "alternative": "staffing"},
    {"phrase": "salesman", "group": "gendered", "alternative": "salesperson"},
    {"phrase": "saleswoman", "group": "gendered", "alternative": "salesperson"},
    {"phrase": "fireman", "group": "gendered", "alternative": "firefighter"},
    {"phrase": "policeman", "group": "gendered", "alternative": "police officer"},
    {"phrase": "waitress", "group": "gendered", "alternative": "the name of the role"},
    {"phrase": "young and dynamic", "group": "age_coded", "alternative": "wording that describes the work"},
    {"phrase": "recent graduate", "group": "age_coded", "alternative": "the skill the work needs, if it needs one"},
    {"phrase": "digital native", "group": "age_coded", "alternative": "the digital skill the work needs, if it needs one"},
    {"phrase": "youthful", "group": "age_coded", "alternative": "wording that describes the work"},
    {"phrase": "mature candidate", "group": "age_coded", "alternative": "the experience the work needs, if it needs any"},
    {"phrase": "school leaver", "group": "age_coded", "alternative": "the skill the work needs, if it needs one"},
    {"phrase": "native English speaker", "group": "language", "alternative": "a stated standard of English, if the role needs one"},
    {"phrase": "native speaker of English", "group": "language", "alternative": "a stated standard of English, if the role needs one"},
    {"phrase": "must have a degree", "group": "degree", "alternative": "the qualification the work needs, if it needs one"},
    {"phrase": "degree essential", "group": "degree", "alternative": "the qualification the work needs, if it needs one"},
    {"phrase": "degree in any subject", "group": "degree", "alternative": "the qualification the work needs, if it needs one"},
    {"phrase": "bachelor's degree", "group": "degree", "alternative": "the qualification the work needs, if it needs one"},
    {"phrase": "bachelors degree", "group": "degree", "alternative": "the qualification the work needs, if it needs one"},
    {"phrase": "honours degree", "group": "degree", "alternative": "the qualification the work needs, if it needs one"},
    {"phrase": "must be able to lift", "group": "physical", "alternative": "the task, if a physical task is intrinsic to the work"},
    {"phrase": "must be physically fit", "group": "physical", "alternative": "the task, if a physical task is intrinsic to the work"},
)

HEALTH_PHRASES: tuple[str, ...] = (
    "how many sick days",
    "medical history",
    "are you disabled",
    "do you have a disability",
    "health questionnaire",
    "good health required",
    "sickness absence",
)

OCCUPATIONAL_PHRASES: tuple[str, ...] = (
    "occupational requirement",
    "genuine occupational qualification",
    "only women should apply",
    "only men should apply",
    "women only",
    "men only",
    "this post is reserved for",
    "applicants must be women",
    "applicants must be men",
)

POSITIVE_ACTION_PHRASES: tuple[str, ...] = (
    "positive action",
    "particularly welcome applications from",
    "tie-break in favour",
    "tie break in favour",
)

DISTRESS_PHRASES: tuple[str, ...] = (
    "at the end of my tether",
    "at the end of their tether",
    "at the end of her tether",
    "at the end of his tether",
    "can't go on",
    "cannot go on",
    "don't want to be here",
    "do not want to be here",
    "feel unsafe",
    "don't feel safe",
    "do not feel safe",
    "being threatened",
    "safeguarding",
    "self-harm",
    "self harm",
    "suicidal",
    "no way out",
    "afraid to come to work",
)

SCORING_PHRASES: tuple[str, ...] = (
    "score the candidates",
    "score candidates",
    "rank the applicants",
    "rank applicants",
    "rank the candidates",
    "rank people",
    "score this advert against",
    "score the advert against",
    "which candidate is best",
)

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


def _denied_at(sentence: str, phrase: str, index: int) -> bool:
    folded = sentence.casefold()
    before = folded[:index]
    after = folded[index + len(phrase):]
    if _BEFORE.search(before):
        return True
    if _AFTER.match(after):
        return True
    return False


def phrase_is_denied(sentence: str, phrase: str) -> bool:
    """True when the first occurrence of the phrase is governed by a negation."""

    if not sentence or not phrase:
        return False
    folded = sentence.casefold()
    index = folded.find(phrase.casefold())
    if index < 0:
        return False
    return _denied_at(sentence, phrase, index)


def affirmed(text: str, phrase: str) -> bool:
    """True when one occurrence of the phrase sits outside a negation."""

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
            if before_ok and after_ok and not _denied_at(sentence, phrase, index):
                return True
            start = index + max(len(needle), 1)
    return False


def affirmed_sentence(text: str, phrase: str) -> str | None:
    """The first sentence that affirms the phrase, or None. Callers must not store a cue."""

    if not text or not phrase:
        return None
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
            if before_ok and after_ok and not _denied_at(sentence, phrase, index):
                return sentence
            start = index + max(len(needle), 1)
    return None


def any_affirmed(text: str, phrases: tuple[str, ...] | list[str]) -> bool:
    return any(affirmed(text, phrase) for phrase in phrases)
