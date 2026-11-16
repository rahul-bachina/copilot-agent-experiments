"""Pinned pages opened for Experiment 56 on 16 November 2026.

The core does not download these pages when it runs. A pin older than
``STALE_AFTER_DAYS`` is not quoted. Equal to 180 days is still current.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 11, 16)
STALE_AFTER_DAYS = 180
LINK_STALE_AFTER_DAYS = 365
INTERVAL_MIN_DAYS = 1
INTERVAL_MAX_DAYS = 3650

SOURCES = (
    {
        "id": "uk-gdpr-art-5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "opened": "2026-11-16",
        "taken": (
            "Article 5(1)(d): personal data shall be accurate and, where necessary, "
            "kept up to date; every reasonable step must be taken to ensure that "
            "personal data that are inaccurate, having regard to the purposes for "
            "which they are processed, are erased or rectified without delay "
            "(accuracy). Article 6 and Article 9 were not opened. Article 84B was "
            "not opened. No lawful basis is asserted. accuracy_met stays false. "
            "This starter does not erase or rectify a contact."
        ),
    },
    {
        "id": "accessibility-regs",
        "title": "The Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018",
        "url": "https://www.legislation.gov.uk/uksi/2018/952",
        "opened": "2026-11-16",
        "taken": (
            "SI 2018/952. The contents page and regulations 3, 4, 6, and 8 were "
            "opened. Regulation 3 defines the accessibility requirement as making "
            "a website or mobile application perceivable, operable, understandable "
            "and robust. Regulation 4(2)(g) says the Regulations do not apply to "
            "content of extranets and intranets published before 23rd September "
            "2019, until such websites undergo a substantial revision. Regulation "
            "4(3)(b) defines extranets and intranets as a website that is only "
            "available for a closed group of people and not to the general public. "
            "Regulation 6: subject to regulation 7, public sector bodies must "
            "comply with the accessibility requirement. Regulation 7 was not "
            "opened. Regulation 8(1): a public sector body must provide an "
            "accessibility statement and keep that statement under regular review. "
            "The pages said there are currently no known outstanding effects for "
            "regulations 4, 6, and 8. This starter does not decide whether a page "
            "is in scope and does not assess that requirement."
        ),
    },
    {
        "id": "service-standard",
        "title": "Service Standard",
        "url": "https://www.gov.uk/service-manual/service-standard",
        "opened": "2026-11-16",
        "taken": (
            "The index lists 14 points. Point 5, opened the same day, is Make "
            "sure everyone can use the service: provide a service that everyone "
            "can use, including disabled people and people with other legally "
            "protected characteristics. Point 8, opened the same day, is Iterate "
            "and improve frequently: make sure you have the capacity, resources "
            "and technical flexibility to iterate and improve the service "
            "frequently. The point 8 page says services are never finished. "
            "Point 5 was last updated 30 May 2022, with no change to the point "
            "itself. This is the Service Standard. It is not a finding that an "
            "intranet met it."
        ),
    },
    {
        "id": "content-design",
        "title": "Understand content design",
        "url": "https://www.gov.uk/guidance/content-design/what-is-content-design",
        "opened": "2026-11-16",
        "taken": (
            "The page is GOV.UK content and publishing guidance. It says well "
            "designed GOV.UK content should be kept up to date, and that content "
            "should either be current, meeting a user need and kept up to date, "
            "or no longer current but kept as a record of the government's past "
            "work. An intranet is not GOV.UK. This starter does not unpublish a page."
        ),
    },
    {
        "id": "graph-sitepage",
        "title": "sitePage resource type",
        "url": "https://learn.microsoft.com/en-us/graph/api/resources/sitepage?view=graph-rest-1.0",
        "opened": "2026-11-16",
        "taken": (
            "Microsoft Graph v1.0. A sitePage is a page in the sitePages list. "
            "Properties opened that day include title, name, description, "
            "contentType, createdDateTime, lastModifiedDateTime, pageLayout, "
            "publishingState, promotionKind, and webUrl. The property list does "
            "not include a content owner, a review interval, a last-reviewed "
            "date, or page views. Those are starter fields on the synthetic "
            "inventory. This starter does not call Graph. The list-pages "
            "permission table was not re-opened on this date."
        ),
    },
    {
        "id": "graph-planner-task",
        "title": "plannerTask resource type",
        "url": "https://learn.microsoft.com/en-us/graph/api/resources/plannertask?view=graph-rest-1.0",
        "opened": "2026-11-16",
        "taken": (
            "Microsoft Graph v1.0. A plannerTask belongs to a plan and can be "
            "assigned to a bucket. The create-task page, opened the same day, "
            "is POST /planner/tasks. Delegated least privileged permission shown "
            "is Tasks.ReadWrite. Application least privileged permission shown "
            "is Tasks.ReadWrite.All. planId must be an existing plan. This "
            "starter does not call the API. A task stub in the JSON is not a "
            "Planner task."
        ),
    },
    {
        "id": "power-automate-approvals",
        "title": "Get started with Power Automate approvals",
        "url": "https://learn.microsoft.com/en-us/power-automate/get-started-approvals",
        "opened": "2026-11-16",
        "taken": (
            "The page says that when you submit an approval, approvers are "
            "notified. Start and wait for an approval waits for the response. "
            "Approve/Reject - First to respond completes when any assigned "
            "approver approves or rejects. Approval flows are saved in Dataverse. "
            "The approvals connector is described as a standard connector. This "
            "starter does not call the connector and does not send the approval "
            "request. The only message a deployment of that action would send, "
            "in this design, is that approval request to the named content owner."
        ),
    },
    {
        "id": "harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened": "2026-11-16",
        "taken": (
            "The page names three harnesses: Microsoft Copilot harness, Customer "
            "Conversation harness, and standard harness. The standard harness "
            "powers rule-based agents. The comparison table says it follows the "
            "topics and rules you define. The Microsoft Copilot harness is "
            "described for reasoning-heavy multi-step work. It supports skills "
            "and memory, creates and edits files, and runs each task in a secure "
            "sandbox. Agents on this harness use Copilot Credits. The page states "
            "no price. The page opened on this date does not use the words "
            "GitHub Copilot harness and does not say it is not the GitHub "
            "Copilot service. That older wording is unverified against this page."
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
