"""Quotes opened on 23 November 2026. The core does not download them again.

Article 84B was not opened. The section 46 code document was not opened.
Orders under section 45(2) of the Constitutional Reform and Governance Act
2010 were not opened. None of these quotes is a finding that a duty was met
or that an offence was committed.
"""

from __future__ import annotations

OPENED_ON = "2026-11-23"

ARTICLE_5_1_E = (
    "kept in a form which permits identification of data subjects for no longer "
    "than is necessary for the purposes for which the personal data are processed; "
    "personal data may be stored for longer periods insofar as the personal data "
    "will be processed solely for archiving purposes in the public interest, "
    "scientific or historical research purposes or statistical purposes in "
    "accordance with Article 84B (‘storage limitation’)"
)

SECTION_46_1 = (
    "The Secretary of State shall issue, and may from time to time revise, a code "
    "of practice providing guidance to relevant authorities as to the practice "
    "which it would, in his opinion, be desirable for them to follow in connection "
    "with the keeping, management and destruction of their records."
)

SECTION_77_1 = (
    "Where (a) a request for information has been made to a public authority, and "
    "(b) under section 1 of this Act the applicant would have been entitled "
    "(subject to payment of any fee) to communication of any information in "
    "accordance with that section, any person to whom this subsection applies is "
    "guilty of an offence if he alters, defaces, blocks, erases, destroys or "
    "conceals any record held by the public authority, with the intention of "
    "preventing the disclosure by that authority of all, or any part, of the "
    "information to the communication of which the applicant would have been entitled."
)

PRA_3_1 = (
    "It shall be the duty of every person responsible for public records of any "
    "description which are not in the Public Record Office or a place of deposit "
    "appointed by the Secretary of State under this Act to make arrangements for "
    "the selection of those records which ought to be permanently preserved and "
    "for their safe-keeping."
)

PRA_3_4 = (
    "Public records selected for permanent preservation under this section shall "
    "be transferred not later than 20 years after their creation either to the "
    "Public Record Office or to such other place of deposit appointed by the "
    "Secretary of State under this Act as the Secretary of State may direct"
)

PRA_3_4_PROVISO = (
    "Provided that any records may be retained after the said period if, in the "
    "opinion of the person who is responsible for them, they are required for "
    "administrative purposes or ought to be retained for any other special reason "
    "and, where that person is not the Secretary of State, the Secretary of State "
    "has been informed of the facts and given his approval."
)

TNA_PAGE_SENTENCE = (
    "Section 46 of the Freedom of Information Act 2000 required the Lord Chancellor "
    "to issue a Code of Practice on the management of records."
)


def citations() -> list[dict]:
    return [
        {
            "id": "uk_gdpr_article_5_1_e",
            "instrument": "UK GDPR Article 5(1)(e)",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
            "opened_on": OPENED_ON,
            "quote": ARTICLE_5_1_E,
            "for": "records_owner",
            "applied_as_a_finding": False,
            "unverified": [
                "Article 84B was not opened.",
                "The extract did not show an up-to-date-on-or-before date.",
                "The editorial marker F4 on the page is not part of the quote.",
            ],
        },
        {
            "id": "foia_section_46",
            "instrument": "Freedom of Information Act 2000, section 46(1)",
            "url": "https://www.legislation.gov.uk/ukpga/2000/36/section/46",
            "opened_on": OPENED_ON,
            "quote": SECTION_46_1,
            "for": "records_owner",
            "applied_as_a_finding": False,
            "unverified": [
                "The page said there are currently no known outstanding effects, and also that revised legislation on the site may not be fully up to date.",
                "The code of practice issued under this section was not opened. Its paragraphs are unverified.",
                "The National Archives page was opened. It is not the code.",
            ],
            "tna_page_sentence": TNA_PAGE_SENTENCE,
            "tna_page_url": "https://www.nationalarchives.gov.uk/information-management/manage-information/planning/records-management-code/",
            "note": (
                "The revised section 46(1) names the Secretary of State. "
                "The National Archives page still says the Lord Chancellor was required to issue the code. "
                "Both sentences are from the pages opened on this date. The code itself is not quoted."
            ),
        },
        {
            "id": "foia_section_77",
            "instrument": "Freedom of Information Act 2000, section 77(1)",
            "url": "https://www.legislation.gov.uk/ukpga/2000/36/section/77",
            "opened_on": OPENED_ON,
            "quote": SECTION_77_1,
            "for": "records_owner",
            "applied_as_a_finding": False,
            "unverified": [
                "The page said there are currently no known outstanding effects, and also that revised legislation on the site may not be fully up to date.",
                "Words omitted from section 77(1)(b) by the Data Protection Act 2018 were not reconstructed.",
            ],
            "note": "This starter does not decide that an offence was committed.",
        },
        {
            "id": "public_records_act_section_3",
            "instrument": "Public Records Act 1958, section 3(1) and section 3(4)",
            "url": "https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/3",
            "opened_on": OPENED_ON,
            "quote": PRA_3_4,
            "quote_section_3_1": PRA_3_1,
            "quote_proviso": PRA_3_4_PROVISO,
            "for": "records_owner",
            "applied_as_a_finding": False,
            "applies_only_when_pinned_inventory_says_public_record": True,
            "unverified": [
                "The page said there are currently no known outstanding effects, and also that revised legislation on the site may not be fully up to date.",
                "Section 3(4A) was on the page. Orders under Constitutional Reform and Governance Act 2010 section 45(2) were not opened.",
                "The 20 years in section 3(4) is the latest transfer point for records selected for permanent preservation. It is not a minimum retention period for every record.",
            ],
        },
    ]
