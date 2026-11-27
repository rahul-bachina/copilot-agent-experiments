"""Quotes opened on 27 November 2026. The core does not download these pages.

Footnote markers on legislation.gov.uk are not part of the operative words.
The strings below are those words. They are not a finding that a duty was met.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 27)
REVIEW_DUE = date(2027, 5, 27)

ARTICLE_12_3 = (
    "The controller shall provide information on action taken on a request made under or by virtue "
    "of Articles 15 to 22D to the data subject without undue delay and in any event before the end "
    "of the applicable time period (see Article 12A)."
)
ARTICLE_12A_1 = (
    "In Article 12, “ the applicable time period” means the period of one month beginning with "
    "the relevant time, subject to paragraph 3."
)
ARTICLE_12A_2 = (
    "“ The relevant time” means the latest of the following— (a) when the controller receives the "
    "request in question; (b) when the controller receives the information (if any) requested in "
    "connection with a request under Article 12(6); (c) when the fee (if any) charged in connection "
    "with the request under Article 12(5) is paid."
)
ARTICLE_12A_3 = (
    "The controller may, by giving notice to the data subject, extend the applicable time period "
    "by two further months where that is necessary by reason of— (a) the complexity of requests "
    "made by the data subject, or (b) the number of such requests."
)
ARTICLE_12A_4 = (
    "A notice under paragraph 3 must— (a) be given before the end of the period of one month "
    "beginning with the relevant time, and (b) state the reasons for the delay."
)
ARTICLE_12A_5 = (
    "Where the controller reasonably requires further information in order to identify the "
    "information or processing activities to which a request under Article 15 relates— (a) the "
    "controller may ask the data subject to provide the further information, and (b) the period "
    "beginning with the day on which the controller makes the request and ending with the day on "
    "which the controller receives the information does not count towards— (i) the applicable time "
    "period, or (ii) the period described in paragraph 4(a)."
)
ARTICLE_12A_6 = (
    "An example of a case in which a controller may reasonably require further information is "
    "where the controller processes a large amount of information concerning the data subject."
)
ARTICLE_12_6 = (
    "where the controller has reasonable doubts concerning the identity of the natural person "
    "making the request made under or by virtue of Articles 15 to 22D, the controller may request "
    "the provision of additional information necessary to confirm the identity of the data subject, "
    "and delay dealing with the request until the identity is confirmed."
)
ARTICLE_15_1 = (
    "The data subject shall have the right to obtain from the controller confirmation as to whether "
    "or not personal data concerning him or her are being processed, and, where that is the case, "
    "access to the personal data and the following information:"
)
ARTICLE_15_1A = (
    "Under paragraph 1, the data subject is only entitled to such confirmation, personal data and "
    "other information as the controller is able to provide based on a reasonable and proportionate "
    "search for the personal data and other information described in that paragraph."
)
ARTICLE_15_4 = (
    "The right to obtain a copy referred to in paragraph 3 shall not adversely affect the rights "
    "and freedoms of others."
)
SECTION_45_1 = (
    "A data subject is entitled to obtain from the controller— (a) confirmation as to whether or "
    "not personal data concerning him or her is being processed, and (b) where that is the case, "
    "access to the personal data and the information set out in subsection (2)."
)
SECTION_45_2A = (
    "Under subsection (1), the data subject is only entitled to such confirmation, personal data "
    "and other information as the controller is able to provide based on a reasonable and "
    "proportionate search for the personal data and other information described in that subsection."
)
SECTION_45_3 = (
    "Where a data subject makes a request under subsection (1), the information to which the data "
    "subject is entitled must be provided in writing — (a) without undue delay, and (b) in any "
    "event, before the end of the applicable time period (as to which see section 54)."
)
SECTION_54_2 = (
    "“ The applicable time period” means the period of one month beginning with the relevant time, "
    "subject to subsection (3A)."
)
SECTION_54_3C = (
    "Where the controller reasonably requires further information in order to identify the "
    "information or processing activities to which a request under section 45(1) relates— (a) the "
    "controller may ask the data subject to provide the further information, and (b) the period "
    "beginning with the day on which the controller makes the request and ending with the day on "
    "which the controller receives the information does not count towards— (i) the applicable time "
    "period, or (ii) the period described in subsection (3B)(a)."
)
FOI_S40_1 = (
    "Any information to which a request for information relates is exempt information if it "
    "constitutes personal data of which the applicant is the data subject."
)
PARA_16_1 = (
    "Article 15(1) to (3) of the UK GDPR (confirmation of processing, access to data and safeguards "
    "for third country transfers), and Article 5 of the UK GDPR so far as its provisions correspond "
    "to the rights and obligations provided for in Article 15(1) to (3), do not oblige a controller "
    "to disclose information to the data subject to the extent that doing so would involve disclosing "
    "information relating to another individual who can be identified from the information."
)
PARA_19 = (
    "The listed GDPR provisions do not apply to personal data that consists of— (a) information in "
    "respect of which a claim to legal professional privilege or, in Scotland, confidentiality of "
    "communications, could be maintained in legal proceedings, or (b) information in respect of "
    "which a duty of confidentiality is owed by a professional legal adviser to a client of the adviser."
)
PARA_22 = (
    "The listed GDPR provisions do not apply to personal data processed for the purposes of "
    "management forecasting or management planning in relation to a business or other activity to "
    "the extent that the application of those provisions would be likely to prejudice the conduct "
    "of the business or activity concerned."
)
PARA_23 = (
    "The listed GDPR provisions do not apply to personal data that consists of records of the "
    "intentions of the controller in relation to any negotiations with the data subject to the "
    "extent that the application of those provisions would be likely to prejudice those negotiations."
)
PARA_24 = (
    "The listed GDPR provisions do not apply to personal data consisting of a reference given "
    "(or to be given) in confidence for the purposes of— (a) the education, training or employment "
    "(or prospective education, training or employment) of the data subject"
)
SCH3_PARA_2_2 = (
    "For the purposes of this Part of this Schedule, the “serious harm test” is met with respect "
    "to data concerning health if the application of Article 15 of the UK GDPR to the data would "
    "be likely to cause serious harm to the physical or mental health of the data subject or another individual."
)
SCH3_PARA_7_2 = (
    "For the purposes of this Part of this Schedule, the “serious harm test” is met with respect "
    "to social work data if the application of Article 15 of the UK GDPR to the data would be "
    "likely to prejudice carrying out social work, because it would be likely to cause serious harm "
    "to the physical or mental health of the data subject or another individual."
)
SCH3_PARA_21_2 = (
    "Article 15(1) to (3) of the UK GDPR (confirmation of processing, access to data and safeguards "
    "for third country transfers) do not apply to child abuse data to the extent that the application "
    "of that provision would not be in the best interests of the data subject."
)
ICO_MONTH = (
    "To calculate a month, you must start from the actual date you receive the request, fee or "
    "other requested information and count forward to the end of the same date in the following month."
)
ICO_SHORT_MONTH = (
    "If the same date doesn’t exist in the following month (because it’s shorter), use the last day of that month instead."
)
ICO_WEEKEND = (
    "If the date for responding falls on a weekend or is a public holiday, the deadline moves to the end of the next working day."
)
ICO_STOP = (
    "If you do ask for clarification, the time limit pauses on the day you request clarification "
    "and resumes on the day after you receive it. This is referred to as ‘stopping the clock’."
)
ICO_EXTEND = (
    "You must calculate the extension as three months from the original start date."
)


def uk_context() -> dict:
    return {
        "pinned_on": PINNED_ON.isoformat(),
        "review_due": REVIEW_DUE.isoformat(),
        "quotes_are_context": True,
        "not_a_finding_that_the_duty_was_met": True,
        "not_legal_advice": True,
        "opened_on": PINNED_ON.isoformat(),
        "article_12_url": "https://www.legislation.gov.uk/eur/2016/679/article/12",
        "article_12a_url": "https://www.legislation.gov.uk/eur/2016/679/article/12A.",
        "article_12a_url_without_the_trailing_dot_returned_404": True,
        "article_15_url": "https://www.legislation.gov.uk/eur/2016/679/article/15",
        "section_45_url": "https://www.legislation.gov.uk/ukpga/2018/12/section/45",
        "section_54_url": "https://www.legislation.gov.uk/ukpga/2018/12/section/54",
        "foi_section_40_url": "https://www.legislation.gov.uk/ukpga/2000/36/section/40",
        "schedule_2_paragraph_16_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/16",
        "schedule_2_paragraph_19_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/19",
        "schedule_2_paragraph_22_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/22",
        "schedule_2_paragraph_23_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/23",
        "schedule_2_paragraph_24_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/2/paragraph/24",
        "schedule_3_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/3",
        "schedule_4_url": "https://www.legislation.gov.uk/ukpga/2018/12/schedule/4",
        "ico_time_url": (
            "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
            "individual-rights/right-of-access/what-should-we-consider-when-responding-to-a-request"
        ),
        "ico_page_latest_update_line": "08 December 2025",
        "section_76_opened": False,
        "section_76_noted_from_the_article_12a_textual_amendment": True,
        "statutory_instrument_2026_82_opened": False,
        "section_52_opened": False,
        "section_53_opened": False,
        "interpretation_act_1978_opened": False,
        "banking_and_financial_dealings_act_1971_opened": False,
        "article_6_opened": False,
        "article_9_opened": False,
        "quotes": {
            "article_12_3": ARTICLE_12_3,
            "article_12_6": ARTICLE_12_6,
            "article_12a_1": ARTICLE_12A_1,
            "article_12a_5": ARTICLE_12A_5,
            "article_15_1a": ARTICLE_15_1A,
            "article_15_4": ARTICLE_15_4,
            "section_45_3": SECTION_45_3,
            "section_54_2": SECTION_54_2,
            "foi_section_40_1": FOI_S40_1,
            "schedule_2_paragraph_16_1": PARA_16_1,
            "ico_month": ICO_MONTH,
            "ico_stop_the_clock": ICO_STOP,
        },
    }
