"""Pins opened on 17 November 2026. The core does not download them.

Anything this file does not quote from a page opened that day is unverified.
"""

from __future__ import annotations

from datetime import date

PINNED_ON = date(2026, 11, 17)
LAST_VERIFIED = "2026-11-17"
STALE_AFTER_DAYS = 90

EA_S19 = "https://www.legislation.gov.uk/ukpga/2010/15/section/19"
EA_S20 = "https://www.legislation.gov.uk/ukpga/2010/15/section/20"
EA_S21 = "https://www.legislation.gov.uk/ukpga/2010/15/section/21"
ERA_PART_6A = "https://www.legislation.gov.uk/ukpga/1996/18/part/6A"
ERA_S63D = "https://www.legislation.gov.uk/ukpga/1996/18/section/63D"
GOVUK_TIME_OFF = "https://www.gov.uk/training-study-work-your-rights"
GOVUK_LEVY_PAY = "https://www.gov.uk/guidance/pay-apprenticeship-levy"
GOVUK_FUNDING = "https://www.gov.uk/guidance/apprenticeship-funding-rules"
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

# Starter refusal list. Not a quotation of section 4.
STARTER_EXTRA_CHARACTERISTICS = ("pregnancy", "maternity")


def source_rows(current: bool) -> list[dict]:
    """Short pins. `taken` is never filled by this starter."""

    rows = [
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
                "or before 17 November 2026."
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
                "information, the steps include an accessible format. Section 20(7): A is not "
                "entitled to require the disabled person to pay A's costs of complying. "
                "The page said it was up to date with changes known to be in force on or "
                "before 16 November 2026."
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
                "16 November 2026."
            ),
        },
        {
            "id": "era-1996-part-6a",
            "title": "Employment Rights Act 1996, Part 6A",
            "url": ERA_PART_6A,
            "opened_on": LAST_VERIFIED,
            "extent": "E+W+S",
            "quote": (
                "Part 6A is headed Study and training, sections 63D to 63K. The page said "
                "it was up to date with all changes known to be in force on or before "
                "17 November 2026. The page did not show a repeal of Part 6A. The footnote "
                "says Part 6A was inserted (6.4.2010 for certain purposes and otherwise "
                "prospective) by the Apprenticeships, Skills, Children and Learning Act 2009, "
                "section 40(2); S.I. 2010/303. That instrument was not opened as its own page. "
                "Section 63D(1): a qualifying employee may make an application. Section 63D(4): "
                "the purpose is to improve the employee's effectiveness in the employer's "
                "business and the performance of the employer's business. Section 63D(5): the "
                "application must state that it is an application under that section. "
                "Section 63F(5): the employer may refuse only if the employer thinks that one "
                "or more of the permissible grounds applies. Section 63I(5), as shown, is six "
                "months, with a footnote that the word was substituted on 1 October 2026 by "
                "the Employment Rights Act 2025, Schedule 12, paragraph 4(19); S.I. 2026/954. "
                "That instrument was not opened as its own page."
            ),
        },
        {
            "id": "govuk-time-off-to-train",
            "title": "Training and study at work: your rights",
            "url": GOVUK_TIME_OFF,
            "opened_on": LAST_VERIFIED,
            "extent": "GOV.UK summary, not the statute",
            "quote": (
                "The page 'Who can and cannot ask for time off to train' stated: staff must "
                "be classed as an employee; they must have worked for their employer for at "
                "least 26 weeks; training must help staff do their job better; at least 250 "
                "people must work in the organisation. It stated that time off is usually "
                "unpaid unless the employer agrees to pay it. It listed who cannot ask, "
                "including an agency worker, the armed forces, compulsory school age, a young "
                "person who already has the right to paid time off, and a person aged 16 to 18 "
                "already expected to take part in education or training. No last-updated date "
                "was in the text returned on 17 November 2026. That date is unverified."
            ),
        },
        {
            "id": "govuk-apprenticeship-levy-pay",
            "title": "Pay Apprenticeship Levy",
            "url": GOVUK_LEVY_PAY,
            "opened_on": LAST_VERIFIED,
            "extent": "HMRC guidance",
            "quote": (
                "Published 12 December 2016. Last updated 6 April 2026, as shown on the page. "
                "Apprenticeship Levy is paid at 0.5% of an employer's annual pay bill. An "
                "employer has to pay it each month if the annual pay bill is more than "
                "£3 million, or if connected companies or charities have a combined annual "
                "pay bill of more than £3 million. The allowance reduces the amount to pay "
                "by £15,000 across the year. Unused allowance cannot be carried into the next "
                "tax year. This page is about paying the levy. It does not say which training "
                "the funds can buy."
            ),
        },
        {
            "id": "govuk-apprenticeship-funding-rules",
            "title": "Funding rules for apprenticeships",
            "url": GOVUK_FUNDING,
            "opened_on": LAST_VERIFIED,
            "extent": "England only, as the collection page stated",
            "quote": (
                "A collection page. It stated that responsibility moved to the Department for "
                "Work and Pensions on 1 April 2026, that the collection applies to England "
                "only, and that there are different funding rules for different apprenticeship "
                "start dates. The current-year link was 'Apprenticeship funding rules: 2026 to "
                "2027', dated 3 August 2026 on that index. That document was not opened. What "
                "the levy can pay for is unverified here."
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
                "Conversation harness, and standard harness. The standard harness follows the "
                "topics and rules the maker defines. The Microsoft Copilot harness is described "
                "for reasoning-heavy work, with skills, memory, file creation, and a sandbox, "
                "billed in Copilot Credits. The page states no price. It does not use the words "
                "GitHub Copilot harness. Older wording that this harness is not the GitHub "
                "Copilot service is unverified against the page opened on this date."
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
