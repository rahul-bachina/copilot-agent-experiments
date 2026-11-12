"""Pages opened for this starter. The core does not download them when it runs."""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 12)
STALE_AFTER_DAYS = 180
EXPORT_STALE_AFTER_DAYS = 14

QUOTE_PURPOSE = (
    "collected (whether from the data subject or otherwise) for specified, "
    "explicit and legitimate purposes and not further processed by or on behalf "
    "of a controller in a manner that is incompatible with the purposes for "
    "which the controller collected the data"
)
QUOTE_MINIMISATION = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed"
)
QUOTE_FOIA_1_1 = (
    "Any person making a request for information to a public authority is entitled "
    "to be informed in writing by the public authority whether it holds information "
    "of the description specified in the request, and if that is the case, to have "
    "that information communicated to him."
)

# Titles and URLs as read on 12 November 2026.
ICO_MONITORING_TITLE = "Employment practices and data protection: monitoring workers"
ICO_MONITORING_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "employment/monitoring-workers/"
)
ICO_MESSAGES_TITLE = (
    "Specific data protection considerations for different ways or methods "
    "of monitoring workers"
)
ICO_MESSAGES_URL = (
    "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
    "employment/monitoring-workers/"
    "specific-data-protection-considerations-for-different-ways-or-methods-of-monitoring-workers"
)


def source_rows(as_of: str) -> tuple[list[dict], bool]:
    """Return citation rows. Quotes are omitted when the pin is stale."""
    opened = date.fromisoformat(as_of)
    age = (opened - SOURCES_PINNED_ON).days
    current = 0 <= age <= STALE_AFTER_DAYS
    rows = [
        {
            "id": "uk-gdpr-article-5",
            "title": "UK GDPR Article 5",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": QUOTE_PURPOSE if current else None,
            "note": (
                "Article 5(1)(b) and Article 5(1)(c) were read. "
                "Article 5(1)(e) now refers to Article 84B. Article 84B was not opened. "
                "Article 6 and Article 9 were not opened."
            ),
        },
        {
            "id": "foia-section-1",
            "title": "Freedom of Information Act 2000, section 1",
            "url": "https://www.legislation.gov.uk/ukpga/2000/36/section/1",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": QUOTE_FOIA_1_1 if current else None,
            "note": (
                "Section 1(1) is the right of access. Section 1(2) says that right "
                "is subject to section 1 and to sections 2, 9, 12 and 14. "
                "Those sections were not opened. The page said there are currently "
                "no known outstanding effects for section 1."
            ),
        },
        {
            "id": "ico-monitoring-workers",
            "title": ICO_MONITORING_TITLE,
            "url": ICO_MONITORING_URL,
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "The hub says the guidance is under review because of the "
                "Data (Use and Access) Act and may change. This starter does not "
                "decide that monitoring workers is lawful."
            ),
        },
        {
            "id": "ico-monitoring-messages",
            "title": ICO_MESSAGES_TITLE,
            "url": ICO_MESSAGES_URL,
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "The page says messages include instant messages and the chat "
                "functions in collaboration tools. It says a DPIA must be completed "
                "before monitoring emails and messages. It says content should be "
                "distinguished from network data, and that content is for exceptional "
                "circumstances with advance notice. This starter does not decide that "
                "a DPIA is required and does not complete one."
            ),
        },
        {
            "id": "graph-list-channel-messages",
            "title": "List channel messages, Microsoft Graph v1.0",
            "url": "https://learn.microsoft.com/en-us/graph/api/channel-list-messages?view=graph-rest-1.0",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "GET /teams/{team-id}/channels/{channel-id}/messages returns messages "
                "without replies unless $expand=replies is used. Delegated least "
                "privilege on that page is ChannelMessage.Read.All. Application least "
                "privilege is ChannelMessage.Read.Group, which uses resource-specific "
                "consent. Personal Microsoft accounts are not supported. $top and "
                "$expand are the supported query options. A date filter is not a "
                "supported query option on that page. This starter does not call Graph."
            ),
        },
        {
            "id": "copilot-studio-harnesses",
            "title": "Harnesses in Copilot Studio",
            "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "The standard harness follows the topics and rules the maker defines. "
                "The GitHub Copilot harness is a Copilot Studio framework, not the "
                "GitHub Copilot service. Agents on it use Copilot Credits. The page "
                "states no price."
            ),
        },
        {
            "id": "teams-copilot-overview",
            "title": "Overview of AI in Microsoft Teams",
            "url": "https://learn.microsoft.com/en-us/microsoftteams/copilot-ai-agents-overview",
            "opened_on": SOURCES_PINNED_ON.isoformat(),
            "taken": None,
            "note": (
                "Copilot in Teams chats and channels is described as helping a user "
                "catch up. The linked end-user article was not opened. Channel Agent "
                "is described as a channel collaboration agent. The overview table "
                "lists an article about creating and sending emails with Channel Agent. "
                "That article was not opened. This starter does not use Channel Agent "
                "and does not send."
            ),
        },
    ]
    return rows, current
