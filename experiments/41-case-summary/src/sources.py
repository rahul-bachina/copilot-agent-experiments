"""Pages opened for Experiment 41. The summariser does not fetch them again.

`last_verified` is the day the page was opened. A later as-of date can mark a
row stale. A page that was not opened is not stale-tested and is not quoted.
"""

from __future__ import annotations

SOURCES: tuple[dict, ...] = (
    {
        "id": "uk-gdpr-article-5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "last_verified": "2026-11-09",
        "opened": True,
        "stale_applicable": True,
        "note": (
            "Opened on 9 November 2026. Article 5(1)(a) is lawfulness, fairness and transparency. "
            "Article 5(1)(c) is data minimisation: adequate, relevant and limited to what is necessary. "
            "Article 5(1)(d) is accuracy: accurate and, where necessary, kept up to date, and every "
            "reasonable step must be taken to erase or rectify inaccurate personal data without delay. "
            "Article 5(2) is accountability. Article 5(3) says processing is not lawful by virtue only "
            "of being compatible with the purposes for which the personal data was collected. "
            "This starter does not erase or rectify a record, and it does not choose a lawful basis."
        ),
    },
    {
        "id": "uk-gdpr-article-22",
        "title": "UK GDPR Article 22",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22",
        "last_verified": "2026-11-09",
        "opened": True,
        "stale_applicable": True,
        "note": (
            "Opened on 9 November 2026. The article page showed Article 22 omitted. "
            "The textual amendment says Chapter 3 Section 4A was substituted for Article 22 "
            "by the Data (Use and Access) Act 2025, section 80(1), for specified purposes on "
            "19 June 2025 and otherwise on 5 February 2026 by S.I. 2026/82, regulation 2(j). "
            "The S.I. text was not opened. This starter does not quote a pre-substitution Article 22."
        ),
    },
    {
        "id": "uk-gdpr-article-22a",
        "title": "UK GDPR Article 22A",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
        "last_verified": "2026-11-09",
        "opened": True,
        "stale_applicable": True,
        "note": (
            "Opened on 9 November 2026. Article 22A(1) says a decision is based solely on automated "
            "processing if there is no meaningful human involvement in the taking of the decision, "
            "and a decision is significant if it produces a legal effect or a similarly significant "
            "effect. Article 22A(2) says that, when considering meaningful human involvement, a person "
            "must consider, among other things, the extent to which the decision is reached by means "
            "of profiling. This starter does not certify that involvement."
        ),
    },
    {
        "id": "duaa-section-80",
        "title": "Data (Use and Access) Act 2025, section 80",
        "url": "https://www.legislation.gov.uk/ukpga/2025/18/section/80",
        "last_verified": "2026-11-09",
        "opened": True,
        "stale_applicable": True,
        "note": (
            "Opened on 9 November 2026. Section 80(1) substitutes Articles 22A to 22D. "
            "The substituted text of Articles 22B, 22C, and 22D was read on that page. "
            "Separate article pages for 22B, 22C, and 22D were not opened. "
            "Article 22C(2) lists information, representations, human intervention, and contesting "
            "a decision. Article 22D allows regulations. No regulations under Article 22D were opened. "
            "Section 80(3) substitutes Data Protection Act 2018 sections 50A to 50D for law-enforcement "
            "processing. This starter does not apply that regime. "
            "The page says section 80 is in force on 5 February 2026 so far as not already in force, "
            "by S.I. 2026/82, regulation 2(j). The S.I. text was not opened."
        ),
    },
    {
        "id": "ico-ai-accuracy",
        "title": "ICO, What do we need to know about accuracy and statistical accuracy?",
        "url": (
            "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/"
            "artificial-intelligence/guidance-on-ai-and-data-protection/"
            "what-do-we-need-to-know-about-accuracy-and-statistical-accuracy/"
        ),
        "last_verified": None,
        "opened": False,
        "stale_applicable": False,
        "note": (
            "Requested on 9 November 2026. The site returned HTTP 403 behind a Cloudflare challenge. "
            "The page was not read. No sentence from it is quoted. A search result listed this URL. "
            "A search snippet is not the page. Unverified."
        ),
    },
    {
        "id": "copilot-studio-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": "2026-11-09",
        "opened": True,
        "stale_applicable": True,
        "note": (
            "Opened on 9 November 2026. The GitHub Copilot harness is a Microsoft Copilot Studio "
            "authoring and orchestration framework, not the GitHub Copilot service. The standard "
            "harness follows the topics and rules the maker defines. The Customer Conversation "
            "harness is for customer voice and chat. Agents on the GitHub Copilot harness and the "
            "Customer Conversation harness use Copilot Credits. The overview did not mark the "
            "harness as preview. Linked billing pages were not opened. No price is copied."
        ),
    },
)

PIN_WINDOW_DAYS = 90
