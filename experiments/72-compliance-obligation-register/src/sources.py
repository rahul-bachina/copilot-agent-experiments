"""Pins opened for this starter. The core does not download them again.

The quotes are context. They are not a finding that a synthetic firm must
comply, and they are not the obligation text in the register.
"""

from __future__ import annotations

OPENED = "2026-11-23"

SYSC_6_1_1R = (
    "A firm must establish, implement and maintain adequate policies and "
    "procedures sufficient to ensure compliance of the firm including its "
    "managers, employees and appointed representatives (or where applicable, "
    "tied agents) with its obligations under the regulatory system and for "
    "countering the risk that the firm might be used to further financial crime."
)

FSMA_59_1 = (
    "An authorised person (“A”) must take reasonable care to ensure that no "
    "person performs a controlled function under an arrangement entered into "
    "by A in relation to the carrying on by A of a regulated activity, unless "
    "that person is acting in accordance with an approval given by the "
    "appropriate regulator under this section."
)

FSMA_59ZA_2 = (
    "A function is a “senior management function”, in relation to the carrying "
    "on of a regulated activity by an authorised person, if— (a) the function "
    "will require the person performing it to be responsible for managing one "
    "or more aspects of the authorised person's affairs, so far as relating to "
    "the activity, and (b) those aspects involve, or might involve, a risk of "
    "serious consequences— (i) for the authorised person, or (ii) for business "
    "or other interests in the United Kingdom."
)

FSMA_63E_1 = (
    "An authorised person (“A”) must take reasonable care to ensure that no "
    "employee of A performs a specified function under an arrangement entered "
    "into by A in relation to the carrying on by A of a regulated activity, "
    "unless the employee has a valid certificate issued by A under section 63F."
)


def context_pins() -> list[dict]:
    return [
        {
            "pin_id": "SYSC-6.1.1R",
            "source": "FCA Handbook SYSC 6.1",
            "url": "https://www.handbook.fca.org.uk/handbook/SYSC/6/1.html",
            "opened": OPENED,
            "quote": SYSC_6_1_1R,
            "where": (
                "The application table names SYSC 6.1.1R for adequate policy "
                "and procedures. The sentence above is the paragraph under that heading."
            ),
            "currency": (
                "The handbook page does not show an 'up to date on or before' line. "
                "Currency against legislation.gov.uk does not apply to the handbook. "
                "The handbook currency is unverified beyond the page opened on this date."
            ),
            "statutory_minimum_stated": False,
            "statutory_minimum": None,
            "applies": None,
            "final_advice": False,
            "pins_confirmed": False,
            "note": (
                "SYSC 1 Annex 1 was not applied. The sentence is context for a "
                "compliance-function example. It is not a decision that the synthetic firm is in scope."
            ),
        },
        {
            "pin_id": "FSMA-2000-s59-1",
            "source": "Financial Services and Markets Act 2000, section 59(1)",
            "url": "https://www.legislation.gov.uk/ukpga/2000/8/section/59",
            "opened": OPENED,
            "quote": FSMA_59_1,
            "where": "Section 59(1). The page showed footnote F1 around the words after 'unless'.",
            "currency": (
                "Up to date with all changes known to be in force on or before 21 November 2026. "
                "There are changes that may be brought into force at a future date. "
                "Revised legislation carried on the site may not be fully up to date."
            ),
            "statutory_minimum_stated": False,
            "statutory_minimum": None,
            "applies": None,
            "final_advice": False,
            "pins_confirmed": False,
            "note": "Section 59ZA defines a senior management function. It was opened separately.",
        },
        {
            "pin_id": "FSMA-2000-s59ZA-2",
            "source": "Financial Services and Markets Act 2000, section 59ZA(2)",
            "url": "https://www.legislation.gov.uk/ukpga/2000/8/section/59ZA",
            "opened": OPENED,
            "quote": FSMA_59ZA_2,
            "where": "Section 59ZA(2). Subsection (3) was read and is not copied here.",
            "currency": (
                "Up to date with all changes known to be in force on or before 19 November 2026. "
                "There are changes that may be brought into force at a future date. "
                "Revised legislation carried on the site may not be fully up to date."
            ),
            "statutory_minimum_stated": False,
            "statutory_minimum": None,
            "applies": None,
            "final_advice": False,
            "pins_confirmed": False,
            "note": "The quote has a space in the rendered page before 'senior management function'. It is kept.",
        },
        {
            "pin_id": "FSMA-2000-s63E-1",
            "source": "Financial Services and Markets Act 2000, section 63E(1)",
            "url": "https://www.legislation.gov.uk/ukpga/2000/8/section/63E",
            "opened": OPENED,
            "quote": FSMA_63E_1,
            "where": "Section 63E(1). The page showed footnote F3 on the opening word 'An'.",
            "currency": (
                "Up to date with all changes known to be in force on or before 21 November 2026. "
                "There are changes that may be brought into force at a future date. "
                "Revised legislation carried on the site may not be fully up to date."
            ),
            "statutory_minimum_stated": False,
            "statutory_minimum": None,
            "applies": None,
            "final_advice": False,
            "pins_confirmed": False,
            "note": "Section 63F was not opened. No certificate rule from the handbook was opened.",
        },
        {
            "pin_id": "FCA-SMCR-overview",
            "source": "FCA Senior Managers and Certification Regime",
            "url": "https://www.fca.org.uk/firms/senior-managers-and-certification-regime",
            "opened": OPENED,
            "quote": (
                "The Senior Managers and Certification Regime (SM&CR) aims to reduce harm to "
                "consumers and strengthen market integrity by making individuals more accountable "
                "for their conduct and competence."
            ),
            "where": "Opening paragraph. The page said last updated 24/04/2026.",
            "currency": "The page said last updated 24/04/2026. SUP 10C, COCON, and the statement of responsibilities were not opened.",
            "statutory_minimum_stated": False,
            "statutory_minimum": None,
            "applies": None,
            "final_advice": False,
            "pins_confirmed": False,
            "unverified": (
                "The page said the regime is undergoing reform. Which firms and which functions "
                "are in scope was not verified from the Handbook. That point is unverified."
            ),
            "note": "The page names three parts: the Senior Managers Regime, the Certification Regime, and the Conduct Rules.",
        },
    ]
