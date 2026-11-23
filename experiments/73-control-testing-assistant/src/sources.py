"""UK context quoted for the tester. Not a finding that either text was met.

Provision 29 was read from a company-hosted PDF of the January 2024 Code.
The FRC library page was opened and does not carry the full provision.
SYSC 4.1.1R was read from the FCA Handbook page that said it was showing
the chapter as of 23/11/2026. Neither text was opened on legislation.gov.uk.
"""

from __future__ import annotations

OPENED_ON = "2026-11-23"

PROVISION_29 = (
    "The board should monitor the company's risk management and internal control "
    "framework and, at least annually, carry out a review of its effectiveness. "
    "The monitoring and review should cover all material controls, including "
    "financial, operational, reporting and compliance controls. "
    "The board should provide in the annual report: "
    "A description of how the board has monitored and reviewed the effectiveness of the framework; "
    "a declaration of effectiveness of the material controls as at the balance sheet date; and "
    "a description of any material controls which have not operated effectively as at the balance "
    "sheet date, the action taken, or proposed, to improve them and any action taken to address "
    "previously reported issues."
)

PROVISION_29_FOOTNOTE = (
    "This Provision will apply for financial years beginning on or after 1 January 2026. "
    "Until then, Provision 29 of the 2018 UK Corporate Governance Code applies."
)

SYSC_4_1_1R = (
    "A firm must have robust governance arrangements, which include a clear organisational "
    "structure with well defined, transparent and consistent lines of responsibility, "
    "effective processes to identify, manage, monitor and report the risks it is or might "
    "be exposed to, and internal control mechanisms, including sound administrative and "
    "accounting procedures and effective control and safeguard arrangements for information "
    "processing systems."
)


def uk_context() -> dict:
    return {
        "context_only": True,
        "decides_effectiveness": False,
        "opened_on": OPENED_ON,
        "legislation_gov_uk": "not_opened",
        "currency_on_legislation_gov_uk": "unverified",
        "provision_29": {
            "instrument": "UK Corporate Governance Code 2024",
            "provision": "29",
            "quote": PROVISION_29,
            "footnote_from_the_same_pdf": PROVISION_29_FOOTNOTE,
            "source_opened": (
                "https://corporate.unitedutilities.com/globalassets/documents/corporate-documents/"
                "uk_corporate_governance_code_2024_.pdf"
            ),
            "source_note": (
                "The PDF is titled UK Corporate Governance Code, January 2024, and is marked "
                "as copyright The Financial Reporting Council Limited 2024. It is hosted by "
                "United Utilities. A footnote marker after the last word was not copied into the quote."
            ),
            "frc_library_page": (
                "https://www.frc.org.uk/library/standards-codes-policy/corporate-governance/"
                "uk-corporate-governance-code/"
            ),
            "frc_library_note": (
                "Opened on 23 November 2026. The page says the 2024 Code has applied since "
                "1 January 2025, with Provision 29 becoming applicable from 1 January 2026. "
                "The full provision text was not on that HTML page. The FRC media PDF was not opened. "
                "A byte-for-byte match to the FRC file is unverified."
            ),
            "unverified_against_legislation_gov_uk": True,
        },
        "sysc_4_1_1R": {
            "instrument": "FCA Handbook SYSC 4.1.1R",
            "quote": SYSC_4_1_1R,
            "source_opened": "https://handbook.fca.org.uk/handbook/sysc4",
            "source_note": (
                "The page said it was showing SYSC 4 General organisational requirements as of "
                "23/11/2026, last updated on 26/06/2026. The application table lists General "
                "requirements as SYSC 4.1.1R, SYSC 4.1.1-AR, and SYSC 4.1.2R. The sentence above "
                "is paragraph (1) under General requirements. The converted page did not print "
                "the characters SYSC 4.1.1R on the line immediately above that sentence."
            ),
            "unverified_against_legislation_gov_uk": True,
        },
    }
