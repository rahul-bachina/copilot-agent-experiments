"""Legal context opened on legislation.gov.uk on 24 November 2026.

Quotes are the words on those pages. This module does not decide that a
duty was met, and it does not decide that a benefits answer is a significant
decision.
"""

from __future__ import annotations

OPENED_ON = "2026-11-24"

ARTICLE_22A_1 = (
    "1. For the purposes of Articles 22B and 22C— "
    "(a) a decision is based solely on automated processing if there is no meaningful human involvement in the taking of the decision, and "
    "(b) a decision is a significant decision, in relation to a data subject, if— "
    "(i) it produces a legal effect for the data subject, or "
    "(ii) it has a similarly significant effect for the data subject."
)

ARTICLE_22C_2 = (
    "2. The safeguards must consist of or include measures which— "
    "(a) provide the data subject with information about decisions described in paragraph 1 taken in relation to the data subject; "
    "(b) enable the data subject to make representations about such decisions; "
    "(c) enable the data subject to obtain human intervention on the part of the controller in relation to such decisions; "
    "(d) enable the data subject to contest such decisions."
)

ARTICLE_22_FOOTNOTE = (
    "F1 Ch. 3 Section 4A substituted for Art. 22 "
    "(19.6.2025 for specified purposes, 5.2.2026 in so far as not already in force) "
    "by Data (Use and Access) Act 2025 (c. 18), ss. 80(1), 142(1)(2)(h); "
    "S.I. 2026/82, reg. 2(j) (with reg. 5)"
)

SECTION_80_COMMENCEMENT = (
    "I1 S. 80 in force at Royal Assent for specified purposes, see s. 142(1)(2)(h). "
    "I2 S. 80 in force at 5.2.2026 in so far as not already in force by S.I. 2026/82, reg. 2(j) (with reg. 5)."
)

SECTION_142_2_H = (
    "any other provision of this Act (including provision modifying other legislation) "
    "so far as it confers power to make regulations or is otherwise necessary for enabling "
    "the exercise of such a power on or after the day on which this Act is passed."
)

EQUALITY_S20_3 = (
    "The first requirement is a requirement, where a provision, criterion or practice of A's "
    "puts a disabled person at a substantial disadvantage in relation to a relevant matter in "
    "comparison with persons who are not disabled, to take such steps as it is reasonable to "
    "have to take to avoid the disadvantage."
)

EQUALITY_S149_1 = (
    "A public authority must, in the exercise of its functions, have due regard to the need to— "
    "(a) eliminate discrimination, harassment, victimisation and any other conduct that is "
    "prohibited by or under this Act; "
    "(b) advance equality of opportunity between persons who share a relevant protected "
    "characteristic and persons who do not share it; "
    "(c) foster good relations between persons who share a relevant protected characteristic "
    "and persons who do not share it."
)


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "not_a_legal_opinion": True,
        "duty_decided": False,
        "significant_decision_decided": False,
        "article_22": {
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22",
            "opened_on": OPENED_ON,
            "pre_substitution_text_shown": False,
            "footnote": ARTICLE_22_FOOTNOTE,
            "note": "The page did not show the pre-substitution Article 22 text. That wording is not quoted.",
        },
        "article_22a": {
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
            "opened_on": OPENED_ON,
            "quote": ARTICLE_22A_1,
            "paragraph": "22A(1)",
        },
        "article_22c": {
            "url": "https://www.legislation.gov.uk/ukpga/2025/18/section/80",
            "opened_on": OPENED_ON,
            "quote": ARTICLE_22C_2,
            "paragraph": "22C(2)",
            "source": "Data (Use and Access) Act 2025 s.80(1), the substituted Article 22C",
        },
        "commencement": {
            "section_80_note": SECTION_80_COMMENCEMENT,
            "section_142_2_h": SECTION_142_2_H,
            "section_142_url": "https://www.legislation.gov.uk/ukpga/2025/18/section/142",
            "si_2026_82_url": "https://www.legislation.gov.uk/uksi/2026/82/regulation/2",
            "si_2026_82_reg_2_j_opened": True,
            "reg_5_not_quoted": True,
            "note": (
                "Section 142(2)(h) commenced the regulation-making power at Royal Assent. "
                "S.I. 2026/82 regulation 2(j) brought section 80 into force on 5 February 2026 "
                "so far as not already in force. Regulation 5 was not quoted."
            ),
        },
        "equality_act_s20": {
            "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/20",
            "opened_on": OPENED_ON,
            "page_currency_line": "up to date with all changes known to be in force on or before 23 November 2026",
            "quote": EQUALITY_S20_3,
            "subsection": "20(3)",
            "duty_decided": False,
        },
        "equality_act_s149": {
            "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/149",
            "opened_on": OPENED_ON,
            "page_currency_line": "up to date with all changes known to be in force on or before 22 November 2026",
            "quote": EQUALITY_S149_1,
            "subsection": "149(1)",
            "duty_decided": False,
        },
        "govuk_benefit_pages_quoted": False,
        "benefit_rates_quoted_as_current": False,
    }
