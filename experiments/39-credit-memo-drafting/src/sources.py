"""Pages opened on 6 November 2026. The drafter does not fetch them again.

A quote is a short operative sentence from a page that was opened that day.
A page that was not opened is listed and is not quoted. Update last_verified
only after opening the page again.
"""

from __future__ import annotations

from datetime import date
from typing import Any

LAST_VERIFIED = "2026-11-06"
DEFAULT_STALE_AFTER_DAYS = 90

SOURCES: tuple[dict[str, Any], ...] = (
    {
        "id": "uk-gdpr-article-5",
        "title": "UK GDPR Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "Personal data shall be: (a) processed lawfully, fairly and in a transparent "
            "manner in relation to the data subject ('lawfulness, fairness and transparency'); "
            "(c) adequate, relevant and limited to what is necessary in relation to the "
            "purposes for which they are processed ('data minimisation'); (d) accurate and, "
            "where necessary, kept up to date."
        ),
        "note": (
            "Opened 6 November 2026. Article 5(1)(a), (c) and (d) were read, as was "
            "Article 5(2) on accountability. Article 5(3) was inserted by the Data (Use and "
            "Access) Act 2025 and says processing is not lawful by virtue only of being "
            "compatible with the purposes for which the personal data was collected. This "
            "starter does not choose an Article 6 basis and does not erase or rectify anything."
        ),
    },
    {
        "id": "uk-gdpr-article-9",
        "title": "UK GDPR Article 9",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/9",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "Processing of personal data revealing racial or ethnic origin, political "
            "opinions, religious or philosophical beliefs, or trade union membership, and "
            "the processing of genetic data, biometric data for the purpose of uniquely "
            "identifying a natural person, data concerning health or data concerning a "
            "natural person's sex life or sexual orientation shall be prohibited."
        ),
        "note": (
            "Opened 6 November 2026. Article 9(1) was read. Article 9(2) lists conditions "
            "that can disapply paragraph 1, including explicit consent and a domestic-law "
            "basis. This starter does not apply a condition. The Data Protection Act 2018 "
            "section 10 was not opened."
        ),
    },
    {
        "id": "uk-gdpr-article-22",
        "title": "UK GDPR Article 22",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": None,
        "note": (
            "Opened 6 November 2026. Article 22 is shown as omitted. Chapter 3 Section 4A "
            "was substituted for Article 22 by the Data (Use and Access) Act 2025, "
            "section 80(1), in force for remaining purposes on 5 February 2026 "
            "(S.I. 2026/82, regulation 2(j)). The old Article 22 text is not quoted."
        ),
    },
    {
        "id": "uk-gdpr-article-22a",
        "title": "UK GDPR Article 22A",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A decision is based solely on automated processing if there is no meaningful "
            "human involvement in the taking of the decision, and a decision is a "
            "significant decision, in relation to a data subject, if it produces a legal "
            "effect for the data subject, or it has a similarly significant effect for the "
            "data subject."
        ),
        "note": (
            "Opened 6 November 2026. Article 22A(1) was read. Article 22A(2) says that, "
            "when considering meaningful human involvement, a person must consider, among "
            "other things, the extent to which the decision is reached by means of "
            "profiling. This starter does not take a credit decision and does not certify "
            "meaningful human involvement."
        ),
    },
    {
        "id": "uk-gdpr-article-22b",
        "title": "UK GDPR Article 22B",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22B",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A significant decision based entirely or partly on processing described in "
            "Article 9(1) (processing of special categories of personal data) may not be "
            "taken based solely on automated processing, unless one of the following "
            "conditions is met. The first condition is that the decision is based entirely "
            "on processing of personal data to which the data subject has given explicit consent."
        ),
        "note": (
            "Opened 6 November 2026. Paragraphs 1, 2, 3 and 4 were read from the page and "
            "the data.xml. Paragraph 3 is the contract or law condition together with "
            "Article 9(2)(g). Paragraph 4 restricts a significant decision based solely on "
            "automated processing where the decision-maker relies on Article 6(1)(ea). "
            "This starter does not take the decision and does not rely on either condition."
        ),
    },
    {
        "id": "uk-gdpr-article-22c",
        "title": "UK GDPR Article 22C",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22C",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "The safeguards must consist of or include measures which provide the data "
            "subject with information about decisions described in paragraph 1 taken in "
            "relation to the data subject; enable the data subject to make representations "
            "about such decisions; enable the data subject to obtain human intervention on "
            "the part of the controller in relation to such decisions; enable the data "
            "subject to contest such decisions."
        ),
        "note": (
            "Opened 6 November 2026. Article 22C(2) was read. This starter does not provide "
            "those safeguards, because it does not take the decision. A deployment that "
            "did take a significant decision would have to meet them. This folder does not."
        ),
    },
    {
        "id": "uk-gdpr-article-22d",
        "title": "UK GDPR Article 22D",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/22D",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "The Secretary of State may by regulations provide that, for the purposes of "
            "Article 22A(1)(a), there is, or is not, to be taken to be meaningful human "
            "involvement in the taking of a decision in cases described in the regulations."
        ),
        "note": (
            "Opened 6 November 2026. Article 22D(1) was read. No regulations under "
            "Article 22D were opened. This starter does not treat any regulation as "
            "defining meaningful human involvement for credit."
        ),
    },
    {
        "id": "equality-act-s4",
        "title": "Equality Act 2010, section 4",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/4",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "The following characteristics are protected characteristics: age; disability; "
            "gender reassignment; marriage and civil partnership; pregnancy and maternity; "
            "race; religion or belief; sex; sexual orientation."
        ),
        "note": (
            "Opened 6 November 2026. The page said section 4 is up to date with all changes "
            "known to be in force on or before 6 November 2026. The list is a theme list "
            "for the credit officer. It is not a finding of discrimination."
        ),
    },
    {
        "id": "equality-act-s13",
        "title": "Equality Act 2010, section 13",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/13",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A person (A) discriminates against another (B) if, because of a protected "
            "characteristic, A treats B less favourably than A treats or would treat others."
        ),
        "note": (
            "Opened 6 November 2026. Section 13(1) was read. Section 13(2) is the age "
            "justification. This starter does not decide less favourable treatment and "
            "does not apply section 13(2)."
        ),
    },
    {
        "id": "equality-act-s19",
        "title": "Equality Act 2010, section 19",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/19",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A person (A) discriminates against another (B) if A applies to B a provision, "
            "criterion or practice which is discriminatory in relation to a relevant "
            "protected characteristic of B's."
        ),
        "note": (
            "Opened 6 November 2026. Section 19(1) and 19(3) were read. Section 19(3) lists "
            "age, disability, gender reassignment, marriage and civil partnership, race, "
            "religion or belief, sex, and sexual orientation. It does not list pregnancy "
            "and maternity. This starter does not decide that a provision, criterion or "
            "practice is discriminatory."
        ),
    },
    {
        "id": "equality-act-s29",
        "title": "Equality Act 2010, section 29",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/29",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A person (a \"service-provider\") concerned with the provision of a service to "
            "the public or a section of the public (for payment or not) must not discriminate "
            "against a person requiring the service by not providing the person with the service."
        ),
        "note": (
            "Opened 6 November 2026. The page said section 29 is up to date with all changes "
            "known to be in force on or before 5 November 2026. Section 29(1) and 29(2) were "
            "read. Section 29(2) covers terms, terminating the service, and any other "
            "detriment. Schedule 3 was not opened, so no services exception is applied. "
            "This starter does not decide that lending is or is not a service in a given case."
        ),
    },
    {
        "id": "prin-2a-1",
        "title": "FCA Handbook, PRIN 2A.1",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "The Consumer Duty applies in relation to a firm's retail market business or "
            "where the firm communicates or approves financial promotions which are "
            "addressed to, or disseminated in such a way that they are likely to be "
            "received by, a retail customer."
        ),
        "note": (
            "Opened 6 November 2026. The page says the application is set out in PRIN 3, "
            "including PRIN 3.2.6R to PRIN 3.2.12G. PRIN 3 was not opened. The page says "
            "the definition of a retail customer for the purposes of the Consumer Duty "
            "includes a prospective customer. The glossary definition of a retail customer, "
            "including any SME limb, was not opened. This starter does not decide that a "
            "firm is in retail market business, and it does not decide that the Duty was met. "
            "FG22/5 is named on the page and was not opened."
        ),
    },
    {
        "id": "prin-2a-2-not-retrieved",
        "title": "FCA Handbook, PRIN 2A.2",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/2.html",
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": (
            "Requested on 6 November 2026. The response did not include the rule text. "
            "The cross-cutting obligations are not quoted. They are not applied."
        ),
    },
    {
        "id": "mlr-2017-reg-21",
        "title": "Money Laundering Regulations 2017, regulation 21",
        "url": "https://www.legislation.gov.uk/uksi/2017/692/regulation/21",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "An individual in the relevant person's firm must be appointed as a nominated "
            "officer. Where a disclosure is made to the nominated officer, that officer must "
            "consider it in the light of any relevant information which is available to the "
            "relevant person and determine whether it gives rise to knowledge or suspicion "
            "or reasonable grounds for knowledge or suspicion that a person is engaged in "
            "money laundering or terrorist financing."
        ),
        "note": (
            "Opened 6 November 2026. Regulation 21(3) and 21(5) were read. The page said "
            "regulation 21 is up to date with all changes known to be in force on or before "
            "5 November 2026. This starter does not appoint the officer and does not make "
            "the regulation 21(5) determination. Regulation 28 was not re-opened for this "
            "experiment. JMLSG guidance was not opened."
        ),
    },
    {
        "id": "poca-s330",
        "title": "Proceeds of Crime Act 2002, section 330",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/330",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A person commits an offence if the conditions in subsections (2) to (4) are "
            "satisfied. The first condition is that he knows or suspects, or has reasonable "
            "grounds for knowing or suspecting, that another person is engaged in money "
            "laundering. The fourth condition is that he does not make the required "
            "disclosure to a nominated officer, or a person authorised for the purposes of "
            "this Part by the Director General of the National Crime Agency, as soon as is "
            "practicable."
        ),
        "note": (
            "Opened 6 November 2026. The page said section 330 is up to date with all "
            "changes known to be in force on or before 6 November 2026. Subsections (1) to "
            "(5) were read. The required disclosure is defined in subsection (5). This "
            "starter does not decide that the conditions are met and does not make the "
            "disclosure. Schedule 9, which determines a business in the regulated sector, "
            "was not opened."
        ),
    },
    {
        "id": "poca-s331",
        "title": "Proceeds of Crime Act 2002, section 331",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/331",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "A person nominated to receive disclosures under section 330 commits an offence "
            "if the conditions in subsections (2) to (4) are satisfied."
        ),
        "note": (
            "Opened 6 November 2026. Section 331(1) and 331(4) were read. Subsection (4) "
            "is the nominated officer's required disclosure to a person authorised by the "
            "Director General of the National Crime Agency. The MLRO, not this starter, "
            "decides any SAR. This starter does not make that disclosure."
        ),
    },
    {
        "id": "poca-s338",
        "title": "Proceeds of Crime Act 2002, section 338",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/338",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "For the purposes of this Part a disclosure is authorised if it is a disclosure "
            "to a constable, a customs officer or a nominated officer by the alleged offender "
            "that property is criminal property, and the first, second or third condition "
            "set out below is satisfied."
        ),
        "note": (
            "Opened 6 November 2026. Section 338(1) was read. This starter does not make "
            "an authorised disclosure and does not decide that property is criminal property."
        ),
    },
    {
        "id": "poca-s333a-not-opened",
        "title": "Proceeds of Crime Act 2002, section 333A",
        "url": "https://www.legislation.gov.uk/ukpga/2002/29/section/333A",
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": (
            "Not opened on 6 November 2026. Tipping-off wording is not quoted. The control "
            "in this starter is that no customer text is produced."
        ),
    },
    {
        "id": "harness-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "The GitHub Copilot harness is a Microsoft Copilot Studio authoring and "
            "orchestration framework, not the GitHub Copilot service."
        ),
        "note": (
            "Opened 6 November 2026. The page says customer data is not sent to or processed "
            "by the GitHub Copilot service when agents run in Copilot Studio. It says the "
            "GitHub Copilot harness can take a goal, break it into steps, supports skills "
            "and memory, creates and edits Word, Excel, PowerPoint, and PDF files, runs in "
            "a sandbox, and that agents and workflows on it use Copilot Credits. The billing "
            "pages linked from the table were not opened. The page did not mark the harness "
            "as preview. The standard harness is described as following the topics and rules "
            "the maker defines."
        ),
    },
    {
        "id": "generative-orchestration",
        "title": "Generative orchestration guidance",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-orchestration",
        "last_verified": LAST_VERIFIED,
        "stale_applicable": True,
        "opened": True,
        "quote": (
            "In generative orchestration, the planner can invoke topics not only by trigger "
            "phrases but also whenever their described purpose matches the user's need."
        ),
        "note": (
            "Opened 6 November 2026. The page says names carry more weight than descriptions. "
            "It does not describe numeric routing weights. It uses the words \"Standard harness "
            "(planner)\" for an LLM planning layer. The harness overview uses \"standard harness\" "
            "for rule-based agents. This starter does not treat those as the same component. "
            "That identification is unverified. The page describes autonomous triggers. This "
            "starter does not use one. Whether the GitHub Copilot harness uses this planner "
            "was not stated on the harness overview. That link is unverified."
        ),
    },
    {
        "id": "equality-act-schedule-3-not-opened",
        "title": "Equality Act 2010, Schedule 3",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/schedule/3",
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": "Not opened. No services exception, including any financial-services exception, is applied.",
    },
    {
        "id": "prin-3-not-opened",
        "title": "FCA Handbook, PRIN 3",
        "url": "https://www.handbook.fca.org.uk/handbook/PRIN/3/",
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": "Not opened. Whether a product is retail market business is not decided here.",
    },
    {
        "id": "fg22-5-not-opened",
        "title": "FCA FG22/5",
        "url": "https://www.fca.org.uk/publication/finalised-guidance/fg22-5.pdf",
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": "Named on the PRIN 2A.1 page. Not opened. Not applied.",
    },
    {
        "id": "foundry-not-opened",
        "title": "Microsoft Foundry",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": (
            "A product page was not opened on 6 November 2026. Foundry is named because "
            "the catalogue stack is FND. It is not called. UK region availability is unverified."
        ),
    },
    {
        "id": "fabric-not-opened",
        "title": "Microsoft Fabric",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": (
            "A product page was not opened on 6 November 2026. Fabric is named because the "
            "catalogue stack is FAB. A lakehouse, a warehouse, and a Power BI report are "
            "unverified. This starter does not write one."
        ),
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue boundary for B009",
        "url": None,
        "last_verified": None,
        "stale_applicable": False,
        "opened": False,
        "quote": None,
        "note": (
            "Autonomy A1. The credit officer owns the recommendation and every approval. "
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
                "opened": source["opened"],
                "age_days": age,
                "stale": stale,
                "quote": source["quote"],
                "note": source["note"],
                "applied_as_a_finding": False,
            }
        )
    return rows, any_stale


def regulatory_notes(product_label: str) -> list[dict[str, Any]]:
    """Context for the credit officer. None of these notes is a finding."""
    notes = [
        {
            "id": "no-solely-automated-credit-decision",
            "applies_because": "every pack",
            "text": (
                "Article 22 was shown as omitted on 6 November 2026. Article 22A(1) says a "
                "decision is based solely on automated processing if there is no meaningful "
                "human involvement. A credit decision can be a significant decision. This "
                "draft does not take it. solely_automated_decision stays false. That flag "
                "does not certify meaningful human involvement."
            ),
            "source_ids": ["uk-gdpr-article-22", "uk-gdpr-article-22a", "uk-gdpr-article-22c"],
            "applied_as_a_finding": False,
        },
        {
            "id": "article-9-not-a-credit-factor",
            "applies_because": "every pack",
            "text": (
                "Article 9(1) prohibits processing the special categories it lists, unless "
                "a condition in Article 9(2) applies. Article 22B(1) restricts a significant "
                "decision based on that processing when the decision is solely automated. "
                "This draft does not apply an Article 9 condition and does not take the decision. "
                "A theme in a cited line is shown for the credit officer and the data "
                "protection officer. It is not a reason to approve or decline."
            ),
            "source_ids": ["uk-gdpr-article-9", "uk-gdpr-article-22b"],
            "applied_as_a_finding": False,
        },
        {
            "id": "equality-act-lending-theme",
            "applies_because": "every pack",
            "text": (
                "Section 4 lists the protected characteristics. Section 13(1) is direct "
                "discrimination. Section 19(1) is indirect discrimination. Section 29(1) "
                "and 29(2) restrict discrimination in the provision of a service, including "
                "as to terms. Schedule 3 was not opened. A word from section 4 in a cited "
                "line is a theme for the credit officer. It is not a finding that section "
                "13, 19, or 29 was contravened."
            ),
            "source_ids": [
                "equality-act-s4",
                "equality-act-s13",
                "equality-act-s19",
                "equality-act-s29",
                "equality-act-schedule-3-not-opened",
            ],
            "applied_as_a_finding": False,
        },
        {
            "id": "financial-crime-narrative-only",
            "applies_because": "every pack",
            "text": (
                "Regulation 21(3) requires a nominated officer. Regulation 21(5) is that "
                "officer's consideration of a disclosure. Section 330 is the regulated-sector "
                "disclosure offence. Section 331 is the nominated officer's offence. Section "
                "338 defines an authorised disclosure. The MLRO decides any SAR. This draft "
                "copies a flagged line for that person. It does not decide suspicion, it "
                "does not make a disclosure, and it does not produce customer text. Section "
                "333A was not opened."
            ),
            "source_ids": [
                "mlr-2017-reg-21",
                "poca-s330",
                "poca-s331",
                "poca-s338",
                "poca-s333a-not-opened",
            ],
            "applied_as_a_finding": False,
        },
    ]
    if product_label in {"retail", "sme_consumer_facing"}:
        notes.append(
            {
                "id": "consumer-duty-context",
                "applies_because": product_label,
                "text": (
                    "PRIN 2A.1 says the Consumer Duty applies to a firm's retail market "
                    "business, and that the application is set out in PRIN 3. PRIN 3 was "
                    "not opened. The glossary definition of a retail customer, including "
                    "any treatment of an SME, was not opened. The caller label is not a "
                    "decision that the firm is in retail market business. PRIN 2A.2 was "
                    "requested and the rule text was not returned, so the cross-cutting "
                    "obligations are not quoted. This note is not a finding that the Duty was met."
                ),
                "source_ids": ["prin-2a-1", "prin-2a-2-not-retrieved", "prin-3-not-opened"],
                "applied_as_a_finding": False,
            }
        )
    elif product_label == "commercial_non_consumer":
        notes.append(
            {
                "id": "consumer-duty-not-applied-on-this-label",
                "applies_because": product_label,
                "text": (
                    "The caller labelled the pack commercial_non_consumer. PRIN 2A.1 was "
                    "read and is not applied as if the Duty covered this pack. The label is "
                    "not a decision that the firm is outside retail market business. PRIN 3 "
                    "was not opened."
                ),
                "source_ids": ["prin-2a-1", "prin-3-not-opened"],
                "applied_as_a_finding": False,
            }
        )
    else:
        notes.append(
            {
                "id": "consumer-duty-label-not-usable",
                "applies_because": product_label,
                "text": (
                    "The product label is missing or not in the closed list. PRIN 2A is not "
                    "applied. The agent does not choose the label."
                ),
                "source_ids": ["prin-2a-1"],
                "applied_as_a_finding": False,
            }
        )
    return notes
