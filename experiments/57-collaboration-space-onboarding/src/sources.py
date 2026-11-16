"""Pages opened for this starter. The core does not download them."""

from __future__ import annotations

SOURCES_PINNED_ON = "2026-11-16"
STALE_AFTER_DAYS = 30

SOURCES = (
    {
        "id": "uk_gdpr_art_5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Article 5(1)(c) is data minimisation: adequate, relevant and limited "
            "to what is necessary. Article 5(1)(f) is integrity and confidentiality: "
            "appropriate security, including protection against unauthorised or "
            "unlawful processing. Article 5(2) is accountability. Article 6 and "
            "Article 9 were not opened. No lawful basis is asserted."
        ),
    },
    {
        "id": "gscp",
        "title": "Government Security Classifications Policy",
        "url": "https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Updated 5 August 2024. Paragraph 1: not a statutory scheme. "
            "Paragraph 5: three tiers, OFFICIAL, SECRET and TOP SECRET. "
            "Paragraph 25: the -SENSITIVE marking is an additional marking on "
            "OFFICIAL. Principle Five is need-to-know balanced with need-to-share. "
            "The fixture order that ranks OFFICIAL-SENSITIVE above OFFICIAL is "
            "not a sentence of this policy."
        ),
    },
    {
        "id": "ncsc_iam",
        "title": "NCSC 10 Steps: Identity and access management",
        "url": "https://www.ncsc.gov.uk/collection/10-steps/identity-and-access-management",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Published 11 May 2021, reviewed 11 May 2021, version 1.0. An identity "
            "and access management policy should cover who should have access to "
            "which systems, data or functionality, why, and under what circumstances, "
            "including contractors and visitors. Account management includes a "
            "joiners, movers and leavers policy. Full-privilege accounts are used "
            "only when absolutely necessary, and privileged access is reviewed and "
            "revoked when no longer required. The page does not use the words "
            "least privilege. The NCSC introduction page that does use those words "
            "was not opened."
        ),
    },
    {
        "id": "teams_overview",
        "title": "Introduction to Microsoft Teams for admins",
        "url": "https://learn.microsoft.com/en-us/microsoftteams/teams-overview",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Teams is built on Microsoft 365 groups, Microsoft Graph, and "
            "identities stored in Microsoft Entra ID. Creating a team creates a "
            "Microsoft 365 group, a SharePoint site and document library, an "
            "Exchange Online shared mailbox and calendar, and a OneNote notebook."
        ),
    },
    {
        "id": "teams_guest",
        "title": "Guest access in Microsoft Teams",
        "url": "https://learn.microsoft.com/en-us/microsoftteams/guest-access",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Guest access is an organisation-wide setting. Sensitivity labels can "
            "control guest access for an individual team. Adding a guest to the "
            "Microsoft 365 group associated with a team gives the guest access to "
            "the team. External access, for chat and meetings with other Microsoft "
            "365 organisations, is a different feature. The page points to Microsoft "
            "Entra access reviews for guests in groups or teams. This starter does "
            "not create a review and does not send an invitation."
        ),
    },
    {
        "id": "graph_members",
        "title": "Add members - Microsoft Graph v1.0",
        "url": "https://learn.microsoft.com/en-us/graph/api/group-post-members?view=graph-rest-1.0",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "POST /groups/{group-id}/members/$ref adds a member. For a user, the "
            "least privileged delegated and application permission named on the "
            "page is GroupMember.ReadWrite.All. A successful call returns 204 No "
            "Content. This starter does not send the request."
        ),
    },
    {
        "id": "graph_owners",
        "title": "Add owners - Microsoft Graph v1.0",
        "url": "https://learn.microsoft.com/en-us/graph/api/group-post-owners?view=graph-rest-1.0",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "POST /groups/{id}/owners/$ref adds an owner. The least privileged "
            "permission named on the page is Group.ReadWrite.All. The page says "
            "an owner who should make changes in a team also needs to be a member, "
            "and that owner changes can take up to 2 hours to synchronise with "
            "Teams. A successful call returns 204 No Content. This starter does "
            "not send the request."
        ),
    },
    {
        "id": "entra_reviews",
        "title": "What are access reviews?",
        "url": "https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Microsoft Entra access reviews cover group memberships, access to "
            "enterprise applications, and role assignments. The page says the "
            "feature requires Microsoft Entra ID Governance or Microsoft Entra "
            "Suite, and that some capabilities may operate with Microsoft Entra "
            "ID P2. This starter does not create a review. Which SKU a tenant "
            "needs was not checked beyond that paragraph."
        ),
    },
    {
        "id": "purview_containers",
        "title": "Use sensitivity labels with Microsoft Teams, Microsoft 365 groups, and SharePoint sites",
        "url": "https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Sensitivity labels can protect containers: Microsoft Teams sites, "
            "Microsoft 365 groups, and SharePoint sites. Items in the container "
            "do not inherit the container label. Privacy can be Public, Private, "
            "or None. External user access controls whether the owner can add "
            "guests. External sharing from the SharePoint site is a separate "
            "setting. A fixture Government Security Classifications marking is "
            "not a Purview label."
        ),
    },
    {
        "id": "harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened": SOURCES_PINNED_ON,
        "taken": (
            "Three harnesses are named: Microsoft Copilot harness, Customer "
            "Conversation harness, and standard harness. The standard harness "
            "follows the topics and rules the maker defines. The Microsoft "
            "Copilot harness is described for reasoning-heavy multi-step work, "
            "with skills, memory, file creation, and a sandbox, billed in "
            "Copilot Credits. The page states no price. The page does not use "
            "the words GitHub Copilot harness. Older wording that this harness "
            "is not the GitHub Copilot service is unverified against the page "
            "opened on this date."
        ),
    },
)


def source_rows(as_of: str) -> tuple[list[dict], bool]:
    rows = []
    current = True
    for source in SOURCES:
        age_note = "Pinned on %s. as_of is %s." % (source["opened"], as_of)
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "opened": source["opened"],
                "taken": source["taken"],
                "note": age_note,
            }
        )
        if as_of < source["opened"]:
            current = False
    return rows, current
