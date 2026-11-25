"""Quotes opened on legislation.gov.uk on 25 November 2026.

The core does not download these pages when it runs. Article 12(3) on that
day does not itself say "one month". The one-month words are in Article 12A(1).
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 25)
REVIEW_DUE = date(2027, 11, 25)

QUOTE_FOI_S1 = (
    "Any person making a request for information to a public authority is entitled— "
    "(a) to be informed in writing by the public authority whether it holds information "
    "of the description specified in the request, and (b) if that is the case, to have "
    "that information communicated to him."
)
QUOTE_FOI_S10 = (
    "Subject to subsections (2) and (3), a public authority must comply with section 1(1) "
    "promptly and in any event not later than the twentieth working day following the date of receipt."
)
QUOTE_FOI_WORKING_DAY = (
    "“ working day” means any day other than a Saturday, a Sunday, Christmas Day, "
    "Good Friday or a day which is a bank holiday under the Banking and Financial Dealings Act 1971 "
    "in any part of the United Kingdom."
)
QUOTE_ARTICLE_15 = (
    "The data subject shall have the right to obtain from the controller confirmation as to whether "
    "or not personal data concerning him or her are being processed, and, where that is the case, "
    "access to the personal data and the following information:"
)
QUOTE_ARTICLE_12_3 = (
    "The controller shall provide information on action taken on a request made under or by virtue "
    "of Articles 15 to 22D to the data subject without undue delay and in any event before the end "
    "of the applicable time period (see Article 12A)."
)
QUOTE_ARTICLE_12A_1 = (
    "In Article 12, “ the applicable time period” means the period of one month beginning with "
    "the relevant time, subject to paragraph 3."
)


def uk_context() -> dict:
    return {
        "pinned_on": PINNED_ON.isoformat(),
        "review_due": REVIEW_DUE.isoformat(),
        "quotes_are_context": True,
        "not_a_finding_that_the_duty_was_met": True,
        "not_legal_advice": True,
        "foi": {
            "act": "Freedom of Information Act 2000",
            "section_1_url": "https://www.legislation.gov.uk/ukpga/2000/36/section/1",
            "section_10_url": "https://www.legislation.gov.uk/ukpga/2000/36/section/10",
            "section_1_1": QUOTE_FOI_S1,
            "section_10_1": QUOTE_FOI_S10,
            "section_10_6_working_day": QUOTE_FOI_WORKING_DAY,
            "opened_on": PINNED_ON.isoformat(),
            "outstanding_effects_recorded_on_the_page": "none known",
            "bank_holidays_act_opened": False,
            "time_for_compliance_regulations_opened": False,
        },
        "sar": {
            "instrument": "UK GDPR",
            "article_15_url": "https://www.legislation.gov.uk/eur/2016/679/article/15",
            "article_12_url": "https://www.legislation.gov.uk/eur/2016/679/article/12",
            "article_12a_url": "https://www.legislation.gov.uk/eur/2016/679/article/12A.",
            "article_15_1_opening": QUOTE_ARTICLE_15,
            "article_12_3": QUOTE_ARTICLE_12_3,
            "article_12a_1": QUOTE_ARTICLE_12A_1,
            "opened_on": PINNED_ON.isoformat(),
            "article_12_3_does_not_itself_say_one_month": True,
            "one_month_words_are_in_article_12a_1": True,
            "article_12a_url_without_the_trailing_dot_returned_404": True,
            "section_76_url": "https://www.legislation.gov.uk/ukpga/2025/18/section/76",
            "section_76_opened": True,
            "extension_of_two_further_months_not_applied": True,
        },
    }
