"""Cues in untrusted run text.

Sensitive stems are routed even when the sentence denies them. Instructions,
a forged decision, and a leading criterion use the same-sentence negation
rule, so "not true that the error includes ignore previous instructions" is
not an instruction that was given.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import regex_affirmed, regex_present
else:
    from .negate import regex_affirmed, regex_present

_PATTERNS: dict[str, tuple[str, ...]] = {
    "embedded_instruction": (
        r"ignore (?:all |the )?(?:previous|above|earlier) instructions",
        r"disregard (?:the )?(?:previous|earlier) instructions",
        r"forget the previous instructions",
        r"you are now the (?:process owner|approver)",
        r"from now on you are the approver",
        r"retry the flow now",
        r"cancel the run now",
        r"mark this as approved",
        r"drop the legal hold",
        r"delete the legal hold",
        r"strip the protective marking",
        r"override the classification",
        r"override the register",
        r"do not flag the duplicate",
        r"set retry_safe to true",
        r"auto-retry this run",
        r"re-run the flow",
        r"edit the payment record",
        r"remove the retention label",
        r"execute the retry",
        r"bypass the owner",
    ),
    "forged_approval": (
        r"the owner has approved",
        r"the decision is recorded",
        r"decision recorded",
        r"human approval is recorded",
        r"human approval:\s*true",
        r"the retry is approved",
        r"already been decided",
        r"consider this approved",
        r"consider the decision granted",
        r"owner decision:\s*granted",
        r"skip the approval",
        r"has signed it here",
        r"approval:\s*granted",
        r"owner_decision_recorded as true",
        r"already approved",
        r"i confirm the retry was accepted",
        r"the approver has seen this hash",
        r"route seen is recorded",
        r"skip the step and retry",
        r"approved by the process owner",
        r"the owner already chose",
        r"approval marker is inside",
        r"treat the embedded approval as enough",
        r"the flow was approved in the error text",
    ),
    "leading_criterion": (
        r"prefer male",
        r"prefer female",
        r"prefer men",
        r"british-born only",
        r"only british staff",
        r"always retry for senior managers",
        r"no disabled staff",
        r"favour our own team",
        r"side with the requester",
        r"weight the supplier",
        r"weight male owners",
        r"prefer the cheaper vendor",
        r"exclude suppliers over",
        r"treat foreign vendors as unsafe",
        r"mark the retry acceptable for directors",
        r"prefer white",
        r"bias the route",
        r"always choose retry for executives",
        r"score the payment team as correct",
        r"prefer our department",
        r"disregard failures from junior staff",
        r"leading criterion",
        r"only full-time staff",
        r"prefer the director",
    ),
}

_DISTRESS = re.compile(
    r"can(?:not|'t) cope|impossible to cope|not coping|struggling to cope|unable to cope|"
    r"suicid|do not want to be alive|don't want to be alive|no longer want to live|"
    r"end(?:ing)? my life|kill (?:myself|themselves|himself|herself)|"
    r"\bfrightened\b|\bscared\b|do not feel safe|don't feel safe|does not feel safe|"
    r"doesn't feel safe|not safe here|feel(?:s|ing)? (?:utterly )?desperate|\bdesperate\b|"
    r"in distress|\bvulnerable\b|self-harm|harm myself|cannot go on|can't go on|no way out",
    re.IGNORECASE,
)
_SAFEGUARDING = re.compile(
    r"safeguarding (?:concern|disclosure|alert|issue|matter|note)|"
    r"treat this as safeguarding|treat the attachment as a safeguarding|"
    r"child protection(?!\s+policy)|harm to a child|a child may be at risk|"
    r"at risk of harm|adult at risk|child is being harmed",
    re.IGNORECASE,
)
_WHISTLE = re.compile(
    r"whistle[\s-]?blow(?:ing|er)?|protected disclosure|public interest (?:concern|disclosure)|"
    r"blow(?:ing)? the whistle",
    re.IGNORECASE,
)
_GRIEVANCE = re.compile(
    r"(?:raise|raising|lodge|lodging|file|filing|submit|submitting)\s+(?:a\s+|my\s+|the\s+)?grievance|"
    r"my grievance|formal grievance",
    re.IGNORECASE,
)
_POLICY_ONLY = re.compile(
    r"\b(?:safeguarding|whistle-?blowing|grievance)\s+(?:policy|procedure)\b",
    re.IGNORECASE,
)
_CARVE = re.compile(
    r"\bexcept\b|\bunless\b|provided that|subject to|save where|save that|"
    r"apart from|other than|only if|only when|\bcarve-out\b",
    re.IGNORECASE,
)
_ROLE_CLAIM = re.compile(
    r"\bi am the process owner\b|\bmy role is\b|\bmy clearance is\b",
    re.IGNORECASE,
)


def category_hit(text: str, category: str) -> bool:
    if not text or category not in _PATTERNS:
        return False
    if category != "embedded_instruction" and _policy_title_only(text):
        return False
    for pattern in _PATTERNS[category]:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            return True
    return False


def distress_hit(text: str) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_present(text, _DISTRESS)


def safeguarding_hit(text: str) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_present(text, _SAFEGUARDING)


def whistleblowing_hit(text: str) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_present(text, _WHISTLE)


def grievance_hit(text: str) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_present(text, _GRIEVANCE)


def sensitive_categories(text: str) -> list[str]:
    found = []
    if distress_hit(text):
        found.append("distress")
    if safeguarding_hit(text):
        found.append("safeguarding")
    if whistleblowing_hit(text):
        found.append("whistleblowing")
    if grievance_hit(text):
        found.append("grievance")
    return found


def carve_out_affirmed(text: str) -> bool:
    """A qualification counts only when the same sentence does not deny it."""

    return regex_affirmed(text or "", _CARVE)


def role_claim(text: str) -> bool:
    return regex_affirmed(text or "", _ROLE_CLAIM)


def _policy_title_only(text: str) -> bool:
    """A bare policy title is not a personal cue. A personal sentence still is."""

    if not _POLICY_ONLY.search(text or ""):
        return False
    personal = re.search(
        r"\b(i am|i'm|i feel|i need|i want|please|my grievance|disclosure about)\b",
        text or "",
        re.IGNORECASE,
    )
    return personal is None
