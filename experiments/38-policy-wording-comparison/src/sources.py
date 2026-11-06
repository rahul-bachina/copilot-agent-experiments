"""Pinned notes. Pages were opened on 6 November 2026 unless the note says otherwise.

The text here is a limit on what the starter may say. It is not a coverage
opinion, a favourability finding, or a finding that a firm met the Consumer Duty.
"""

from __future__ import annotations

from datetime import date
from typing import Any

LAST_VERIFIED = "2026-11-06"
DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "ia2015-s2",
        "title": "Insurance Act 2015, section 2",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/2",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 2(1): this Part applies to non-consumer "
            "insurance contracts only. Section 2(2) applies the Part to variations of "
            "those contracts. This starter does not decide that a contract is non-consumer."
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
            "Opened 6 November 2026. Section 3(1) is the duty of fair presentation before "
            "the contract is entered into. Section 3(3)(b) requires disclosure in a manner "
            "which would be reasonably clear and accessible to a prudent insurer. Section "
            "3(4) is the disclosure, including section 3(4)(b), the notice that a prudent "
            "insurer needs to make further enquiries. This comparison does not decide that "
            "a presentation was fair and it does not make those enquiries."
        ),
    },
    {
        "id": "ia2015-s9",
        "title": "Insurance Act 2015, section 9",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/9",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 9 applies to representations by the insured "
            "in connection with a proposed non-consumer insurance contract or variation. "
            "Such a representation is not capable of being converted into a warranty by "
            "any provision of the contract, including by declaring the representation to "
            "form the basis of the contract. This starter records whether those words "
            "appear in a cited span. It does not decide that a clause is of no effect."
        ),
    },
    {
        "id": "ia2015-s10",
        "title": "Insurance Act 2015, section 10",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/10",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 10(1) abolishes the rule that breach of a "
            "warranty discharges the insurer's liability. Section 10(2) suspends liability "
            "for loss after a breach and before remedy, subject to subsection (3). This "
            "starter does not decide that a warranty was breached or that liability is suspended."
        ),
    },
    {
        "id": "ia2015-s11",
        "title": "Insurance Act 2015, section 11",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/11",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 11 applies to a term, other than a term "
            "defining the risk as a whole, if compliance would tend to reduce the risk of "
            "loss of a particular kind, at a particular location, or at a particular time. "
            "The insurer may not rely on non-compliance for the actual loss if the insured "
            "shows the non-compliance could not have increased the risk of that loss. This "
            "starter does not apply section 11 to a cited clause."
        ),
    },
    {
        "id": "ia2015-s16",
        "title": "Insurance Act 2015, section 16",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/16",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 16(1): a term that would put the insured in "
            "a worse position as respects representations to which section 9 applies is of "
            "no effect to that extent. Section 16(2): a term that would put the insured in "
            "a worse position as respects the other matters in Parts 2, 3, or 4 is of no "
            "effect unless section 17 has been satisfied. This starter does not decide that "
            "a term puts the insured in a worse position."
        ),
    },
    {
        "id": "ia2015-s17",
        "title": "Insurance Act 2015, section 17",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/17",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 17(1) defines the disadvantageous term by "
            "reference to section 16(2), and the page shows an amendment pointing at "
            "section 16A(4). Section 16A was not opened. Section 17(2): the insurer must "
            "take sufficient steps to draw the disadvantageous term to the insured's "
            "attention before the contract is entered into or the variation agreed. "
            "Section 17(3): the term must be clear and unambiguous as to its effect. "
            "Section 17(4) takes account of the characteristics of insured persons of the "
            "kind in question and the circumstances of the transaction. This comparison "
            "does not decide that a term is disadvantageous or that subsection (2) or (3) "
            "was met."
        ),
    },
    {
        "id": "cra2015-s61",
        "title": "Consumer Rights Act 2015, section 61",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/61",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 61(1): this Part applies to a contract between "
            "a trader and a consumer. Section 61(2) excludes a contract of employment or "
            "apprenticeship. The page did not state an insurance-specific exclusion. This "
            "starter does not decide that a wording is a consumer contract."
        ),
    },
    {
        "id": "cra2015-s62",
        "title": "Consumer Rights Act 2015, section 62",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/62",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 62(1): an unfair term of a consumer contract "
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
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 64(1) and (2): a term may not be assessed for "
            "fairness under section 62 to the extent that it specifies the main subject "
            "matter, or the assessment is of the appropriateness of the price, only if the "
            "term is transparent and prominent. Section 64(3): a term is transparent for "
            "the purposes of this Part if it is expressed in plain and intelligible language "
            "and, if written, is legible. This starter does not decide that a term is "
            "transparent or prominent. Schedule 2 was not opened."
        ),
    },
    {
        "id": "cra2015-s68",
        "title": "Consumer Rights Act 2015, section 68",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/68",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 68(1): a trader must ensure that a written "
            "term of a consumer contract, or a consumer notice in writing, is transparent. "
            "Section 68(2) defines transparent for a consumer notice: plain and intelligible "
            "language, and legible. The definition of a transparent term is in section 64(3), "
            "which was also opened. This starter does not decide that section 68 was met."
        ),
    },
    {
        "id": "cra2015-s69",
        "title": "Consumer Rights Act 2015, section 69",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/69",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Section 69(1): if a term in a consumer contract, or a "
            "consumer notice, could have different meanings, the meaning that is most "
            "favourable to the consumer is to prevail. This starter does not choose a "
            "meaning and does not apply section 69. favourable_to stays null."
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
            "Opened 6 November 2026. Article 5(1) lists the principles, including data "
            "minimisation at (c) and accuracy at (d). Article 5(1)(e) refers to Article 84B. "
            "Article 5(3) was inserted by the Data (Use and Access) Act 2025. This starter "
            "copies cited lines and does not fill a gap by inference. It does not choose "
            "an Article 6 basis and it does not rectify."
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
            "Opened 6 November 2026. The article heading remains and the body is shown as "
            "omitted. Chapter 3 Section 4A was substituted by the Data (Use and Access) Act "
            "2025, section 80(1), in force for this purpose from 5 February 2026 "
            "(S.I. 2026/82). The section 80 page itself was not opened. This starter does "
            "not quote a pre-substitution Article 22 as current law."
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
            "Opened 6 November 2026. Article 22A(1)(a): a decision is based solely on "
            "automated processing if there is no meaningful human involvement in the taking "
            "of the decision. Article 22A(1)(b): a significant decision produces a legal "
            "effect or a similarly significant effect. Article 22A(2) says that, when "
            "considering meaningful human involvement, a person must consider the extent to "
            "which the decision is reached by means of profiling. This starter does not take "
            "a coverage decision and does not certify meaningful human involvement."
        ),
    },
    {
        "id": "ukgdpr-art22b",
        "title": "UK GDPR, Article 22B",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22B",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Paragraph 1 was read: a significant decision based "
            "entirely or partly on processing described in Article 9(1) may not be taken "
            "based solely on automated processing unless one of the conditions is met. "
            "Paragraphs 3 and 4 were read. Paragraph 2 was not in the text returned on that "
            "open, so it is not quoted. This starter does not take the decision."
        ),
    },
    {
        "id": "ukgdpr-art22c",
        "title": "UK GDPR, Article 22C",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22C",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Article 22C(1) requires safeguards where a significant "
            "decision is based entirely or partly on personal data and based solely on "
            "automated processing. Article 22C(2) includes information, representations, "
            "human intervention, and a right to contest. This starter does not provide "
            "those safeguards and does not take the decision."
        ),
    },
    {
        "id": "ukgdpr-art22d",
        "title": "UK GDPR, Article 22D",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22D",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. Article 22D(1) allows regulations to say when there "
            "is, or is not, meaningful human involvement for Article 22A(1)(a). Article "
            "22D(3) allows regulations about the Article 22C safeguards. No such regulations "
            "were opened. This starter does not treat its own refusal to decide as the "
            "certification those regulations might describe."
        ),
    },
    {
        "id": "prin-2a-5",
        "title": "FCA Handbook, PRIN 2A.5",
        "url": "https://handbook.fca.org.uk/handbook/PRIN/2A/5.html",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. The page is titled consumer understanding and says it "
            "was last updated on 26 June 2026. It says a firm must support retail customer "
            "understanding so that communications meet information needs, are likely to be "
            "understood, and equip retail customers to make effective, timely and properly "
            "informed decisions, and must communicate in a way which is clear, fair and not "
            "misleading. Later text on the same page refers to that duty as PRIN 2A.5.3R(1). "
            "The page also names PRIN 2A.5.10R and PRIN 2A.5.15R. This starter does not "
            "decide that a firm met the outcome. PRIN 2A.2.5R and PRIN 2A.10 were named and "
            "were not opened."
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
            "Opened 6 November 2026. The GitHub Copilot harness is a Microsoft Copilot "
            "Studio authoring and orchestration framework, not the GitHub Copilot service. "
            "Customer data is not sent to or processed by the GitHub Copilot service when "
            "agents run in Copilot Studio. The page names three harnesses: GitHub Copilot, "
            "Customer Conversation, and standard. It says the GitHub Copilot harness can "
            "take a goal, break it into steps, create and edit Word, Excel, PowerPoint, "
            "and PDF files, supports skills and memory, runs in a sandbox, and that agents "
            "and workflows on it use Copilot Credits. The billing page linked from the "
            "table was not opened. The page did not mark the harness as preview."
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
            "Opened 6 November 2026. The page says the planner can invoke a topic not only "
            "by trigger phrases but also whenever its described purpose matches the user's "
            "need. It says to prefer tool names, and that names carry more weight than "
            "descriptions. It does not describe numeric routing weights. Whether the GitHub "
            "Copilot harness uses this planner was not stated on the harness overview. "
            "That link is unverified."
        ),
    },
    {
        "id": "document-intelligence",
        "title": "Azure Document Intelligence in Foundry Tools",
        "url": "https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "note": (
            "Opened 6 November 2026. The page title is Azure Document Intelligence in "
            "Foundry Tools. It describes a cloud service with Read and Layout models for "
            "text and structure, and says v4.0 (2024-11-30) is GA. It does not name an "
            "insurance wording comparison model. The product-availability page it points "
            "to was not opened, so UK region availability is unverified. This starter does "
            "not call the service. The page uses the words Foundry Tools. It did not, in "
            "the portion read, use the current catalogue name Microsoft Foundry as the "
            "product title."
        ),
    },
    {
        "id": "prin-2a-1-not-reread",
        "title": "FCA Handbook, PRIN 2A.1",
        "url": "https://handbook.fca.org.uk/handbook/PRIN/2A/1.html",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": (
            "Requested on 6 November 2026. The page returned only the FCA office address, "
            "so the application section is not quoted from this experiment. Experiment 37 "
            "recorded an open on 5 November 2026. Those sentences are not repeated here "
            "as a fresh quotation."
        ),
    },
    {
        "id": "prin-2a-2-not-opened",
        "title": "FCA Handbook, PRIN 2A.2",
        "url": "https://handbook.fca.org.uk/handbook/PRIN/2A/2.html",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened for this experiment. The cross-cutting obligations are not re-quoted.",
    },
    {
        "id": "section-16a-not-opened",
        "title": "Insurance Act 2015, section 16A",
        "url": "https://www.legislation.gov.uk/ukpga/2015/4/section/16A",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. The amendment note in section 17(1) is recorded. Section 16A is not applied.",
    },
    {
        "id": "schedule-2-not-opened",
        "title": "Consumer Rights Act 2015, Schedule 2",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/schedule/2",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. The grey list is not applied. No term is marked unfair.",
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
        "id": "lloyds-not-opened",
        "title": "Lloyd's byelaws",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": "Not opened. No Lloyd's byelaw is applied. No syndicate is named.",
    },
    {
        "id": "comparison-api-not-found",
        "title": "Policy wording comparison API",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": (
            "Not found on the Document Intelligence overview opened 6 November 2026. "
            "No Azure comparison product for policy wordings is cited. The diff in this "
            "starter is local Python."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue boundary for B008",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "note": (
            "Autonomy A0. A wording specialist validates every interpretation. "
            "This row is not a web page."
        ),
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
    """Context only. Nothing here is a favourability finding or a recommendation."""
    commercial = market_label == "commercial_non_consumer"
    retail = market_label == "retail"
    return [
        {
            "id": "ia2015-clarity",
            "when": "The caller labelled the pack commercial_non_consumer.",
            "shown": commercial,
            "text": (
                "Section 2(1) limits this Part to non-consumer insurance contracts. "
                "Section 3(3)(b) is about a presentation that is reasonably clear and "
                "accessible to a prudent insurer. Sections 9, 10, and 11 are about "
                "warranties and other terms. Sections 16 and 17 are about contracting "
                "out and the transparency requirements, including section 17(3), that a "
                "disadvantageous term must be clear and unambiguous as to its effect. "
                "A textual difference is not a finding that a term is disadvantageous, "
                "that section 17 was met, or that one wording is more favourable."
            ),
        },
        {
            "id": "ia2015-part2-not-applied",
            "when": "The caller did not label the pack commercial_non_consumer.",
            "shown": not commercial,
            "text": (
                "Section 2(1) limits Part 2 to non-consumer insurance contracts. This "
                "starter does not apply Part 2, or sections 9 to 11 and 16 to 17, as if "
                "the contract had been decided to be non-consumer, unless the caller "
                "used the commercial_non_consumer label. The label is not that decision."
            ),
        },
        {
            "id": "cra-2015",
            "when": "The caller labelled the pack retail.",
            "shown": retail,
            "text": (
                "Section 61(1) applies Part 2 to a contract between a trader and a "
                "consumer. This starter does not decide that the wording is that contract. "
                "Section 62(4) is the unfairness test. Section 64(3) and section 68(1) "
                "are the transparency provisions that were read. Section 69(1) would "
                "prefer the meaning most favourable to the consumer where a term could "
                "have different meanings. This starter does not choose a meaning, does "
                "not assess fairness, and does not set favourable_to."
            ),
        },
        {
            "id": "cra-not-applied",
            "when": "The caller did not label the pack retail.",
            "shown": not retail,
            "text": (
                "Part 2 of the Consumer Rights Act 2015 was read. It is shown as context "
                "only when the caller labelled the pack retail. A missing or other label "
                "does not decide that the wording is, or is not, a consumer contract."
            ),
        },
        {
            "id": "prin-2a-5",
            "when": "The caller labelled the pack retail.",
            "shown": retail,
            "text": (
                "PRIN 2A.5, opened 6 November 2026, is the consumer understanding outcome. "
                "The page requires communications that support understanding and that are "
                "clear, fair and not misleading, and it refers to that duty as "
                "PRIN 2A.5.3R(1). This comparison is not a finding that a firm met it. "
                "PRIN 2A.1 was not re-read on 6 November 2026."
            ),
        },
        {
            "id": "prin-2a-not-applied",
            "when": "The caller did not label the pack retail.",
            "shown": not retail,
            "text": (
                "PRIN 2A.5 was opened. It is shown when the caller labelled the pack "
                "retail. This starter does not decide that a firm is in retail market "
                "business. PRIN 2A.1 and PRIN 2A.2 were not quoted from a fresh open."
            ),
        },
        {
            "id": "ukgdpr-art5-art22",
            "when": "Always, as a limit on this starter.",
            "shown": True,
            "text": (
                "Article 5 was read, including data minimisation and accuracy. A topic "
                "that is absent from a wording is not stated. It is not inferred. "
                "Article 22 was shown as omitted on 6 November 2026. Articles 22A to 22D "
                "were read. A coverage comparison is not a solely automated coverage "
                "decision. This starter does not certify meaningful human involvement."
            ),
        },
    ]
