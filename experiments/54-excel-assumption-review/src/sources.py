"""Pinned pages opened for Experiment 54 on 13 November 2026.

The core does not download these pages when it runs. A page that was not
opened is listed in NOT_OPENED and is not treated as decided.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 13)
SOURCE_WINDOW_DAYS = 180

SOURCES: list[dict] = [
    {
        "id": "aqua-book-2025",
        "title": "The AQuA Book",
        "url": "https://www.gov.uk/guidance/the-aqua-book",
        "opened": "2026-11-13",
        "note": (
            "The page title is The AQuA Book. Published 30 July 2025. From the "
            "Government Operational Research Service, the Government Analysis "
            "Function, the Government Actuary's Department, and the Office for "
            "National Statistics. Section 1.1 says the last version was published "
            "in 2015, following Sir Nicholas Macpherson's Review of quality "
            "assurance of government models. The assumptions log, under "
            "Documentation, should describe each assumption, quantify its effect "
            "and reliability, set out when it was made, explain why it was made, "
            "and explain who made it and who signed it off. Section 1.3.3 "
            "distinguishes verification from validation. This starter does not "
            "sign an assumptions log, does not decide that analysis is fit for "
            "purpose, and does not decide that a model is business-critical."
        ),
    },
    {
        "id": "macpherson-2013",
        "title": "Review of quality assurance of government models",
        "url": "https://www.gov.uk/government/publications/review-of-quality-assurance-of-government-models",
        "opened": "2026-11-13",
        "note": (
            "HM Treasury. Published 5 March 2013. The page describes the final "
            "report by Sir Nicholas Macpherson, then Permanent Secretary to the "
            "Treasury, into the quality assurance of analytical models that "
            "inform government policy. The page lists a final report PDF. A "
            "guessed asset URL returned 404, so the PDF was not opened. "
            "Recommendation numbers are not quoted from the report."
        ),
    },
    {
        "id": "aqua-book-2015-pdf",
        "title": "The Aqua Book: guidance on producing quality analysis for government (March 2015 PDF)",
        "url": "https://analysisfunction.civilservice.gov.uk/wp-content/uploads/2018/03/Aqua-Book-4.pdf",
        "opened": "2026-11-13",
        "note": (
            "This is the March 2015 edition, not the current GOV.UK page. "
            "Paragraph 1.4 summarises headline recommendations of the review, "
            "including quality assurance of inputs, methodology, and outputs "
            "for business-critical models, and a single senior responsible "
            "owner for each model. Those sentences are the 2015 book's summary. "
            "They are not a quotation from the 2013 PDF, which was not opened. "
            "This starter does not appoint a senior responsible owner and does "
            "not decide that a model is business-critical."
        ),
    },
    {
        "id": "harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened": "2026-11-13",
        "note": (
            "The page names three harnesses: the Microsoft Copilot harness, the "
            "Customer Conversation harness, and the standard harness. The "
            "standard harness follows the topics and rules the maker defines. "
            "The Microsoft Copilot harness is described as reasoning-heavy and "
            "multi-step. The page says it creates and edits Word, Excel, "
            "PowerPoint, and PDF files, supports skills and memory, and uses "
            "Copilot Credits. The page states no price. The page opened on "
            "13 November 2026 does not use the words GitHub Copilot harness and "
            "does not say that the harness is not the GitHub Copilot service. "
            "Earlier experiments in this repository recorded that sentence from "
            "pages opened in October and early November 2026. It was not on the "
            "page opened for this experiment. The catalogue still uses the "
            "older name. This starter does not edit an Excel file, including "
            "where the Microsoft Copilot harness can."
        ),
    },
    {
        "id": "copilot-overview",
        "title": "What is Microsoft Copilot?",
        "url": "https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview",
        "opened": "2026-11-13",
        "note": (
            "Under Microsoft 365 Copilot (Basic), the in-app Excel line is: "
            "analyse data, generate insights, create formulas and visuals. The "
            "same page says that to use Copilot a person signs in with a work "
            "or school account and the file must be editable, not read-only. "
            "A dedicated Copilot in Excel product page was not opened. This "
            "starter does not call Copilot in Excel."
        ),
    },
    {
        "id": "graph-excel",
        "title": "Working with Excel in Microsoft Graph",
        "url": "https://learn.microsoft.com/en-us/graph/api/resources/excel?view=graph-rest-1.0",
        "opened": "2026-11-13",
        "note": (
            "The Excel REST API reads and modifies workbooks stored in OneDrive "
            "for Business, a SharePoint site, or a group drive. Office Open XML "
            "workbooks only. Files.Read is listed for read actions. "
            "Files.ReadWrite is listed for read and write actions. The page "
            "says that if a call does not send a workbook-session-id header, "
            "changes made during the call are persisted to the file. A "
            "non-persistent session is described as not saving changes to the "
            "source. This starter calls neither, and it does not create a session."
        ),
    },
]

NOT_OPENED: list[dict] = [
    {
        "id": "macpherson-pdf",
        "title": "Review of quality assurance of government models: final report PDF",
        "note": "Listed on the publication page. Not opened. No recommendation number is quoted from it.",
    },
    {
        "id": "copilot-excel-dedicated",
        "title": "A dedicated Microsoft 365 Copilot in Excel product page",
        "note": "Not opened. The overview sentence is the limit of what this starter says about Copilot in Excel.",
    },
    {
        "id": "graph-permissions-table",
        "title": "The permissions table on range-get, beyond the Excel resource page",
        "note": "Not opened. Files.Read and Files.ReadWrite are taken from the Excel resource page only.",
    },
    {
        "id": "entra-agent-id",
        "title": "Microsoft Entra Agent ID",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "conditional-access",
        "title": "Conditional Access for agents",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "prompt-shields",
        "title": "Microsoft Foundry prompt shields",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "key-vault",
        "title": "Key Vault",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "purview",
        "title": "Microsoft Purview",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "app-insights",
        "title": "Application Insights",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "dlp",
        "title": "Power Platform DLP as a configured policy",
        "note": "Not opened on 13 November 2026. Unverified here.",
    },
    {
        "id": "billing",
        "title": "Copilot Studio billing pages linked from the harness overview",
        "note": "Not opened. No price is copied.",
    },
    {
        "id": "uk-gdpr-articles",
        "title": "UK GDPR Articles 6 and 9",
        "note": "Not opened. No lawful basis is asserted.",
    },
]


def sources_current(as_of: date) -> bool:
    """Equal to the window is still current. One day past it is not."""
    return (as_of - PINNED_ON).days <= SOURCE_WINDOW_DAYS
