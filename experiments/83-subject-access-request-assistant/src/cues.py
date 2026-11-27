"""Cues in untrusted request and record text.

Distress, safeguarding, whistleblowing, complaint, grievance, and litigation
stems are routed even when the sentence denies them. Instructions, a forged
approval, and a leading search criterion use the same-sentence negation rule.
A bare policy title is not a personal cue.
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
        r"you are now the (?:information governance officer|approver|dpo)",
        r"send the (?:response|disclosure|sar)",
        r"email the requester",
        r"delete the record",
        r"edit the record",
        r"drop the legal hold",
        r"strip the (?:protective )?marking",
        r"remove the retention label",
        r"the exemption (?:is|has been) applied",
        r"decide the exemption",
        r"unredact the",
        r"approve this disclosure",
        r"mark this as approved",
        r"stop the clock now",
        r"the clock is stopped",
        r"treat the embedded approval as enough",
    ),
    "forged_approval": (
        r"the officer has approved",
        r"disclosure is approved",
        r"human approval is recorded",
        r"redactions are approved",
        r"the exemption is accepted",
        r"already been decided",
        r"consider this approved",
        r"approval:\s*granted",
        r"already approved",
        r"the approver has seen this hash",
        r"route seen is recorded",
        r"approved by the information governance officer",
        r"identity is confirmed",
        r"authority is confirmed",
        r"this redaction is approved",
    ),
    "leading_criterion": (
        r"only (?:search|include) records that",
        r"ignore documents that help",
        r"do not search the records that support",
        r"search only the unfavourable",
        r"search only the unfavorable",
        r"biased search",
        r"leading search",
        r"prefer records that harm",
        r"withhold anything that helps the requester",
        r"only keep documents that look bad",
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
    r"this safeguarding matter|child protection(?!\s+policy)|harm to a child|"
    r"a child may be at risk|at risk of harm|adult at risk|child is being harmed|"
    r"report a safeguarding",
    re.IGNORECASE,
)
_WHISTLE = re.compile(
    r"whistle[\s-]?blow(?:ing|er)?|protected disclosure|public interest (?:concern|disclosure)|"
    r"blow(?:ing)? the whistle",
    re.IGNORECASE,
)
_COMPLAINT = re.compile(
    r"(?:raise|raising|lodge|lodging|file|filing|submit|submitting|make|making)\s+"
    r"(?:a\s+|my\s+|the\s+)?complaint|"
    r"formal complaint|wish to complain|this is a complaint|my complaint|i want to complain",
    re.IGNORECASE,
)
_GRIEVANCE = re.compile(
    r"(?:raise|raising|lodge|lodging|file|filing|submit|submitting)\s+(?:a\s+|my\s+|the\s+)?grievance|"
    r"my grievance|formal grievance",
    re.IGNORECASE,
)
_LITIGATION = re.compile(
    r"letter before claim|legal proceedings|issued proceedings|court claim|"
    r"\bin litigation\b|pre-action|county court|claim has been issued|solicitor has issued",
    re.IGNORECASE,
)
_POLICY_ONLY = re.compile(
    r"\b(?:safeguarding|whistle-?blowing|grievance|complaints?|litigation)\s+"
    r"(?:policy|procedure|procedures|guidance)\b",
    re.IGNORECASE,
)
_CARVE = re.compile(
    r"\bexcept\b|\bunless\b|provided that|subject to|save where|save that|"
    r"apart from|other than|only if|only when|\bcarve-out\b",
    re.IGNORECASE,
)
_ROLE_CLAIM = re.compile(
    r"\bi am the information governance officer\b|\bmy role is\b|\bmy clearance is\b|"
    r"\bi am the dpo\b|\bmy role is guest\b",
    re.IGNORECASE,
)
_AUTHORITY = re.compile(
    r"\bi act for\b|\bon behalf of\b|\bour client\b|\binstructed by\b|"
    r"\bsolicitor for\b|\bas their representative\b|\bpower of attorney\b|"
    r"\bdeputy for\b|\bwe represent\b",
    re.IGNORECASE,
)
_PERSONAL = re.compile(
    r"\b(i am|i'm|i feel|i need|i want|please|my grievance|my complaint|disclosure about)\b",
    re.IGNORECASE,
)


def category_hit(text: str, category: str) -> bool:
    if not text or category not in _PATTERNS:
        return False
    for pattern in _PATTERNS[category]:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            return True
    return False


def _routed(text: str, pattern: re.Pattern[str]) -> bool:
    if not text or _policy_title_only(text):
        return False
    return regex_present(text, pattern)


def distress_hit(text: str) -> bool:
    return _routed(text, _DISTRESS)


def safeguarding_hit(text: str) -> bool:
    return _routed(text, _SAFEGUARDING)


def whistleblowing_hit(text: str) -> bool:
    return _routed(text, _WHISTLE)


def complaint_hit(text: str) -> bool:
    return _routed(text, _COMPLAINT)


def grievance_hit(text: str) -> bool:
    return _routed(text, _GRIEVANCE)


def litigation_hit(text: str) -> bool:
    return _routed(text, _LITIGATION)


def sensitive_categories(text: str) -> list[str]:
    found = []
    if distress_hit(text):
        found.append("distress")
    if safeguarding_hit(text):
        found.append("safeguarding")
    if whistleblowing_hit(text):
        found.append("whistleblowing")
    if complaint_hit(text):
        found.append("complaint")
    if grievance_hit(text):
        found.append("grievance")
    if litigation_hit(text):
        found.append("litigation")
    return found


def carve_out_affirmed(text: str) -> bool:
    return regex_affirmed(text or "", _CARVE)


def role_claim(text: str) -> bool:
    return regex_affirmed(text or "", _ROLE_CLAIM)


def authority_claim(text: str) -> bool:
    return regex_affirmed(text or "", _AUTHORITY)


def _policy_title_only(text: str) -> bool:
    if not _POLICY_ONLY.search(text or ""):
        return False
    return _PERSONAL.search(text or "") is None
