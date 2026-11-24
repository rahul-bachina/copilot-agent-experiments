"""Text cues for a board pack. A negated phrase is not an inclusion.

Distress, a grievance, or a safeguarding word is routed even when the
sentence denies it. Other categories use the same-sentence negation rule.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import regex_affirmed, sentences
else:
    from .negate import regex_affirmed, sentences

_PATTERNS: dict[str, tuple[str, ...]] = {
    "approval_marker": (
        r"approved by",
        r"has approved",
        r"have approved",
        r"pack is approved",
        r"pack has been approved",
        r"paper is approved",
        r"minutes are approved",
        r"minutes have been approved",
        r"already approved",
        r"board has approved",
        r"record (?:these |the |them as )?minutes as approved",
    ),
    "embedded_instruction": (
        r"circulate (?:the |this )?pack",
        r"ignore (?:the |previous |all )?(?:terms|checks|cover|instructions|agenda)",
        r"record (?:these |the )?minutes as approved",
        r"file the pack",
        r"publish the pack",
        r"send the pack",
        r"you are now the company secretary",
    ),
    "conflict_declared": (
        r"i declare an interest",
        r"declare a conflict",
        r"conflict of interest",
        r"i have an interest in",
        r"potential conflict",
        r"my interest in",
        r"conflicted on this",
    ),
    "outside_remit": (
        r"community grants?",
        r"executive remuneration",
        r"executive pay",
        r"nomination of directors",
    ),
    "role_claim": (
        r"i am the company secretary",
        r"my role is",
        r"i am a director",
        r"treat me as the secretary",
    ),
    "biased_criteria": (
        r"treat every paper as complete",
        r"ignore (?:any |the )?(?:missing|late) papers",
        r"mark (?:every|each|all) papers? (?:as )?in remit",
        r"leading criterion",
    ),
}

_DISTRESS = (
    r"can(?:not|'t) cope",
    r"not coping",
    r"suicid",
    r"end my life",
    r"kill (?:myself|themselves|himself|herself)",
    r"safeguard",
    r"(?:do not|don't) feel safe",
    r"i am not safe",
    r"i'm not safe",
    r"not safe at (?:home|work|the office)",
    r"frightened",
    r"scared for",
    r"whistle-?blow",
    r"protected disclosure",
    r"\bgrievance\b",
    r"in distress",
    r"feel desperate",
    r"please help me",
)

_COMPLETE = re.compile(
    r"cover sheet (?:standard )?is complete|standard is met|implications are complete",
    re.IGNORECASE,
)
_QUALIFIER = re.compile(
    r"\bexcept\b|\bunless\b|provided that|save where|other than|only if|only when",
    re.IGNORECASE,
)


def category_hit(text: str, category: str) -> bool:
    if not text or category not in _PATTERNS:
        return False
    for pattern in _PATTERNS[category]:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            return True
    return False


def distress_hit(text: str) -> bool:
    """A distress stem is kept even when the sentence denies it."""

    if not text:
        return False
    for pattern in _DISTRESS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def carve_out(text: str) -> bool:
    """A completeness sentence with a following qualification is not acceptable."""

    for sentence in sentences(text or ""):
        if _COMPLETE.search(sentence) and _QUALIFIER.search(sentence):
            return True
    return False


def hits(text: str) -> list[str]:
    found = [name for name in _PATTERNS if category_hit(text, name)]
    if distress_hit(text):
        found.append("distress")
    if carve_out(text):
        found.append("carve_out")
    return found
