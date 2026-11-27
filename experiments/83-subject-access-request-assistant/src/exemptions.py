"""Candidate exemptions. A phrase match is not a decision that the exemption applies.

Negation in the same sentence is not a match. The officer accepts or rejects
each candidate. applied stays false.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from negate import affirmed
else:
    from .negate import affirmed

# Paragraph numbers were read on legislation.gov.uk on 27 November 2026.
CANDIDATES = (
    {
        "exemption_id_prefix": "sch2-p19",
        "schedule": "2",
        "paragraph": "19",
        "verified": True,
        "label": "Legal professional privilege",
        "phrases": (
            "legal professional privilege",
            "legally privileged",
            "counsel's opinion",
            "solicitor's advice",
            "solicitors' advice",
            "confidentiality of communications",
            "privileged legal advice",
            "advice from counsel",
            "without prejudice",
        ),
    },
    {
        "exemption_id_prefix": "sch2-p22",
        "schedule": "2",
        "paragraph": "22",
        "verified": True,
        "label": "Management forecasting or management planning",
        "phrases": (
            "management forecast",
            "management forecasting",
            "management planning",
            "management plan",
        ),
    },
    {
        "exemption_id_prefix": "sch2-p23",
        "schedule": "2",
        "paragraph": "23",
        "verified": True,
        "label": "Negotiations with the data subject",
        "phrases": (
            "negotiations with the data subject",
            "settlement negotiation",
            "in negotiation",
            "negotiating with",
            "settlement offer",
            "without prejudice",
        ),
    },
    {
        "exemption_id_prefix": "sch2-p24",
        "schedule": "2",
        "paragraph": "24",
        "verified": True,
        "label": "Confidential references",
        "phrases": (
            "confidential reference",
            "reference given in confidence",
            "employment reference",
            "reference in confidence",
        ),
    },
    {
        "exemption_id_prefix": "sch3-p2",
        "schedule": "3",
        "paragraph": "2",
        "verified": True,
        "label": "Health data and the serious harm test",
        "phrases": (
            "medical record",
            "health record",
            "clinical note",
            "data concerning health",
            "diagnosis",
        ),
    },
    {
        "exemption_id_prefix": "sch3-p7",
        "schedule": "3",
        "paragraph": "7",
        "verified": True,
        "label": "Social work data and the serious harm test",
        "phrases": ("social work", "social-work"),
    },
    {
        "exemption_id_prefix": "sch3-p21",
        "schedule": "3",
        "paragraph": "21",
        "verified": True,
        "label": "Child abuse data",
        "phrases": ("child abuse", "child abuse data"),
    },
    {
        "exemption_id_prefix": "sch4-p2",
        "schedule": "4",
        "paragraph": "2",
        "verified": True,
        "label": "Human fertilisation and embryology information",
        "phrases": ("human fertilisation", "human fertilization", "embryology information"),
    },
    {
        "exemption_id_prefix": "sch4-p3",
        "schedule": "4",
        "paragraph": "3",
        "verified": True,
        "label": "Adoption records and reports",
        "phrases": ("adoption record", "adoption records"),
    },
    {
        "exemption_id_prefix": "sch4-p4",
        "schedule": "4",
        "paragraph": "4",
        "verified": True,
        "label": "Statements of special educational needs",
        "phrases": (
            "statement of special educational needs",
            "special educational needs statement",
        ),
    },
    {
        "exemption_id_prefix": "sch4-p6",
        "schedule": "4",
        "paragraph": "6",
        "verified": True,
        "label": "Information provided by the Principal Reporter",
        "phrases": ("children's hearing", "principal reporter"),
    },
)


def phrase_hits(text: str) -> list[dict]:
    """Return candidate rows. The matched phrase is an id, not a quotation of the file."""

    found = []
    for spec in CANDIDATES:
        hits = [phrase for phrase in spec["phrases"] if affirmed(text or "", phrase)]
        if not hits:
            continue
        found.append({
            "schedule": spec["schedule"],
            "paragraph": spec["paragraph"],
            "verified": True,
            "label": spec["label"],
            "matched_phrases": hits,
            "applied": False,
            "human_decision": None,
            "decided_by_agent": False,
        })
    return found


def third_party_candidate() -> dict:
    return {
        "schedule": "2",
        "paragraph": "16",
        "verified": True,
        "label": "Information relating to another individual",
        "matched_phrases": ["third-party personal data proposed for redaction"],
        "applied": False,
        "human_decision": None,
        "decided_by_agent": False,
        "reason": (
            "A third-party identifier was proposed for redaction. Schedule 2 paragraph 16(1) "
            "does not oblige disclosure to the extent that would identify another individual. "
            "Paragraph 16(2), consent or reasonable disclosure without consent, is for the officer."
        ),
    }
