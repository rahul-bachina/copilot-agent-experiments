"""Pins opened on 18 November 2026. The core does not download them.

Anything this file does not quote from a page opened that day is unverified.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 18)
LAST_VERIFIED = "2026-11-18"
STALE_AFTER_DAYS = 90

EA_S13 = "https://www.legislation.gov.uk/ukpga/2010/15/section/13"
EA_S19 = "https://www.legislation.gov.uk/ukpga/2010/15/section/19"
EA_S20 = "https://www.legislation.gov.uk/ukpga/2010/15/section/20"
EA_S21 = "https://www.legislation.gov.uk/ukpga/2010/15/section/21"
EA_S39 = "https://www.legislation.gov.uk/ukpga/2010/15/section/39"
UK_GDPR_A5 = "https://www.legislation.gov.uk/eur/2016/679/article/5"
UK_GDPR_A22 = "https://www.legislation.gov.uk/eur/2016/679/article/22"
UK_GDPR_A22A = "https://www.legislation.gov.uk/eur/2016/679/article/22A"
DUAA_S80 = "https://www.legislation.gov.uk/ukpga/2025/18/section/80"
HARNESS = "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview"

# Section 19(3) as read on the section 19 page. Pregnancy and maternity are
# not in that list. Section 4 of the Act was not opened.
SECTION_19_CHARACTERISTICS = (
    "age",
    "disability",
    "gender reassignment",
    "marriage and civil partnership",
    "race",
    "religion or belief",
    "sex",
    "sexual orientation",
)

# Starter refusal list. Not a quotation of section 4. Length of service is
# treated as an age proxy when someone asks the tool to infer suitability.
STARTER_EXTRA_CHARACTERISTICS = (
    "pregnancy",
    "maternity",
    "length of service",
    "years of service",
    "part-time",
    "part time",
    "sickness",
)


def source_rows(current: bool) -> list[dict]:
    """Short pins. `taken` is never filled by this starter."""

    rows = [
        {
            "id": "ea-2010-s13",
            "title": "Equality Act 2010, section 13",
            "url": EA_S13,
            "opened_on": LAST_VERIFIED,
            "extent": "E+W+S",
            "quote": (
                "Section 13(1): a person (A) discriminates against another (B) if, "
                "because of a protected characteristic, A treats B less favourably than "
                "A treats or would treat others. Section 13(2): if the protected "
                "characteristic is age, A does not discriminate against B if A can show "
                "A's treatment of B to be a proportionate means of achieving a legitimate "
                "aim. This starter does not apply that justification and does not decide "
                "that treatment was less favourable. The page said it was up to date with "
                "all changes known to be in force on or before 18 November 2026."
            ),
        },
        {
            "id": "ea-2010-s19",
            "title": "Equality Act 2010, section 19",
            "url": EA_S19,
            "opened_on": LAST_VERIFIED,
            "extent": "E+W+S",
            "quote": (
                "Section 19(1): a person (A) discriminates against another (B) if A applies "
                "to B a provision, criterion or practice which is discriminatory in relation "
                "to a relevant protected characteristic of B's. Section 19(2)(d): A cannot "
                "show it to be a proportionate means of achieving a legitimate aim. "
                "Section 19(3) lists age, disability, gender reassignment, marriage and "
                "civil partnership, race, religion or belief, sex, and sexual orientation. "
                "The page said it was up to date with all changes known to be in force on "
                "or before 18 November 2026."
            ),
        },
        {
            "id": "ea-2010-s20",
            "title": "Equality Act 2010, section 20",
            "url": EA_S20,
            "opened_on": LAST_VERIFIED,
            "extent": "E+W+S",
            "quote": (
                "Section 20(3) is the first requirement, where a provision, criterion or "
                "practice puts a disabled person at a substantial disadvantage. Section 20(4) "
                "is the physical-feature requirement. Section 20(5) is the auxiliary-aid "
                "requirement. Section 20(6): where the first or third requirement relates to "
                "the provision of information, the steps include an accessible format. "
                "Section 20(7): A is not entitled to require the disabled person to pay A's "
                "costs of complying. The page said it was up to date with changes known to "
                "be in force on or before 16 November 2026. That banner date is what the "
                "page showed when it was opened on 18 November 2026."
            ),
        },
        {
            "id": "ea-2010-s21",
            "title": "Equality Act 2010, section 21",
            "url": EA_S21,
            "opened_on": LAST_VERIFIED,
            "extent": "E+W+S",
            "quote": (
                "Section 21(1): a failure to comply with the first, second or third "
                "requirement is a failure to comply with a duty to make reasonable "
                "adjustments. Section 21(2): A discriminates against a disabled person if "
                "A fails to comply with that duty in relation to that person. The page said "
                "it was up to date with changes known to be in force on or before "
                "18 November 2026."
            ),
        },
        {
            "id": "ea-2010-s39",
            "title": "Equality Act 2010, section 39",
            "url": EA_S39,
            "opened_on": LAST_VERIFIED,
            "extent": "E+W+S",
            "quote": (
                "Section 39 is headed Employees and applicants. Section 39(2): an employer "
                "(A) must not discriminate against an employee of A's (B) in the ways the "
                "subsection lists, including section 39(2)(b), access to opportunities for "
                "promotion, transfer or training or for receiving any other benefit, "
                "facility or service. Section 39(5): a duty to make reasonable adjustments "
                "applies to an employer. This starter does not decide that access was "
                "afforded or refused. The page said it was up to date with all changes "
                "known to be in force on or before 18 November 2026."
            ),
        },
        {
            "id": "uk-gdpr-article-5",
            "title": "UK GDPR Article 5",
            "url": UK_GDPR_A5,
            "opened_on": LAST_VERIFIED,
            "extent": "UK GDPR, as amended",
            "quote": (
                "Article 5(1)(b), as shown: personal data shall be collected (whether from "
                "the data subject or otherwise) for specified, explicit and legitimate "
                "purposes and not further processed by or on behalf of a controller in a "
                "manner that is incompatible with the purposes for which the controller "
                "collected the data ('purpose limitation'). Article 5(3), as shown: for the "
                "avoidance of doubt, processing is not lawful by virtue only of being "
                "processing in a manner that is compatible with the purposes for which the "
                "personal data was collected. The footnotes name the Data (Use and Access) "
                "Act 2025, section 71, and S.I. 2026/82. That instrument was not opened as "
                "its own page. The extract returned on 18 November 2026 did not include an "
                "Equality Act-style revision-date banner. That banner date is unverified. "
                "Article 6 was not opened."
            ),
        },
        {
            "id": "uk-gdpr-article-22",
            "title": "UK GDPR Article 22",
            "url": UK_GDPR_A22,
            "opened_on": LAST_VERIFIED,
            "extent": "UK GDPR, as amended",
            "quote": (
                "The Article 22 page showed the body omitted. The textual amendment says "
                "Chapter 3 Section 4A was substituted for Article 22 by the Data (Use and "
                "Access) Act 2025, section 80(1), in force at 5 February 2026 in so far as "
                "not already in force by S.I. 2026/82, regulation 2(j). That instrument was "
                "not opened as its own page. The old Article 22 wording was not on the page "
                "and is not quoted here."
            ),
        },
        {
            "id": "uk-gdpr-article-22a",
            "title": "UK GDPR Article 22A",
            "url": UK_GDPR_A22A,
            "opened_on": LAST_VERIFIED,
            "extent": "UK GDPR, as amended",
            "quote": (
                "Article 22A(1): for the purposes of Articles 22B and 22C, a decision is "
                "based solely on automated processing if there is no meaningful human "
                "involvement in the taking of the decision, and a decision is a significant "
                "decision if it produces a legal effect or a similarly significant effect "
                "for the data subject. Article 22A(2): when considering meaningful human "
                "involvement, a person must consider, among other things, the extent to "
                "which the decision is reached by means of profiling. This starter does not "
                "take a selection decision and does not decide whether a vacancy note would "
                "be a significant decision."
            ),
        },
        {
            "id": "duaa-2025-s80",
            "title": "Data (Use and Access) Act 2025, section 80",
            "url": DUAA_S80,
            "opened_on": LAST_VERIFIED,
            "extent": "UK",
            "quote": (
                "Section 80(1) substitutes Articles 22A, 22B, 22C, and 22D for Article 22 "
                "of the UK GDPR. Article 22B restricts a significant decision based solely "
                "on automated processing in the cases the article states. Article 22C(2) "
                "requires safeguards which provide information, enable representations, "
                "enable human intervention, and enable the data subject to contest the "
                "decision. The commencement note says section 80 is in force at 5 February "
                "2026 in so far as not already in force, by S.I. 2026/82, regulation 2(j). "
                "That instrument was not opened as its own page. This starter does not "
                "decide that those safeguards were met."
            ),
        },
        {
            "id": "copilot-studio-harnesses",
            "title": "Harnesses in Copilot Studio",
            "url": HARNESS,
            "opened_on": LAST_VERIFIED,
            "extent": "Microsoft Learn",
            "quote": (
                "The page names three harnesses: Microsoft Copilot harness, Customer "
                "Conversation harness, and standard harness. The standard harness follows "
                "the topics and rules the maker defines. The Microsoft Copilot harness is "
                "described for reasoning-heavy work, with skills, memory, file creation, "
                "and a sandbox, billed in Copilot Credits. The page states no price. It "
                "does not use the words GitHub Copilot harness. Older wording that this "
                "harness is not the GitHub Copilot service is unverified against the page "
                "opened on this date."
            ),
        },
    ]
    for row in rows:
        row["rules_current"] = current
        row["refreshed_from_the_web"] = False
        row["taken"] = None
        row["applied_to_a_person"] = False
    return rows


def pins_current(as_of: date) -> bool:
    age = (as_of - PINNED_ON).days
    return 0 <= age <= STALE_AFTER_DAYS
