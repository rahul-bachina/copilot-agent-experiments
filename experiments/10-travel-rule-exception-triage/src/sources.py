"""Pinned sources for the Travel Rule checklist.

The triage does not download these pages. A person opened them on
26 October 2026. Update last_verified only after opening the page again.

The operative threshold is £800, from the revised text of regulations
64C(4) and 64G(1)(b). The August 2023 JMLSG annex still says 1,000 euros.
That euro figure is recorded here and is not used.
"""

from __future__ import annotations

LAST_VERIFIED = "2026-10-26"
DEFAULT_STALE_AFTER_DAYS = 90
THRESHOLD_GBP = 800

# Words printed in SI 2026/621 regulation 32 as the text being replaced.
# Not a number the checklist compares.
JMLSG_THRESHOLD_WORDS_NOT_USED = "1,000 euros"

SOURCES: list[dict] = [
    {
        "id": "mlr-part-7a",
        "title": "Money Laundering Regulations 2017, Part 7A (Cryptoasset transfers)",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/part/7A",
        "page_as_at": "2026-10-25",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Revised Part 7A, opened 26 October 2026. The page says it is up to "
            "date with all changes known to be in force on or before 25 October "
            "2026. Part 7A inserted (1.9.2023) by SI 2022/860, regs 1(3), 5(5). "
            "Regulations 64A to 64H were read. The sum in regulation 64C(4) and "
            "in regulation 64G(1)(b) is shown as £800, annotated as substituted "
            "on 30 June 2026 by SI 2026/621."
        ),
    },
    {
        "id": "si-2022-860",
        "title": "Money Laundering and Terrorist Financing (Amendment) (No. 2) Regulations 2022",
        "url": "https://www.legislation.gov.uk/uksi/2022/860/regulation/1",
        "page_as_at": "2022-07-21",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Made 21 July 2022 by the Treasury, under the Sanctions and "
            "Anti-Money Laundering Act 2018. Regulation 1(3): regulation 5 "
            "(cryptoasset transfers) comes into force on 1 September 2023. "
            "The introduction page was opened as well as regulation 1. This is "
            "the instrument the FCA statement calls HM Treasury's July 2022 amendments."
        ),
    },
    {
        "id": "si-2026-621-reg-32",
        "title": "Money Laundering and Terrorist Financing (Amendment) Regulations 2026, regulation 32",
        "url": "https://www.legislation.gov.uk/uksi/2026/621/regulation/32",
        "page_as_at": "2026-06-30",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Regulation 32: in regulation 64C(4), for '1,000 euros' substitute "
            "'£800'. Regulation 1 was opened. Regulation 32 is not in the list "
            "of provisions given a later commencement. The 30 June 2026 date is "
            "the legislation.gov.uk annotation on the revised Part 7A, not a "
            "date this repository calculated. Regulation 33 was not opened as a "
            "separate page. The revised regulation 64G(1)(b) shows the same £800 "
            "substitution."
        ),
    },
    {
        "id": "fca-travel-rule",
        "title": "FCA sets out expectations for UK cryptoasset businesses complying with the Travel Rule",
        "url": "https://www.fca.org.uk/news/statements/fca-sets-out-expectations-uk-cryptoasset-businesses-complying-travel-rule",
        "page_as_at": "2026-02-06",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "First published 17 August 2023, last updated 6 February 2026. "
            "Collect, verify and share from 1 September 2023. Firms remain "
            "responsible when using a third-party supplier. Sending to a "
            "jurisdiction without the Travel Rule: take all reasonable steps "
            "to establish whether the firm can receive the information; if it "
            "cannot, still collect and verify as required by the MLRs and store "
            "that information before making the transfer. Receiving from such a "
            "jurisdiction, where information is missing or incomplete: consider "
            "the countries and the Travel Rule status in a risk-based assessment "
            "of whether to make the cryptoassets available. The page does not "
            "say this waives regulation 64D. It does not use the word sunrise. "
            "The 1 September 2023 update says final guidance is on JMLSG's website."
        ),
    },
    {
        "id": "jmlsg-annex-i-2023",
        "title": "JMLSG Part II, Sector 22 Annex I, Cryptoasset transfers (Travel Rule), August 2023",
        "url": "https://www.jmlsg.org.uk/wp-content/uploads/2023/08/Board-approved_JMLSG-Guidance_Part-II-Sector-22-Annex-I_Aug2023.pdf",
        "page_as_at": "2023-08-01",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Board-approved PDF opened 26 October 2026. Paragraph 10 uses "
            "'sunrise issue' and tells firms to take account of FCA communications. "
            "Paragraphs 13 and 45 still say 1,000 euros. That figure is not the "
            "operative threshold. Paragraph 8 (same cryptoasset business) is not "
            "in regulation 64A as opened, so it is not applied. Paragraph 24 "
            "(a truncated name may have an explanation) is not used to clear a "
            "mismatch. Paragraph 33 (a return is not itself a Travel Rule "
            "transfer) is not applied as a statutory exclusion. Paragraph 38 "
            "points to a SAR. This agent does not draft or file one. No day "
            "count for 'reasonable time' was found."
        ),
    },
    {
        "id": "jmlsg-revisions",
        "title": "JMLSG revisions list",
        "url": "https://www.jmlsg.org.uk/revisions/",
        "page_as_at": "2026-09-01",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 26 October 2026. The August 2023 Sector 22 Annex I is still "
            "the annex listed. September 2026 entries are Part I paragraphs, "
            "marked awaiting HM Treasury approval. No later Annex I was listed. "
            "That is not proof that no other copy exists."
        ),
    },
    {
        "id": "jmlsg-hmt-approval",
        "title": "JMLSG: ministerial approval of Sector 22 guidance",
        "url": "https://www.jmlsg.org.uk/latest-news/ministerial-approval-of-jmlsg-guidance-6/",
        "page_as_at": None,
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 26 October 2026. Says HM Treasury ministerial approval has "
            "been received for Part II Sector 22, including Annex 1 on "
            "cryptoasset transfers. The fetched page did not show a publication "
            "date. The date is unverified."
        ),
    },
]


UNVERIFIED: list[dict] = [
    {
        "id": "reasonable-time",
        "statement": (
            "No number of days was found for 'a reasonable time' in regulation "
            "64D(2)(c)(ii), regulation 64E(2)(b)(ii), or the JMLSG paragraphs opened."
        ),
    },
    {
        "id": "jmlsg-approval-date",
        "statement": (
            "The JMLSG ministerial-approval page states that approval was "
            "received. It did not show a date when opened on 26 October 2026."
        ),
    },
    {
        "id": "jmlsg-annex-not-revised-for-800",
        "statement": (
            "The revisions page did not list an Annex I later than August 2023. "
            "That does not prove no other version exists. Paragraphs 13 and 45 "
            "of the PDF that was opened still say 1,000 euros."
        ),
    },
    {
        "id": "fca-statement-not-a-waiver",
        "statement": (
            "The FCA statement does not say that a sunrise receipt waives "
            "regulation 64D. This starter does not treat it as a waiver. "
            "Whether a court or the FCA would read it that way was not decided."
        ),
    },
    {
        "id": "regulation-14a-not-opened",
        "statement": (
            "Regulation 14A, which defines a cryptoasset exchange provider and "
            "a custodian wallet provider, was not opened. The checklist uses "
            "the Part 7A cross-reference and does not restate the definition."
        ),
    },
    {
        "id": "sanctions-and-poca-not-opened",
        "statement": (
            "The sanctions regime and the Proceeds of Crime Act 2002 were not "
            "opened. A firm marker is passed through as a reason to escalate. "
            "It is not a legal analysis, and it is not a suspicious activity report."
        ),
    },
    {
        "id": "three-working-days-not-calculated",
        "statement": (
            "Regulation 64B defines a working day using bank holidays in any "
            "part of the United Kingdom. That calendar is not encoded, so no "
            "due date is returned for regulation 64C(2)."
        ),
    },
    {
        "id": "harness-licensing-beyond-overview",
        "statement": (
            "The Copilot Studio harness overview was opened on 26 October 2026. "
            "The separate billing and standard-harness licensing articles were "
            "not re-opened that day. Licence coverage beyond the overview is unverified."
        ),
    },
]


def source_by_id() -> dict[str, dict]:
    """Return the catalogue keyed by source id."""
    return {source["id"]: source for source in SOURCES}
