"""Closed keyword lists. A hit is not a classification decision.

A keyword inside a detected instruction is not counted. The instruction
scanner blanks that line first. A negation immediately before the keyword
is not counted either.
"""

from __future__ import annotations

import re

CATEGORIES = (
    {
        "id": "grievance",
        "label": "Grievance",
        "keywords": (
            "formal grievance",
            "raise a grievance",
            "raising a grievance",
            "my grievance",
            "grievance about",
            "grievance",
        ),
        "route": "hr_grievance_officer",
        "route_label": "HR grievance officer",
        "time_reference_ids": (
            "acas_para_1",
            "acas_para_4",
            "acas_para_32",
            "acas_para_33",
            "acas_para_40",
        ),
    },
    {
        "id": "absence",
        "label": "Absence",
        "keywords": (
            "sickness absence",
            "off sick",
            "fit note",
            "absent from work",
            "has not attended work",
        ),
        "route": "hr_absence_adviser",
        "route_label": "HR absence adviser",
        "time_reference_ids": ("absence_no_period",),
    },
    {
        "id": "flexible_working",
        "label": "Flexible working",
        "keywords": (
            "flexible working",
            "flexible-working",
            "request to work from home",
            "compressed hours",
        ),
        "route": "hr_flexible_working_adviser",
        "route_label": "HR flexible working adviser",
        "time_reference_ids": ("era_80g_1b",),
    },
    {
        "id": "protected_disclosure",
        "label": "Whistleblowing / protected disclosure",
        "keywords": (
            "protected disclosure",
            "whistleblowing",
            "whistle-blowing",
            "public interest disclosure",
            "making a disclosure",
        ),
        "route": "designated_whistleblowing_officer",
        "route_label": "Designated whistleblowing officer",
        "time_reference_ids": (
            "era_43a",
            "era_43b_1",
            "era_43c",
            "era_43j",
            "era_43l_sexual_harassment",
            "acas_foreword_separate",
        ),
        "confidentiality": True,
    },
    {
        "id": "harassment",
        "label": "Harassment",
        "keywords": (
            "sexual harassment",
            "unwanted conduct",
            "hostile environment",
            "harassment",
        ),
        "route": "hr_employee_relations_officer",
        "route_label": "HR employee-relations officer",
        "time_reference_ids": (
            "eqa_26_1",
            "eqa_26_2",
            "eqa_26_5",
            "acas_foreword_separate",
            "acas_para_33",
        ),
    },
)

CATEGORY_IDS = tuple(item["id"] for item in CATEGORIES)

ROUTES = {
    "hr_grievance_officer": "HR grievance officer",
    "hr_absence_adviser": "HR absence adviser",
    "hr_flexible_working_adviser": "HR flexible working adviser",
    "designated_whistleblowing_officer": "Designated whistleblowing officer",
    "hr_employee_relations_officer": "HR employee-relations officer",
    "hr_officer_to_classify": "HR officer, to classify",
}

UNRESOLVED_ROUTE = "hr_officer_to_classify"

# Longer keywords are tested first so "sexual harassment" is recorded
# before the shorter "harassment" inside it. Both still count as the
# same category. The shorter one is dropped when it sits inside the longer.
_SORTED = {
    item["id"]: tuple(sorted(item["keywords"], key=len, reverse=True))
    for item in CATEGORIES
}

_NEGATION = re.compile(
    r"(?:not a|not the|is not a|isn't a|isnt a)\s+$",
    re.IGNORECASE,
)

SPECIAL_CATEGORY_INDICATORS = (
    ("data_concerning_health", re.compile(
        r"\b(?:fit note|off sick|sickness absence|mental health|medical condition|disability)\b",
        re.IGNORECASE,
    )),
    ("data_concerning_sex_life_or_sexual_orientation", re.compile(
        r"\b(?:sex life|sexual orientation)\b",
        re.IGNORECASE,
    )),
    ("racial_or_ethnic_origin", re.compile(
        r"\b(?:racist|racial|ethnic origin)\b",
        re.IGNORECASE,
    )),
    ("religious_or_philosophical_belief", re.compile(
        r"\b(?:religious belief|religion or belief)\b",
        re.IGNORECASE,
    )),
    ("trade_union_membership", re.compile(
        r"\btrade union\b",
        re.IGNORECASE,
    )),
)


def _negated(text: str, start: int) -> bool:
    window = text[max(0, start - 16):start]
    return _NEGATION.search(window) is not None


def keyword_hits(text: str) -> dict[str, list[str]]:
    """Return closed keywords found outside a negation.

    ``text`` should already have instruction lines blanked. The returned
    phrases are the keyword list, not a copy of the narrative.
    """

    lower = text.lower()
    found: dict[str, list[str]] = {}
    for item in CATEGORIES:
        hits: list[str] = []
        spans: list[tuple[int, int]] = []
        for keyword in _SORTED[item["id"]]:
            start = 0
            while True:
                index = lower.find(keyword, start)
                if index < 0:
                    break
                end = index + len(keyword)
                start = end
                if _negated(lower, index):
                    continue
                if any(index >= left and end <= right for left, right in spans):
                    continue
                spans.append((index, end))
                if keyword not in hits:
                    hits.append(keyword)
        if hits:
            found[item["id"]] = hits
    return found


def special_category_indicators(text: str) -> list[str]:
    labels = []
    for label, pattern in SPECIAL_CATEGORY_INDICATORS:
        if pattern.search(text):
            labels.append(label)
    return labels
