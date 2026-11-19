"""Pages opened on 19 November 2026. The core does not download them again.

A sentence is stored only when that page was opened. A banner that was not
on the extract is marked unverified. This file does not decide that any
Article was met.
"""

from __future__ import annotations

from datetime import date, timedelta

LAST_VERIFIED = date(2026, 11, 19)
# Starter default, not a period stated on the pages that were opened.
PIN_WINDOW_DAYS = 180

DPA_S4_STAMP = date(2026, 11, 18)
DPA_S10_STAMP = date(2026, 11, 19)


def source_rows(question: date, current: bool) -> list[dict]:
    return [
        {
            "id": "ukgdpr-art-5",
            "title": "UK GDPR Article 5",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": (
                "The extract returned on 19 November 2026 did not include an "
                "up-to-date-on-or-before banner. That date line is unverified."
            ),
            "used": (
                "Article 5(1)(a) to (f) and Article 5(2) were read. "
                "Article 5(1)(b) includes the words inserted by the Data (Use and Access) Act 2025. "
                "Article 5(1)(e) refers to Article 84B. Article 84B was not opened. "
                "Article 5(3) was read: processing is not lawful by virtue only of being compatible "
                "with the purposes for which the personal data was collected."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "ukgdpr-art-6",
            "title": "UK GDPR Article 6",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/6",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": (
                "The page said there are currently no known outstanding effects for Article 6, "
                "and that revised legislation may not be fully up to date. "
                "An Equality Act-style stamp was not in the extract. That date line is unverified."
            ),
            "used": (
                "Article 6(1)(a) to (f), including point (ea), was read. "
                "The page says points (ea) and (f) shall not apply to processing carried out "
                "by public authorities in the performance of their tasks. "
                "Article 6(4) is shown as omitted. This starter does not choose a basis."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "ukgdpr-art-13",
            "title": "UK GDPR Article 13",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/13",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": "No up-to-date-on-or-before banner was in the extract. That date line is unverified.",
            "used": (
                "Article 13(1) and 13(2) were read, including 13(2)(b) and 13(2)(f). "
                "Article 13(2)(f) refers to safeguards under Article 22C. Article 22C was not opened. "
                "Article 13(4) to 13(7) were read. This starter does not decide that the information was provided."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "ukgdpr-art-21",
            "title": "UK GDPR Article 21",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/21",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": (
                "No up-to-date-on-or-before banner was in the extract. That date line is unverified. "
                "Paragraphs 2 and 3 were not in the extract. Their text is not quoted."
            ),
            "used": (
                "Article 21(1) and 21(4) were read. Article 21(1) is the right to object where processing "
                "is based on point (e), (ea) or (f) of Article 6(1). "
                "This starter does not decide that the controller has compelling legitimate grounds."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "ukgdpr-art-22",
            "title": "UK GDPR Article 22",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": "The body on the page was omitted. The old Article 22 wording is not quoted.",
            "used": (
                "The textual amendment says Chapter 3 Section 4A was substituted for Article 22 "
                "by the Data (Use and Access) Act 2025, section 80(1). S.I. 2026/82 was not opened."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "ukgdpr-art-22a",
            "title": "UK GDPR Article 22A",
            "url": "https://www.legislation.gov.uk/eur/2016/679/article/22A",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": "No up-to-date-on-or-before banner was in the extract. That date line is unverified.",
            "used": (
                "Article 22A(1) and 22A(2) were read. A decision is based solely on automated processing "
                "if there is no meaningful human involvement. A significant decision produces a legal effect "
                "or a similarly significant effect. This starter does not take that decision and does not "
                "decide that a skills note would be one. Articles 22B, 22C and 22D were not opened."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "dpa-2018-s4",
            "title": "Data Protection Act 2018, section 4",
            "url": "https://www.legislation.gov.uk/ukpga/2018/12/section/4",
            "opened": "2026-11-19",
            "banner": DPA_S4_STAMP.isoformat(),
            "banner_note": (
                "The page said section 4 is up to date with all changes known to be in force "
                "on or before 18 November 2026."
            ),
            "used": (
                "Section 4(1): this Part is relevant to most processing of personal data. "
                "Section 4(2): this Part applies to processing to which the UK GDPR applies by virtue of "
                "Article 2, and supplements and must be read with the UK GDPR. Article 2 was not opened."
            ),
            "current_for_question_date": question <= DPA_S4_STAMP,
        },
        {
            "id": "dpa-2018-s10",
            "title": "Data Protection Act 2018, section 10",
            "url": "https://www.legislation.gov.uk/ukpga/2018/12/section/10",
            "opened": "2026-11-19",
            "banner": DPA_S10_STAMP.isoformat(),
            "banner_note": (
                "The page said section 10 is up to date with all changes known to be in force "
                "on or before 19 November 2026."
            ),
            "used": (
                "Section 10(1) refers to Article 9(1) of the UK GDPR as the prohibition on processing "
                "special categories of personal data, and to conditions in Article 9(2). "
                "Article 9 was not opened as its own page. Schedule 1 was not opened. "
                "This starter does not decide that a condition was met."
            ),
            "current_for_question_date": question <= DPA_S10_STAMP,
        },
        {
            "id": "ico-monitoring",
            "title": "ICO, Employment practices and data protection: monitoring workers",
            "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/monitoring-workers/data-protection-and-monitoring-workers/",
            "opened": "2026-11-19",
            "banner": "under_review",
            "banner_note": (
                "The page says that because of the Data (Use and Access) Act the guidance is under review "
                "and may change. No legislation-style stamp was on the page."
            ),
            "used": (
                "The page says you must be clear about the purpose for monitoring and must document why. "
                "It says you should not monitor workers just in case. "
                "It says you can only change your purpose if the new purpose is compatible, you get consent, "
                "or you have a clear obligation or function set out in law. "
                "It says you must not collect more information than you need. "
                "The ethernet example says that information should not be reused for performance management "
                "without a new lawful basis and a necessity and proportionality assessment. "
                "This starter does not decide that monitoring was lawful."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "ico-ai",
            "title": "ICO, How do we ensure lawfulness in AI?",
            "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-lawfulness-in-ai/",
            "opened": "2026-11-19",
            "banner": "2024-10-28",
            "banner_note": (
                "The chapter says latest update 28 October 2024, and that the guidance is under review "
                "because of the Data (Use and Access) Act. The parent guidance page said it was updated "
                "on 15 March 2023. Those are the dates on the pages, not a legislation stamp."
            ),
            "used": (
                "The chapter says you must identify a purpose and an appropriate lawful basis for each "
                "processing operation, and that it is the controller's responsibility to decide which basis applies. "
                "On inferences, it says an inference is likely to be special category data if you can or intend "
                "to infer that information, or intend to treat someone differently on the basis of the inference. "
                "This starter does not draw that inference and does not decide Article 9."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "fabric-overview",
            "title": "What is Microsoft Fabric",
            "url": "https://learn.microsoft.com/en-us/fabric/fundamentals/microsoft-fabric-overview",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": "The page did not show a last-updated line in the extract. That date is unverified.",
            "used": (
                "The page describes Fabric as a SaaS analytics platform with OneLake, and names workloads "
                "including Data Engineering, Data Factory, Data Warehouse and Power BI. "
                "It says Fabric IQ is in preview. It says Fabric integrates with Microsoft 365 and with "
                "Microsoft Foundry. This starter does not deploy a Fabric item and does not call Foundry."
            ),
            "current_for_question_date": current,
        },
        {
            "id": "harness-overview",
            "title": "Harnesses in Copilot Studio",
            "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
            "opened": "2026-11-19",
            "banner": "unverified",
            "banner_note": "No last-updated line was in the extract. That date is unverified.",
            "used": (
                "Three harnesses are named: Microsoft Copilot harness, Customer Conversation harness, "
                "and standard harness. The standard harness follows the topics and rules the maker defines. "
                "The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, "
                "file creation, and a sandbox, billed in Copilot Credits. The page states no price. "
                "It does not use the words GitHub Copilot harness."
            ),
            "current_for_question_date": current,
        },
    ]


def pins_current(question: date) -> bool:
    """True when the dated stamps cover the question date and the window has not passed.

    Pages with no stamp are listed as unverified. They do not, by themselves,
    make this true. may_be_relied_on stays false in the inventory either way.
    """

    if question > LAST_VERIFIED + timedelta(days=PIN_WINDOW_DAYS):
        return False
    if question > DPA_S4_STAMP or question > DPA_S10_STAMP:
        return False
    if question > LAST_VERIFIED:
        return False
    return True
