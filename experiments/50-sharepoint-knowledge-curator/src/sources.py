"""Quotations pinned on 12 November 2026.

A run does not fetch these pages again. Article 6, Article 9, and Article 84B
were not opened. Freedom of Information Act 2000 section 48 was not opened.
The 2021 code PDF does not use the words "Lord Chancellor". Section 46(1),
as opened the same day, names the Secretary of State.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 12)
STALE_AFTER_DAYS = 180

UK_GDPR_ARTICLE_5_URL = "https://www.legislation.gov.uk/eur/2016/679/article/5"
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
CONTENT_DESIGN_URL = "https://www.gov.uk/guidance/content-design"
RETIRE_URL = (
    "https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/"
    "plan-manage-content/retire-content/"
)
HARNESS_URL = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview"
SHAREPOINT_KNOWLEDGE_URL = (
    "https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint"
)
SITEPAGE_URL = "https://learn.microsoft.com/en-us/graph/api/resources/sitepage?view=graph-rest-1.0"
SITEPAGE_LIST_URL = (
    "https://learn.microsoft.com/en-us/graph/api/sitepage-list?view=graph-rest-1.0"
)
SELECTED_URL = "https://learn.microsoft.com/en-us/graph/permissions-selected-overview"

# Distinctive phrases withheld when the pin is stale. Do not put them in fixtures.
QUOTE_ACCURACY = "accurate and, where necessary, kept up to date"
QUOTE_STORAGE = (
    "kept in a form which permits identification of data subjects for no longer "
    "than is necessary for the purposes for which the personal data are processed"
)
QUOTE_ARTICLE_84B = "in accordance with Article 84B"
QUOTE_AUTHORISED = "Those taking disposition decisions must be properly authorised to do so"


def source_rows(current: bool) -> list[dict]:
    """Return the pin. Quotes are omitted when the pin is stale."""

    rows = (
        {
            "id": "uk-gdpr-art-5",
            "name": "UK GDPR Article 5",
            "url": UK_GDPR_ARTICLE_5_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "Article 5(1)(d) says personal data shall be accurate and, where "
                "necessary, kept up to date, and that every reasonable step must be "
                "taken to ensure that personal data that are inaccurate are erased "
                "or rectified without delay. Article 5(1)(e) says personal data shall "
                "be kept in a form which permits identification of data subjects for "
                "no longer than is necessary for the purposes for which the personal "
                "data are processed. The longer-storage limb says processing solely "
                "for archiving in the public interest, scientific or historical "
                "research, or statistics is in accordance with Article 84B. Article "
                "84B was not opened. This starter does not decide that either "
                "principle was met, and it does not erase personal data."
            ),
        },
        {
            "id": "foia-s46",
            "name": "Freedom of Information Act 2000, section 46",
            "url": FOIA_SECTION_46_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "Section 46(1) says the Secretary of State shall issue, and may "
                "revise, a code of practice providing guidance to relevant "
                "authorities on the practice which it would, in his opinion, be "
                "desirable for them to follow in connection with the keeping, "
                "management and destruction of their records. The words Secretary "
                "of State in subsection (1) were substituted on 9 December 2015. "
                "Section 46(6) requires the code to be laid before Parliament. "
                "Section 46(7) defines a relevant authority. The page said there "
                "are currently no known outstanding effects. Section 46(5)(b) "
                "now says the Commission, after a substitution dated 30 September "
                "2026. That instrument was not opened. Section 48 was not opened."
            ),
        },
        {
            "id": "s46-code",
            "name": "Code of Practice on the management of records, section 46",
            "url": CODE_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "The GOV.UK page, published 15 July 2021 by The National Archives, "
                "links a 32-page PDF. The PDF says it was presented to Parliament "
                "by the Secretary of State for Digital, Culture, Media and Sport "
                "pursuant to section 46(6), and laid before Parliament on 15 July "
                "2021. The extracted PDF text does not contain the words Lord "
                "Chancellor. Paragraph 1.4.3 says the code does not apply to bodies "
                "subject to the Freedom of Information (Scotland) Act 2002. "
                "Paragraph 2.3.1 says authorities must define how long to keep "
                "information and dispose of it when it is no longer needed. "
                "Paragraph 2.5 paraphrases Article 5(1)(e) in the code's own words. "
                "That paraphrase predates the Article 84B substitution. Paragraph "
                "2.6.2 says disposition decisions must be recorded and that those "
                "taking them must be properly authorised to do so. This starter "
                "does not take a disposition decision."
            ),
        },
        {
            "id": "govuk-content",
            "name": "GOV.UK content design and retiring content",
            "url": RETIRE_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "Requesting the content design guidance URL returned a page titled "
                "Writing to GOV.UK standards. The retire-content page says withdraw "
                "keeps content at the same URL with a banner, and unpublish removes "
                "it. It says guidance should usually be updated rather than "
                "withdrawn. News articles and press releases that are over a year "
                "old are an example of content that can be withdrawn. Unpublish "
                "includes the case where content has been included in another page, "
                "and the case where it contains someone's personal details. This "
                "guidance is about GOV.UK publishing. An intranet is not GOV.UK. "
                "This starter does not withdraw, unpublish, or delete."
            ),
        },
        {
            "id": "graph-sitepage",
            "name": "Microsoft Graph sitePage resource, v1.0",
            "url": SITEPAGE_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "The sitePage resource lists title, contentType as contentTypeInfo, "
                "publishingState, webUrl, createdBy, and lastModifiedDateTime. The "
                "property list that was opened does not include an audience column, "
                "a review date, or an owner column. Delete and Publish are methods "
                "on the resource. The list-pages page lists Sites.Read.All as the "
                "least privileged permission for delegated and application access, "
                "and Sites.ReadWrite.All as higher. Sites.Selected is described on "
                "a separate page as access to specific site collections after an "
                "explicit assignment. That list-pages page does not say Sites.Selected "
                "is accepted. This starter calls neither API."
            ),
        },
        {
            "id": "copilot-sharepoint-knowledge",
            "name": "Copilot Studio SharePoint knowledge source",
            "url": SHAREPOINT_KNOWLEDGE_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "The page says it describes features used in agents or agent flows "
                "powered by the standard harness. It says the agent surfaces only "
                "content the user has permission to access, and that without "
                "permission the agent responds with no response. Read is the minimum "
                "it states. It says the agent searches the registered URL and "
                "subpaths, and does not crawl hyperlinks inside a registered page. "
                "SharePoint lists added as knowledge are described as ingested into "
                "Dataverse. The GitHub Copilot harness knowledge-sources page was "
                "not opened."
            ),
        },
        {
            "id": "harness",
            "name": "Harnesses in Copilot Studio",
            "url": HARNESS_URL,
            "opened_on": "2026-11-12",
            "quote": (
                "The standard harness follows the topics and rules the maker defines. "
                "The GitHub Copilot harness is a Copilot Studio authoring and "
                "orchestration framework, not the GitHub Copilot service. The page "
                "says customer data is not sent to or processed by the GitHub "
                "Copilot service when agents run in Copilot Studio. Agents on the "
                "GitHub Copilot harness use Copilot Credits. The page states no price. "
                "The comparison table says files, skills, and memory are not a focus "
                "of the standard harness."
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
