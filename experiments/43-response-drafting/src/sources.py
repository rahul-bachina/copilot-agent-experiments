"""Pinned sources for the response drafter.

The core does not download these pages. Dates are the day the page was opened
for this experiment. A later reader has to open the page again before treating
a quotation as current.
"""

from datetime import date

PINNED_ON = date(2026, 11, 9)
SOURCE_WINDOW_DAYS = 180

SOURCES = (
    {
        "id": "prin-2a-5",
        "title": "PRIN 2A.5 Consumer Duty: retail customer outcome on consumer understanding",
        "url": "https://handbook.fca.org.uk/handbook/prin2a/prin2as5",
        "pdf_url": "https://api-handbook.fca.org.uk/files/sourcebook/PRIN.pdf",
        "opened_on": "2026-11-09",
        "what_was_read": (
            "The PDF says it was last updated in June 2026. PRIN 2A.5.3 requires "
            "a firm to support retail customer understanding and to communicate in "
            "a way which is clear, fair and not misleading. The same PDF "
            "cross-refers to that paragraph as PRIN 2A.5.3R. PRIN 2A.5.7 says a "
            "firm should use plain and intelligible language. The status letter on "
            "2A.5.7 was not cleanly labelled in the PDF text extraction. "
            "PRIN 2A.5.10 requires testing and monitoring where appropriate, and "
            "the same PDF cross-refers to it as PRIN 2A.5.10R."
        ),
        "applied_outside_financial_services": False,
        "outcome_decided_here": False,
    },
    {
        "id": "uk-gdpr-article-12",
        "title": "UK GDPR Article 12",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/12",
        "opened_on": "2026-11-09",
        "what_was_read": (
            "Article 12(1) requires clear and plain language for information "
            "referred to in Articles 13 and 14 and for communications under "
            "Articles 15 to 22D and Article 34. A routine service reply is not, "
            "by itself, that information."
        ),
        "article_12_met_decided_here": False,
    },
    {
        "id": "equality-act-section-20",
        "title": "Equality Act 2010, section 20",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/20",
        "opened_on": "2026-11-09",
        "what_was_read": (
            "Section 20(6): where the first or third requirement relates to the "
            "provision of information, the steps which it is reasonable to take "
            "include an accessible format. Section 29 was not opened."
        ),
        "duty_met_decided_here": False,
    },
    {
        "id": "copilot-studio-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened_on": "2026-11-09",
        "what_was_read": (
            "The GitHub Copilot harness is a Copilot Studio authoring and "
            "orchestration framework, not the GitHub Copilot service. The "
            "standard harness follows topics and rules the maker defines. The "
            "Customer Conversation harness is described for customer voice and "
            "chat. Billing pages linked from the overview were not opened."
        ),
    },
)

NOT_OPENED = (
    "UK GDPR Article 5",
    "UK GDPR Article 6",
    "UK GDPR Article 9",
    "UK GDPR Article 22A",
    "Equality Act 2010 section 29",
    "Equality Act 2010 Schedule 2",
    "PRIN 2A.2",
    "FG22/5",
    "DISP",
    "ATRS mandatory scope policy",
)
