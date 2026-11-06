"""Closed theme lists. A hit is a word in a cited line. It is not a finding.

Equality Act 2010 section 4 was read on 6 November 2026. Section 19(3) omits
pregnancy and maternity from indirect discrimination. Both facts are recorded.
Neither is applied.

Article 9(1) was read the same day. A phrase from that paragraph is a theme
for the data protection officer. No Article 9 condition is applied.

Financial-crime phrases are narrative for the MLRO. Suspicion is not decided.
"""

from __future__ import annotations

import re

# Section 4 characteristics. Short words use a boundary so "ageing" is not "age".
EQUALITY_THEMES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("age", re.compile(r"\bage\b", re.I)),
    ("disability", re.compile(r"\bdisability\b", re.I)),
    ("gender_reassignment", re.compile(r"\bgender reassignment\b", re.I)),
    ("marriage_and_civil_partnership", re.compile(r"\b(?:marriage and civil partnership|civil partnership)\b", re.I)),
    ("pregnancy_and_maternity", re.compile(r"\b(?:pregnancy|maternity)\b", re.I)),
    ("race", re.compile(r"\brace\b", re.I)),
    ("religion_or_belief", re.compile(r"\breligion(?: or belief)?\b", re.I)),
    ("sex", re.compile(r"\bsex\b", re.I)),
    ("sexual_orientation", re.compile(r"\bsexual orientation\b", re.I)),
)

# Section 19(3) does not list pregnancy and maternity. The flag records that.
NOT_IN_SECTION_19_3 = frozenset({"pregnancy_and_maternity"})

SPECIAL_CATEGORY_THEMES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("racial_or_ethnic_origin", re.compile(r"\b(?:racial|ethnic) origin\b", re.I)),
    ("political_opinions", re.compile(r"\bpolitical opinions?\b", re.I)),
    ("religious_or_philosophical_beliefs", re.compile(r"\b(?:religious|philosophical) beliefs?\b", re.I)),
    ("trade_union_membership", re.compile(r"\btrade union\b", re.I)),
    ("genetic_data", re.compile(r"\bgenetic data\b", re.I)),
    ("biometric_data", re.compile(r"\bbiometric\b", re.I)),
    ("health", re.compile(r"\bhealth\b", re.I)),
    ("sex_life", re.compile(r"\bsex life\b", re.I)),
    ("sexual_orientation", re.compile(r"\bsexual orientation\b", re.I)),
)

FINANCIAL_CRIME_PHRASES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("unusual", re.compile(r"\bunusual\b", re.I)),
    ("money_laundering", re.compile(r"\bmoney laundering\b", re.I)),
    ("terrorist_financing", re.compile(r"\bterrorist financing\b", re.I)),
)


def _hits(text: str, table: tuple[tuple[str, re.Pattern[str]], ...]) -> list[str]:
    found = []
    for code, pattern in table:
        if pattern.search(text) and code not in found:
            found.append(code)
    return found


def equality_themes(texts: list[str]) -> dict:
    themes = []
    for text in texts:
        for code in _hits(text, EQUALITY_THEMES):
            if code not in themes:
                themes.append(code)
    return {
        "themes": themes,
        "themes_not_in_section_19_3": [code for code in themes if code in NOT_IN_SECTION_19_3],
        "discrimination_found": False,
        "section_13_applied": False,
        "section_19_applied": False,
        "section_29_applied": False,
        "schedule_3_opened": False,
        "decides_less_favourable_treatment": False,
    }


def special_category_themes(texts: list[str]) -> dict:
    themes = []
    for text in texts:
        for code in _hits(text, SPECIAL_CATEGORY_THEMES):
            if code not in themes:
                themes.append(code)
    return {
        "themes": themes,
        "article_9_condition_applied": False,
        "used_as_a_credit_factor": False,
    }


def financial_crime_narrative(texts: list[str]) -> dict:
    phrases = []
    for text in texts:
        for code in _hits(text, FINANCIAL_CRIME_PHRASES):
            if code not in phrases:
                phrases.append(code)
    return {
        "phrases": phrases,
        "narrative_for_human_review": bool(phrases),
        "audience": "MLRO",
        "suspicion_decided": False,
        "sar_filed": False,
        "authorised_disclosure_made": False,
        "mlro_decides": True,
        "customer_text_produced": False,
        "section_333a_opened": False,
    }
