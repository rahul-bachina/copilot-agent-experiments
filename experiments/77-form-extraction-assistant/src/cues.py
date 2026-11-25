"""Text cues. A negated phrase is not an inclusion.

Distress, safeguarding, and whistleblowing use the same sentence window.
"It is not true that this form includes a safeguarding concern" is not that cue.
"I do not feel safe" is the cue, because the phrase itself is the concern.
Instructions in the form are recorded and not followed.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import regex_affirmed
else:
    from .negate import regex_affirmed

_PATTERNS: dict[str, tuple[str, ...]] = {
    "distress": (
        r"can(?:not|'t) cope",
        r"\bnot coping\b",
        r"suicid",
        r"end my life",
        r"kill (?:myself|himself|herself|themselves)",
        r"\bfrightened\b",
        r"scared for my",
        r"\bin distress\b",
        r"feel desperate",
        r"cannot go on",
        r"\bno way out\b",
        r"want to die",
    ),
    "safeguarding": (
        r"safeguarding concern",
        r"safeguarding disclosure",
        r"adult at risk",
        r"child at risk",
        r"do not feel safe",
        r"\bnot safe\b",
        r"being harmed",
        r"welfare concern",
        r"someone is hurting",
    ),
    "whistleblowing": (
        r"whistle-?blow",
        r"protected disclosure",
        r"\bgrievance\b",
        r"public interest disclosure",
        r"report wrongdoing",
        r"speak up about fraud",
        r"misconduct concern",
    ),
    "embedded_instruction": (
        r"ignore previous instructions",
        r"ignore (?:all |the |my )?instructions",
        r"ignore the (?:schema|pinned schema|form schema)",
        r"you are now the reviewer",
        r"mark the signature verified",
        r"treat the signature as verified",
        r"set verified to true",
        r"drop the legal hold",
        r"ignore (?:the )?retention",
        r"disregard the (?:marking|hold|label|schema)",
        r"strip the (?:marking|legal hold|retention)",
        r"perform the call-?back",
        r"call-?back (?:has been |is )?completed",
        r"decide the application",
        r"approve this form",
        r"write (?:this |it )?to production",
        r"send the (?:form|record|extraction)",
    ),
    "approval_marker": (
        r"(?:the )?reviewer has approved",
        r"(?:the )?applicant has approved",
        r"this form is approved",
        r"this record is approved",
        r"already approved",
        r"approval:\s*granted",
        r"human approval is recorded",
        r"consider this approved",
        r"signature verified",
        r"bank details verified",
    ),
    "callback_claim": (
        r"call-?back (?:has been |is |was )?completed",
        r"call-?back (?:has been |is |was )?done",
        r"callback completed",
        r"phone check (?:has been |is |was )?completed",
        r"bank details (?:have been |were )?verified by phone",
    ),
}


def category_hit(text: str, category: str) -> bool:
    if not text or category not in _PATTERNS:
        return False
    for pattern in _PATTERNS[category]:
        if regex_affirmed(text, re.compile(pattern, re.IGNORECASE)):
            return True
    return False


def route_categories(text: str) -> list[str]:
    return [name for name in ("distress", "safeguarding", "whistleblowing") if category_hit(text, name)]


def hits(text: str) -> list[str]:
    return [name for name in _PATTERNS if category_hit(text, name)]
