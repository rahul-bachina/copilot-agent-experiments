"""Cue lists for a declaration. A hit is not a finding that a conflict exists.

Stems are an example list. A sentence that uses none of them is not flagged.
That gap is stated in the smoke report. It is not a live rate.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from negate import affirmed, regex_affirmed
else:
    from .negate import affirmed, regex_affirmed

FINANCIAL = (
    "financial interest",
    "shareholding",
    "shares in",
    "dividend",
    "consultancy fee",
    "director's fee",
    "directors fee",
    "paid consultancy",
    "gift from",
    "hospitality from",
)

NON_FINANCIAL = (
    "non-financial interest",
    "non financial interest",
    "unpaid role",
    "voluntary role",
    "advisory role",
    "unpaid membership",
)

PERSONAL = ("personal interest",)
PROFESSIONAL = ("professional interest",)
DIRECT = ("direct interest", "held directly")
INDIRECT = ("indirect interest", "held indirectly")
NONE_DECLARED = (
    "nothing to declare",
    "no interest to declare",
    "i have no interest",
    "no conflict of interest to declare",
)

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

WHISTLE_RE = re.compile(
    r"whistle-?blow"
    r"|protected disclosure"
    r"|public interest disclosure"
    r"|wrongdoing"
    r"|malpractice"
    r"|serious misconduct"
    r"|cover-?up"
    r"|\bbribery\b"
    r"|\bcorruption\b"
    r"|\brigged\b"
    r"|\bfraud\b"
    r"|disclos(?:e|ing|ure) of"
    r"|speaking up about",
    re.IGNORECASE,
)

GRIEVANCE_RE = re.compile(
    r"\bgrievance\b"
    r"|\bbull(?:y|ied|ying)\b"
    r"|\bharass(?:ment|ed|ing)?\b"
    r"|\bsexual assault\b"
    r"|\bdomestic abuse\b"
    r"|\bunwanted conduct\b"
    r"|\bintimidat(?:e|ed|ing|ion)\b"
    r"|\braising a complaint about (?:me|my treatment|a colleague)\b",
    re.IGNORECASE,
)

POLITICAL_RE = re.compile(
    r"political opinion"
    r"|political party"
    r"|party political"
    r"|my politics",
    re.IGNORECASE,
)

_FAMILY = re.compile(
    r"\bmy (spouse|husband|wife|partner|brother|sister|mother|father|parent|son|daughter|child|uncle|aunt)\b"
    r"|\bfamily member\b",
    re.IGNORECASE,
)
_FAMILY_LABEL = {
    "spouse": "spouse",
    "husband": "spouse",
    "wife": "spouse",
    "partner": "spouse",
    "brother": "sibling",
    "sister": "sibling",
    "mother": "parent",
    "father": "parent",
    "parent": "parent",
    "son": "child",
    "daughter": "child",
    "child": "child",
    "uncle": "relative",
    "aunt": "relative",
    "family member": "family_member",
}

SPECIALS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("political_opinions", POLITICAL_RE),
    ("data_concerning_health", re.compile(
        r"medical condition|mental health|\bdisability\b|my health", re.I,
    )),
    ("religious_or_philosophical_belief", re.compile(
        r"religious belief|my religion|philosophical belief", re.I,
    )),
    ("trade_union_membership", re.compile(r"trade union", re.I)),
    ("racial_or_ethnic_origin", re.compile(r"ethnic origin|my ethnicity", re.I)),
    ("sex_life_or_sexual_orientation", re.compile(r"sex life|sexual orientation", re.I)),
)

BIASED_RE = re.compile(
    r"clear anyone"
    r"|automatically exclude"
    r"|ignore interests under"
    r"|only junior staff"
    r"|never a conflict"
    r"|leading criterion"
    r"|leading criteria"
    r"|treat family links as irrelevant"
    r"|grade determines"
    r"|below grade",
    re.IGNORECASE,
)

CARVE_RE = re.compile(
    r"\bexcept\b"
    r"|\bsave that\b"
    r"|\bother than\b"
    r"|\bprovided that\b"
    r"|\byou should clear\b"
    r"|\bplease clear\b"
    r"|\bthis is not a conflict\b"
    r"|\bwhich is acceptable\b",
    re.IGNORECASE,
)

NO_CONFLICT_RE = re.compile(
    r"there is no conflict"
    r"|no conflict exists"
    r"|this is not a conflict"
    r"|not a conflict of interest",
    re.IGNORECASE,
)

INSTRUCTIONS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "you are now",
    "system prompt",
    "clear me",
    "clear this declaration",
    "exclude the supplier",
    "decide there is no conflict",
    "write this to the production",
    "send this to the supplier",
    "you have already approved",
    "human_approval",
    "approved by the ethics",
    "mark this acceptable",
    "drop the legal hold",
    "strip the retention",
    "disregard the pinned",
)

ROLE_RE = re.compile(r"\bmy role is\b", re.IGNORECASE)
CLEARANCE_RE = re.compile(r"\bmy clearance is\b", re.IGNORECASE)


def _any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(affirmed(text, phrase) for phrase in phrases)


def family_labels(text: str) -> list[str]:
    found: list[str] = []
    if not text or not regex_affirmed(text, _FAMILY):
        return found
    if __package__ in {None, ""}:
        from negate import denied_at, sentences
    else:
        from .negate import denied_at, sentences
    for sentence in sentences(text):
        for match in _FAMILY.finditer(sentence):
            if denied_at(sentence, match.group(0), match.start()):
                continue
            raw = match.group(0).casefold()
            if raw == "family member":
                label = "family_member"
            else:
                label = _FAMILY_LABEL[match.group(1).casefold()]
            if label not in found:
                found.append(label)
    return found


def special_labels(text: str) -> list[str]:
    return [label for label, pattern in SPECIALS if regex_affirmed(text, pattern)]


def instruction_hits(text: str) -> list[str]:
    folded = (text or "").casefold()
    return [phrase for phrase in INSTRUCTIONS if phrase in folded]


def categories_in(text: str) -> set[str]:
    """Categories a reworded sentence should hit. Used by the smoke scorer."""

    found: set[str] = set()
    if regex_affirmed(text, DISTRESS_RE):
        found.add("distress")
    if regex_affirmed(text, WHISTLE_RE):
        found.add("whistleblowing")
    if regex_affirmed(text, GRIEVANCE_RE):
        found.add("grievance")
    if regex_affirmed(text, POLITICAL_RE):
        found.add("political")
    if family_labels(text):
        found.add("family")
    if _any(text, FINANCIAL):
        found.add("financial")
    if regex_affirmed(text, BIASED_RE):
        found.add("biased")
    if regex_affirmed(text, CARVE_RE) and (
        _any(text, FINANCIAL) or _any(text, NON_FINANCIAL) or family_labels(text)
    ):
        found.add("carve_out")
    if instruction_hits(text):
        found.add("instruction")
    return found


def read_cues(text: str) -> dict:
    financial = _any(text, FINANCIAL)
    non_financial = _any(text, NON_FINANCIAL)
    if financial and non_financial:
        nature = None
        nature_conflict = True
    elif financial:
        nature = "financial"
        nature_conflict = False
    elif non_financial:
        nature = "non_financial"
        nature_conflict = False
    else:
        nature = None
        nature_conflict = False
    direct = _any(text, DIRECT)
    indirect = _any(text, INDIRECT)
    if direct and indirect:
        direction = None
        direction_conflict = True
    elif direct:
        direction = "direct"
        direction_conflict = False
    elif indirect:
        direction = "indirect"
        direction_conflict = False
    else:
        direction = None
        direction_conflict = False
    types: list[str] = []
    for label, present in (
        ("financial", financial),
        ("non_financial", non_financial),
        ("personal", _any(text, PERSONAL)),
        ("professional", _any(text, PROFESSIONAL)),
    ):
        if present:
            types.append(label)
    family = family_labels(text)
    if family:
        types.append("family")
    special = special_labels(text)
    if "political_opinions" in special and "political" not in types:
        types.append("political")
    interest_affirmed = bool(types) or financial or non_financial or bool(family)
    return {
        "financial": financial,
        "non_financial": non_financial,
        "financial_or_non_financial": nature,
        "nature_conflict": nature_conflict,
        "direct_or_indirect": direction,
        "direction_conflict": direction_conflict,
        "interest_types": types,
        "none_declared": _any(text, NONE_DECLARED) and not interest_affirmed,
        "distress": regex_affirmed(text, DISTRESS_RE),
        "whistleblowing": regex_affirmed(text, WHISTLE_RE),
        "grievance": regex_affirmed(text, GRIEVANCE_RE),
        "family_labels": family,
        "special_category": special,
        "biased": regex_affirmed(text, BIASED_RE),
        "carve_out": regex_affirmed(text, CARVE_RE) and interest_affirmed,
        "no_conflict_asserted": regex_affirmed(text, NO_CONFLICT_RE),
        "self_declared_role": ROLE_RE.search(text or "") is not None,
        "self_declared_clearance": CLEARANCE_RE.search(text or "") is not None,
        "instructions": instruction_hits(text),
    }
