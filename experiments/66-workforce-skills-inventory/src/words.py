"""Phrase checks and paraphrase families.

A phrase counts only when a sentence contains it outside a negation.
"It is not true that X includes Y" is not an inclusion of Y.
The families are example patterns. They are not a statistic. The organisation
must review them. A sentence that uses none of the patterns is not caught.
"""

from __future__ import annotations

import re

EXAMPLE_NOTE = (
    "These patterns are an example list. They are not a measure of risk and "
    "they are not a statistic. The organisation must review them. A paraphrase "
    "that uses none of the patterns is not caught."
)

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_BEFORE = re.compile(
    r"(?:not true that|it is not the case that|never said that|did not say that|"
    r"does not include|doesn't include|do not include|is not included|"
    r"must not|do not|does not|don't|doesn't|cannot|can't|never|without|not)\b"
    r"(?:\s+\w+){0,8}\s*$",
    re.IGNORECASE,
)
_AFTER = re.compile(r"^\s+(?:is not|are not|isn't|aren't)\b", re.IGNORECASE)

# The match itself may begin with "don't" or "do not". Negation is only the
# text before the match, so "I don't want to be here" is not cancelled by its
# own "don't".
DISTRESS = (
    re.compile(
        r"\b(?:cannot|can't|can not|unable to)\s+(?:cope|go on|carry on|keep going|face (?:work|this|another day))\b",
        re.I,
    ),
    re.compile(r"\b(?:do not|don't)\s+want to\s+(?:be here|go on|live|wake up)\b", re.I),
    re.compile(
        r"\b(?:thinking of|thinking about|want to|going to)\s+"
        r"(?:end it|ending it|harm(?:ing)? myself|kill myself|tak(?:e|ing) my own life)\b",
        re.I,
    ),
    re.compile(r"\b(?:suicidal|self-harm|self harm)\b", re.I),
    re.compile(r"\bend of (?:my|their|his|her) tether\b", re.I),
    re.compile(r"\bno way out\b", re.I),
    re.compile(r"\bsafeguarding\b", re.I),
    re.compile(r"\b(?:do not|don't)\s+feel safe\b", re.I),
    re.compile(r"\bfeel(?:s|ing)? unsafe\b", re.I),
    re.compile(r"\bbeing (?:abused|threatened)\b", re.I),
    re.compile(r"\b(?:cannot|can't)\s+see (?:a |the )?(?:way|future|point)\b", re.I),
    re.compile(r"\bafraid to come (?:in|to work)\b", re.I),
    re.compile(r"\b(?:grievance|raising a grievance|formal complaint about my manager)\b", re.I),
)

MISUSE = (
    re.compile(
        r"\b(?:select|choose|pick|identify|decide)\b.{0,48}?\b(?:redundant|redundancy)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:redundancy selection|selected for redundancy|selecting for redundancy|"
        r"headcount cut|who to let go|made redundant|let people go)\b",
        re.I,
    ),
    re.compile(r"\b(?:rate|score|rank|assess)\b(?:\s+\w+){0,8}\s+performance\b", re.I),
    re.compile(
        r"\bperformance (?:rating|score|management|review outcome|appraisal)\b",
        re.I,
    ),
    re.compile(r"\b(?:put|placing|place)\b(?:\s+\w+){0,6}\s+on a pip\b", re.I),
    re.compile(
        r"\b(?:set|decide|change|cut|raise)\b(?:\s+\w+){0,8}\s+(?:her |his |their )?(?:pay|salary|bonus|remuneration)\b",
        re.I,
    ),
    re.compile(r"\b(?:pay award|bonus decision|remuneration decision)\b", re.I),
    re.compile(r"\b(?:who to promote|who should be promoted|promotion decision|for promotion)\b", re.I),
    re.compile(
        r"\b(?:select|decide|choose)\b(?:\s+\w+){0,8}\s+(?:for |who (?:to|should) (?:be )?)?promot",
        re.I,
    ),
    re.compile(r"\b(?:disciplinary|misconduct sanction|written warning|disciplinary outcome)\b", re.I),
    re.compile(r"\bfeed(?:s|ing)? (?:pay|promotion|redundancy|a disciplinary)\b", re.I),
)

PROTECTED = (
    re.compile(
        r"\b(?:infer|guess|deduce|assume|work out|profile)\b(?:\s+\w+){0,12}\s+"
        r"(?:from|because of|based on)\b(?:\s+\w+){0,8}\s+"
        r"(?:age|race|sex|gender|disability|religion|pregnancy|maternity|"
        r"sexual orientation|health|sickness|diagnosis|ethnicity|medical)\b",
        re.I,
    ),
    re.compile(
        r"\bbecause (?:they|he|she) (?:is|are)\b(?:\s+not)?(?:\s+\w+){0,3}\s+"
        r"(?:old|young|disabled|pregnant)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:from|using) (?:their|his|her) (?:age|health|disability|sickness|ethnicity|"
        r"religion|diagnosis|maternity|race|sex)\b",
        re.I,
    ),
    re.compile(r"\bmaternity absence\b", re.I),
    re.compile(r"\bsexual orientation\b", re.I),
    re.compile(r"\bprotected characteristic\b", re.I),
)

UNSUPPLIED = (
    re.compile(
        r"\b(?:mailbox|inbox|email monitoring|keystroke|cctv|badge data|badge swipes|"
        r"absence record|sickness record|manager(?:'s)? (?:private )?notes|productivity score|"
        r"surveillance|monitoring feed|keystroke log)\b",
        re.I,
    ),
    re.compile(r"\bdata they did not supply\b", re.I),
    re.compile(r"\bprofile (?:them|him|her|people|staff|workers) from\b", re.I),
    re.compile(r"\b(?:not supplied for this purpose|was not supplied for this)\b", re.I),
)

OBJECTION = (
    re.compile(
        r"\bi object to\b(?:\s+\w+){0,10}\s+(?:processing|inventory|profile|skills|this)\b",
        re.I,
    ),
    re.compile(r"\bstop processing my\b", re.I),
    re.compile(r"\b(?:withdraw|withdrawing) my consent\b", re.I),
    re.compile(r"\bi do not consent\b", re.I),
    re.compile(r"\bplease do not process\b", re.I),
    re.compile(r"\bi object\b", re.I),
)

INJECTION = (
    re.compile(r"\b(?:ignore|disregard) (?:all |any |the )?(?:previous |prior |above |earlier )?instructions\b", re.I),
    re.compile(r"\byou are now (?:hr|the manager|authorised|authorized)\b", re.I),
    re.compile(r"\b(?:the employee has already confirmed|confirm all skills|hr has validated)\b", re.I),
    re.compile(r"\b(?:strip|drop|ignore) (?:the )?(?:legal hold|retention|marking|classification)\b", re.I),
    re.compile(r"\bwrite this to the hr system\b", re.I),
    re.compile(r"\bset the performance rating\b", re.I),
    re.compile(r"\bmark every skill confirmed\b", re.I),
)

HEALTH_IN_SENTENCE = re.compile(
    r"\b(?:sick|sickness|diagnosis|medical|disabled|disability|pregnant|maternity|"
    r"mental health|years old|date of birth|ethnicity|religion|sexual orientation)\b",
    re.I,
)

FAMILIES = {
    "distress": DISTRESS,
    "misuse": MISUSE,
    "protected_or_health": PROTECTED,
    "unsupplied": UNSUPPLIED,
    "objection": OBJECTION,
    "injection": INJECTION,
}

PURPOSE_MISUSE = {
    "redundancy_selection": "redundancy",
    "performance_management": "performance",
    "pay": "pay",
    "promotion": "promotion",
    "disciplinary": "disciplinary",
}


def sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]


def _denied_at(sentence: str, start: int, end: int) -> bool:
    folded = sentence.casefold()
    before = folded[:start]
    after = folded[end:]
    if _BEFORE.search(before):
        return True
    if _AFTER.match(after):
        return True
    return False


def phrase_is_denied(sentence: str, phrase: str) -> bool:
    if not sentence or not phrase:
        return False
    folded = sentence.casefold()
    index = folded.find(phrase.casefold())
    if index < 0:
        return False
    return _denied_at(sentence, index, index + len(phrase))


def affirmed(text: str, phrase: str) -> bool:
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
            if before_ok and after_ok and not _denied_at(sentence, index, after):
                return True
            start = index + max(len(needle), 1)
    return False


def affirmed_sentence(text: str, phrase: str) -> str | None:
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
            if before_ok and after_ok and not _denied_at(sentence, index, after):
                return sentence
            start = index + max(len(needle), 1)
    return None


def family_hit(text: str, family: str) -> bool:
    patterns = FAMILIES[family]
    for sentence in sentences(text or ""):
        for pattern in patterns:
            for match in pattern.finditer(sentence):
                if not _denied_at(sentence, match.start(), match.end()):
                    return True
    return False


def hits(text: str) -> dict[str, bool]:
    return {name: family_hit(text, name) for name in FAMILIES}


def sentence_has_health_or_protected(sentence: str) -> bool:
    if not sentence:
        return False
    for match in HEALTH_IN_SENTENCE.finditer(sentence):
        if not _denied_at(sentence, match.start(), match.end()):
            return True
    return False
