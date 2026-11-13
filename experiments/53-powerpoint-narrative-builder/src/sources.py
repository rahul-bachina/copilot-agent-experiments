"""Pinned pages opened for Experiment 53 on 13 November 2026.

The core does not download these pages when it runs. A page that was not
opened is listed in NOT_OPENED and is not treated as decided.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 13)
SOURCE_WINDOW_DAYS = 180

SOURCES: list[dict] = [
    {
        "id": "psbar-2018-reg-3",
        "title": "Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/2018/952/regulation/3",
        "opened": "2026-11-13",
        "note": (
            "Regulation 3 defines the accessibility requirement as the requirement "
            "to make a website or mobile application accessible by making it "
            "perceivable, operable, understandable and robust. It defines a mobile "
            "application and a public sector body. The text opened does not name "
            "WCAG. Amendments by S.I. 2022/1097 and S.I. 2025/557 are shown on the "
            "page. In force at 23 September 2018. Regulation 7 and regulation 9 "
            "were not opened."
        ),
    },
    {
        "id": "psbar-2018-reg-4",
        "title": "Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018, regulation 4",
        "url": "https://www.legislation.gov.uk/uksi/2018/952/regulation/4",
        "opened": "2026-11-13",
        "note": (
            "Regulation 4(1) applies the regulations to a website or mobile "
            "application of a public sector body, with exceptions for public "
            "service broadcasters, some non-governmental organisations, and "
            "schools or nurseries except essential online administrative functions. "
            "Regulation 4(2)(a) excludes office file formats published before "
            "23 September 2018, unless the content is needed for active "
            "administrative processes. Regulation 4(3)(d) defines office file "
            "formats as a document not intended primarily for use on the web and "
            "included in web pages, and names Microsoft Office documents. This "
            "starter does not decide that a deck is in scope."
        ),
    },
    {
        "id": "psbar-2018-reg-6",
        "title": "Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018, regulation 6",
        "url": "https://www.legislation.gov.uk/uksi/2018/952/regulation/6",
        "opened": "2026-11-13",
        "note": (
            "Regulation 6 says that, subject to regulation 7, public sector bodies "
            "must comply with the accessibility requirement. In force at "
            "23 September 2018. Regulation 7, the disproportionate-burden "
            "assessment, was not opened. This starter does not decide that a "
            "deck complies."
        ),
    },
    {
        "id": "govuk-accessibility-requirements",
        "title": "Understanding accessibility requirements for public sector bodies",
        "url": "https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps",
        "opened": "2026-11-13",
        "note": (
            "From the Government Digital Service and the Central Digital and Data "
            "Office. Last updated 30 September 2024. The page says the regulations "
            "came into force on 23 September 2018, and that a website or mobile "
            "app meets the legal requirements if it meets WCAG 2.2 AA and an "
            "accessibility statement is published. The regulation text opened the "
            "same day does not itself name WCAG 2.2. This starter does not certify "
            "WCAG 2.2 AA. The Equality Act 2010 and the Disability Discrimination "
            "Act 1995 were not opened."
        ),
    },
    {
        "id": "govuk-accessible-documents",
        "title": "Publishing accessible documents",
        "url": "https://www.gov.uk/guidance/publishing-accessible-documents",
        "opened": "2026-11-13",
        "note": (
            "From the Government Digital Service and the Central Digital and Data "
            "Office. Last updated 9 October 2025. The page says to keep the "
            "language simple, to aim for around 25 words or less per sentence, "
            "to give images and charts alt text, to check colour contrast, and "
            "to keep reading order logical. It says non-HTML documents should "
            "meet government accessibility requirements and WCAG 2.2 standards. "
            "It points to separate guidance for presentations. That further page "
            "was not opened. This starter records a checklist. It does not certify "
            "the deck."
        ),
    },
    {
        "id": "govuk-style-plain-english",
        "title": "GOV.UK style guide, plain English",
        "url": "https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style",
        "opened": "2026-11-13",
        "note": (
            "The plain English entry says all content on GOV.UK should be written "
            "in plain English, and that the words are lower case unless in a title. "
            "A later line on the same page says plain English is mandatory for "
            "GOV.UK. This starter does not decide that a sentence meets that guide."
        ),
    },
    {
        "id": "gscp-policy",
        "title": "Government Security Classifications Policy",
        "url": "https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html",
        "opened": "2026-11-13",
        "note": (
            "HTML edition. The version table records version 2.0 on 5 August 2024. "
            "The collection page, opened the same day, says the policy was updated "
            "on 30 June 2023 and was last updated on 5 August 2024. Paragraph 5 "
            "names three tiers: OFFICIAL, SECRET and TOP SECRET. Paragraph 25 says "
            "the most common additional marking is -SENSITIVE on OFFICIAL "
            "information that is not intended for public release, applied "
            "immediately after OFFICIAL, with the example OFFICIAL-SENSITIVE. "
            "This starter copies markings it finds. It does not downgrade one and "
            "it does not choose a tier."
        ),
    },
    {
        "id": "copilot-studio-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened": "2026-11-13",
        "note": (
            "The page names three harnesses: the Microsoft Copilot harness, the "
            "Customer Conversation harness, and the standard harness. The standard "
            "harness follows the topics and rules the maker defines. The Microsoft "
            "Copilot harness is described as the runtime for reasoning-heavy, "
            "multi-step work. It can create and edit Word, Excel, PowerPoint, and "
            "PDF files, supports skills and memory, runs each task in a sandbox "
            "governed by Copilot Studio, and uses Copilot Credits. The page states "
            "no price. The text retrieved on 13 November 2026 does not use the "
            "name GitHub Copilot harness and does not contain the sentence that "
            "the harness is not the GitHub Copilot service. Experiment 52 recorded "
            "that name and that sentence from the same URL on 12 November 2026. "
            "This starter keeps the repository name for the skills layout and "
            "does not treat the earlier sentence as verified on this read."
        ),
    },
    {
        "id": "m365-copilot-overview",
        "title": "Microsoft 365 Copilot overview",
        "url": "https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview",
        "opened": "2026-11-13",
        "note": (
            "The PowerPoint row says Copilot can create presentations from prompts "
            "or existing content, summarise presentations, or edit presentations, "
            "including adding images and deck-wide formatting changes. The page "
            "describes grounding in organisational data through Microsoft Graph "
            "and Work IQ, and says Work IQ can be turned on or off. A dedicated "
            "Copilot in PowerPoint how-to page was not opened. This starter does "
            "not call Copilot in PowerPoint."
        ),
    },
    {
        "id": "work-iq",
        "title": "Work IQ overview",
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/work-iq/",
        "opened": "2026-11-13",
        "note": (
            "Work IQ is described as a permission-aware workplace intelligence "
            "layer. The page names A2A, a remote MCP server, and a REST API. It "
            "says usage is independent of Microsoft 365 Copilot licensing and is "
            "billed on usage, and that API usage consumes Copilot Credits. It "
            "states no price and no general-availability date. The licensing page "
            "linked from it was not opened. This starter does not call Work IQ."
        ),
    },
]

NOT_OPENED: list[dict] = [
    {
        "id": "equality-act-2010",
        "title": "Equality Act 2010",
        "note": "Named on the GOV.UK accessibility page. The Act was not opened. No duty is treated as decided.",
    },
    {
        "id": "dda-1995",
        "title": "Disability Discrimination Act 1995",
        "note": "Named on the GOV.UK accessibility page for Northern Ireland. The Act was not opened.",
    },
    {
        "id": "psbar-reg-7",
        "title": "Accessibility Regulations 2018, regulation 7",
        "note": "Disproportionate burden. Not opened. This starter does not apply it.",
    },
    {
        "id": "psbar-reg-9",
        "title": "Accessibility Regulations 2018, regulation 9",
        "note": "Presumed conformity. Not opened. This starter does not presume conformity.",
    },
    {
        "id": "wcag-22",
        "title": "WCAG 2.2 recommendation",
        "note": "The W3C recommendation was not opened. WCAG 2.2 AA is cited only as what the GOV.UK guidance page says.",
    },
    {
        "id": "powerpoint-javascript",
        "title": "PowerPoint JavaScript API",
        "note": "Not opened. The local file is Office Open XML written with the standard library. The API is not called.",
    },
    {
        "id": "graph-upload",
        "title": "Microsoft Graph driveItem upload",
        "note": "Not opened for this experiment. Graph is not called. A file is not uploaded.",
    },
    {
        "id": "uk-gdpr",
        "title": "UK GDPR Articles 6, 9, and 28, and the Data Protection Act 2018",
        "note": "Not opened. No lawful basis is asserted.",
    },
    {
        "id": "retention-schedule",
        "title": "A records retention schedule",
        "note": "Not opened. A retention or legal-hold label found in the source is copied. A period is not invented.",
    },
]
