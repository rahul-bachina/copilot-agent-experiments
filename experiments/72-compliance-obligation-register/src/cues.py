"""Distress, grievance, injection, and biased wording.

A paraphrase that uses one of these stems is flagged. A paraphrase that uses
none of them is not. The smoke report states recall on the fixture sentences.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import sentences
else:
    from .negate import sentences

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
    r"|\bthreatened with\b"
    r"|\bdisclos(?:e|es|ed|ing|ure)\b(?:\s+\w+){0,8}\s+\babuse\b"
    r"|\bintimidat(?:e|ed|ing|ion)\b",
    re.IGNORECASE,
)
INJECTION_RE = re.compile(
    r"ignore (?:all |any )?(?:previous|prior|above) instructions"
    r"|you are now"
    r"|mark (?:every|all) obligations?(?: as)? covered"
    r"|strip the (?:legal hold|retention)"
    r"|drop the (?:legal hold|retention|label)"
    r"|pretend the owner"
    r"|owner has (?:already )?approved"
    r"|assign accountability"
    r"|send the register"
    r"|disregard the (?:directory|pinned)"
    r"|pasted register as the source"
    r"|override the pinned"
    r"|forget the approval"
    r"|final legal advice"
    r"|this is final advice"
    r"|write to production"
    r"|jailbreak"
    r"|new instructions"
    r"|do not follow the deterministic"
    r"|\bsystem:"
    r"|approve the change now",
    re.IGNORECASE,
)
BIASED_RE = re.compile(
    r"\bnative english\b"
    r"|\bnot be disabled\b"
    r"|\bnot disabled\b"
    r"|\bmust be a man\b"
    r"|\bmust be a woman\b"
    r"|\bexclude women\b"
    r"|\bexclude men\b"
    r"|\brestricted to white\b"
    r"|\bprefer younger\b"
    r"|\bno pregnant\b"
    r"|\bmust be christian\b"
    r"|\bonly christian\b"
    r"|\bprefer men\b"
    r"|\bable-bodied only\b"
    r"|\bno one over \d+\b"
    r"|\benglish speaker only\b"
    r"|\bonly (?:men|women|young people)\b",
    re.IGNORECASE,
)
_ROLE = re.compile(
    r"\bmy role is\b|\bi am the compliance owner\b|\bmy clearance is\b",
    re.IGNORECASE,
)
_SMALL = re.compile(
    r"\b([1-9]\d*)\s+(staff|people|employees|individuals|persons|customers)\b",
    re.IGNORECASE,
)
_WORD_COUNT = re.compile(
    r"\b(?:several|many|some|a few)\s+(staff|people|employees|individuals|persons|customers)\b",
    re.IGNORECASE,
)


def cue_categories(text: str) -> list[str]:
    found: list[str] = []
    body = text or ""
    if DISTRESS_RE.search(body):
        found.append("distress")
    if GRIEVANCE_RE.search(body):
        found.append("grievance")
    if "safeguard" in body.casefold() or "child is not safe" in body.casefold():
        if "safeguarding" not in found:
            found.append("safeguarding")
    return found


def injection_signals(text: str) -> list[str]:
    found = []
    for sentence in sentences(text or ""):
        if INJECTION_RE.search(sentence):
            found.append("instruction")
            break
    return found


def biased(text: str) -> bool:
    return bool(BIASED_RE.search(text or ""))


def self_declared(text: str) -> bool:
    return bool(_ROLE.search(text or ""))


def people_mentions(text: str) -> dict:
    """A count below 5 is not stored. An unreadable word is not stored as zero."""

    numbers = []
    unreadable = False
    for match in _SMALL.finditer(text or ""):
        numbers.append(int(match.group(1)))
    if _WORD_COUNT.search(text or ""):
        unreadable = True
    small = [number for number in numbers if number < 5]
    return {
        "below_threshold": bool(small) or unreadable,
        "unreadable": unreadable,
        "number_stored": False,
        "coerced": False,
        "threshold": 5,
    }
