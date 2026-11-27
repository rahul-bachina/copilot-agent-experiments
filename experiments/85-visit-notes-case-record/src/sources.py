"""Pages opened for this starter. The assistant does not download them again.

Opened on 27 November 2026. Quotes are the words copied below.
This is context for the practitioner. It is not legal advice. It is not a
needs assessment and it is not a decision to make a safeguarding enquiry.
"""

from __future__ import annotations

OPENED_ON = "2026-11-27"

CARE_ACT_9_1 = (
    "Where it appears to a local authority that an adult may have needs for "
    "care and support, the authority must assess—"
)
CARE_ACT_9_4_B = "the outcomes that the adult wishes to achieve in day-to-day life, and"
CARE_ACT_42_1_A = (
    "has needs for care and support (whether or not the authority is meeting "
    "any of those needs),"
)
CARE_ACT_42_1_B = "is experiencing, or is at risk of, abuse or neglect, and"
CARE_ACT_42_1_C = (
    "as a result of those needs is unable to protect himself or herself "
    "against the abuse or neglect or the risk of it."
)
CARE_ACT_42_2 = (
    "The local authority must make (or cause to be made) whatever enquiries "
    "it thinks necessary to enable it to decide whether any action should be "
    "taken in the adult's case (whether under this Part or otherwise) and, "
    "if so, what and by whom."
)
CARE_ACT_42_3_A = "having money or other property stolen,"
CARE_ACT_42_3_C = "being put under pressure in relation to money or other property, and"
UK_GDPR_9_1 = (
    "Processing of personal data revealing racial or ethnic origin, political "
    "opinions, religious or philosophical beliefs, or trade union membership, "
    "and the processing of genetic data, biometric data for the purpose of "
    "uniquely identifying a natural person, data concerning health or data "
    "concerning a natural person's sex life or sexual orientation shall be "
    "prohibited."
)
CALDICOTT_3 = (
    "Where use of confidential information is considered to be necessary, "
    "each item of information must be justified so that only the minimum "
    "amount of confidential information is included as necessary for a given "
    "function."
)
CALDICOTT_8 = (
    "A range of steps should be taken to ensure no surprises for patients "
    "and service users, so they can have clear expectations about how and why "
    "their confidential information is used, and what choices they have about "
    "this."
)
NHS_CHECK = (
    "People using ambient scribes must check the notes or letters that have "
    "been made by the ambient scribe to make sure they are accurate. They do "
    "this before adding any information to your record and are responsible "
    "for making sure the information in your record remains correct."
)
NHS_OBJECT = "You can ask for an ambient scribe not to be used during your appointment."


def pinned_sources() -> dict:
    return {
        "opened_on": OPENED_ON,
        "legal_advice": False,
        "assessment_made": False,
        "enquiry_decided": False,
        "quotes": [
            {
                "source": "Care Act 2014",
                "section": "section 9(1)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/9",
                "text": CARE_ACT_9_1,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Section 9(1)(a) and (b), and section 9(2) to (7), were on "
                    "the page. Section 1, section 2, section 4, and section 11 "
                    "were named and were not opened. This starter does not "
                    "carry out a needs assessment."
                ),
            },
            {
                "source": "Care Act 2014",
                "section": "section 9(4)(b)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/9",
                "text": CARE_ACT_9_4_B,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The person's wishes are copied from the transcript. They are not an assessment of need.",
            },
            {
                "source": "Care Act 2014",
                "section": "section 42(1)(a)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/42",
                "text": CARE_ACT_42_1_A,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "Section 42(1)(b) and (c) and section 42(2) and (3) were on the same page.",
            },
            {
                "source": "Care Act 2014",
                "section": "section 42(1)(b)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/42",
                "text": CARE_ACT_42_1_B,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "A flag is not a finding that abuse or neglect is happening.",
            },
            {
                "source": "Care Act 2014",
                "section": "section 42(1)(c)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/42",
                "text": CARE_ACT_42_1_C,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "This starter does not decide whether the adult is unable to protect themselves.",
            },
            {
                "source": "Care Act 2014",
                "section": "section 42(2)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/42",
                "text": CARE_ACT_42_2,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The enquiries are the local authority's. This starter does not make them.",
            },
            {
                "source": "Care Act 2014",
                "section": "section 42(3)(a)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/42",
                "text": CARE_ACT_42_3_A,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "Section 42(3)(b), (c), and (d) were on the page. (c) is also quoted.",
            },
            {
                "source": "Care Act 2014",
                "section": "section 42(3)(c)",
                "url": "https://www.legislation.gov.uk/ukpga/2014/23/section/42",
                "text": CARE_ACT_42_3_C,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "Financial-abuse wording in a transcript is flagged. It is not a finding of financial abuse.",
            },
            {
                "source": "UK GDPR",
                "section": "Article 9(1)",
                "url": "https://www.legislation.gov.uk/eur/2016/679/article/9",
                "text": UK_GDPR_9_1,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Article 9(2) to (5) were on the page. Article 6 was not "
                    "opened. Data Protection Act 2018 sections 10 and 11 were "
                    "named in Article 9(5) and were not opened. No lawful basis "
                    "is asserted. Article 9(2)(h) is not quoted in full because "
                    "the page shows editorial footnote markers inside the sentence."
                ),
            },
            {
                "source": "National Data Guardian",
                "section": "Caldicott principle 3",
                "url": "https://www.gov.uk/government/publications/the-caldicott-principles",
                "text": CALDICOTT_3,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "Principles 1, 2, 4, 5, 6, and 7 were on the HTML page. The PDF was not opened.",
            },
            {
                "source": "National Data Guardian",
                "section": "Caldicott principle 8",
                "url": "https://www.gov.uk/government/publications/the-caldicott-principles",
                "text": CALDICOTT_8,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The rest of principle 8 was on the page and is not quoted.",
            },
            {
                "source": "NHS England Digital",
                "section": "Making sure notes and summaries are accurate",
                "url": "https://digital.nhs.uk/data-and-information/information-governance/guidance/using-ai-enabled-ambient-scribing-products-in-health-and-care-settings",
                "text": NHS_CHECK,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The page says the person using the scribe checks the note before anything is added to the record. This starter does not add it.",
            },
            {
                "source": "NHS England Digital",
                "section": "Objecting to ambient scribes",
                "url": "https://digital.nhs.uk/data-and-information/information-governance/guidance/using-ai-enabled-ambient-scribing-products-in-health-and-care-settings",
                "text": NHS_OBJECT,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "A refusal to record is flagged. It is not overridden.",
            },
        ],
        "unverified": [
            {
                "item": "Published local-authority pilots of AI note-taking",
                "unverified": True,
                "note": (
                    "Those pages were not opened on 27 November 2026. A "
                    "supplier's reported result is not repeated and no figure "
                    "is stated."
                ),
            },
            {
                "item": "Article 9(2)(h) in full",
                "unverified": True,
                "note": "The sub-paragraph was on the page with editorial footnote markers. It is not quoted in full.",
            },
        ],
    }


def limitations() -> list[str]:
    return [
        "The draft copies lines. It does not invent a fact, a diagnosis, or a quote.",
        "A concern flag is not an assessment of eligibility, risk, or need.",
        "The paraphrase list is a fixture. Wording that uses none of the stems is not flagged.",
        "Masking is not anonymisation. described_as_anonymised stays false.",
        "Working days skip Saturday and Sunday. Bank holidays are not applied.",
        "The marking order is a starter rule. The Government Security Classifications Policy was not re-opened.",
        "The small-number threshold of 5 is a starter control. It is not anonymisation.",
        "Article 6 was not opened. No lawful basis is asserted.",
        "Care Act 2014 sections 1, 2, 4, and 11 were not opened. This starter does not carry out a section 9 assessment or a section 42 enquiry.",
        "Published local-authority pilot pages were not opened. No supplier result is stated.",
        "Northmarsh Council is invented. The people in the directory are not real.",
    ]
