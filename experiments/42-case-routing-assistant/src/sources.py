"""Pages opened for this starter. The assistant does not download them."""

from __future__ import annotations

from datetime import date

RETRIEVED_ON = date(2026, 11, 9)
STALE_AFTER_DAYS = 180


def _source(
    source_id: str,
    title: str,
    url: str,
    retrieved: str,
    *,
    opened: bool,
    taken: str,
) -> dict:
    return {
        "id": source_id,
        "title": title,
        "url": url,
        "retrieved": retrieved,
        "opened_on_9_november_2026": opened,
        "taken": taken,
    }


SOURCES: dict[str, dict] = {
    "duaa_s80": _source(
        "duaa_s80",
        "Data (Use and Access) Act 2025, section 80",
        "https://www.legislation.gov.uk/ukpga/2025/18/section/80",
        "2026-11-09",
        opened=True,
        taken=(
            "Section 80(1) substitutes Articles 22A to 22D for Article 22 of the UK GDPR. "
            "Article 22A(1)(a) says a decision is based solely on automated processing if there "
            "is no meaningful human involvement in the taking of the decision. Article 22A(1)(b) "
            "says a decision is significant if it produces a legal effect or a similarly significant "
            "effect. Article 22C(2) requires safeguards which include information, representations, "
            "human intervention, and the ability to contest. The page states that section 80 is in "
            "force at 5 February 2026 in so far as not already in force, by S.I. 2026/82, regulation 2(j). "
            "That instrument was not opened."
        ),
    ),
    "uk_gdpr_art_22": _source(
        "uk_gdpr_art_22",
        "UK GDPR Article 22",
        "https://www.legislation.gov.uk/eur/2016/679/article/22",
        "2026-11-09",
        opened=True,
        taken=(
            "The article text is omitted. A footnote says Chapter 3 Section 4A was substituted "
            "for Article 22 by the Data (Use and Access) Act 2025, section 80(1), from 5 February 2026 "
            "in so far as not already in force, by S.I. 2026/82. The instrument was not opened."
        ),
    ),
    "uk_gdpr_art_12": _source(
        "uk_gdpr_art_12",
        "UK GDPR Article 12",
        "https://www.legislation.gov.uk/eur/2016/679/article/12",
        "2026-11-09",
        opened=True,
        taken=(
            "Article 12(3) says the controller provides information on action taken on a request "
            "under Articles 15 to 22D without undue delay and in any event before the end of the "
            "applicable time period, and it points to Article 12A. Article 12A was not opened. "
            "This starter does not state a number of days for a subject access request."
        ),
    ),
    "equality_s19": _source(
        "equality_s19",
        "Equality Act 2010, section 19",
        "https://www.legislation.gov.uk/ukpga/2010/15/section/19",
        "2026-11-09",
        opened=True,
        taken=(
            "Section 19(1) and (2) define indirect discrimination as a provision, criterion or "
            "practice that puts people who share a relevant protected characteristic at a particular "
            "disadvantage, and that is not shown to be a proportionate means of achieving a legitimate "
            "aim. Section 19(3) lists age, disability, gender reassignment, marriage and civil "
            "partnership, race, religion or belief, sex, and sexual orientation. This starter does "
            "not decide that a rule meets or fails that test."
        ),
    ),
    "equality_s29": _source(
        "equality_s29",
        "Equality Act 2010, section 29",
        "https://www.legislation.gov.uk/ukpga/2010/15/section/29",
        "2026-11-09",
        opened=True,
        taken=(
            "Section 29(1) says a service-provider must not discriminate against a person requiring "
            "the service by not providing it. Section 29(2) covers the terms, terminating the service, "
            "and any other detriment. Section 29(7) says a duty to make reasonable adjustments applies "
            "to a service-provider. Section 20 was not opened, so the content of that duty is not quoted."
        ),
    ),
    "equality_s149": _source(
        "equality_s149",
        "Equality Act 2010, section 149",
        "https://www.legislation.gov.uk/ukpga/2010/15/section/149",
        "2026-11-09",
        opened=True,
        taken=(
            "Section 149(1) says a public authority must, in the exercise of its functions, have due "
            "regard to the need to eliminate discrimination, advance equality of opportunity, and "
            "foster good relations. Section 149(7) lists the relevant protected characteristics for "
            "that duty. Marriage and civil partnership is not in that list. It is in section 19(3). "
            "This starter does not carry out the due-regard assessment."
        ),
    ),
    "foia_s10": _source(
        "foia_s10",
        "Freedom of Information Act 2000, section 10",
        "https://www.legislation.gov.uk/ukpga/2000/36/section/10",
        "2026-11-09",
        opened=True,
        taken=(
            "Section 10(1), subject to subsections (2) and (3), says a public authority must comply "
            "with section 1(1) promptly and in any event not later than the twentieth working day "
            "following the date of receipt. Section 10(6) defines a working day as any day other than "
            "a Saturday, a Sunday, Christmas Day, Good Friday, or a bank holiday under the Banking and "
            "Financial Dealings Act 1971 in any part of the United Kingdom. This starter does not "
            "calculate that day. Experiment 05's England and Wales calendar is not used for this Act."
        ),
    ),
    "eir_reg5": _source(
        "eir_reg5",
        "Environmental Information Regulations 2004, regulation 5",
        "https://www.legislation.gov.uk/uksi/2004/3391/regulation/5",
        "2026-11-09",
        opened=True,
        taken=(
            "Regulation 5(2) says information shall be made available under paragraph (1) as soon as "
            "possible and no later than 20 working days after the date of receipt of the request. "
            "Regulation 2, which would define working day, was not opened. The day is not calculated."
        ),
    ),
    "harnesses": _source(
        "harnesses",
        "Harnesses in Copilot Studio",
        "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "2026-11-09",
        opened=True,
        taken=(
            "The GitHub Copilot harness is a Microsoft Copilot Studio authoring and orchestration "
            "framework, not the GitHub Copilot service. The standard harness follows the topics and "
            "rules the maker defines. The Customer Conversation harness is described for contact-centre "
            "voice and chat, with a route to a human representative. Agents on the GitHub Copilot "
            "harness and on the Customer Conversation harness use Copilot Credits. No price is stated "
            "on the overview. The billing and licensing articles were not opened."
        ),
    ),
}


NOT_OPENED = (
    "UK GDPR Article 6",
    "UK GDPR Article 9",
    "UK GDPR Article 12A",
    "UK GDPR Article 22D regulations",
    "S.I. 2026/82",
    "Equality Act 2010, section 4",
    "Equality Act 2010, section 13",
    "Equality Act 2010, section 20",
    "Environmental Information Regulations 2004, regulation 2",
    "DISP",
    "The Housing Ombudsman Complaint Handling Code",
    "The AI Playbook",
    "The ATRS scope policy",
)
