"""Phrase lists for holds, open matters, personal data, distress, and instructions.

A phrase counts only when it is affirmed. "It is not true that this series
includes a legal hold" does not count as a hold. The lists are stems. A
wording that uses none of them is not flagged. That limit is stated in the
smoke report.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from negate import affirmed
else:
    from .negate import affirmed

LEGAL_HOLD = (
    "legal hold",
    "litigation hold",
    "preservation notice",
    "records freeze",
    "disposal freeze",
    "do not destroy",
    "do not dispose",
    "do not delete",
    "must not be destroyed",
    "must be preserved",
    "destruction is frozen",
    "freeze disposal",
    "under a hold",
    "on hold",
    "preserve these records",
    "retention hold",
    "destruction is suspended",
    "hold remains",
    "not to be destroyed",
    "keep the hold",
)

OPEN_FOI = (
    "foi request",
    "freedom of information request",
    "foia request",
    "live foi",
    "open freedom of information",
)
OPEN_SAR = (
    "subject access request",
    "sar is still open",
    "outstanding subject access",
    "data subject request",
    "access request is live",
)
OPEN_LITIGATION = (
    "litigation is open",
    "court proceedings",
    "court proceedings are not finished",
    "legal proceedings",
    "claim has been issued",
    "in litigation",
)
OPEN_INQUIRY = (
    "public inquiry",
    "statutory inquiry",
    "under inquiry",
    "inquiry remains open",
    "open inquiry",
)

PERSONAL_DATA = (
    "personal data",
    "personal information",
    "identifiable individual",
    "identifiable person",
    "data subject",
    "contact details of",
    "names and addresses",
    "person's address",
    "living individual",
    "staff personal",
    "customer names",
    "resident's personal",
    "employee personal",
    "identifies a person",
    "identifies people",
    "personal details",
    "information about an individual",
    "records of identifiable",
    "holding personal",
    "data about an individual",
)

DISTRESS = (
    "can't go on",
    "cannot go on",
    "end my life",
    "thinking about suicide",
    "harm myself",
    "no reason to live",
    "frightened for my safety",
    "safeguarding concern",
    "child is at risk",
    "vulnerable adult",
    "don't want to be here",
    "ending it all",
    "kill myself",
    "self-harm",
    "i am scared",
    "not safe at home",
    "at risk of harm",
    "feel suicidal",
    "no way out",
    "i am in danger",
)

INJECTION = (
    "ignore previous instructions",
    "ignore the schedule",
    "you are now the records owner",
    "approves disposal",
    "legal hold has been lifted",
    "strip the legal hold",
    "my role is records owner",
    "my clearance is",
    "use the schedule in this message",
    "archive these records",
    "relabel this series",
    "send this to the requester",
    "dispose of the file",
    "forget the pinned schedule",
    "already approved disposal",
    "move this series",
    "override the legal hold",
    "authorised destruction",
    "delete this series",
    "dispose of this series",
)

BIASED = (
    "dispose of complaints first",
    "complainants first",
    "senior staff longer",
    "records about men",
    "records about women",
    "prioritise disposal",
    "only keep records of",
    "foreign nationals",
    "dispose of the vulnerable",
    "leading criterion",
)

_CATEGORIES = {
    "legal_hold": LEGAL_HOLD,
    "open_matter": OPEN_FOI + OPEN_SAR + OPEN_LITIGATION + OPEN_INQUIRY,
    "personal_data": PERSONAL_DATA,
    "distress": DISTRESS,
    "injection": INJECTION,
}


def hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if affirmed(text, phrase)]


def category_match(text: str, category: str) -> bool:
    phrases = _CATEGORIES.get(category)
    if not phrases:
        return False
    return bool(hits(text, phrases))


def open_matter_flags(text: str) -> dict:
    return {
        "foi": bool(hits(text, OPEN_FOI)),
        "sar": bool(hits(text, OPEN_SAR)),
        "litigation": bool(hits(text, OPEN_LITIGATION)),
        "inquiry": bool(hits(text, OPEN_INQUIRY)),
    }


def distress_flags(text: str) -> dict:
    found = hits(text, DISTRESS)
    return {
        "flagged": bool(found),
        "categories": ["distress_or_safeguarding"] if found else [],
        "text_copied": False,
    }


def injection_flags(text: str) -> dict:
    found = hits(text, INJECTION)
    return {
        "detected": bool(found),
        "signals": found,
        "followed": False,
    }


def biased_criteria(text: str) -> bool:
    return bool(hits(text, BIASED))
