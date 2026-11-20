"""Sentence matching for a regulatory notice.

"It is not true that X includes Y" does not count as Y. A qualification that
follows a topic keeps that topic out of the plain list. Leading wording is
flagged and is never applied. Cue stems are an example list, not a statistic.
"""

from __future__ import annotations

import re

_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_BEFORE = re.compile(
    r"(?:not true that|not the case that|not correct that|does not include|"
    r"doesn't include|do not include|never includes|no longer includes|"
    r"is not included|not included|does not cover|doesn't cover|do not cover|"
    r"does not apply to|doesn't apply to|must not|shall not|do not|does not|"
    r"don't|doesn't|cannot|can't|never|without|nothing|no|not)\b"
    r"(?:\s+\S+){0,8}\s*$",
    re.IGNORECASE,
)
_AFTER_DENY = re.compile(
    r"^(?:\s+\w+){0,6}\s+(?:is|are|was|were)\s+(?:not|no longer)\s+included\b",
    re.IGNORECASE,
)
_CARVE = re.compile(
    r"\b(?:except|unless|other than|save that|save for|excluding|carve-out|"
    r"carve out|does not cover|doesn't cover|does not apply to|doesn't apply to|"
    r"do not apply to)\b",
    re.IGNORECASE,
)
_WITHDRAWN = re.compile(
    r"\bwithdr[ae]wn\b|\bwithdrew\b|\bwithdrawal of this\b",
    re.IGNORECASE,
)
_SUPERSEDED = re.compile(r"\bsuperseded\b", re.IGNORECASE)
_SUPERSEDES_ID = re.compile(
    r"\bsupersedes\s+(SYN-[A-Z0-9]+(?:-[A-Z0-9]+)+)\b",
    re.IGNORECASE,
)
_SUPERSEDED_BY = re.compile(
    r"\bsuperseded by\s+(SYN-[A-Z0-9]+(?:-[A-Z0-9]+)+)\b",
    re.IGNORECASE,
)
_LEADING = re.compile(
    r"\b(?:prefer|prefers|preferred|exclude|excludes|excluding|only|must be|"
    r"restricted to)\b.{0,48}?\b(?:disabled|disability|women|men|woman|man|"
    r"christian|muslim|jewish|white|black|asian|young|older|pregnant|gay|"
    r"lesbian|native english)\b"
    r"|\bnot disabled\b"
    r"|\bnative english speaker\b",
    re.IGNORECASE,
)
_SMALL_COUNT = re.compile(
    r"\b([1-9]\d*)\s+(customers|residents|individuals|people|complainants|staff|persons)\b",
    re.IGNORECASE,
)
_DECIMAL_COUNT = re.compile(
    r"\b\d+\.\d+\s+(customers|residents|individuals|people|complainants|staff|persons)\b",
    re.IGNORECASE,
)
_WORD_COUNT = re.compile(
    r"\b(?:several|many|some|a few)\s+(customers|residents|individuals|people|"
    r"complainants|staff|persons)\b",
    re.IGNORECASE,
)

DISTRESS_RE = re.compile(
    r"end of (?:my|their|his|her|our) tether"
    r"|can(?:not|'t| not) (?:go on|cope|carry on|take (?:this|any more))"
    r"|do(?:n't|es not| not) want to (?:be here|live|carry on|continue|wake up)"
    r"|feel(?:s|ing)? (?:unsafe|frightened|terrified|hopeless)"
    r"|safeguard"
    r"|self[-\s]?harm"
    r"|suicid"
    r"|kill (?:myself|himself|herself|themselves)"
    r"|end (?:my|their|his|her) life"
    r"|no way out"
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
    r"|\bdisclos(?:e|es|ed|ing|ure)\b(?:\s+\w+){0,8}\s+\babuse\b"
    r"|\braising a grievance\b"
    r"|\blodg(?:e|ing) a grievance\b"
    r"|\bintimidat(?:e|ed|ing|ion)\b"
    r"|\bunwanted conduct\b"
    r"|\bsubjected to\b(?:\s+\w+){0,6}\s+\b(?:bullying|harassment|abuse)\b",
    re.IGNORECASE,
)

INJECTION_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |any )?(?:the )?(?:previous|prior|above|your) instructions", re.I)),
    ("forget_rules", re.compile(r"forget (?:all )?(?:your|the) (?:rules|instructions)", re.I)),
    ("persona", re.compile(r"\byou are now\b", re.I)),
    ("mark_applicable", re.compile(r"\bmark this (?:change|notice|publication) as (?:not )?applicable\b", re.I)),
    ("decide_applies", re.compile(r"\b(?:decide|treat) (?:that )?this change (?:as |does )?(?:not )?appl(?:y|ies)\b", re.I)),
    ("change_policy", re.compile(r"\b(?:change|update|amend) the (?:policy|control|record)\b", re.I)),
    ("send", re.compile(r"\bsend (?:the|this) briefing\b", re.I)),
    ("approved_in_text", re.compile(r"\b(?:compliance owner|officer) has (?:already )?approved\b", re.I)),
    ("strip_label", re.compile(r"\b(?:strip|remove|ignore) the (?:legal hold|retention(?: label)?)\b", re.I)),
    ("system_role", re.compile(r"(?m)^\s*system\s*:", re.I)),
    ("developer_role", re.compile(r"(?m)^\s*developer\s*:", re.I)),
    ("disregard_register", re.compile(r"\bdisregard the (?:register|policy register)\b", re.I)),
)

SMALL_NUMBER_THRESHOLD = 5


def sentences(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in _SENTENCE.split(text) if part.strip()]


def span_is_denied(sentence: str, start: int) -> bool:
    """True when a negation in the same sentence governs the match."""

    if start <= 0:
        return False
    return _BEFORE.search(sentence[:start]) is not None


def _index(sentence: str, phrase: str) -> int:
    folded = sentence.casefold()
    needle = phrase.casefold()
    start = 0
    while True:
        index = folded.find(needle, start)
        if index < 0:
            return -1
        after = index + len(needle)
        before_ok = index == 0 or not folded[index - 1].isalnum()
        after_ok = after == len(folded) or not folded[after].isalnum()
        if before_ok and after_ok:
            return index
        start = index + max(len(needle), 1)


def _denied_at(sentence: str, index: int, phrase: str) -> bool:
    if span_is_denied(sentence, index) or _CARVE.search(sentence[:index]):
        return True
    return _AFTER_DENY.search(sentence[index + len(phrase):]) is not None


def phrase_is_denied(sentence: str, phrase: str) -> bool:
    index = _index(sentence, phrase)
    if index < 0:
        return False
    return _denied_at(sentence, index, phrase)


def phrase_relation(text: str, phrase: str) -> str:
    """plain, qualified, denied, or absent. One denied or qualified sentence blocks plain."""

    saw_plain = False
    saw_qualified = False
    saw_denied = False
    for sentence in sentences(text):
        index = _index(sentence, phrase)
        if index < 0:
            continue
        if _denied_at(sentence, index, phrase):
            saw_denied = True
            continue
        if _CARVE.search(sentence[index + len(phrase):]):
            saw_qualified = True
            continue
        saw_plain = True
    if saw_qualified or (saw_plain and saw_denied):
        return "qualified"
    if saw_denied and not saw_plain:
        return "denied"
    if saw_plain:
        return "plain"
    return "absent"


def plain_inclusion(text: str, phrase: str) -> bool:
    return phrase_relation(text, phrase) == "plain"


def affirmed_sentence(text: str, phrase: str) -> str | None:
    if phrase_relation(text, phrase) != "plain":
        return None
    for sentence in sentences(text):
        index = _index(sentence, phrase)
        if index < 0:
            continue
        if _denied_at(sentence, index, phrase):
            continue
        if _CARVE.search(sentence[index + len(phrase):]):
            continue
        return sentence
    return None


def pattern_affirmed(text: str, pattern: re.Pattern[str]) -> bool:
    for sentence in sentences(text):
        match = pattern.search(sentence)
        if match and not span_is_denied(sentence, match.start()):
            return True
    return False


def withdrawn_affirmed(text: str) -> bool:
    return pattern_affirmed(text, _WITHDRAWN)


def superseded_affirmed(text: str) -> bool:
    return pattern_affirmed(text, _SUPERSEDED)


def supersedes_ids(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text):
        for pattern in (_SUPERSEDES_ID,):
            for match in pattern.finditer(sentence):
                if span_is_denied(sentence, match.start()):
                    continue
                value = match.group(1).upper()
                if value not in found:
                    found.append(value)
    return found


def superseded_by_ids(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text):
        for match in _SUPERSEDED_BY.finditer(sentence):
            if span_is_denied(sentence, match.start()):
                continue
            value = match.group(1).upper()
            if value not in found:
                found.append(value)
    return found


def cue_categories(text: str) -> dict:
    distress = False
    grievance = False
    for sentence in sentences(text):
        if DISTRESS_RE.search(sentence):
            distress = True
        if GRIEVANCE_RE.search(sentence):
            grievance = True
    return {"distress": distress, "grievance": grievance}


def injection_signals(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text or ""):
        for name, pattern in INJECTION_RES:
            if pattern.search(sentence) and name not in found:
                found.append(name)
    return found


def leading_criteria(text: str) -> dict:
    """Flag leading wording. applied stays false even when the sentence is negated."""

    flagged = False
    for sentence in sentences(text or ""):
        if _LEADING.search(sentence):
            flagged = True
            break
    return {"flagged": flagged, "applied": False, "note_copied": False}


def people_counts(text: str) -> dict:
    """Aggregate person counts. A count below the threshold is not stored."""

    groups = []
    unparseable = False
    for match in _DECIMAL_COUNT.finditer(text or ""):
        unparseable = True
        groups.append(
            {
                "kind": match.group(1).lower(),
                "suppressed": False,
                "value": None,
                "reason": "unparseable",
                "threshold": SMALL_NUMBER_THRESHOLD,
                "coerced": False,
            }
        )
    for match in _WORD_COUNT.finditer(text or ""):
        unparseable = True
        groups.append(
            {
                "kind": match.group(1).lower(),
                "suppressed": False,
                "value": None,
                "reason": "unparseable",
                "threshold": SMALL_NUMBER_THRESHOLD,
                "coerced": False,
            }
        )
    for match in _SMALL_COUNT.finditer(text or ""):
        number = int(match.group(1))
        kind = match.group(2).lower()
        if number < SMALL_NUMBER_THRESHOLD:
            groups.append(
                {
                    "kind": kind,
                    "suppressed": True,
                    "value": None,
                    "reason": "small_number",
                    "threshold": SMALL_NUMBER_THRESHOLD,
                    "coerced": False,
                }
            )
        else:
            groups.append(
                {
                    "kind": kind,
                    "suppressed": False,
                    "value": number,
                    "reason": None,
                    "threshold": SMALL_NUMBER_THRESHOLD,
                    "coerced": False,
                }
            )
    return {
        "threshold": SMALL_NUMBER_THRESHOLD,
        "groups": groups,
        "unparseable": unparseable,
        "values_stored_for_small_numbers": False,
        "coerced": False,
    }


def content_sentences(text: str) -> list[str]:
    """Sentences that can be quoted. Instructions, cues, and cover lines are skipped."""

    kept: list[str] = []
    for sentence in sentences(text):
        if injection_signals(sentence):
            continue
        cues = cue_categories(sentence)
        if cues["distress"] or cues["grievance"]:
            continue
        stripped = sentence.strip()
        upper = stripped.upper()
        if upper in {"SECRET", "TOP SECRET", "OFFICIAL", "OFFICIAL-SENSITIVE", "LEGAL HOLD"}:
            continue
        if re.match(r"(?i)retention\s*:", stripped):
            continue
        if re.search(r"(?i)\bmy clearance is\b|\bmy role is\b|\bmy name is\b", stripped):
            continue
        if _SMALL_COUNT.search(stripped) or _DECIMAL_COUNT.search(stripped):
            continue
        kept.append(stripped)
    return kept
