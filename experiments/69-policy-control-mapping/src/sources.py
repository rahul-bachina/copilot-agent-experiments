"""Public context opened for this starter. The PDF was not opened.

The HTML page https://www.ncsc.gov.uk/collection/cyber-assessment-framework
was opened on 20 November 2026. It states Version 4.0, Published 18 April 2024,
and Reviewed 30 October 2026. The same page lists a blog title dated 6 August
2025, "Cyber Assessment Framework v4.0 released". Those dates are what the page
showed. They are not reconciled here.

The PDF linked from that page was not opened. Principle pages were not opened.
Indicator wording is unverified and is not copied. ISO/IEC 27001 control text
is not copied. Identifiers only.
"""

from __future__ import annotations

CAF_PAGE = "https://www.ncsc.gov.uk/collection/cyber-assessment-framework"
CAF_VERSION = "4.0"
CAF_OPENED_ON = "2026-11-20"
CAF_PUBLISHED_ON_PAGE = "2024-04-18"
CAF_REVIEWED_ON_PAGE = "2026-10-30"
CAF_PDF_OPENED = False
CAF_PRINCIPLE_PAGES_OPENED = False

# The four objective titles are the words on the HTML page opened on
# CAF_OPENED_ON. They are not a finding that an objective is achieved.
CAF_OBJECTIVES = (
    "Managing security risk",
    "Protecting against cyber attack",
    "Detecting cyber security events",
    "Minimising the impact of cyber security incidents",
)

ISO_IDENTIFIER = "ISO/IEC 27001:2022"

HARNESS_PAGE = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview"
HARNESS_OPENED_ON = "2026-11-20"


def caf_note() -> dict:
    return {
        "page": CAF_PAGE,
        "version_on_page": CAF_VERSION,
        "opened_on": CAF_OPENED_ON,
        "published_on_page": CAF_PUBLISHED_ON_PAGE,
        "reviewed_on_page": CAF_REVIEWED_ON_PAGE,
        "pdf_opened": CAF_PDF_OPENED,
        "principle_pages_opened": CAF_PRINCIPLE_PAGES_OPENED,
        "indicators_unverified": True,
        "indicator_text_copied": False,
        "objectives_on_page": list(CAF_OBJECTIVES),
        "page_also_showed_blog_title_dated": "2025-08-06",
        "dates_not_reconciled": True,
        "used_as": "optional public context",
        "achievement_decided": False,
    }


def harness_note() -> dict:
    return {
        "page": HARNESS_PAGE,
        "opened_on": HARNESS_OPENED_ON,
        "harnesses_named_on_the_page": [
            "Microsoft Copilot harness",
            "Customer Conversation harness",
            "standard harness",
        ],
        "github_copilot_harness_words_on_page": False,
        "copilot_credits_stated_for_microsoft_copilot_harness": True,
        "price_stated": False,
        "pricing_pages_opened": False,
        "page_says_the_harness_is_not_the_github_copilot_service": False,
    }


def iso_note() -> dict:
    return {
        "standard": ISO_IDENTIFIER,
        "control_text_copied": False,
        "referred_to_by_identifier_only": True,
    }
