"""Pages opened for this starter. The assistant does not download them again.

Opened on 25 November 2026. Quotes are the words copied below.
Article 22B, Article 22C, Article 22D, and Article 84B were not opened.
S.I. 2026/82 was not opened. This is context. It is not legal advice, and
it is not a finding that a duty was met or that a decision is significant.
"""

from __future__ import annotations

OPENED_ON = "2026-11-25"

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


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "legal_advice": False,
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
                    "whether a comparison is a significant decision."
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
        ],
    }
