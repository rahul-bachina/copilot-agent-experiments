"""Sentence matching. A negated phrase is not an inclusion.

"It is not true that X includes Y" does not count as Y. The window is the
same sentence, up to eight words before the match. Cue stems are an example
list the organisation must review. They are not a statistic.
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_BEFORE = re.compile(
    r"(?:not true that|not the case that|not correct that|does not include|"
    r"doesn't include|do not include|never includes|no longer includes|"
    r"is not included|not included|must not|shall not exclude|do not|does not|"
    r"don't|doesn't|cannot|can't|never|without|nothing|no|not)\b"
    r"(?:\s+\S+){0,8}\s*$",
    re.IGNORECASE,
)

DISTRESS_RE = re.compile(
    r"end of (?:my|their|his|her|our) tether"
    r"|can(?:not|'t| not) (?:go on|cope|carry on|take (?:this|any more))"
    r"|do(?:n't| not) want to (?:be here|live|carry on|continue|wake up)"
    r"|feel(?:s|ing)? (?:unsafe|frightened|terrified|hopeless)"
    r"|safeguard"
    r"|self[-\s]?harm"
    r"|suicid"
    r"|kill (?:myself|himself|herself|themselves)"
    r"|end (?:my|their|his|her) life"
    r"|no way out"
    r"|afraid to (?:come|return|sign|be)"
    r"|breaking point"
    r"|want to die"
    r"|hurt (?:myself|themselves)"
    r"|ending it all"
    r"|can(?:not|'t| not) see a way forward"
    r"|thoughts of (?:ending|suicide|dying)"
    r"|not safe at home"
    r"|child is not safe",
    re.IGNORECASE,
)

GRIEVANCE_RE = re.compile(
    r"\bgrievance\b"
    r"|\bbull(?:y|ied|ying)\b"
    r"|\bharass(?:ment|ed|ing)?\b"
    r"|\bsexual assault\b"
    r"|\bdomestic abuse\b"
    r"|\bwhistleblow(?:er|ing)?\b"
    r"|\bbeing threatened\b"
    r"|\bdisclos(?:e|ed|ing|ure)\b(?:\s+\w+){0,8}\s+\babuse\b"
    r"|\braising a complaint\b"
    r"|\blodg(?:e|ing) a grievance\b"
    r"|\bintimidat(?:e|ed|ing|ion)\b"
    r"|\bunwanted conduct\b"
    r"|\bsubjected to\b(?:\s+\w+){0,6}\s+\b(?:bullying|harassment|abuse)\b",
    re.IGNORECASE,
)

DEATH_PI_RES: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:exclude|excludes|excluding|excluded|exclusion of|restrict|restricts|"
        r"restricted|restriction of)\b(?:\s+\w+){0,8}\s+\b(?:liability|responsibility)\b"
        r"(?:\s+\w+){0,10}\s+\b(?:death|personal injury|bodily injury|fatal injury)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:no|without)\s+liability\b(?:\s+\w+){0,8}\s+\b(?:death|personal injury|"
        r"bodily injury|fatal injury)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:not|never)\s+(?:be\s+)?liable\b(?:\s+\w+){0,8}\s+\b(?:death|"
        r"personal injury|bodily injury|fatal injury)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bnot\s+responsible\b(?:\s+\w+){0,8}\s+\b(?:death|personal injury|"
        r"bodily injury|fatal injury|injury)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\baccepts?\s+no\s+responsibility\b(?:\s+\w+){0,12}\s+\b(?:death|dies|died|"
        r"personal injury|bodily injury|fatal injury|injured)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:death|personal injury|bodily injury|fatal injury)\b(?:\s+\w+){0,8}\s+"
        r"\b(?:is|are)\s+excluded\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:death or (?:personal )?injury|injury or death|personal injury)\b"
        r"(?:\s+\w+){0,6}\s+\b(?:excluded|at your own risk)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bwaiv(?:e|es|er)\b(?:\s+\w+){0,8}\s+\b(?:liability for\s+)?(?:death|"
        r"personal injury|bodily injury)\b",
        re.IGNORECASE,
    ),
)

AUTO_RENEW_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bauto[- ]?renew(?:s|al|ed|ing)?\b", re.IGNORECASE),
    re.compile(r"\bautomatically renew(?:s|ed|al)?\b", re.IGNORECASE),
    re.compile(r"\brenews?\s+unless\b", re.IGNORECASE),
    re.compile(r"\bsuccessive (?:periods|terms)\b", re.IGNORECASE),
    re.compile(r"\bevergreen\b", re.IGNORECASE),
    re.compile(r"\brolls over\b", re.IGNORECASE),
    re.compile(r"\bextend(?:s|ed)? automatically\b", re.IGNORECASE),
)

INJECTION_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |any )?(?:the )?(?:previous|prior|above|your) instructions", re.I)),
    ("forget_rules", re.compile(r"forget (?:all )?(?:your|the) (?:rules|instructions)", re.I)),
    ("persona", re.compile(r"\byou are now\b", re.I)),
    ("accept_terms", re.compile(r"\baccept (?:these|the|all) terms\b", re.I)),
    ("sign", re.compile(r"\bsign (?:this|the) (?:contract|agreement)\b", re.I)),
    ("send", re.compile(r"\bsend (?:this|the) (?:contract|agreement)\b", re.I)),
    ("redline", re.compile(r"\bredline\b", re.I)),
    ("approved_in_text", re.compile(r"\b(?:lawyer|solicitor) has (?:already )?approved\b", re.I)),
    ("mark_safe", re.compile(r"\bmark (?:every|all) (?:clauses?|deviations?) as (?:preferred|acceptable|safe)\b", re.I)),
    ("disregard_playbook", re.compile(r"\bdisregard the playbook\b", re.I)),
    ("on_behalf", re.compile(r"\bon (?:our|the customer(?:'s|s)?) behalf\b", re.I)),
    ("authorised_to_sign", re.compile(r"\bauthori[sz]ed to (?:sign|accept)\b", re.I)),
    ("strip_label", re.compile(r"\b(?:strip|remove|ignore) the (?:legal hold|retention(?: label)?)\b", re.I)),
    ("system_role", re.compile(r"(?m)^\s*system\s*:", re.I)),
    ("developer_role", re.compile(r"(?m)^\s*developer\s*:", re.I)),
)

_CLEARANCE_CLAIM = re.compile(r"\bmy clearance is\b", re.IGNORECASE)
_ROLE_CLAIM = re.compile(
    r"\bmy role is\b|\bi am the lawyer\b|\bi am a lawyer\b|\bi am authorised\b",
    re.IGNORECASE,
)
_AMBIGUOUS = re.compile(
    r"\bto be agreed\b|\btbc\b|\btba\b|\bto be confirmed\b|"
    r"\breasonable (?:cap|amount|notice|sum)\b|\bor such other (?:amount|law|period)\b",
    re.IGNORECASE,
)


def sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]


def span_is_denied(sentence: str, start: int) -> bool:
    """True when a negation governs the match that begins at start."""

    if start <= 0:
        return False
    return _BEFORE.search(sentence[:start]) is not None


def first_affirmed_match(sentence: str, pattern: re.Pattern[str]) -> re.Match[str] | None:
    for match in pattern.finditer(sentence):
        if not span_is_denied(sentence, match.start()):
            return match
    return None


def pattern_affirmed_sentence(text: str, pattern: re.Pattern[str]) -> str | None:
    for sentence in sentences(text):
        if first_affirmed_match(sentence, pattern):
            return sentence
    return None


def any_pattern_affirmed(text: str, patterns: tuple[re.Pattern[str], ...]) -> str | None:
    for sentence in sentences(text):
        for pattern in patterns:
            if first_affirmed_match(sentence, pattern):
                return sentence
    return None


def pattern_denied_sentence(text: str, patterns: tuple[re.Pattern[str], ...]) -> str | None:
    """A sentence where the pattern occurs and a negation governs it."""

    for sentence in sentences(text):
        for pattern in patterns:
            for match in pattern.finditer(sentence):
                if span_is_denied(sentence, match.start()):
                    return sentence
    return None


def phrase_is_denied(sentence: str, phrase: str) -> bool:
    if not sentence or not phrase:
        return False
    folded = sentence.casefold()
    index = folded.find(phrase.casefold())
    if index < 0:
        return False
    return span_is_denied(sentence, index)


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
            if before_ok and after_ok and not span_is_denied(sentence, index):
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
            if before_ok and after_ok and not span_is_denied(sentence, index):
                return sentence
            start = index + max(len(needle), 1)
    return None


def death_pi(text: str) -> dict:
    """Affirmed exclusion, and a denied mention that reads as a carve-out."""

    affirmed_at: list[str] = []
    denied_at: list[str] = []
    for sentence in sentences(text):
        affirmed_here = False
        denied_here = False
        for pattern in DEATH_PI_RES:
            for match in pattern.finditer(sentence):
                if span_is_denied(sentence, match.start()):
                    denied_here = True
                else:
                    affirmed_here = True
        if affirmed_here and sentence not in affirmed_at:
            affirmed_at.append(sentence)
        elif denied_here and sentence not in denied_at:
            denied_at.append(sentence)
    return {"affirmed": affirmed_at, "denied": denied_at}


def cue_categories(text: str) -> dict:
    """Category flags only. The cue sentence is not returned."""

    distress = False
    grievance = False
    for sentence in sentences(text):
        if DISTRESS_RE.search(sentence):
            distress = True
        if GRIEVANCE_RE.search(sentence):
            grievance = True
    return {
        "distress": distress,
        "grievance": grievance,
        "text_copied": False,
    }


def injection_signals(text: str) -> list[str]:
    """Instruction names. A sentence that refuses the act is not a signal."""

    found: list[str] = []
    for sentence in sentences(text):
        for name, pattern in INJECTION_RES:
            match = pattern.search(sentence)
            if not match:
                continue
            if span_is_denied(sentence, match.start()):
                continue
            if name not in found:
                found.append(name)
    return found


def ambiguous_sentence(text: str) -> str | None:
    for sentence in sentences(text):
        if _AMBIGUOUS.search(sentence) and not span_is_denied(sentence, _AMBIGUOUS.search(sentence).start()):
            return sentence
    return None


def claims_role(text: str) -> bool:
    return any(_ROLE_CLAIM.search(sentence) for sentence in sentences(text))


def claims_clearance(text: str) -> bool:
    return any(_CLEARANCE_CLAIM.search(sentence) for sentence in sentences(text))
