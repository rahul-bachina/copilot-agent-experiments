"""Pinned pages for the promotions checklist.

The checker does not download these pages. A person opened them on
30 October 2026. Update last_verified only after opening the page again.
"""

from __future__ import annotations

LAST_VERIFIED = "2026-10-30"
DEFAULT_STALE_AFTER_DAYS = 90

# COBS 4.12A.11R(1)(d), Handbook page last updated 23 October 2025.
# The Handbook uses a typographic apostrophe. Comparison folds that to
# a straight apostrophe. The words are the Handbook's.
RISK_WARNING_CRYPTO = (
    "Don't invest unless you're prepared to lose all the money you invest. "
    "This is a high-risk investment and you should not expect to be protected "
    "if something goes wrong."
)
# COBS 4.12A.11R(2)(a), where a third-party marketing provider's character
# limit is exceeded. This checker cannot see that limit.
RISK_WARNING_CRYPTO_SHORT = (
    "Don't invest unless you're prepared to lose all the money you invest."
)
# COBS 4.12A.11R(1)(a), for non-readily realisable securities. Not the
# qualifying-cryptoasset warning. Recorded so a draft that uses it is not
# treated as (1)(d).
RISK_WARNING_NRR = (
    "Don't invest unless you're prepared to lose all the money you invest. "
    "This is a high-risk investment and you are unlikely to be protected "
    "if something goes wrong."
)
# COBS 4.12A.11R(3)(a)(i).
RISK_LINK_TEXT = "Take 2 mins to learn more."
# COBS 4.12A.20R(1)(b), apart from the client-name prefix.
PERSONALISED_RISK_CORE = (
    "this is a high-risk investment. How would you feel if you lost the "
    "money you're about to invest?"
)

SOURCES: list[dict] = [
    {
        "id": "fsma-s21",
        "title": "Financial Services and Markets Act 2000, section 21",
        "url": "https://www.legislation.gov.uk/ukpga/2000/8/section/21",
        "page_published": "2000-06-14",
        "page_last_updated": "2026-10-25",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Opened 30 October 2026. The page says section 21 is up to date "
            "with all changes known to be in force on or before 25 October 2026, "
            "and that there are changes that may be brought into force at a "
            "future date. Subsection (1) is the restriction. Subsection (2) is "
            "the authorised-person route and the approval route. Subsection (2A) "
            "says approval is only if permitted under section 55NA or within an "
            "exemption under section 55NB. Those two sections were not opened. "
            "The commencement note on (2A) says 7 February 2024 in so far as not "
            "already in force. Subsection (14) includes a cryptoasset in the "
            "meaning of investment."
        ),
    },
    {
        "id": "fsma-s25",
        "title": "Financial Services and Markets Act 2000, section 25",
        "url": "https://www.legislation.gov.uk/ukpga/2000/8/section/25",
        "page_published": "2000-06-14",
        "page_last_updated": "2024-02-07",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Opened 30 October 2026. Section 25(1)(b) is imprisonment for a "
            "term not exceeding two years, or a fine, or both, on conviction "
            "on indictment. This checker does not apply the offence or the "
            "defence in subsection (2)."
        ),
    },
    {
        "id": "fpo-26f",
        "title": "Financial Promotion Order 2005, Schedule 1, paragraph 26F",
        "url": "https://www.legislation.gov.uk/uksi/2005/1529/schedule/1/paragraph/26F",
        "page_published": "2005-06-15",
        "page_last_updated": "2026-02-25",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Opened 30 October 2026. The displayed text defines a qualifying "
            "cryptoasset as any cryptoasset which is fungible and transferable, "
            "subject to the exclusions in sub-paragraph (3). The textual note "
            "says the paragraph was substituted by SI 2026/102, 25 February 2026 "
            "for specified purposes, otherwise prospective. Those purposes were "
            "not opened. This checker does not decide that a product falls "
            "inside paragraph 26F."
        ),
    },
    {
        "id": "fpo-73za",
        "title": "Financial Promotion (Amendment) Order 2023, article 7 (article 73ZA as made)",
        "url": "https://www.legislation.gov.uk/uksi/2023/612/article/7/made",
        "page_published": "2023-06-07",
        "page_last_updated": "2023-06-07",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Opened 30 October 2026 as the original made text, not as a later "
            "consolidation of the 2005 Order. Article 73ZA(1) disapplies the "
            "financial promotion restriction for a communication which relates "
            "only to qualifying cryptoassets and is communicated by a registered "
            "person, or on behalf of one where it is non-real time and that "
            "person prepared the content. A registered person in article 73ZA(3) "
            "is an MLR cryptoasset exchange provider or custodian wallet provider "
            "on the FCA register, and not an authorised person. This checker "
            "does not decide that a firm is on that register."
        ),
    },
    {
        "id": "fca-marketing",
        "title": "Cryptoasset firms marketing to UK consumers",
        "url": "https://www.fca.org.uk/firms/cryptoassets/marketing-uk-consumers",
        "page_published": "2023-06-08",
        "page_last_updated": "2026-02-06",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "First published 8 June 2023, last updated 6 February 2026. Says "
            "the regime applies from 8 October 2023. Lists four routes. Still "
            "says legislation on a regulatory gateway for approvers was making "
            "its way through Parliament. This catalogue does not overwrite that "
            "sentence. PS23/6, FG23/3, and GC23/2 are named and were not opened. "
            "Experiment 04 pinned the same page on 24 October 2026."
        ),
    },
    {
        "id": "cobs-4-2",
        "title": "COBS 4.2 Fair, clear and not misleading communications",
        "url": "https://www.handbook.fca.org.uk/handbook/COBS/4/2.html",
        "page_published": None,
        "page_last_updated": "2025-10-23",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Handbook page last updated 23 October 2025. COBS 4.2.1R is the "
            "fair, clear and not misleading rule. COBS 4.2.5G names "
            "'guaranteed', 'protected' or 'secure', or a similar term. "
            "Flagging a word is not a decision that the term fails the guidance."
        ),
    },
    {
        "id": "cobs-4-12a",
        "title": "COBS 4.12A Promotion of restricted mass market investments",
        "url": "https://www.handbook.fca.org.uk/handbook/COBS/4/12A.html",
        "page_published": None,
        "page_last_updated": "2025-10-23",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Handbook page last updated 23 October 2025. A future version dated "
            "25 October 2027 is listed and was not opened. COBS 4.12A.7R is the "
            "incentive rule. COBS 4.12A.8G is the examples list on that page. "
            "COBS 4.12A.11R(1)(d) is the qualifying-cryptoasset risk warning. "
            "COBS 4.12A.15R to 4.12A.28R are the direct-offer conditions, "
            "including a cooling-off period of at least 24 hours. COBS 4 Annex "
            "1R, COBS 4.12A.36R, COBS 4.12A.38R, COBS 10, and COBS 10A were "
            "named and not opened. The glossary definition of direct offer "
            "financial promotion was not opened."
        ),
    },
    {
        "id": "fca-foi-alerts-2026",
        "title": "Information on crypto-related alerts - February 2026",
        "url": "https://www.fca.org.uk/freedom-information/information-crypto-related-alerts-february-2026",
        "page_published": "2026-02-20",
        "page_last_updated": "2026-02-20",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "FOI release 20 February 2026, case FOI2026/00006. For 1 January "
            "to 31 December 2025 the FCA issued 1,528 alerts with respect to "
            "unauthorised crypto entities and promotions, and 2,329 alerts in "
            "total. Context only. Not an input to a checklist row."
        ),
    },
]


def source_by_id() -> dict[str, dict]:
    """Return the catalogue keyed by source id."""
    return {source["id"]: source for source in SOURCES}
