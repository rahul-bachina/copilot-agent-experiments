"""Quotations pinned on 11 November 2026.

A run does not fetch these pages again. Article 6, Article 9, Article 84B,
Freedom of Information Act 2000 section 48, the Public Records Act 1958
First Schedule, and any FCA Handbook provision were not opened. Where a
sentence is the section 46 code's paraphrase, the source is the code PDF.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 11)
STALE_AFTER_DAYS = 180

PRA_URL = "https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51"
PRA_SECTION_3_URL = "https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/3"
PRA_SECTION_10_URL = "https://www.legislation.gov.uk/ukpga/Eliz2/6-7/51/section/10"
FOIA_SECTION_46_URL = "https://www.legislation.gov.uk/ukpga/2000/36/section/46"
CODE_URL = (
    "https://www.gov.uk/government/publications/"
    "code-of-practice-on-the-management-of-records-issued-under-section-46-"
    "the-freedom-of-information-act-2000"
)
CODE_PDF_URL = (
    "https://assets.publishing.service.gov.uk/government/uploads/system/"
    "uploads/attachment_data/file/1010395/"
    "Freedom_Information_Code_Practice_Web_Accessible.pdf"
)
GSCP_URL = (
    "https://www.gov.uk/government/publications/government-security-classifications/"
    "government-security-classifications-policy-html"
)
GSCP_OFFICIAL_URL = (
    "https://www.gov.uk/government/publications/government-security-classifications/"
    "guidance-11-working-at-official-html"
)
UK_GDPR_ARTICLE_5_URL = "https://www.legislation.gov.uk/eur/2016/679/article/5"
HARNESS_URL = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview"
PURVIEW_RECORDS_URL = "https://learn.microsoft.com/en-us/purview/get-started-with-records-management"
PURVIEW_SENSITIVITY_URL = "https://learn.microsoft.com/en-us/purview/sensitivity-labels"

# Distinctive phrases withheld when the pin is stale. Do not put them in fixtures.
QUOTE_STORAGE = (
    "kept in a form which permits identification of data subjects for no longer "
    "than is necessary for the purposes for which the personal data are processed"
)
QUOTE_ARTICLE_84B = "in accordance with Article 84B"
QUOTE_TWENTY_YEARS = "not later than 20 years"
QUOTE_THREE_TIERS = "three classification tiers (OFFICIAL, SECRET and TOP SECRET)"


def source_rows(current: bool) -> list[dict]:
    """Return the pin. Quotes are omitted when the pin is stale."""

    rows = (
        {
            "id": "pra-s3",
            "name": "Public Records Act 1958, section 3",
            "url": PRA_SECTION_3_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "Section 3(1) places a duty on every person responsible for public "
                "records which are not in the Public Record Office or an appointed "
                "place of deposit to make arrangements for the selection of those "
                "records which ought to be permanently preserved and for their "
                "safe-keeping. Section 3(4) says records selected for permanent "
                "preservation shall be transferred not later than 20 years after "
                "their creation, subject to the retention proviso in that subsection. "
                "Section 3(6) says records rejected as not required for permanent "
                "preservation shall be destroyed or, with the approval required by "
                "that subsection, disposed of in any other way. This starter does "
                "not select, transfer, destroy, or dispose."
            ),
        },
        {
            "id": "pra-s10",
            "name": "Public Records Act 1958, section 10",
            "url": PRA_SECTION_10_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "Section 10(1) says public records has the meaning assigned by the "
                "First Schedule, and records includes records conveying information "
                "by any means. The First Schedule was not opened. This starter does "
                "not decide that a body, or a record, is a public record."
            ),
        },
        {
            "id": "foia-s46",
            "name": "Freedom of Information Act 2000, section 46",
            "url": FOIA_SECTION_46_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "Section 46(1) says the Secretary of State shall issue, and may "
                "revise, a code of practice providing guidance to relevant "
                "authorities on the practice which it would, in his opinion, be "
                "desirable for them to follow in connection with the keeping, "
                "management and destruction of their records. Section 46(7) defines "
                "a relevant authority as any public authority, and any office or "
                "body which is not a public authority but whose administrative and "
                "departmental records are public records. The page said there are "
                "currently no known outstanding effects. Section 48 was not opened."
            ),
        },
        {
            "id": "s46-code",
            "name": "Code of Practice on the management of records, section 46",
            "url": CODE_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "The GOV.UK page, published 15 July 2021 by The National Archives, "
                "links a 32-page PDF. The PDF says it was laid before Parliament on "
                "15 July 2021. Paragraph 2.3.1 says authorities must define how long "
                "to keep information and dispose of it when it is no longer needed, "
                "by destroying it, transferring it to another body, or transferring "
                "it to an archive. Paragraph 2.3.2 includes exceptional circumstances "
                "such as a moratorium on destruction, a police investigation, a "
                "public inquiry, or legal action. Paragraph 2.5 cites UK GDPR "
                "Article 5(1)(e) in the code's own words. Paragraph 2.6.2 says "
                "disposition decisions must be recorded and taken by people "
                "authorised to do so. Annex B says the code fulfils the section "
                "46(1) duty to provide guidance, and that the Commissioner may "
                "issue a practice recommendation under section 48. The section 48 "
                "text was not opened. This starter does not decide that the code "
                "was followed, and it does not destroy a record."
            ),
        },
        {
            "id": "gscp",
            "name": "Government Security Classifications Policy",
            "url": GSCP_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "The HTML page says it was updated on 5 August 2024. The executive "
                "summary describes three classification tiers (OFFICIAL, SECRET and "
                "TOP SECRET). Paragraph 1 says the policy is not a statutory scheme. "
                "Paragraph 9 points to the section 46 code for keeping, management "
                "and destruction. Paragraph 25 says the -SENSITIVE marking is applied "
                "to OFFICIAL information and should be applied immediately after the "
                "OFFICIAL classification. The policy's own handling example is "
                "written OFFICIAL-SENSITIVE. -SENSITIVE is not a fourth tier. "
                "Guidance 1.1 was opened the same day. This starter does not decide "
                "the marking and does not downgrade one."
            ),
        },
        {
            "id": "uk-gdpr-art-5",
            "name": "UK GDPR Article 5",
            "url": UK_GDPR_ARTICLE_5_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "Article 5(1)(e) says personal data shall be kept in a form which "
                "permits identification of data subjects for no longer than is "
                "necessary for the purposes for which the personal data are "
                "processed. Personal data may be stored for longer periods insofar "
                "as they will be processed solely for archiving purposes in the "
                "public interest, scientific or historical research purposes or "
                "statistical purposes in accordance with Article 84B. The words "
                "Article 84B were substituted on 5 February 2026. Article 84B was "
                "not opened. Article 5(2) is the accountability principle. This "
                "starter does not decide that storage limitation was met."
            ),
        },
        {
            "id": "purview-records",
            "name": "Microsoft Purview records management",
            "url": PURVIEW_RECORDS_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "The get-started page describes a file plan for retention and "
                "deletion settings, retention labels applied by a person or "
                "automatically, and disposition reviews so that somebody reviews "
                "and approves before content is deleted at the end of its retention "
                "period. It recommends the Records Management admin role group. "
                "The service-description licensing table was not opened. This "
                "starter does not call Purview."
            ),
        },
        {
            "id": "purview-sensitivity",
            "name": "Microsoft Purview sensitivity labels",
            "url": PURVIEW_SENSITIVITY_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "The page says sensitivity labels let an organisation classify and "
                "protect data, including encryption and content markings. Each item "
                "can have a single sensitivity label from the organisation. "
                "Documents and emails can have both a sensitivity label and a "
                "retention label. Extending labels to the Microsoft Purview Data "
                "Map is described as currently in preview. This starter does not "
                "apply a label in a tenant."
            ),
        },
        {
            "id": "harness",
            "name": "Harnesses in Copilot Studio",
            "url": HARNESS_URL,
            "opened_on": "2026-11-11",
            "quote": (
                "The overview says the GitHub Copilot harness is a Microsoft "
                "Copilot Studio authoring and orchestration framework, not the "
                "GitHub Copilot service, and that customer data is not sent to or "
                "processed by the GitHub Copilot service when agents run in "
                "Copilot Studio. Agents and workflows on that harness use Copilot "
                "Credits. The standard harness follows the topics and rules the "
                "maker defines. The page states no price. The linked billing pages "
                "were not opened."
            ),
        },
    )
    published = []
    for row in rows:
        item = {
            "id": row["id"],
            "name": row["name"],
            "url": row["url"],
            "opened_on": row["opened_on"],
            "taken": row["quote"] if current else None,
        }
        published.append(item)
    return published
