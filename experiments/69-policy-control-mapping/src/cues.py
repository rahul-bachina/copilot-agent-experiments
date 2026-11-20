"""Distress, grievance, and instruction cues.

A paraphrase that uses none of these stems is not flagged. That limit is
stated on the smoke report. The stems are an example list, not a statistic.
"""

from __future__ import annotations

import re

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

INJECTION_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (?:all |any |the )?(?:previous|prior|above) instructions", re.I)),
    ("ignore_instructions", re.compile(r"disregard (?:the )?(?:previous|prior|above) (?:instructions|controls|rules)", re.I)),
    ("mark_met", re.compile(r"mark (?:the |this )?(?:control|mapping|gap).{0,40}\b(?:met|closed|approved)\b", re.I)),
    ("close_gap", re.compile(r"close (?:the |this |that )?gap", re.I)),
    ("edit_policy", re.compile(r"\bedit (?:the |this )?policy\b", re.I)),
    ("edit_policy", re.compile(r"\b(?:change|rewrite|update) the policy text\b", re.I)),
    ("write_grc", re.compile(r"\bwrite (?:this |the result |it )?to the grc\b", re.I)),
    ("write_grc", re.compile(r"\b(?:update|post) (?:the |to the )?grc system\b", re.I)),
    ("role_override", re.compile(r"\byou are now\b", re.I)),
    ("system_prompt", re.compile(r"\bsystem prompt\b", re.I)),
    ("forged_approval", re.compile(r"\b(?:the control owner has approved|human_approval is true|approved\s*[:=]\s*true)\b", re.I)),
    ("self_role", re.compile(r"\bmy role is\b", re.I)),
    ("self_clearance", re.compile(r"\bmy clearance is\b", re.I)),
    ("pretend_approved", re.compile(r"\bpretend (?:this |the )?(?:mapping|control) is approved\b", re.I)),
)

BIASED_RE = re.compile(
    r"\bonly\b(?:\s+\w+){0,4}\s+\b(?:junior|younger|older|male|female|women|men)\b"
    r"|\bblame\b(?:\s+\w+){0,4}\s+\b(?:user|users|staff|employee|employees|worker|workers)\b"
    r"|\bignore\b(?:\s+\w+){0,6}\s+\b(?:exception|exceptions)\b(?:\s+\w+){0,6}\s+\b(?:senior|directors|managers)\b"
    r"|\bonly count\b(?:\s+\w+){0,6}\s+\bfailures\b"
    r"|\bprefer\b(?:\s+\w+){0,3}\s+\b(?:male|female|men|women)\b"
    r"|\bwomen should not\b"
    r"|\bmen should not\b"
    r"|\bage over\b"
    r"|\bdiscount\b(?:\s+\w+){0,4}\s+\bstatements\b"
    r"|\bled by\b(?:\s+\w+){0,3}\s+\b(?:gender|age|race)\b"
    r"|\bbias(?:ed)? criterion\b"
    r"|\bcount it against\b(?:\s+\w+){0,4}\s+\b(?:junior|women|older)\b",
    re.IGNORECASE,
)

_ROLE_CLAIM = re.compile(r"\bmy role is\b", re.IGNORECASE)
_CLEARANCE_CLAIM = re.compile(r"\bmy clearance is\b", re.IGNORECASE)


def cue_categories(text: str) -> list[str]:
    found: list[str] = []
    if text and DISTRESS_RE.search(text):
        found.append("distress")
    if text and GRIEVANCE_RE.search(text):
        found.append("grievance")
    return found


def injection_codes(text: str) -> list[str]:
    """Phrases are recorded. A negation in the same sentence does not hide them.

    The phrase is not followed. A sentence that tells a person not to follow
    an embedded instruction is still recorded, and it is still not followed.
    """

    if not text:
        return []
    found: list[str] = []
    for code, pattern in INJECTION_RES:
        if pattern.search(text) and code not in found:
            found.append(code)
    return found


def biased(text: str) -> bool:
    return bool(text and BIASED_RE.search(text))


def claims_role(text: str) -> bool:
    return bool(text and _ROLE_CLAIM.search(text))


def claims_clearance(text: str) -> bool:
    return bool(text and _CLEARANCE_CLAIM.search(text))
