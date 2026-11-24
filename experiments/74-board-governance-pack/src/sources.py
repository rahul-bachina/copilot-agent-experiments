"""UK context for the company secretary. Not a finding that a duty was met.

Companies Act 2006 sections 171, 172, 173, 174, 175, 176, 177, and 248 were
opened on legislation.gov.uk on 24 November 2026. Each page said the section
was up to date with all changes known to be in force on or before 23 November
2026. The quotes are the operative text. Modification notes were not copied.

UK Corporate Governance Code 2024 Principles F and I, and Provisions 7 and 16,
were read from a company-hosted PDF of the January 2024 Code. The FRC media
file was not opened. A byte-for-byte match to that file is unverified. The
Code was not opened on legislation.gov.uk.

The FRC guidance page was opened on 24 November 2026. That page says the
guidance is not mandatory and not part of the Code. Those paragraphs are
labelled as guidance.
"""

from __future__ import annotations

OPENED_ON = "2026-11-24"

CODE_PDF = (
    "https://corporate.unitedutilities.com/globalassets/documents/corporate-documents/"
    "uk_corporate_governance_code_2024_.pdf"
)
GUIDANCE_PAGE = (
    "https://www.frc.org.uk/library/standards-codes-policy/corporate-governance/"
    "corporate-governance-code-guidance/"
)

PRINCIPLE_F = (
    "The chair leads the board and is responsible for its overall effectiveness in directing the "
    "company. They should demonstrate objective judgement throughout their tenure and "
    "promote a culture of openness and debate. In addition, the chair facilitates constructive board "
    "relations and the effective contribution of all non-executive directors, and ensures that "
    "directors receive accurate, timely and clear information."
)

PRINCIPLE_I = (
    "The board, supported by the company secretary, should ensure that it has the policies, "
    "processes, information, time and resources it needs in order to function effectively and "
    "efficiently."
)

PROVISION_16 = (
    "All directors should have access to the advice of the company secretary, who is responsible for "
    "advising the board on all governance matters. Both the appointment and removal of the "
    "company secretary should be a matter for the whole board."
)

PROVISION_7 = (
    "The board should take action to identify and manage conflicts of interest, including those "
    "resulting from significant shareholdings, and ensure that the influence of third parties does "
    "not compromise or override independent judgement."
)

GUIDANCE_NOT_THE_CODE = (
    "The guidance is not mandatory, and not part of the Code itself, and is not prescriptive."
)

GUIDANCE_80 = (
    "The company secretary is responsible for ensuring that board procedures are complied with, "
    "advising the board on all governance matters, supporting the chair and helping the board and "
    "its committees to function efficiently."
)

GUIDANCE_82 = (
    "Under the direction of the chair, the company secretary\u2019s responsibilities include ensuring "
    "good information flows within the board and its committees and between senior management "
    "and non-executive directors, as well as facilitating induction, arranging board training and "
    "assisting with professional development as required."
)

GUIDANCE_BOARD_PAPERS = (
    "Be accurate, clear, comprehensive and up\u2011to\u2011date. "
    "Contain a summary of the contents of any paper. "
    "Inform the director what is expected of them on that issue. "
    "Be delivered sufficiently in advance of the meeting."
)

SECTION_171 = (
    "A director of a company must— "
    "(a) act in accordance with the company's constitution, and "
    "(b) only exercise powers for the purposes for which they are conferred."
)

SECTION_172_1 = (
    "A director of a company must act in the way he considers, in good faith, would be most likely "
    "to promote the success of the company for the benefit of its members as a whole, and in doing "
    "so have regard (amongst other matters) to— "
    "(a) the likely consequences of any decision in the long term, "
    "(b) the interests of the company's employees, "
    "(c) the need to foster the company's business relationships with suppliers, customers and others, "
    "(d) the impact of the company's operations on the community and the environment, "
    "(e) the desirability of the company maintaining a reputation for high standards of business conduct, and "
    "(f) the need to act fairly as between members of the company."
)

SECTION_173_1 = "A director of a company must exercise independent judgment."

SECTION_174_1 = "A director of a company must exercise reasonable care, skill and diligence."

SECTION_175_1 = (
    "A director of a company must avoid a situation in which he has, or can have, a direct or "
    "indirect interest that conflicts, or possibly may conflict, with the interests of the company."
)

SECTION_176_1 = (
    "A director of a company must not accept a benefit from a third party conferred by reason of— "
    "(a) his being a director, or "
    "(b) his doing (or not doing) anything as director."
)

SECTION_177_1 = (
    "If a director of a company is in any way, directly or indirectly, interested in a proposed "
    "transaction or arrangement with the company, he must declare the nature and extent of that "
    "interest to the other directors."
)

SECTION_248 = (
    "(1) Every company must cause minutes of all proceedings at meetings of its directors to be recorded. "
    "(2) The records must be kept for at least ten years from the date of the meeting."
)


def _act(section: str, quote: str) -> dict:
    return {
        "instrument": "Companies Act 2006",
        "section": section,
        "quote": quote,
        "source_opened": f"https://www.legislation.gov.uk/ukpga/2006/46/section/{section}",
        "opened_on": OPENED_ON,
        "page_currency_note": (
            "The page said the section is up to date with all changes known to be in force "
            "on or before 23 November 2026."
        ),
        "unverified": False,
    }


def uk_context() -> dict:
    return {
        "context_only": True,
        "decides_a_duty": False,
        "minutes_approved_by_this_quote": False,
        "opened_on": OPENED_ON,
        "companies_act": [
            _act("171", SECTION_171),
            _act("172", SECTION_172_1),
            _act("173", SECTION_173_1),
            _act("174", SECTION_174_1),
            _act("175", SECTION_175_1),
            _act("176", SECTION_176_1),
            _act("177", SECTION_177_1),
            _act("248", SECTION_248),
        ],
        "corporate_governance_code": {
            "instrument": "UK Corporate Governance Code 2024",
            "source_opened": CODE_PDF,
            "source_note": (
                "The PDF is titled UK Corporate Governance Code, January 2024, and is marked "
                "as copyright The Financial Reporting Council Limited 2024. It is hosted by "
                "United Utilities. The FRC media PDF was not opened. A byte-for-byte match "
                "to the FRC file is unverified."
            ),
            "opened_on": OPENED_ON,
            "unverified_against_legislation_gov_uk": True,
            "principles": {
                "F": {"quote": PRINCIPLE_F, "about": "board information"},
                "I": {"quote": PRINCIPLE_I, "about": "company secretary supporting the board"},
            },
            "provisions": {
                "7": {"quote": PROVISION_7, "about": "conflicts of interest"},
                "16": {"quote": PROVISION_16, "about": "company secretary"},
            },
        },
        "frc_guidance": {
            "part_of_the_code": False,
            "source_opened": GUIDANCE_PAGE,
            "opened_on": OPENED_ON,
            "page_says_not_the_code": GUIDANCE_NOT_THE_CODE,
            "paragraph_80": GUIDANCE_80,
            "paragraph_82": GUIDANCE_82,
            "board_papers_bullets_between_78_and_79": GUIDANCE_BOARD_PAPERS,
            "unverified_against_legislation_gov_uk": True,
            "note": (
                "The board-paper bullets sit on the guidance page between paragraphs 78 and 79 "
                "and have no paragraph number on that page. They are guidance, not a Code principle."
            ),
        },
    }
