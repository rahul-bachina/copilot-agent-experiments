"""Text cues.

Distress, safeguarding, whistleblowing, grievance, and sensitive disclosure
stems are routed even when the sentence denies them. Instructions, a forged
approval, a self-declared role, and a leading criterion use the same-sentence
negation rule, so "not true that the note says to ignore previous instructions"
is not an instruction that was given.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import affirmed, regex_affirmed, regex_present, sentences
else:
    from .negate import affirmed, regex_affirmed, regex_present, sentences

_PATTERNS: dict[str, tuple[str, ...]] = {
    "distress": (
        r"\bcop(?:e|ing)\b",
        r"suicid",
        r"kill myself",
        r"end(?:ing)? my life",
        r"do not want to be alive",
        r"\bfrightened\b",
        r"\bscared\b",
        r"feel safe",
        r"\bdesperate\b",
        r"in distress",
        r"\bvulnerable\b",
    ),
    "safeguarding": (
        r"safeguarding",
        r"child protection",
        r"adult at risk",
        r"harm to a child",
        r"child may be at risk",
        r"being harmed",
        r"young person",
    ),
    "whistleblowing": (
        r"whistle",
        r"protected disclosure",
        r"public interest disclosure",
        r"public interest concern",
    ),
    "grievance": (
        r"\bgrievance\b",
        r"bullied by my manager",
        r"being bullied",
        r"unfair treatment by my line manager",
    ),
    "disclosure": (
        r"\bdiagnosis\b",
        r"medical condition",
        r"i am pregnant",
        r"my health",
        r"mental health",
        r"\bdepression\b",
        r"disclosing my health",
    ),
    "embedded_instruction": (
        r"ignore previous instructions",
        r"ignore all previous instructions",
        r"you are now the approver",
        r"drop the legal hold",
        r"strip the protective marking",
        r"disregard the retention",
        r"send the pack",
        r"submit the request",
        r"sign on my behalf",
        r"set approved to true",
        r"override the matrix",
        r"use this approval matrix",
        r"approve this pack",
        r"reject this pack",
    ),
    "forged_approval": (
        r"this pack is approved",
        r"approved by the director",
        r"approval:\s*granted",
        r"has been signed off",
        r"i approve this request",
        r"human approval is recorded",
        r"consider this approved",
        r"already approved",
        r"the approver has seen this",
        r"skip the approval",
    ),
    "self_declared": (
        r"my clearance is",
        r"my role is",
        r"i am a guest",
        r"i have delegated authority",
        r"treat me as the approver",
    ),
    "leading_criterion": (
        r"prefer male",
        r"prefer female",
        r"british-born",
        r"british-owned",
        r"because they are senior",
        r"weight the requester",
        r"no disabled",
        r"favour the director",
        r"mark the pack acceptable",
        r"approve the friends",
        r"cheaper quote without",
        r"only men should",
    ),
    "split_cue": (
        r"split this so",
        r"stay under the threshold",
        r"stays under the limit",
        r"break it into smaller",
        r"dodge the threshold",
        r"keep each part under",
    ),
}

_ACCEPT = re.compile(r"\bacceptable\b|\bis complete\b|\bsigned off\b", re.IGNORECASE)
_QUALIFIER = re.compile(
    r"\bexcept\b|\bunless\b|\bhowever\b|\bbut\b|provided that|save that",
    re.IGNORECASE,
)
_SENSITIVE = ("distress", "safeguarding", "whistleblowing", "grievance", "disclosure")


def category_hit(text: str, category: str) -> bool:
    if not text or category not in _PATTERNS:
        return False
    patterns = _PATTERNS[category]
    present = category in _SENSITIVE
    for pattern in patterns:
        compiled = re.compile(pattern, re.IGNORECASE)
        if present:
            if regex_present(text, compiled):
                return True
        elif regex_affirmed(text, compiled):
            return True
    return False


def concern_hits(text: str) -> dict:
    found = {name: category_hit(text, name) for name in _SENSITIVE}
    found["any"] = any(found.values())
    return found


def carve_out(text: str) -> bool:
    for sentence in sentences(text or ""):
        if _ACCEPT.search(sentence) and _QUALIFIER.search(sentence):
            return True
    return False


def text_says_acceptable(text: str) -> bool:
    """A qualifier after acceptable wording is not an acceptance. Text never is."""

    if not text or carve_out(text):
        return False
    if affirmed(text, "acceptable"):
        return True
    return affirmed(text, "is complete")
