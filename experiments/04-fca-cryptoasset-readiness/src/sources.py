"""Pinned FCA pages for the gap register.

The checker does not download these pages. A person opened them on
24 October 2026. Update last_verified only after opening the page again.
"""

from __future__ import annotations

LAST_VERIFIED = "2026-10-24"
DEFAULT_STALE_AFTER_DAYS = 90
DEFAULT_DOCUMENT_STALE_AFTER_DAYS = 365

APPLICATION_WINDOW_OPENS = "2026-09-30"
APPLICATION_WINDOW_CLOSES = "2027-02-28"
REGIME_COMMENCEMENT = "2027-10-25"

SOURCES: list[dict] = [
    {
        "id": "fca-regime-overview",
        "title": "Overview of our cryptoassets regime policy statements",
        "url": "https://www.fca.org.uk/publications/policy-statements/cryptoasset-regime",
        "page_published": "2026-06-30",
        "page_last_updated": "2026-06-30",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Published and last updated 30 June 2026. Names PS26/9 to PS26/13, "
            "FG26/5, FG26/6, FG26/7, GC26/4 and GC26/5, and the sourcebooks "
            "CRYPTO 2 to CRYPTO 10, CASS 7, CASS 16, CASS 17, COREPRU and CRYPTOPRU. "
            "Those PDFs and the Handbook were not opened. The page says the full "
            "scope of regulated activities expands from 25 October 2027, that "
            "existing registrations will not convert automatically, and that the "
            "application window is scheduled to open on 30 September 2026 and close "
            "on 28 February 2027 for firms that wish to rely on the savings provisions. "
            "The later gateway page is more specific about saving and transitional provisions."
        ),
    },
    {
        "id": "fca-mlr-application",
        "title": "Cryptoassets: what we expect to see in an application for registration",
        "url": "https://www.fca.org.uk/firms/cryptoassets/application-registration",
        "page_published": "2023-03-22",
        "page_last_updated": "2026-06-30",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "First published 22 March 2023, last updated 30 June 2026. States that "
            "the new regime starts on 25 October 2027. Describes BWRA, CRA, CDD, "
            "on-chain and off-chain monitoring rules and thresholds, Travel Rule "
            "procedures and a flow of funds, a financial promotions policy, and the "
            "MLRO. Says registering under the MLRs does not of itself subject the "
            "firm to SM&CR. Regulation numbers below are the numbers this page uses. "
            "This checker does not interpret the MLRs."
        ),
    },
    {
        "id": "fca-gateway",
        "title": "Cryptoassets: how the gateway will operate",
        "url": "https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/how-gateway-will-operate",
        "page_published": "2026-01-08",
        "page_last_updated": "2026-09-30",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Last updated 30 September 2026. Says the application period started on "
            "30 September 2026 and will close on 28 February 2027, as set out in the "
            "FCA's direction. Says MLR registration will not convert automatically. "
            "Distinguishes firms that apply during the period (saving provision if "
            "the application is not determined by commencement), firms that apply "
            "outside the period but before commencement (transitional provision: "
            "pre-existing contracts only, no new UK contracts), and firms that do "
            "not apply (run off before commencement, no saving or transitional provision). "
            "The s.21 approvers page named here was not opened."
        ),
    },
    {
        "id": "fca-what-you-need-to-do",
        "title": "What you need to do when preparing for the new cryptoasset regulatory regime",
        "url": "https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation/what-you-need-to-do",
        "page_published": "2026-04-30",
        "page_last_updated": "2026-09-16",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Last updated 16 September 2026. Says the application period is open from "
            "30 September 2026 to 28 February 2027, and that the regime starts on "
            "25 October 2027 when the Financial Services and Markets Act 2000 "
            "(Cryptoassets) Regulations 2026 take effect. Encourages firms to carry "
            "out a gap analysis. That sentence is the FCA's, not a claim that this tool performs it."
        ),
    },
    {
        "id": "fca-regime-landing",
        "title": "A new regime for cryptoasset regulation",
        "url": "https://www.fca.org.uk/firms/new-regime-cryptoasset-regulation",
        "page_published": "2026-01-08",
        "page_last_updated": "2026-09-30",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Last updated 30 September 2026. Says the Financial Services and Markets "
            "Act 2000 (Cryptoassets) Regulations 2026 were made on 4 February 2026, "
            "and that the new regime is expected to come into force on 25 October 2027. "
            "The word expected is the landing page's. The what-you-need-to-do page says starts."
        ),
    },
    {
        "id": "fca-ps26-18",
        "title": "PS26/18: Cryptoasset perimeter guidance",
        "url": "https://www.fca.org.uk/publications/policy-statements/ps26-18-cryptoasset-perimeter-guidance",
        "page_published": "2026-09-16",
        "page_last_updated": "2026-09-16",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "Policy statement page published 16 September 2026. The PDF was not opened. "
            "The page says that from 25 October 2027 the Cryptoassets Regulations "
            "introduce new regulated activities, that existing registrations and "
            "permissions will not convert automatically, and that the application "
            "window opens on 30 September 2026 and closes on 28 February 2027 for "
            "firms wanting to use the transitional arrangements. It also says the FCA "
            "plans to consult on further perimeter guidance in late 2026."
        ),
    },
    {
        "id": "fca-travel-rule",
        "title": "FCA sets out expectations for UK cryptoasset businesses complying with the Travel Rule",
        "url": "https://www.fca.org.uk/news/statements/fca-sets-out-expectations-uk-cryptoasset-businesses-complying-travel-rule",
        "page_published": "2023-08-17",
        "page_last_updated": "2026-02-06",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "pdf_opened": False,
        "notes": (
            "First published 17 August 2023, last updated 6 February 2026. Says that "
            "from 1 September 2023 UK cryptoasset businesses will be required to "
            "collect, verify and share information about cryptoasset transfers. "
            "Cites Part 7A of the MLRs. Says firms remain responsible when using "
            "third-party suppliers, and sets expectations for jurisdictions where "
            "the Travel Rule is not in force. JMLSG guidance is mentioned and is "
            "not an FCA page, so it is not a source in this catalogue."
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
            "Last updated 6 February 2026. Says the financial promotions regime "
            "applies from 8 October 2023, lists four communication routes, and says "
            "promotions must be fair, clear and not misleading, with risk warnings "
            "and a 24-hour cooling-off period. Names PS23/6 and FG23/3. Those "
            "documents were not opened. The page still describes GC23/2 as a "
            "guidance consultation and still says legislation on a promotions "
            "gateway was before Parliament. This catalogue does not overwrite that sentence."
        ),
    },
]


def source_by_id() -> dict[str, dict]:
    """Return the catalogue keyed by source id."""
    return {source["id"]: source for source in SOURCES}


KEY_DATES: list[dict] = [
    {
        "id": "application-window",
        "opens": APPLICATION_WINDOW_OPENS,
        "closes": APPLICATION_WINDOW_CLOSES,
        "source_ids": [
            "fca-gateway",
            "fca-what-you-need-to-do",
            "fca-ps26-18",
            "fca-regime-overview",
        ],
        "statement": (
            "The gateway page, last updated 30 September 2026, says the application "
            "period started on 30 September 2026 and will close on 28 February 2027. "
            "The what-you-need-to-do page says the period is open across those dates. "
            "PS26/18 uses the same dates for firms wanting to use the transitional "
            "arrangements. The 30 June 2026 overview says the window is scheduled to "
            "open and close on those dates for the savings provisions."
        ),
    },
    {
        "id": "regime-commencement",
        "date": REGIME_COMMENCEMENT,
        "source_ids": [
            "fca-what-you-need-to-do",
            "fca-regime-landing",
            "fca-regime-overview",
            "fca-ps26-18",
            "fca-mlr-application",
        ],
        "statement": (
            "The what-you-need-to-do page says the regime starts on 25 October 2027, "
            "when the Financial Services and Markets Act 2000 (Cryptoassets) "
            "Regulations 2026 take effect. The regime landing page says the regime "
            "is expected to come into force on that date. PS26/18 says the "
            "Regulations will introduce the new activities from that date. "
            "This checker pins the date and does not choose between starts and expected."
        ),
    },
    {
        "id": "no-automatic-conversion",
        "source_ids": ["fca-gateway", "fca-regime-overview", "fca-ps26-18"],
        "statement": (
            "The gateway page, the 30 June 2026 overview, and PS26/18 each say that "
            "existing registrations do not convert automatically into FSMA permission."
        ),
    },
    {
        "id": "travel-rule-in-force",
        "date": "2023-09-01",
        "source_ids": ["fca-travel-rule"],
        "statement": (
            "The Travel Rule statement says that from 1 September 2023 UK cryptoasset "
            "businesses will be required to collect, verify and share information "
            "about cryptoasset transfers."
        ),
    },
    {
        "id": "financial-promotions-regime",
        "date": "2023-10-08",
        "source_ids": ["fca-marketing"],
        "statement": (
            "The marketing page says cryptoasset firms marketing to UK consumers "
            "need to comply with the financial promotions regime from 8 October 2023."
        ),
    },
]
