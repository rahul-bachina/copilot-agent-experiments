"""Regulation extracts pinned on 27 October 2026.

The review does not download these pages. They were opened that day.
Update last_verified only after opening the page again.

JMLSG Guidance, Part I, is named and was not opened. No paragraph is applied.
The FATF call-for-action list was not opened. Regulation 35 was not opened.
"""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-10-27"
SOURCES_PINNED_ON = date(2026, 10, 27)
DEFAULT_STALE_AFTER_DAYS = 90

# Operative words from the pages that were opened. Not a full transcription.
QUOTES = {
    "reg28_2_a": (
        "identify the customer unless the identity of that customer is known to, "
        "and has been verified by, the relevant person"
    ),
    "reg28_2_b": (
        "verify the customer's identity unless the customer's identity has already "
        "been verified by the relevant person"
    ),
    "reg28_2_c": (
        "assess, and where appropriate obtain information on, the purpose and "
        "intended nature of the business relationship or occasional transaction"
    ),
    "reg28_9": (
        "Relevant persons do not satisfy their requirements under paragraph (4) "
        "by relying solely on information delivered to the registrar"
    ),
    "reg28_11": "The relevant person must conduct ongoing monitoring of a business relationship",
    "reg28_18_a": (
        "verify on the basis of documents or information in either case obtained "
        "from a reliable source which is independent of the person whose identity "
        "is being verified"
    ),
    "reg33_1_b_person": "with a person established in a FATF call for action country",
    "reg33_1_b_transaction": (
        "or in relation to any relevant transaction where either of the parties "
        "to the transaction is established in a FATF call for action country"
    ),
    "reg33_3_a": (
        'a "FATF call for action country" means a country named on the list of '
        "High-Risk Jurisdictions subject to a Call for Action published by the "
        "Financial Action Task Force as such list has effect from time to time"
    ),
    "reg33_1_d": (
        "if a relevant person has determined that a customer or potential customer "
        "is a PEP, or a family member or known close associate of a PEP "
        "(in accordance with regulation 35)"
    ),
    "reg33_1_f_i": (
        "a transaction is unusually complex or unusually large in each case given "
        "the nature of the transaction"
    ),
    "reg33_1_f_ii": "there is an unusual pattern of transactions",
    "reg33_1_f_iii": "the transaction or transactions have no apparent economic or legal purpose",
    "reg33_4_b": (
        "increasing the degree and nature of monitoring of the business relationship "
        "in which the transaction is made to determine whether that transaction or "
        "that relationship appear to be suspicious"
    ),
    "si_2026_621_reg19_b": (
        'for "high-risk third country", in both places it occurs, substitute '
        '"FATF call for action country"'
    ),
    "si_2026_621_reg19_f": (
        'for "complex or unusually large" substitute "unusually complex or unusually '
        'large in each case given the nature of the transaction"'
    ),
    "reg40_1": (
        "a relevant person must keep the records specified in paragraph (2) for "
        "at least the period specified in paragraph (3)"
    ),
    "reg40_3": (
        "the period is five years beginning on the date on which the relevant "
        "person knows, or has reasonable grounds to believe"
    ),
    "reg40_3_a": "that the transaction is complete, for records relating to an occasional transaction",
    "reg40_3_b": "that the business relationship has come to an end",
    "reg40_4": (
        "A relevant person is not required to keep the records referred to in "
        "paragraph (3)(b)(i) for more than 10 years."
    ),
    "poca_333a_1_b": (
        "the disclosure is likely to prejudice any investigation that might be "
        "conducted following the disclosure referred to in that subsection"
    ),
    "poca_333a_3_a": (
        "the person discloses that an investigation into allegations that an "
        "offence under this Part has been committed is being contemplated or "
        "is being carried out"
    ),
}

SOURCES = [
    {
        "id": "mlr-2017-reg-28",
        "title": "Money Laundering Regulations 2017, regulation 28 (customer due diligence measures)",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/regulation/28",
        "page_as_at": "2026-10-26",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "applied_as_a_decision": False,
        "notes": (
            "Opened 27 October 2026. The page says regulation 28 is up to date "
            "with all changes known to be in force on or before 26 October 2026. "
            "There are changes that may be brought into force at a future date. "
            "Paragraphs (9) and (9A) are shown as substituted on 18 November 2025."
        ),
    },
    {
        "id": "mlr-2017-reg-33",
        "title": "Money Laundering Regulations 2017, regulation 33 (enhanced customer due diligence)",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/regulation/33",
        "page_as_at": "2026-10-26",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "applied_as_a_decision": False,
        "notes": (
            "Opened 27 October 2026. The page says regulation 33 is up to date "
            "with all changes known to be in force on or before 26 October 2026. "
            "Paragraphs (1)(b), (1)(f)(i), and (3)(a) are annotated as substituted "
            "on 30 June 2026 by SI 2026/621. The current words are FATF call for "
            "action country, not high-risk third country."
        ),
    },
    {
        "id": "si-2026-621-reg-19",
        "title": "Money Laundering and Terrorist Financing (Amendment) Regulations 2026, regulation 19",
        "url": "https://www.legislation.gov.uk/uksi/2026/621/regulation/19",
        "page_as_at": "2026-06-09",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "applied_as_a_decision": False,
        "notes": (
            "Original version as made, opened 27 October 2026. Substitutes "
            "FATF call for action country for high-risk third country in "
            "regulation 33(1)(b), and replaces the complexity words in "
            "regulation 33(1)(f)(i). The footnote names a FATF web page. "
            "That page was not opened. Regulation 1 was opened: regulation 19 "
            "is not in the delayed-commencement list. The 30 June 2026 date "
            "is the annotation on the revised regulation 33, not a date this "
            "repository calculated."
        ),
    },
    {
        "id": "mlr-2017-reg-40",
        "title": "Money Laundering Regulations 2017, regulation 40 (record-keeping)",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/regulation/40",
        "page_as_at": "2023-09-01",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "applied_as_a_decision": False,
        "notes": (
            "Opened 27 October 2026. The changes banner did not include the "
            "up-to-date-on-or-before sentence that regulations 28 and 33 carried. "
            "Amendments listed on the page: 26 June 2017, 25 May 2018, "
            "6 October 2020, and 1 September 2023. Pending effects shown beside "
            "the provision insert Schedule 6 paragraph 7(ga) and regulation 34A. "
            "They do not amend regulation 40 in the text that was read."
        ),
    },
    {
        "id": "poca-2002-s-333a",
        "title": "Proceeds of Crime Act 2002, section 333A (tipping off: regulated sector)",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/333A",
        "page_as_at": "2026-10-26",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "applied_as_a_decision": False,
        "notes": (
            "Opened 27 October 2026. The page says section 333A is up to date "
            "with all changes known to be in force on or before 26 October 2026. "
            "Subsections (1) and (3) are the reason the customer note avoids "
            "any hint of a disclosure or an investigation. Sections 333B, 333C, "
            "and 333D were not opened. This agent does not send the note."
        ),
    },
    {
        "id": "fca-ai-live-testing-cohort-2",
        "title": "FCA announces second cohort for AI Live Testing",
        "url": "https://www.fca.org.uk/news/press-releases/fca-announces-second-cohort-ai-live-testing",
        "page_as_at": "2026-04-21",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "applied_as_a_decision": False,
        "notes": (
            "Opened 27 October 2026. First published 21 April 2026, last updated "
            "21 April 2026. The page names anti-money laundering detection and "
            "Know Your Customer among the use cases. Firms named include "
            "Barclays, Experian, Lloyds Banking Group (Scottish Widows), and UBS. "
            "An evaluation report is described as due in Q1 2027. Context only. "
            "Not a rule this checklist applies, and not an endorsement of this agent."
        ),
    },
    {
        "id": "jmlsg-part-i",
        "title": "JMLSG Guidance, Part I",
        "url": None,
        "page_as_at": None,
        "last_verified": LAST_VERIFIED,
        "body_opened": False,
        "applied_as_a_decision": False,
        "notes": (
            "Named only. Part I was not opened on 27 October 2026. "
            "No paragraph is quoted or applied."
        ),
    },
]

# Closed phrases. A hit is "these words are in the file". It is not a duty met.
PURPOSE_PHRASES = (
    "purpose and intended nature",
    "purpose of the relationship",
    "intended nature of the business",
    "nature of the business relationship",
)
BENEFICIAL_OWNER_PHRASES = ("beneficial owner",)
REGISTRAR_PHRASES = (
    "companies house",
    "psc register",
    "persons with significant control",
)
PEP_PHRASES = (
    "politically exposed person",
    "known close associate",
    "family member of a pep",
)
FATF_PHRASES = (
    "fatf call for action",
    "high-risk third country",
    "high risk third country",
)
UNUSUAL_PHRASES = (
    "unusually complex",
    "unusually large",
    "unusual pattern of transactions",
    "no apparent economic or legal purpose",
    "complex or unusual",
)

IDENTITY_CLASSES = ("identity_document",)
IDENTITY_PHRASES = ("passport", "driving licence", "driving license")
ADDRESS_CLASSES = ("proof_of_address",)
ADDRESS_PHRASES = ("proof of address", "council tax", "utility bill")
