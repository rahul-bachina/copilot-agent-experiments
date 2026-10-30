"""Quotations pinned on 30 October 2026.

A run does not fetch these pages again. The ATRS scope and exemptions
policy was not opened. The Copilot Studio licensing article linked from
the harness overview was not opened. No price is stored here.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 10, 30)
STALE_AFTER_DAYS = 90

UK_GDPR_ARTICLE_35_URL = "https://www.legislation.gov.uk/eur/2016/679/article/35"
ATRS_GUIDANCE_URL = (
    "https://www.gov.uk/government/publications/"
    "guidance-for-organisations-using-the-algorithmic-transparency-recording-standard/"
    "algorithmic-transparency-recording-standard-guidance-for-public-sector-bodies"
)
ATRS_SCOPE_URL = (
    "https://www.gov.uk/government/publications/"
    "algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy"
)
HARNESS_OVERVIEW_URL = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview"

ARTICLE_35_1 = (
    "Where a type of processing in particular using new technologies, and taking "
    "into account the nature, scope, context and purposes of the processing, is "
    "likely to result in a high risk to the rights and freedoms of natural persons, "
    "the controller shall, prior to the processing, carry out an assessment of the "
    "impact of the envisaged processing operations on the protection of personal data."
)

ARTICLE_35_3_INTRO = (
    "A data protection impact assessment referred to in paragraph 1 shall in "
    "particular be required in the case of:"
)

ARTICLE_35_4_NOTE = (
    "On the legislation.gov.uk text opened on 30 October 2026, Article 35(4) "
    "says the Commission shall establish and make public a list of the kind of "
    "processing operations which are subject to the requirement for a data "
    "protection impact assessment. A footnote records that the word Commission "
    "was substituted on 30 September 2026. This tool does not decide whether "
    "any ICO page is that list."
)

ATRS_MANDATORY_ORGS = (
    "It is mandatory for all government departments, and for ALBs which deliver "
    "public or frontline services, or directly interact with the general public."
)

ATRS_MANDATORY_TOOLS = (
    "Within those organisations, the ATRS is mandatory for algorithmic tools "
    "which have a significant influence on a decision-making process with public "
    "effect, or directly interact with the general public."
)

ATRS_RECOMMENDED = (
    "However, the ATRS is recommended by the Data Standards Authority for use "
    "across the entire public sector and we have welcomed ATRS records from "
    "local government, police forces and other broader public sector organisations."
)

HARNESS_NOT_THE_SERVICE = (
    "The GitHub Copilot harness is a Microsoft Copilot Studio authoring and "
    "orchestration framework, not the GitHub Copilot service."
)

HARNESS_DATA = (
    "customer data isn't sent to or processed by the GitHub Copilot service "
    "when agents run in Copilot Studio."
)

SCOPE_POLICY_OPENED = False
LICENSING_ARTICLE_OPENED = False
