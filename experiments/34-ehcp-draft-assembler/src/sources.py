"""Pages opened for this experiment on 4 November 2026.

No rate, pack size, or diagram number is copied. A page that was not opened
is marked and is not stale-tested.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = "2026-11-04"
DEFAULT_STALE_AFTER_DAYS = 90
# This starter's count. The regulations do not define this arithmetic.
TWENTY_WEEKS_AS_DAYS = 140

CATALOGUE_ID = "UK10"
EXPERIMENT_ID = "exp-34-ehcp-draft-assembler"
GATEWAY_CALLER = EXPERIMENT_ID
AUTONOMY = "A1"
LABEL = "DRAFT FOR CASEWORKER — NOT A PLAN"
EXPORT_LABEL = "LOCAL COPY FOR THE CASEWORKER — NOT SENT"

SOURCES: tuple[dict, ...] = (
    {
        "id": "cfa-s36",
        "title": "Children and Families Act 2014, section 36",
        "url": "https://www.legislation.gov.uk/ukpga/2014/6/section/36",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Section 36 is the EHC needs assessment. A request may be made by the parent, the young person, or a person acting for a school or post-16 institution. The local authority decides whether to secure an assessment. This starter does not make that decision.",
    },
    {
        "id": "cfa-s37",
        "title": "Children and Families Act 2014, section 37",
        "url": "https://www.legislation.gov.uk/ukpga/2014/6/section/37",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Section 37(2) says an EHC plan specifies special educational needs, outcomes, special educational provision, related health care provision, and social care provision. The local authority prepares and maintains the plan where section 37(1) applies. This starter does not decide that it applies.",
    },
    {
        "id": "cfa-s38",
        "title": "Children and Families Act 2014, section 38",
        "url": "https://www.legislation.gov.uk/ukpga/2014/6/section/38",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Section 38(5) says the draft EHC plan sent to the parent or young person must not name a school or other institution, or specify a type of school or other institution. Quotes tagged as section I are not copied into this draft.",
    },
    {
        "id": "cfa-s42",
        "title": "Children and Families Act 2014, section 42",
        "url": "https://www.legislation.gov.uk/ukpga/2014/6/section/42",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Section 42 is the duty to secure specified special educational provision, and for the responsible commissioning body to arrange specified health care provision, where the local authority maintains an EHC plan. This draft is not a maintained plan. provision_secured stays false.",
    },
    {
        "id": "cfa-ss37-49",
        "title": "Children and Families Act 2014, sections 37 to 49",
        "url": "https://www.legislation.gov.uk/ukpga/2014/6/part/3/crossheading/education-health-and-care-plans",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "The crossheading page opened on 4 November 2026 includes sections 37 to 49: content (37), the draft (38), finalising where a school is requested (39) or not requested (40), section 41 approval, the duty to secure provision (42), the duty to admit (43), reviews (44), ceasing to maintain (45), maintaining after 25 (46), transfer (47), release from detention (48), and personal budgets (49). This starter does not take those steps. Section 36 was opened as its own page.",
    },
    {
        "id": "send-reg-6",
        "title": "SEND Regulations 2014, regulation 6",
        "url": "https://www.legislation.gov.uk/uksi/2014/1530/regulation/6",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Regulation 6(1) lists the advice the local authority must seek. Paragraphs (a) to (e) are the gap check. Paragraph (f) is discretionary. Paragraph (g) applies where the child or young person is in or beyond year 9. Paragraph (h) is advice the parent or young person reasonably requests. Regulation 6(4) allows existing advice to be reused where everyone is satisfied it is sufficient. This starter does not decide that.",
    },
    {
        "id": "send-reg-10",
        "title": "SEND Regulations 2014, regulation 10",
        "url": "https://www.legislation.gov.uk/uksi/2014/1530/regulation/10",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Regulation 10(4)(a) to (d) sets reasons a time limit need not be met, including a school closure of at least four weeks, exceptional personal circumstances, and absence from the area for at least four weeks. Regulation 13(3) applies those reasons to the 20-week limit. This starter does not apply them.",
    },
    {
        "id": "send-reg-12",
        "title": "SEND Regulations 2014, regulation 12",
        "url": "https://www.legislation.gov.uk/uksi/2014/1530/regulation/12",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Regulation 12 sets sections A to J and, in paragraph (4), section K. Each section must be separately identified. Paragraph (3) requires preparation-for-adulthood provision in or beyond year 9. The headings in this starter follow regulation 12.",
    },
    {
        "id": "send-reg-13",
        "title": "SEND Regulations 2014, regulation 13",
        "url": "https://www.legislation.gov.uk/uksi/2014/1530/regulation/13",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Regulation 13(1) gives at least 15 days to make representations about a draft plan that has been sent, and to request a particular school. Regulation 13(2) says the finalised plan must be sent as soon as practicable and in any event within 20 weeks of the request under section 36(1), or of the authority becoming responsible under section 24. Regulation 13(3) disapplies that limit where regulation 10(4)(a) to (d) makes compliance impractical. This starter does not send the plan and does not find a breach.",
    },
    {
        "id": "send-code-2015",
        "title": "SEND code of practice: 0 to 25 years",
        "url": "https://www.gov.uk/government/publications/send-code-of-practice-0-to-25",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "The GOV.UK publication page was opened on 4 November 2026. It was last updated on 12 September 2024 and points at the January 2015 code. Paragraph 9.62 says the format is agreed locally and that, as a statutory minimum, plans must include sections A to K, separately labelled. Paragraph 9.63 covers preparation for adulthood from year 9. Paragraph 9.69 is about shorter-term targets. It is not the section list.",
    },
    {
        "id": "ukgdpr-art-8",
        "title": "UK GDPR, Article 8",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/8",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Article 8 applies where Article 6(1)(a) consent is the basis, for an information society service offered directly to a child. The UK text sets the age at 13. Article 8(4) says the reference to information society services does not include preventive or counselling services. This starter does not choose a lawful basis and does not offer a service to a child.",
    },
    {
        "id": "ukgdpr-art-9",
        "title": "UK GDPR, Article 9",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/9",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "Article 9(1) prohibits processing special category data, including data concerning health, unless a condition in Article 9(2) applies. SEND advice often includes health. This starter does not assert an Article 9(2) condition. The data protection officer does that before any live file.",
    },
    {
        "id": "cs-harnesses-overview",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "The GitHub Copilot harness is a Copilot Studio authoring and orchestration framework, not the GitHub Copilot service. Customer data is not sent to the GitHub Copilot service when agents run in Copilot Studio. The page does not mark that harness as preview. It describes skills, memory, file creation, and a sandbox. The standard harness follows the topics and rules the maker defines. Skills and memory are listed as 'Not a focus' for the standard harness.",
    },
    {
        "id": "cs-billing-overview",
        "title": "Overview of usage-based billing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/billing-credit-overview",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "For GitHub Copilot harness experiences, Copilot Credits are charged for large language model tokens, tools including knowledge and MCP, and the harness. Unlike the standard harness, which starts billing after publish, the GitHub Copilot harness charges credits from the moment you start building, including testing. A diagram of ranges was on the page. No number from it is copied.",
    },
    {
        "id": "cs-standard-licensing",
        "title": "Standard harness licensing",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing",
        "last_verified": PINNED_ON,
        "stale_applicable": True,
        "reopened_for_this_experiment": True,
        "notes": "A Microsoft 365 Copilot licence lets you use Copilot Studio to build agents for the GitHub Copilot harness. The same page says that, with that licence, classic answers, generative answers, or Microsoft Graph tenant grounding in Copilot Chat, Teams, or SharePoint do not count against the message pack or meter. Those two sentences are not merged. No pack size and no meter rate is copied. The page says the common currency changed from messages to Copilot Credits on 1 September 2025, and that the quantity per prepaid pack and the pay-as-you-go rate did not change. The quantity itself is not stated here.",
    },
    {
        "id": "ico-childrens-code",
        "title": "ICO Children's code, services covered",
        "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/services-covered-by-this-code/",
        "last_verified": None,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "notes": "Direct fetch returned 403 on 4 November 2026. The page was not opened. The code is the Age appropriate design code. Whether section 123 of the Data Protection Act 2018 puts an internal caseworker tool in scope was not verified from the page. The data protection officer decides. This row is not a citation of page text.",
    },
    {
        "id": "catalogue-boundary",
        "title": "Catalogue row UK10",
        "url": "",
        "last_verified": PINNED_ON,
        "stale_applicable": False,
        "reopened_for_this_experiment": False,
        "notes": "Not a Microsoft or legislation page. Autonomy A1. The caseworker authors the final EHCP. Stack in the catalogue: Microsoft Foundry, Azure, and Copilot Studio. This folder does not call Foundry or Azure.",
    },
)


def source_rows(as_of: date, stale_after_days: int) -> list[dict]:
    rows = []
    for source in SOURCES:
        verified = source["last_verified"]
        stale = False
        if source["stale_applicable"] and isinstance(verified, str):
            age = (as_of - date.fromisoformat(verified)).days
            stale = age > stale_after_days
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": verified,
                "stale_applicable": source["stale_applicable"],
                "reopened_for_this_experiment": source["reopened_for_this_experiment"],
                "stale": stale,
                "notes": source["notes"],
            }
        )
    return rows
