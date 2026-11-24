"""Pages opened for this starter. The assistant does not download them.

Opened on 24 November 2026. Quotes are the sentences copied below.
PB1, PB2, and PB3 were not opened. Charities Act 2011 section 14 was
not opened. The reference to section 14 inside section 17(1) is unverified
beyond the words of section 17.
"""

from __future__ import annotations

OPENED_ON = "2026-11-24"

CC3_PURPOSES = (
    "You and your co-trustees must make sure that the charity is carrying out "
    "the purposes for which it is set up, and no other purpose."
)
CC3_PUBLIC_BENEFIT = (
    "All charities must be for the public benefit."
)
CC3_REGARD = (
    "Trustees must have regard to the Commission’s public benefit guidance "
    "PB1, PB2 and PB3 when making decisions they are relevant to."
)
SECTION_17_1 = (
    "The Commission must issue guidance in pursuance of its public benefit "
    "objective (see paragraph 2 of section 14)."
)
SECTION_17_5 = (
    "The charity trustees of a charity must have regard to any such guidance "
    "when exercising any powers or duties to which the guidance is relevant."
)
ARTICLE_5_1_C = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed (‘data minimisation’);"
)


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "quotes": [
            {
                "source": "Charity Commission CC3, The essential trustee",
                "section": "Section 2.1 and section 4",
                "url": "https://www.gov.uk/government/publications/the-essential-trustee-what-you-need-to-know-what-you-need-to-do-cc3/the-essential-trustee-what-you-need-to-know-what-you-need-to-do",
                "text": CC3_PURPOSES,
                "verified_on": OPENED_ON,
                "unverified": False,
            },
            {
                "source": "Charity Commission CC3, The essential trustee",
                "section": "Section 4.2",
                "url": "https://www.gov.uk/government/publications/the-essential-trustee-what-you-need-to-know-what-you-need-to-do-cc3/the-essential-trustee-what-you-need-to-know-what-you-need-to-do",
                "text": CC3_PUBLIC_BENEFIT,
                "verified_on": OPENED_ON,
                "unverified": False,
            },
            {
                "source": "Charity Commission CC3, The essential trustee",
                "section": "Section 4.2",
                "url": "https://www.gov.uk/government/publications/the-essential-trustee-what-you-need-to-know-what-you-need-to-do-cc3/the-essential-trustee-what-you-need-to-know-what-you-need-to-do",
                "text": CC3_REGARD,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "PB1, PB2, and PB3 were not opened. The page was marked updated 16 September 2026.",
            },
            {
                "source": "Charities Act 2011",
                "section": "section 17(1)",
                "url": "https://www.legislation.gov.uk/ukpga/2011/25/section/17",
                "text": SECTION_17_1,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "Section 14 was not opened. The cross-reference is unverified. The page listed no known outstanding effects for section 17 and also said revised legislation on the site may not be fully up to date.",
            },
            {
                "source": "Charities Act 2011",
                "section": "section 17(5)",
                "url": "https://www.legislation.gov.uk/ukpga/2011/25/section/17",
                "text": SECTION_17_5,
                "verified_on": OPENED_ON,
                "unverified": False,
            },
            {
                "source": "UK GDPR",
                "section": "Article 5(1)(c)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
                "text": ARTICLE_5_1_C,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "Article 5 was opened. Article 6 and Article 9 were not opened. No lawful basis is asserted.",
            },
        ],
        "not_a_legal_opinion": True,
        "not_confirmation_that_the_charity_meets_the_duty": True,
    }
