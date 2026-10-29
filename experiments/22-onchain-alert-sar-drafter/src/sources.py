"""Pages opened on 29 October 2026.

The investigation does not download these pages. Update last_verified only
after opening the page again.

The Proceeds of Crime Act pages warn that revised legislation on
legislation.gov.uk may not be fully up to date. No "in force on or before"
date was on the section 330, 331, or 333A extracts. The Money Laundering
Regulations pages say they are up to date with all changes known to be in
force on or before 25 October 2026.

Not opened, and not applied: sections 333B, 333C, 333D, 335, 336, 338, 339,
339A, and 342; Terrorism Act 2000 Part 3 and section 21D; UKFIU chapter 3;
the SAR glossary; the NCA suspicious-activity-reports HTML page (the fetch
timed out); the Financial Crime Guide; JMLSG; Schedule 9 to the 2002 Act.
"""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-10-29"
SOURCES_PINNED_ON = date(2026, 10, 29)
DEFAULT_STALE_AFTER_DAYS = 90
UKFIU_REASON_CHAR_LIMIT = 8000

QUOTES = {
    "poca_330_2": (
        "knows or suspects, or has reasonable grounds for knowing or suspecting, "
        "that another person is engaged in money laundering"
    ),
    "poca_330_4": (
        "does not make the required disclosure to a nominated officer, or to a "
        "person authorised for the purposes of this Part by the Director General "
        "of the National Crime Agency, as soon as is practicable"
    ),
    "poca_331_1": "A person nominated to receive disclosures under section 330",
    "poca_331_5": (
        "The required disclosure is a disclosure of the identity of the other "
        "person, if disclosed to him under section 330, the whereabouts of the "
        "laundered property, so far as disclosed to him under section 330, and "
        "the information or other matter"
    ),
    "poca_333a_1": (
        "the disclosure is likely to prejudice any investigation that might be "
        "conducted following the disclosure referred to in that subsection"
    ),
    "poca_333a_3": (
        "the person discloses that an investigation into allegations that an "
        "offence under this Part has been committed is being contemplated or "
        "is being carried out"
    ),
    "mlr_19_4_d": (
        "anyone in the relevant person's organisation who knows or suspects "
        "(or has reasonable grounds for knowing or suspecting) that a person "
        "is engaged in money laundering or terrorist financing"
    ),
    "mlr_19_4_a": (
        "a transaction is unusually complex or unusually large in each case "
        "given the nature of the transaction, or there is an unusual pattern "
        "of transactions, or the transaction or transactions have no apparent "
        "economic or legal purpose"
    ),
    "mlr_21_3": "An individual in the relevant person's firm must be appointed as a nominated officer.",
    "mlr_21_5": (
        "that officer must consider it in the light of any relevant information "
        "which is available to the relevant person and determine whether it "
        "gives rise to knowledge or suspicion or reasonable grounds for "
        "knowledge or suspicion"
    ),
    "fca_onchain_tool": (
        "selected and configured or built in house a fiat (off-chain) and "
        "cryptoasset (on-chain) transaction monitoring tool"
    ),
    "fca_rules_thresholds": (
        "You must submit the rules and thresholds that you have set within these tools"
    ),
    "fca_no_endorsement": "The FCA cannot recommend or endorse any tool",
    "fca_sar_route": (
        "a clear route of escalation internally to the MLRO/Nominated Officer "
        "as well as externally to the National Crime Agency"
    ),
    "fca_marc_onchain": (
        "narrowing the on-chain monitoring requirement for large UK QCATPs"
    ),
}

NOT_OPENED = (
    "POCA sections 333B, 333C, 333D, 335, 336, 338, 339, 339A, and 342",
    "Terrorism Act 2000 Part 3 and section 21D",
    "UKFIU chapter 3 (defences)",
    "The SAR glossary on the SAR Portal",
    "The NCA suspicious-activity-reports HTML page",
    "The FCA Financial Crime Guide",
    "JMLSG guidance",
    "Schedule 9 to the Proceeds of Crime Act 2002",
)

SOURCES = [
    {
        "id": "poca-2002-s330",
        "title": "Proceeds of Crime Act 2002, section 330 (failure to disclose: regulated sector)",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/330",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": None,
        "notes": (
            "Opened 29 October 2026. The page warns that revised legislation "
            "may not be fully up to date. The extract did not give an "
            "'in force on or before' date."
        ),
    },
    {
        "id": "poca-2002-s331",
        "title": "Proceeds of Crime Act 2002, section 331 (nominated officers in the regulated sector)",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/331",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": None,
        "notes": "Opened 29 October 2026. Same currency warning as section 330.",
    },
    {
        "id": "poca-2002-s333a",
        "title": "Proceeds of Crime Act 2002, section 333A (tipping off: regulated sector)",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/333A",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": None,
        "notes": (
            "Opened 29 October 2026. Subsections (1) and (3) both require that "
            "the disclosure is likely to prejudice an investigation. Subsection (5) "
            "names sections 333B, 333C, and 333D. Those sections were not opened."
        ),
    },
    {
        "id": "mlr-2017-reg-19",
        "title": "Money Laundering Regulations 2017, regulation 19 (policies, controls and procedures)",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/regulation/19",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": "2026-10-25",
        "notes": (
            "Opened 29 October 2026. The page says regulation 19 is up to date "
            "with all changes known to be in force on or before 25 October 2026."
        ),
    },
    {
        "id": "mlr-2017-reg-21",
        "title": "Money Laundering Regulations 2017, regulation 21 (internal controls)",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/regulation/21",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": "2026-10-25",
        "notes": (
            "Opened 29 October 2026. The page says regulation 21 is up to date "
            "with all changes known to be in force on or before 25 October 2026. "
            "Paragraph (3) appoints the nominated officer. Paragraph (5) is the "
            "officer's determination."
        ),
    },
    {
        "id": "fca-mlr-application",
        "title": "Cryptoassets: what we expect to see in an application for registration",
        "url": "https://www.fca.org.uk/firms/cryptoassets/application-registration",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": "2026-06-30",
        "notes": (
            "Opened 29 October 2026. First published 22 March 2023, last updated "
            "30 June 2026. Expects an on-chain and an off-chain monitoring tool, "
            "with the rules and thresholds submitted. Says the FCA cannot "
            "recommend or endorse any tool. Expects a SAR route to the nominated "
            "officer and to the National Crime Agency, and a reference to tipping "
            "off and to DAML or DATF circumstances. Experiment 04 pinned the same "
            "URL on 24 October 2026. This experiment does not re-score that pack."
        ),
    },
    {
        "id": "fca-regime-overview",
        "title": "Overview of our cryptoassets regime policy statements",
        "url": "https://www.fca.org.uk/publications/policy-statements/cryptoasset-regime",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": "2026-06-30",
        "notes": (
            "Opened 29 October 2026. Published and last updated 30 June 2026. "
            "The MARC paragraph says the on-chain monitoring requirement for "
            "large UK QCATPs was narrowed. That sentence is market abuse, not "
            "the AML monitoring expectation on the registration page. The page "
            "says the FCA plans to consult on Financial Crime Guide updates. "
            "The guide was not opened, and a later consultation was not checked."
        ),
    },
    {
        "id": "ukfiu-chapter-2",
        "title": "UKFIU SARs best practice, chapter 2: submitting a SAR",
        "url": "https://www.nationalcrimeagency.gov.uk/who-we-are/publications/775-ukfiu-chapter-2-submitting-a-sar/file",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": "2025-12",
        "notes": (
            "Opened 29 October 2026. The file is marked version 1.1, December 2025. "
            "The reason-for-suspicion field is limited to 8,000 characters. The "
            "chapter asks who is involved, how, when, and why, and asks for a "
            "description of the property, including a sterling figure where the "
            "property is cryptocurrency. Glossary codes are selected in the portal. "
            "The glossary was not opened. The chapter says reporters must be "
            "mindful of tipping off. Chapter 3 was not opened."
        ),
    },
    {
        "id": "copilot-studio-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "page_as_at": None,
        "notes": (
            "Opened 29 October 2026. Describes the GitHub Copilot harness, the "
            "Customer Conversation harness, and the standard harness. The GitHub "
            "Copilot harness is a Copilot Studio authoring and orchestration "
            "framework, not the GitHub Copilot service. Agents on it use Copilot "
            "Credits. This experiment does not use the Customer Conversation harness."
        ),
    },
]


def source_rows(as_of: date, stale_after_days: int) -> list[dict]:
    """Currency of each pin. Equal to the threshold is not stale."""

    rows = []
    for source in SOURCES:
        verified = date.fromisoformat(source["last_verified"])
        stale = (as_of - verified).days > stale_after_days
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "page_as_at": source["page_as_at"],
                "body_opened": source["body_opened"],
                "stale": stale,
                "applied_as_a_decision": False,
            }
        )
    return rows
