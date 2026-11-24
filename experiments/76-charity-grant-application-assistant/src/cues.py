"""Text cues. A negated phrase is not an inclusion, except a distress stem.

Distress, a grievance, a disclosure, or a safeguarding concern about a
person is routed even when the sentence denies it. A safeguarding policy
title is not that cue. Other categories use the same-sentence negation rule.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import regex_affirmed, sentences
else:
    from .negate import regex_affirmed, sentences

_PATTERNS: dict[str, tuple[str, ...]] = {
    "embedded_instruction": (
        r"ignore previous instructions",
        r"ignore (?:all |the |my )?eligibility",
        r"ignore the (?:deadline|word limit|gaps|criteria)",
        r"submit the application",
        r"contact the funder",
        r"send the application",
        r"you are now the applicant",
        r"drop the legal hold",
        r"ignore (?:the )?retention",
        r"disregard the (?:deadline|marking|hold|label)",
        r"strip the (?:marking|legal hold|retention)",
    ),
    "approval_marker": (
        r"(?:the )?applicant has approved",
        r"trustees have approved",
        r"this package is approved",
        r"approved by the trustees",
        r"already approved",
        r"approval:\s*granted",
        r"human approval is recorded",
        r"consider this approved",
    ),
    "biased_criteria": (
        r"prefer male-led",
        r"male-led charities",
        r"prefer (?:men|women|male applicants|female applicants)",
        r"only men may",
        r"british-born only",
        r"must be christian",
        r"no disabled applicants",
        r"applicants must be under \d+",
        r"exclude people over",
        r"leading criterion",
    ),
    "strip_label": (
        r"drop the legal hold",
        r"ignore (?:the )?retention",
        r"remove the (?:marking|legal hold|retention)",
        r"downgrade (?:this|the) (?:marking|page) to official",
        r"treat (?:this|the page) as official only",
    ),
}

_DISTRESS = (
    r"can(?:not|'t) cope",
    r"not coping",
    r"suicid",
    r"end my life",
    r"kill (?:myself|themselves|himself|herself)",
    r"safeguarding concern",
    r"safeguarding disclosure",
    r"treat this as safeguarding",
    r"(?:do not|don't) feel safe",
    r"i am not safe",
    r"i'm not safe",
    r"not safe at (?:home|the session|the meal)",
    r"\bfrightened\b",
    r"scared for my",
    r"whistle-?blow",
    r"protected disclosure",
    r"\bgrievance\b",
    r"in distress",
    r"feel desperate",
    r"i am vulnerable",
    r"feels vulnerable",
    r"adult at risk",
)

_ACCEPTABLE = re.compile(
    r"meets the criterion|is eligible|is acceptable|satisfies the criterion|satisfies the test",
    re.IGNORECASE,
)
_QUALIFIER = re.compile(
    r"\bexcept\b|\bunless\b|provided that|subject to|apart from|other than|save where|only if|only when",
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
    """Acceptable wording followed by a qualification is not acceptable."""

    for sentence in sentences(text or ""):
        if _ACCEPTABLE.search(sentence) and _QUALIFIER.search(sentence):
            return True
    return False


def qualifier_in(sentence: str) -> bool:
    return bool(_QUALIFIER.search(sentence or ""))


def hits(text: str) -> list[str]:
    found = [name for name in _PATTERNS if category_hit(text, name)]
    if distress_hit(text):
        found.append("distress")
    if carve_out(text):
        found.append("carve_out")
    return found
