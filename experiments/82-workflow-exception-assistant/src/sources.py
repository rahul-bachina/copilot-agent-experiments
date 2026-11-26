"""Pages opened for this starter. The assistant does not download them again.

Opened on 26 November 2026. Quotes are the words copied below.
Article 22B, Article 22C, and Article 22D were not opened. S.I. 2026/82 was
not opened. The FCA Handbook section that sets operational-resilience rules
was not opened. This is context. It is not legal advice, and it is not a
finding that a duty was met or that a firm stayed inside an impact tolerance.
"""

from __future__ import annotations

OPENED_ON = "2026-11-26"

ARTICLE_5_1_C = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed (‘data minimisation’);"
)
ARTICLE_22A_1_A = (
    "a decision is based solely on automated processing if there is no "
    "meaningful human involvement in the taking of the decision, and"
)
ARTICLE_22A_1_B = (
    "a decision is a significant decision, in relation to a data subject, if—"
)
FCA_RESILIENCE = (
    "Operational resilience is the ability of firms, financial market "
    "infrastructures and the financial sector to prevent, adapt and respond to, "
    "and recover and learn from operational disruption."
)
FCA_TOLERANCE_DEADLINE = (
    "Firms in scope of our operational resilience rules had until 31 March 2025 "
    "to ensure they could operate their important business services within their "
    "impact tolerances."
)


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "legal_advice": False,
        "decides_impact_tolerance": False,
        "quotes": [
            {
                "source": "UK GDPR",
                "section": "Article 5(1)(c)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
                "text": ARTICLE_5_1_C,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Article 5(1)(a), (b), (d), (e), and (f), Article 5(2), and "
                    "Article 5(3) were on the same page and are not quoted. "
                    "Article 84B, named inside Article 5(1)(e), was not opened."
                ),
            },
            {
                "source": "UK GDPR",
                "section": "Article 22A(1)(a)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
                "text": ARTICLE_22A_1_A,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Article 22B and Article 22C are named in the opening words "
                    "of Article 22A and were not opened. Article 22D was not opened. "
                    "S.I. 2026/82 was not opened. This starter does not decide "
                    "whether a workflow action is a significant decision."
                ),
            },
            {
                "source": "UK GDPR",
                "section": "Article 22A(1)(b)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
                "text": ARTICLE_22A_1_B,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The two sub-paragraphs under Article 22A(1)(b) were on the page. They are not applied here.",
            },
            {
                "source": "FCA",
                "section": "Operational resilience overview, not a Handbook section",
                "url": "https://www.fca.org.uk/firms/operational-resilience",
                "text": FCA_RESILIENCE,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "The same page states the 31 March 2025 sentence quoted below. "
                    "It does not state a retry interval for a flow. This starter "
                    "does not decide that a firm remained within an impact tolerance."
                ),
            },
            {
                "source": "FCA",
                "section": "Operational resilience overview, deadline sentence",
                "url": "https://www.fca.org.uk/firms/operational-resilience",
                "text": FCA_TOLERANCE_DEADLINE,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "SYSC 15A was not opened on 26 November 2026. No Handbook section number is cited.",
            },
        ],
        "not_opened": [
            {
                "source": "FCA Handbook",
                "section": "SYSC 15A",
                "unverified": True,
                "note": "The Handbook page was not opened. No section text is quoted.",
            }
        ],
    }
