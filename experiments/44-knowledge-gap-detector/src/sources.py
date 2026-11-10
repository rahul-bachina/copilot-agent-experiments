"""Pinned sources for the knowledge gap detector.

The core does not download these pages. Dates are the day the page was opened
for this experiment. A later reader has to open the page again before treating
a quotation as current.
"""

from datetime import date

PINNED_ON = date(2026, 11, 10)
SOURCE_WINDOW_DAYS = 180

SOURCES = (
    {
        "id": "prin-2a-5",
        "title": "PRIN 2A.5 Consumer Duty: retail customer outcome on consumer understanding",
        "url": "https://handbook.fca.org.uk/handbook/prin2a/prin2as5",
        "pdf_url": "https://api-handbook.fca.org.uk/files/sourcebook/PRIN.pdf",
        "opened_on": "2026-11-10",
        "what_was_read": (
            "The handbook HTML page did not return the rule text on 10 November "
            "2026. It returned the FCA head-office address. The PRIN sourcebook "
            "PDF was opened the same day. The PDF text says the sourcebook was "
            "last updated in June 2026. The file metadata modification time was "
            "27 August 2026. That metadata is not a handbook sentence, so this "
            "starter does not treat 27 August 2026 as the sourcebook update date. "
            "PRIN 2A.5.3 says a firm must support retail customer understanding "
            "and must communicate in a way which is clear, fair and not "
            "misleading. PRIN 2A.5.4 cross-refers to PRIN 2A.5.3R. PRIN 2A.5.7 "
            "says a firm should use plain and intelligible language and, where "
            "jargon is unavoidable, explain it as simply as possible. The status "
            "letter on 2A.5.7 was not cleanly attached in the PDF text extraction. "
            "PRIN 2A.5.10 says, where appropriate, a firm must test communications "
            "and regularly monitor their impact. Paragraph (2) of that provision "
            "cross-refers to PRIN 2A.5.10R."
        ),
        "applied_outside_financial_services": False,
        "outcome_decided_here": False,
    },
    {
        "id": "uk-gdpr-article-5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "opened_on": "2026-11-10",
        "what_was_read": (
            "Article 5(1)(c): personal data shall be adequate, relevant and "
            "limited to what is necessary in relation to the purposes for which "
            "they are processed ('data minimisation'). The textual amendments "
            "listed on the page did not change paragraph (1)(c). Article 5(3) "
            "was listed as inserted. This starter does not rely on Article 5(3). "
            "Article 6 was not opened, so no lawful basis is chosen."
        ),
        "data_minimisation_met_decided_here": False,
    },
    {
        "id": "equality-act-section-20",
        "title": "Equality Act 2010, section 20",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/20",
        "opened_on": "2026-11-10",
        "what_was_read": (
            "The page said section 20 was up to date with all changes known to "
            "be in force on or before 07 November 2026. It was opened on "
            "10 November 2026. Section 20(6): where the first or third "
            "requirement relates to the provision of information, the steps "
            "which it is reasonable for A to have to take include steps for "
            "ensuring that the information is provided in an accessible format. "
            "The pending changes listed on the page were to other sections. "
            "Section 29 and Schedule 2 were not opened."
        ),
        "duty_met_decided_here": False,
    },
    {
        "id": "copilot-studio-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "opened_on": "2026-11-10",
        "what_was_read": (
            "The GitHub Copilot harness is a Microsoft Copilot Studio authoring "
            "and orchestration framework, not the GitHub Copilot service. The "
            "page says customer data is not sent to or processed by the GitHub "
            "Copilot service when agents run in Copilot Studio. The standard "
            "harness follows the topics and rules the maker defines. The "
            "Customer Conversation harness is described for customer voice and "
            "chat. Agents on the GitHub Copilot harness and the Customer "
            "Conversation harness use Copilot Credits. No price is stated on "
            "the overview. The linked billing pages were not opened. The "
            "overview did not use the word preview for the three harnesses."
        ),
    },
)

NOT_OPENED = (
    "UK GDPR Article 6",
    "UK GDPR Article 9",
    "UK GDPR Article 22A",
    "Equality Act 2010 section 29",
    "Equality Act 2010 Schedule 2",
    "PRIN 2A.2",
    "FG22/5",
    "DISP",
    "ATRS mandatory scope policy",
    "Dynamics 365 Customer Service knowledge-article product pages",
    "Microsoft Fabric product pages",
    "Usage-based billing for Copilot Studio",
    "Licensing for agents powered by the standard harness",
)
