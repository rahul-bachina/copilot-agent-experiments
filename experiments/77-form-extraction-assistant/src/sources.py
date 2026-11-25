"""Pages opened for this starter. The assistant does not download them.

Opened on 25 November 2026. Quotes are the words copied below.
Article 6 and Article 9 were not opened. No lawful basis is asserted.
"""

from __future__ import annotations

OPENED_ON = "2026-11-25"

ARTICLE_5_1_C = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed (‘data minimisation’);"
)
ARTICLE_5_1_D = (
    "accurate and, where necessary, kept up to date; every reasonable step must "
    "be taken to ensure that personal data that are inaccurate, having regard "
    "to the purposes for which they are processed, are erased or rectified "
    "without delay (‘accuracy’);"
)


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "quotes": [
            {
                "source": "UK GDPR",
                "section": "Article 5(1)(c)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
                "text": ARTICLE_5_1_C,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Article 5 was opened on 25 November 2026. Paragraph (c) showed "
                    "no footnote marker. Paragraphs (b) and (e), and paragraph 3, "
                    "did. Article 6 and Article 9 were not opened. No lawful basis "
                    "is asserted. The quote is not a finding that this starter meets the principle."
                ),
            },
            {
                "source": "UK GDPR",
                "section": "Article 5(1)(d)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
                "text": ARTICLE_5_1_D,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Article 5(1)(d) showed no footnote marker on the page opened "
                    "on 25 November 2026. The quote is not a finding that a field is accurate."
                ),
            },
        ],
        "not_a_legal_opinion": True,
        "not_confirmation_that_the_form_is_accurate": True,
    }
