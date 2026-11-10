"""Pages opened on 10 November 2026. The core does not download them again."""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-11-10"

SOURCES: tuple[dict, ...] = (
    {
        "id": "cra2015-s49",
        "title": "Consumer Rights Act 2015, section 49",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/49",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 49(1): every contract to supply a service "
            "is to be treated as including a term that the trader must perform the service "
            "with reasonable care and skill. Section 49(2) points to section 54. This "
            "starter does not decide that the term was met."
        ),
    },
    {
        "id": "cra2015-s50",
        "title": "Consumer Rights Act 2015, section 50",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/50",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 50(1): information said or written to the "
            "consumer about the trader or the service is treated as included as a term if "
            "the consumer takes it into account when deciding to enter the contract, or "
            "when making any decision about the service after entering into the contract. "
            "Section 50(2) subjects that to anything that qualified it on the same occasion "
            "and to any change expressly agreed. This starter does not decide what was "
            "taken into account."
        ),
    },
    {
        "id": "cra2015-s52",
        "title": "Consumer Rights Act 2015, section 52",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/52",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 52(2): where the contract does not fix the "
            "time, and nor does information treated as included under section 50, the "
            "contract is treated as including a term that the trader must perform the "
            "service within a reasonable time. Section 52(3): what is a reasonable time "
            "is a question of fact. This starter does not answer that question."
        ),
    },
    {
        "id": "cra2015-s54",
        "title": "Consumer Rights Act 2015, section 54",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/54",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 54(3): if the service does not conform to "
            "the contract, the consumer's rights are the right to require repeat "
            "performance and the right to a price reduction. Sections 55 and 56 were not "
            "opened, so they are not quoted."
        ),
    },
    {
        "id": "cra2015-s57",
        "title": "Consumer Rights Act 2015, section 57",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/57",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 57(1): a term of a contract to supply a "
            "service is not binding on the consumer to the extent that it would exclude "
            "the trader's liability arising under section 49. Section 57(3) also refers "
            "to sections 51 and 52. Section 51 was not opened. This starter does not "
            "decide that a term is not binding."
        ),
    },
    {
        "id": "cra2015-s62",
        "title": "Consumer Rights Act 2015, section 62",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/62",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 62(1): an unfair term of a consumer contract "
            "is not binding on the consumer. Section 62(4): a term is unfair if, contrary "
            "to the requirement of good faith, it causes a significant imbalance in the "
            "parties' rights and obligations under the contract to the detriment of the "
            "consumer. This starter does not assess fairness."
        ),
    },
    {
        "id": "cra2015-s64",
        "title": "Consumer Rights Act 2015, section 64",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/64",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 64(1) and (2): a term may not be assessed "
            "for fairness under section 62 to the extent that it specifies the main "
            "subject matter, or the assessment is of the appropriateness of the price, "
            "only if the term is transparent and prominent. Section 64(3): a term is "
            "transparent if it is expressed in plain and intelligible language and, in "
            "the case of a written term, is legible. Schedule 2 was not opened. This "
            "starter does not decide that a term is transparent or prominent."
        ),
    },
    {
        "id": "cra2015-s68",
        "title": "Consumer Rights Act 2015, section 68",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/68",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 68(1): a trader must ensure that a written "
            "term of a consumer contract, or a consumer notice in writing, is transparent. "
            "Section 68(2): a consumer notice is transparent if it is expressed in plain "
            "and intelligible language and is legible. This starter does not decide that "
            "section 68 was met."
        ),
    },
    {
        "id": "cra2015-s69",
        "title": "Consumer Rights Act 2015, section 69",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/69",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Section 69(1): if a term in a consumer contract, or "
            "a consumer notice, could have different meanings, the meaning that is most "
            "favourable to the consumer is to prevail. This starter does not choose a "
            "meaning and does not apply section 69."
        ),
    },
    {
        "id": "ukgdpr-art5",
        "title": "UK GDPR, Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Article 5(1)(a) lawfulness, fairness and "
            "transparency. Article 5(1)(c) data minimisation. Article 5(1)(d) accuracy. "
            "Article 5(3): processing is not lawful by virtue only of being compatible "
            "with the purposes for which the personal data was collected. Article 6 was "
            "not opened. No lawful basis is chosen."
        ),
    },
    {
        "id": "ukgdpr-art12",
        "title": "UK GDPR, Article 12",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/12",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Article 12(1): the controller shall take appropriate "
            "measures to provide information referred to in Articles 13 and 14, and "
            "communication under Articles 15 to 22D, in a concise, transparent, "
            "intelligible and easily accessible form, using clear and plain language. "
            "Articles 13 and 14 were not opened. This starter does not decide that "
            "Article 12 was met."
        ),
    },
    {
        "id": "ukgdpr-art22a",
        "title": "UK GDPR, Article 22A",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. Article 22A(1)(a): a decision is based solely on "
            "automated processing if there is no meaningful human involvement in the "
            "taking of the decision. Article 22A(1)(b): a significant decision produces "
            "a legal effect or a similarly significant effect for the data subject. The "
            "page records that Chapter 3 Section 4A was substituted for Article 22 by "
            "the Data (Use and Access) Act 2025, section 80(1). The section 80 page was "
            "not opened. Article 22 was not re-opened. This starter does not take a "
            "significant decision and does not certify meaningful human involvement."
        ),
    },
    {
        "id": "prin-2a-5",
        "title": "FCA Handbook, PRIN 2A.5",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/5.html",
        "last_verified": LAST_VERIFIED,
        "verified": False,
        "relevant_sectors": ("financial_services",),
        "note": (
            "Requested 10 November 2026. The response said JavaScript is required and "
            "did not return the rule text. Unverified on this open. Experiment 38 "
            "recorded a reading on 6 November 2026. That reading is not re-quoted here. "
            "This starter does not decide that the consumer-understanding outcome was met."
        ),
    },
    {
        "id": "harness-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "verified": True,
        "relevant_sectors": ("home_services", "telecoms", "financial_services", "public_service"),
        "note": (
            "Opened 10 November 2026. The page names three harnesses: GitHub Copilot, "
            "Customer Conversation, and standard. The GitHub Copilot harness is a "
            "Microsoft Copilot Studio authoring and orchestration framework, not the "
            "GitHub Copilot service. Customer data is not sent to or processed by the "
            "GitHub Copilot service when agents run in Copilot Studio. Agents on the "
            "GitHub Copilot harness and the Customer Conversation harness use Copilot "
            "Credits. The linked billing pages were not opened, so no price is stated. "
            "The page did not mark the harness as preview. The generative-orchestration "
            "guidance page was not opened. This starter does not assign routing weights."
        ),
    },
)


def assess(as_of: date | None, stale_after_days: int, sector: str | None) -> dict:
    """Mark each pin. An unverified pin is not relied on. Age uses the as-of date."""
    rows = []
    any_stale = False
    relevant_unreliable = False
    for source in SOURCES:
        relevant = sector in source["relevant_sectors"] if sector else False
        verified = bool(source["verified"])
        stale = False
        if as_of is None or not verified:
            do_not_rely = True
        else:
            verified_on = date.fromisoformat(source["last_verified"])
            age = (as_of - verified_on).days
            stale = age < 0 or age > stale_after_days
            do_not_rely = stale
        if stale and relevant:
            any_stale = True
        if relevant and do_not_rely:
            relevant_unreliable = True
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "verified": verified,
                "relevant": relevant,
                "stale": stale,
                "do_not_rely": do_not_rely,
            }
        )
    return {
        "any_relevant_source_stale": any_stale,
        "relevant_sources_unreliable": relevant_unreliable,
        "pins": rows,
    }
