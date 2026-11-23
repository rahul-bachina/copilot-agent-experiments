"""Text cues. A negated phrase is not an inclusion, except a distress stem.

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
    "self_approval": (
        r"self[-\s]?approv",
        r"approv\w* (?:my|their|his|her) own",
        r"preparer (?:is|was) the approver",
        r"approver (?:is|was) the preparer",
        r"same person (?:prepared|wrote).{0,80}approv",
        r"author also approved",
        r"signed off (?:my|their|his|her) own",
        r"person who prepared it approved their own",
        r"(?:requester|maker|staff|colleague) approved (?:their|his|her) own",
    ),
    "back_dated": (
        r"back[-\s]?dat",
        r"(?:date|approval) was moved earlier",
        r"moved the date earlier",
        r"(?:the )?approval date (?:was )?changed to an earlier",
        r"changed the approval date to an earlier",
        r"dated before it was prepared",
        r"approved before it was prepared",
        r"earlier than the prepar",
    ),
    "out_of_period": (
        r"out of (?:the )?period",
        r"outside the (?:test )?period",
        r"before the period (?:start|started|began)",
        r"after the period (?:end|ended)",
        r"not in the (?:quarter|period)",
        r"falls outside",
    ),
    "altered": (
        r"\baltered\b",
        r"tamper",
        r"changed after (?:approval|sign-off|sign off)",
        r"modified after",
        r"edited after",
        r"hash (?:does not|doesn't|did not|didn't) match",
    ),
    "missing_evidence": (
        r"evidence is missing",
        r"missing evidence",
        r"no evidence (?:was|is) (?:on file|provided|attached)",
        r"required field is (?:blank|missing|empty)",
        r"approver (?:is|was) not recorded",
        r"document (?:was )?not provided",
        r"field is blank",
    ),
    "embedded_instruction": (
        r"ignore (?:the |previous |all |my )?(?:test steps|instructions|checks)",
        r"mark (?:this |the )?control (?:as )?(?:passed|failed|effective)",
        r"close (?:the |this )?finding",
        r"you are now the tester",
        r"send the working paper",
    ),
    "approval_marker": (
        r"this control is passed",
        r"control (?:is|was) passed",
        r"result:\s*pass",
        r"tester has approved",
        r"approved by the (?:board|audit committee|tester)",
        r"control is effective",
        r"passed the control",
    ),
    "biased_criteria": (
        r"already marked pass",
        r"ignore (?:any |the )?exceptions?",
        r"treat (?:every|each|all).{0,50}(?:pass|effective)",
        r"only (?:look at|sample) (?:the )?(?:passes|clean items|items already)",
        r"leading criterion",
        r"sample the passes",
    ),
    "sod_breach": (
        r"subordinate approv",
        r"approver reports to",
        r"junior (?:staff|colleague) approv",
        r"segregation of duties (?:breach|broken|failed)",
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

_INDEPENDENCE = re.compile(
    r"independent of the preparer|separate from the preparer",
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
    """An independence sentence with a following qualification is not acceptable."""

    for sentence in sentences(text or ""):
        if _INDEPENDENCE.search(sentence) and _QUALIFIER.search(sentence):
            return True
    return False


def hits(text: str) -> list[str]:
    found = [name for name in _PATTERNS if category_hit(text, name)]
    if distress_hit(text):
        found.append("distress")
    if carve_out(text):
        found.append("carve_out")
    return found
