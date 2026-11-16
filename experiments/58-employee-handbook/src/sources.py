"""Statutory pins opened for this starter. The core does not download them.

Opened on 16 November 2026 unless a row says otherwise. Experiment 11's
Employment Rights Act 2025 dates are not copied here. They are read from
that experiment at runtime, and this file records that those pages were
not re-opened on 16 November 2026.
"""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-11-16"
PINNED_ON = date(2026, 11, 16)
STALE_AFTER_DAYS = 90

# Working Time Regulations 1998 (SI 1998/1833). Extent on the pages: E+W+S.
# Regulation 15B was not opened. Do not describe irregular-hours accrual.
WTR_REG_13_URL = "https://www.legislation.gov.uk/uksi/1998/1833/regulation/13"
WTR_REG_13A_URL = "https://www.legislation.gov.uk/uksi/1998/1833/regulation/13A"
WTR_REG_13_1 = (
    "Subject to paragraph (5), a worker is entitled to four weeks' annual "
    "leave in each leave year."
)
WTR_REG_13A_2_E = (
    "in any leave year beginning on or after 1st April 2009, 1.6 weeks."
)
WTR_REG_13A_3 = (
    "The aggregate entitlement provided for in paragraph (2) and regulation "
    "13(1) is subject to a maximum of 28 days."
)
WTR_REG_13_A1 = (
    "Regulation 13 applies to a worker in respect of any leave years "
    "beginning before 1st April 2024, and to a worker to whom regulation "
    "15B does not apply in respect of any leave years beginning on or after "
    "1st April 2024. Regulation 13A(A1) is in the same terms. Regulation "
    "15B was not opened."
)

# GOV.UK summary. This is not the wording of regulation 13.
GOVUK_HOLIDAY_URL = "https://www.gov.uk/holiday-entitlement-rights"
GOVUK_HOLIDAY_NOTE = (
    "The GOV.UK holiday-entitlement page states that almost all people "
    "classed as workers are legally entitled to 5.6 weeks' paid holiday a "
    "year, that most workers who work a 5-day week must receive at least "
    "28 days' paid annual leave, and that statutory paid holiday is limited "
    "to 28 days. It also states that an employer can include bank holidays "
    "as part of statutory annual leave, and that bank or public holidays do "
    "not have to be given as paid leave. That page is a summary. The "
    "four-weeks and 1.6-weeks figures are the regulations."
)

# Employment Rights Act 1996 section 80F, as amended.
ERA_80F_URL = "https://www.legislation.gov.uk/ukpga/1996/18/section/80F"
ERA_80F_PAGE_AS_AT = (
    "The section 80F page said it was up to date with all changes known to "
    "be in force on or before 15 November 2026, and that there are changes "
    "that may be brought into force at a future date."
)
ERA_80F_4_A = (
    "An employee may not make more than two applications under this section "
    "to the same employer during any period of 12 months."
)
ERA_80F_1 = (
    "A qualifying employee may apply to his employer for a change in his "
    "terms and conditions of employment if the change relates to the hours "
    "he is required to work, the times when he is required to work, or "
    "where, as between his home and a place of business of his employer, "
    "he is required to work, or such other aspect as the Secretary of State "
    "may specify by regulations."
)
ERA_80F_2 = (
    "An application under section 80F must state that it is such an "
    "application, and specify the change applied for and the date on which "
    "it is proposed the change should become effective. Subsection (2)(c) "
    "is shown as omitted. The omitted words were not read."
)
# Footnotes F4, F5 and F8 on the section page. The SI 2024/438 page was not opened.
ERA_80F_COMMENCEMENT_NOTE = (
    "The section 80F footnotes attribute the 6 April 2024 amendments of "
    "subsections (2) and (4) to the Employment Relations (Flexible Working) "
    "Act 2023 (c. 33), sections 1(2) and 1(3), and cite S.I. 2024/438, "
    "regulation 2. That statutory instrument was not opened as its own page."
)
ERA_2025_80F_UNVERIFIED = (
    "The section 80F page listed changes and effects yet to be applied, "
    "including provisions of the Employment Rights Act 2025. Those amending "
    "provisions were not opened. This starter does not state them as in force."
)

# Flexible Working (Amendment) Regulations 2023. Original made version.
SI_2023_1328_URL = "https://www.legislation.gov.uk/uksi/2023/1328/made"
SI_2023_1328_NOTE = (
    "Regulation 1 brings the instrument into force on 6 April 2024 and "
    "extends it to England and Wales and Scotland. Regulation 2 omits "
    "regulation 3 of the Flexible Working Regulations 2014. The explanatory "
    "note says the right applies when an employee begins employment, and "
    "that the 26-week condition will not apply to applications made on or "
    "after 6 April 2024."
)

GOVUK_FLEXIBLE_URL = "https://www.gov.uk/flexible-working"
GOVUK_FLEXIBLE_NOTE = (
    "The GOV.UK flexible-working overview says employees can make a request "
    "from the first day in a job, and that employers must deal with requests "
    "in a reasonable manner. It says flexible-working rules are different in "
    "Northern Ireland. It does not state a decision period in the text that "
    "was read. A two-month period is not stated here. The Acas code of "
    "practice on flexible working requests was not opened."
)

# Equality Act 2010. Extent on the pages: E+W+S.
EA_S39_URL = "https://www.legislation.gov.uk/ukpga/2010/15/section/39"
EA_S20_URL = "https://www.legislation.gov.uk/ukpga/2010/15/section/20"
EA_S39_5 = "A duty to make reasonable adjustments applies to an employer."
EA_S39_2 = (
    "An employer must not discriminate against an employee as to terms of "
    "employment, in access to opportunities for promotion, transfer or "
    "training or any other benefit, facility or service, by dismissing the "
    "employee, or by subjecting the employee to any other detriment."
)
EA_S20_3 = (
    "The first requirement is a requirement, where a provision, criterion "
    "or practice puts a disabled person at a substantial disadvantage in "
    "relation to a relevant matter in comparison with persons who are not "
    "disabled, to take such steps as it is reasonable to have to take to "
    "avoid the disadvantage."
)
EA_FUTURE_EFFECTS = (
    "Both section pages listed Employment Rights Act 2025 effects yet to "
    "be applied, including sections 78, 153 and 154 of the Equality Act "
    "2010. Those provisions were not opened. They are not applied here."
)

# Acas landing page opened 16 November 2026. Numbered paragraphs were not on it.
ACAS_LANDING_URL = (
    "https://www.acas.org.uk/acas-code-of-practice-on-disciplinary-and-grievance-procedures"
)
ACAS_LANDING_NOTE = (
    "The landing page says the Acas Code of Practice on disciplinary and "
    "grievance procedures is the minimum an employer should follow, and "
    "that it was published on 11 March 2015. The numbered paragraphs were "
    "not on that page. Paragraph text, where used, is the pin in Experiment "
    "32, last verified there on 4 November 2026, and was not re-opened here."
)

# Experiment 11 pins. Not re-opened on 16 November 2026.
ERA_2025_REOPENED_HERE = False
ERA_2025_EXPERIMENT = "experiments/11-era-2025-hr-assistant"


def source_rows(current: bool) -> list[dict]:
    """Catalogue rows. ``taken`` stays null. The core does not refresh them."""

    rows = [
        ("wtr-reg-13", "Working Time Regulations 1998, regulation 13", WTR_REG_13_URL),
        ("wtr-reg-13a", "Working Time Regulations 1998, regulation 13A", WTR_REG_13A_URL),
        ("govuk-holiday", "GOV.UK, holiday entitlement", GOVUK_HOLIDAY_URL),
        ("era-1996-s80f", "Employment Rights Act 1996, section 80F", ERA_80F_URL),
        ("si-2023-1328", "Flexible Working (Amendment) Regulations 2023", SI_2023_1328_URL),
        ("govuk-flexible", "GOV.UK, flexible working", GOVUK_FLEXIBLE_URL),
        ("ea-2010-s39", "Equality Act 2010, section 39", EA_S39_URL),
        ("ea-2010-s20", "Equality Act 2010, section 20", EA_S20_URL),
        ("acas-landing", "Acas Code of Practice, landing page", ACAS_LANDING_URL),
    ]
    return [
        {
            "id": source_id,
            "title": title,
            "url": url,
            "last_verified": LAST_VERIFIED,
            "stale": not current,
            "taken": None,
            "body_opened": True,
        }
        for source_id, title, url in rows
    ]
