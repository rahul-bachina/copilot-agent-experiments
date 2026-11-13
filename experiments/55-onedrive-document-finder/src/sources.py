"""Pinned pages opened for Experiment 55 on 13 November 2026.

The core does not download these pages when it runs. A pin older than
``STALE_AFTER_DAYS`` is not quoted. Equal to 180 days is still current.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 13)
STALE_AFTER_DAYS = 180
FILE_STALE_AFTER_DAYS = 365

SOURCES = (
    {
        "id": "uk-gdpr-art-5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "opened": "2026-11-13",
        "taken": (
            "Article 5(1)(c): personal data shall be adequate, relevant and "
            "limited to what is necessary in relation to the purposes for which "
            "they are processed (data minimisation). Article 5(2) is accountability. "
            "Article 6 and Article 9 were not opened. No lawful basis is asserted."
        ),
    },
    {
        "id": "foia-s1",
        "title": "Freedom of Information Act 2000, section 1",
        "url": "https://www.legislation.gov.uk/ukpga/2000/36/section/1",
        "opened": "2026-11-13",
        "taken": (
            "Section 1(1) is the general right: to be told whether the authority "
            "holds information of the description specified, and if so to have it "
            "communicated. Section 1(3) covers further information needed to "
            "identify and locate the information. The page said there are currently "
            "no known outstanding effects. This starter does not decide that duty."
        ),
    },
    {
        "id": "gsc-policy",
        "title": "Government Security Classifications Policy",
        "url": "https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html",
        "opened": "2026-11-13",
        "taken": (
            "Updated 5 August 2024. Paragraph 1: the policy is not a statutory "
            "scheme. Paragraph 5 names three tiers: OFFICIAL, SECRET and TOP SECRET. "
            "Paragraph 25: the -SENSITIVE marking is an additional marking on "
            "OFFICIAL, applied immediately after OFFICIAL. Principle Five is "
            "need-to-know balanced with need-to-share. The fixture clearance order "
            "is this starter's rule. It is not a sentence of the policy."
        ),
    },
    {
        "id": "m365-copilot",
        "title": "What is Microsoft Copilot?",
        "url": "https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview",
        "opened": "2026-11-13",
        "taken": (
            "The page says experiences differ by data grounding, integration depth, "
            "and licensing, and that access is scoped by user permissions. Work-data "
            "grounding is described as Microsoft Graph and Work IQ for the experiences "
            "that include work data. Copilot Chat (Basic) primarily uses web data "
            "unless the user provides content. This starter calls none of those APIs."
        ),
    },
    {
        "id": "copilot-studio-knowledge",
        "title": "Knowledge sources summary",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio",
        "opened": "2026-11-13",
        "taken": (
            "SharePoint is described as using GraphSearch, with the agent user's "
            "Microsoft Entra ID authentication. A note says the agent only surfaces "
            "content the specific user can access. OneDrive files and folders are "
            "named as unstructured data with different limits. The limits page was "
            "not opened. Those limits are unverified here."
        ),
    },
    {
        "id": "graph-search-files",
        "title": "Search OneDrive and SharePoint content",
        "url": "https://learn.microsoft.com/en-us/graph/search-concept-files",
        "opened": "2026-11-13",
        "taken": (
            "POST /search/query can set entityTypes to driveItem for files. Example 4 "
            "says it queries OneDrive and SharePoint content to which the signed-in "
            "user has read access. KQL path: can scope a folder. includeHiddenContent "
            "defaults to false and, on that page, only works with delegated permissions."
        ),
    },
    {
        "id": "graph-search-query",
        "title": "searchEntity: query",
        "url": "https://learn.microsoft.com/en-us/graph/api/search-query?view=graph-rest-1.0",
        "opened": "2026-11-13",
        "taken": (
            "v1.0. Delegated least privileged permission shown is Mail.Read, with "
            "higher permissions including Files.Read.All and Sites.Read.All. "
            "Application least privileged permission shown is Files.Read.All. "
            "Whether a driveItem-only query accepts a narrower delegated scope was "
            "not stated. Whether application permissions are trimmed to one user "
            "was not stated. This starter calls neither."
        ),
    },
    {
        "id": "work-iq",
        "title": "Work IQ overview, API, and permissions",
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/",
        "opened": "2026-11-13",
        "taken": (
            "The overview describes a permission-aware workplace intelligence layer. "
            "API access is independent of Microsoft 365 Copilot licensing and is "
            "usage-based. The API overview says requests use delegated authentication, "
            "application-only authentication is not supported, and Microsoft 365 "
            "permissions, sensitivity labels, and compliance policies are enforced "
            "automatically. The permissions reference lists delegated WorkIQ.Read and "
            "WorkIQ.Act. WorkIQ.Act is described as read and change. A "
            "general-availability date was not on the pages opened. That date is "
            "unverified. This starter does not call Work IQ."
        ),
    },
    {
        "id": "purview-labels",
        "title": "Learn about sensitivity labels",
        "url": "https://learn.microsoft.com/en-us/purview/sensitivity-labels",
        "opened": "2026-11-13",
        "taken": (
            "Labels are customisable. The page's examples include Personal, Public, "
            "General, Confidential, and Highly Confidential. A label is stored in "
            "clear text in metadata and stays with the content. An item can have "
            "one sensitivity label from the organisation, and a document can also "
            "carry a retention label. The page says Copilot and agents recognise "
            "sensitivity labels. Data Map labelling is described as currently in "
            "preview. The licensing table was not opened. This starter does not "
            "call Purview. A Government Security Classifications marking in a "
            "fixture is not a Purview label."
        ),
    },
    {
        "id": "harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened": "2026-11-13",
        "taken": (
            "The page names three harnesses: Microsoft Copilot harness, Customer "
            "Conversation harness, and standard harness. The standard harness follows "
            "the topics and rules the maker defines. The Microsoft Copilot harness "
            "is described for reasoning-heavy multi-step work, with skills, memory, "
            "file creation, and a sandbox, billed in Copilot Credits. The page states "
            "no price. The page opened on this date does not use the words GitHub "
            "Copilot harness and does not say it is not the GitHub Copilot service. "
            "That older wording is unverified against this page."
        ),
    },
)


def source_rows(rules_current: bool) -> list[dict]:
    rows = []
    for source in SOURCES:
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "opened": source["opened"],
                "taken": source["taken"] if rules_current else None,
            }
        )
    return rows
