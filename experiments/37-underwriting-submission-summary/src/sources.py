"""Pinned notes. Pages were opened on 5 November 2026 unless the note says otherwise.

The text here is a limit on what the starter may say. It is not a legal opinion
and it is not a finding that a presentation was fair or that a firm met the
Consumer Duty.
"""

from __future__ import annotations

from datetime import date
from typing import Any

LAST_VERIFIED = "2026-11-05"
DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "ia2015-s1",
        "title": "Insurance Act 2015, section 1",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/1",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. A non-consumer insurance contract is a contract "
            "of insurance that is not a consumer insurance contract. Consumer insurance "
            "contract has the same meaning as in the Consumer Insurance (Disclosure and "
            "Representations) Act 2012. That Act's text was not opened."
        ),
    },
    {
        "id": "ia2015-s2",
        "title": "Insurance Act 2015, section 2",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/2",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. Section 2(1): this Part applies to non-consumer "
            "insurance contracts only. Section 2(2) applies the Part to variations of "
            "those contracts, with the risk read as the changes relevant to the variation."
        ),
    },
    {
        "id": "ia2015-s3",
        "title": "Insurance Act 2015, section 3",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/3",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. Section 3(1): before a contract is entered into, "
            "the insured must make a fair presentation of the risk. Section 3(4) requires "
            "disclosure of every material circumstance the insured knows or ought to know, "
            "or, failing that, disclosure which gives the insurer sufficient information "
            "to put a prudent insurer on notice that it needs to make further enquiries. "
            "Section 3(5) lists circumstances that need not be disclosed in the absence "
            "of enquiry, including what the insurer knows, ought to know, or is presumed "
            "to know. This starter does not decide that a presentation was fair and it "
            "does not make those enquiries."
        ),
    },
    {
        "id": "ia2015-s5",
        "title": "Insurance Act 2015, section 5",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/5",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. Section 5 is the insurer's knowledge provision for "
            "section 3(5)(b) to (d). The insurer knows something only if it is known to "
            "an individual who participates in the decision whether to take the risk, and "
            "if so on what terms. What the insurer ought to know, and what it is presumed "
            "to know, are in subsections (2) and (3). This starter does not decide what "
            "the insurer knows."
        ),
    },
    {
        "id": "ia2015-s8",
        "title": "Insurance Act 2015, section 8",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/8",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. The insurer has a remedy for a breach of the duty "
            "of fair presentation only if it shows that, but for the breach, it would not "
            "have entered into the contract at all, or would have done so only on different "
            "terms. Remedies are in Schedule 1, which was not opened. This starter does "
            "not decide that a breach is qualifying and does not apply a remedy."
        ),
    },
    {
        "id": "ukgdpr-art5",
        "title": "UK GDPR, Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. Article 5(1) lists the principles, including purpose "
            "limitation, data minimisation, and accuracy. Article 5(1)(e) now refers to "
            "Article 84B. Article 5(3) was inserted by the Data (Use and Access) Act 2025. "
            "This starter does not choose an Article 6 basis."
        ),
    },
    {
        "id": "ukgdpr-art22",
        "title": "UK GDPR, Article 22",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. The article is shown as omitted. Chapter 3 Section 4A "
            "was substituted by the Data (Use and Access) Act 2025, section 80(1), in force "
            "for this purpose from 5 February 2026 (S.I. 2026/82). This starter does not "
            "quote a pre-substitution Article 22 as current law."
        ),
    },
    {
        "id": "ukgdpr-art22a",
        "title": "UK GDPR, Article 22A",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. Article 22A(1)(a): a decision is based solely on "
            "automated processing if there is no meaningful human involvement in the taking "
            "of the decision. Article 22A(1)(b): a significant decision produces a legal "
            "effect or a similarly significant effect. This starter does not take an "
            "underwriting decision and does not certify meaningful human involvement."
        ),
    },
    {
        "id": "prin-2a-1",
        "title": "FCA Handbook, PRIN 2A.1",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. The page says the Consumer Duty applies to a firm's "
            "retail market business, or where the firm communicates or approves a financial "
            "promotion addressed to, or likely to be received by, a retail customer. It "
            "says the application is set out in PRIN 3, including PRIN 3.2.6R to PRIN 3.2.12G. "
            "PRIN 3 was not opened. FG22/5 was named on the page and was not opened."
        ),
    },
    {
        "id": "prin-2a-2",
        "title": "FCA Handbook, PRIN 2A.2",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/2.html",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. The page states three cross-cutting obligations: a "
            "firm must act in good faith towards retail customers; a firm must avoid "
            "causing foreseeable harm to retail customers; a firm must enable and support "
            "retail customers to pursue their financial objectives. It says those rules "
            "exhaust what is required under Principle 12. This starter does not decide "
            "that a firm met them. The handbook markup did not show every rule number "
            "beside those three sentences, so the rule numbers are not repeated here."
        ),
    },
    {
        "id": "harness-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. The GitHub Copilot harness is a Copilot Studio "
            "authoring and orchestration framework, not the GitHub Copilot service. "
            "Customer data is not sent to or processed by the GitHub Copilot service when "
            "agents run in Copilot Studio. The page says this harness can take a goal, "
            "break it into steps, create and edit Word, Excel, PowerPoint, and PDF files, "
            "supports skills and memory, runs in a sandbox, and uses Copilot Credits. "
            "The billing overview linked from the table was not opened. The page did not "
            "mark the harness as preview."
        ),
    },
    {
        "id": "generative-orchestration",
        "title": "Generative orchestration guidance",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 5 November 2026. The page says the planner can invoke a topic when "
            "its described purpose matches the user's need, and also by trigger phrases. "
            "It says tool names carry more weight than descriptions. It does not describe "
            "numeric routing weights. Whether the GitHub Copilot harness uses this same "
            "planner was not stated on the harness overview. That link is unverified."
        ),
    },
    {
        "id": "schedule-1-not-opened",
        "title": "Insurance Act 2015, Schedule 1",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/schedule/1",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. Remedies are not described and are not applied.",
    },
    {
        "id": "cidra-not-opened",
        "title": "Consumer Insurance (Disclosure and Representations) Act 2012",
        "url": "https://www.legislation.gov.uk/ukpga/2012/6/contents",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. The consumer duty of reasonable care is not quoted.",
    },
    {
        "id": "prin-3-not-opened",
        "title": "FCA Handbook, PRIN 3",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/3/",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. Retail-market application is not decided here.",
    },
    {
        "id": "lloyds-not-opened",
        "title": "Lloyd's byelaws",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. No Lloyd's byelaw is applied. No syndicate is named.",
    },
    {
        "id": "foundry-not-opened",
        "title": "Microsoft Foundry",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "A product page was not opened for this experiment. Foundry is not called. UK region availability is unverified.",
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue boundary for B006",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Autonomy A0. The underwriter owns the coverage and pricing decision. This row is not a web page.",
    },
)


def pin_rows(as_of: str, stale_after_days: int) -> tuple[list[dict[str, Any]], bool]:
    as_of_date = date.fromisoformat(as_of)
    rows: list[dict[str, Any]] = []
    any_stale = False
    for source in SOURCES:
        stale = False
        age = None
        if source["stale_applicable"] and source["last_verified"]:
            verified = date.fromisoformat(source["last_verified"])
            age = (as_of_date - verified).days
            stale = age > stale_after_days or age < 0
        if stale:
            any_stale = True
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "stale_applicable": source["stale_applicable"],
                "reopened_for_this_experiment": source["reopened_for_this_experiment"],
                "stale": stale,
                "age_days": age,
                "note": source["note"],
            }
        )
    return rows, any_stale


def regulatory_notes(market_label: str) -> list[dict[str, Any]]:
    """Context only. Nothing here is a coverage decision or a compliance finding."""
    notes = [
        {
            "id": "ia2015-s3",
            "when": "The caller labelled the submission commercial_non_consumer.",
            "shown": market_label == "commercial_non_consumer",
            "text": (
                "Section 2(1) limits this Part to non-consumer insurance contracts. "
                "Section 3 is the duty of fair presentation. Section 5 is what the "
                "insurer knows, ought to know, or is presumed to know for section 3(5). "
                "Section 8 is the insurer's remedy, which this starter does not apply. "
                "A missing field is shown as not stated. That is not a finding that "
                "section 3(4) was or was not met, and it is not an enquiry to the broker."
            ),
        },
        {
            "id": "prin-2a",
            "when": "The caller labelled the submission retail.",
            "shown": market_label == "retail",
            "text": (
                "PRIN 2A.1, opened 5 November 2026, says the Consumer Duty applies to "
                "retail market business. PRIN 2A.2 states the three cross-cutting "
                "obligations and says they exhaust Principle 12. This starter does not "
                "decide that the firm is in retail market business, and it does not "
                "decide that the firm met the Duty. PRIN 3 was not opened."
            ),
        },
        {
            "id": "prin-2a-not-applied",
            "when": "The caller did not label the submission retail.",
            "shown": market_label != "retail",
            "text": (
                "PRIN 2A.1 says the Consumer Duty applies to retail market business. "
                "This starter does not apply those rules to a label other than retail, "
                "and it does not decide that the caller's label is correct. If the "
                "label is not stated, applicability is not stated."
            ),
        },
        {
            "id": "ukgdpr-art5-art22",
            "when": "Always, as a limit on this starter.",
            "shown": True,
            "text": (
                "Article 5 was read, including data minimisation and accuracy. This "
                "starter copies cited lines and does not fill a gap by inference. "
                "Article 22 was shown as omitted on 5 November 2026. Article 22A(1) "
                "defines a solely automated decision as one with no meaningful human "
                "involvement. Coverage and price stay with the underwriter. This "
                "starter does not certify meaningful human involvement."
            ),
        },
    ]
    return notes
