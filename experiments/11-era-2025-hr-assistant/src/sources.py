"""Pinned sources for the Employment Rights Act 2025 HR checklist.

The review does not download these pages. A person opened them on
27 October 2026. Update last_verified only after opening the page again.

Sections 20 to 22 of the Employment Rights Act 2025 were marked prospective
on that day. SI 2026/1065 regulation 3 appoints them for 30 October 2026.
No regulations specifying "reasonable steps" under the new Equality Act 2010
section 40B were opened. Acas examples are not that list.
"""

from __future__ import annotations

from datetime import date

LAST_VERIFIED = "2026-10-27"
DEFAULT_STALE_AFTER_DAYS = 90
DEFAULT_POLICY_STALE_AFTER_DAYS = 365

# Equality Act 2010 s.40A inserted (26.10.2024) by the Worker Protection
# (Amendment of Equality Act 2010) Act 2023. The section page states the date.
REASONABLE_STEPS_IN_FORCE = date(2024, 10, 26)

# Employment Rights Act 2025 ss.20, 21 and 22. SI 2026/1065 reg. 3(a)-(c).
ALL_REASONABLE_STEPS_IN_FORCE = date(2026, 10, 30)
THIRD_PARTY_IN_FORCE = date(2026, 10, 30)
SPECIFY_STEPS_POWER_IN_FORCE = date(2026, 10, 30)

# Section 23 commencement line: in force 6 April 2026 by SI 2026/323 reg. 3.
# The SI page itself was not opened.
WHISTLEBLOWING_IN_FORCE = date(2026, 4, 6)

# Section 152, by SI 2026/954 reg. 3, subject to reg. 4.
TRIBUNAL_LIMITS_IN_FORCE = date(2026, 10, 1)

# Section 25 remainder, by SI 2026/559 reg. 3, subject to reg. 4.
UNFAIR_DISMISSAL_IN_FORCE = date(2027, 1, 1)

# The power in section 22 is not a list of steps. None were opened.
SPECIFIED_STEPS_REGULATIONS_MADE = False

# GOV.UK timeline, updated 22 October 2026. The instrument was not opened.
SCOTLAND_CONTRACT_TIMELINE_DATE = "2026-11-09"
SCOTLAND_CONTRACT_INSTRUMENT_OPENED = False

# Same timeline. Not a commencement instrument this starter applies.
NDA_TIMETABLE = "September 2027"
NDA_INSTRUMENT_OPENED = False

ACAS_URL = (
    "https://www.acas.org.uk/employment-rights-act-2025/"
    "harassment-law-changes/sexual-harassment"
)
ACAS_UPDATED = "2026-08-26"

# Preparation examples on the Acas page. Not a statutory list.
ACAS_PROMPTS: list[dict] = [
    {
        "id": "policies_reviewed",
        "prompt": "Review and update existing policies.",
    },
    {
        "id": "standalone_sexual_harassment_policy_considered",
        "prompt": "Consider whether a standalone sexual harassment policy is useful for the organisation.",
    },
    {
        "id": "reporting_routes_other_than_line_manager",
        "prompt": "Give workers more than one way to report sexual harassment.",
    },
    {
        "id": "sexual_harassment_training_recorded",
        "prompt": "Provide sexual harassment training suited to the organisation.",
    },
    {
        "id": "prevention_steps_recorded",
        "prompt": "Keep steps in place to prevent sexual harassment, rather than only responding to it.",
    },
]

SOURCES: list[dict] = [
    {
        "id": "ea-2010-s40a",
        "title": "Equality Act 2010, section 40A",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/40A",
        "page_as_at": "2026-10-27",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 27 October 2026. Section 40A(1): an employer must take "
            "reasonable steps to prevent sexual harassment of employees in "
            "the course of their employment. Inserted (26.10.2024) by the "
            "Worker Protection (Amendment of Equality Act 2010) Act 2023. "
            "The changes list shows Employment Rights Act 2025 section 20 "
            "as not yet applied to the text."
        ),
    },
    {
        "id": "era-2025-s20",
        "title": "Employment Rights Act 2025, section 20",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/20",
        "page_as_at": "2026-10-27",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 27 October 2026. The page was marked prospective. It "
            "inserts 'all' before 'reasonable steps' in section 40A(1). "
            "The changes box cites SI 2026/1065 regulation 3(a)."
        ),
    },
    {
        "id": "era-2025-s21",
        "title": "Employment Rights Act 2025, section 21",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/21",
        "page_as_at": "2026-10-27",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 27 October 2026. Prospective. Inserts Equality Act 2010 "
            "section 40(1A) to (1C). An employer permits third-party "
            "harassment only if the third party harasses the employee in "
            "the course of employment and the employer failed to take all "
            "reasonable steps. Extent England and Wales and Scotland. "
            "Commencement: SI 2026/1065 regulation 3(b)."
        ),
    },
    {
        "id": "era-2025-s22",
        "title": "Employment Rights Act 2025, section 22",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/22",
        "page_as_at": "2026-10-27",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 27 October 2026. Prospective. Inserts Equality Act 2010 "
            "section 40B, a power for regulations to specify steps that are "
            "to be regarded as reasonable. Commencement: SI 2026/1065 "
            "regulation 3(c). No regulations made under that power were opened."
        ),
    },
    {
        "id": "si-2026-1065-reg-3",
        "title": "Employment Rights Act 2025 (Commencement No. 6 and Transitional and Saving Provisions) Regulations 2026, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/2026/1065/regulation/3/made",
        "page_as_at": "2026-10-30",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Regulation 3 brings sections 20, 21 and 22 into force on "
            "30 October 2026. The same regulation commences other provisions. "
            "This checklist does not apply those other provisions."
        ),
    },
    {
        "id": "era-2025-s23",
        "title": "Employment Rights Act 2025, section 23",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/23",
        "page_as_at": "2026-04-06",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Opened 27 October 2026. Inserts sexual harassment into the "
            "qualifying disclosures in section 43B of the Employment Rights "
            "Act 1996. The page says the section is in force on 6 April 2026 "
            "by SI 2026/323 regulation 3. That SI was not opened as its own page."
        ),
    },
    {
        "id": "era-2025-s25",
        "title": "Employment Rights Act 2025, section 25",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/25",
        "page_as_at": "2026-10-27",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Substitutes 'six months' for 'two years' in section 108 of the "
            "Employment Rights Act 1996, and omits section 124. Not in force "
            "at Royal Assent. The page shows section 25(5) in force on "
            "1 July 2026 for specified purposes by SI 2026/559 regulation 2. "
            "The remainder is appointed for 1 January 2027. This checklist "
            "does not apply the 1 July power."
        ),
    },
    {
        "id": "si-2026-559-reg-3",
        "title": "Employment Rights Act 2025 (Commencement No. 4 and Transitional and Saving Provisions) Regulations 2026, regulation 3",
        "url": "https://www.legislation.gov.uk/uksi/2026/559/regulation/3/made",
        "page_as_at": "2027-01-01",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Section 25, to the extent not already in force, and Schedule 3, "
            "come into force on 1 January 2027, subject to regulation 4. "
            "This checklist does not decide an effective date of termination "
            "and does not apply regulation 4 to a person."
        ),
    },
    {
        "id": "era-2025-s152",
        "title": "Employment Rights Act 2025, section 152",
        "url": "https://www.legislation.gov.uk/ukpga/2025/36/section/152",
        "page_as_at": "2026-10-01",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Schedule 12 increases employment tribunal time limits in Great "
            "Britain from three months to six months, and in certain cases "
            "industrial tribunals in Northern Ireland. The page says the "
            "section is in force on 1 October 2026 by SI 2026/954 regulation 3, "
            "with regulation 4. This checklist does not state Northern Ireland "
            "law and does not count a time limit. The Northern Ireland limb "
            "of Schedule 12 was not applied."
        ),
    },
    {
        "id": "si-2026-954",
        "title": "Employment Rights Act 2025 (Commencement No. 5 and Transitional Provisions) (Amendment) Regulations 2026",
        "url": "https://www.legislation.gov.uk/uksi/2026/954/body/made",
        "page_as_at": "2026-10-01",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Regulation 3: section 152 and Schedule 12 come into force on "
            "1 October 2026, subject to regulation 4. Regulation 4: the "
            "amendments do not apply where the relevant date is before "
            "1 October 2026. This checklist does not identify a relevant date."
        ),
    },
    {
        "id": "govuk-timeline",
        "title": "Plan to Make Work Pay and Employment Rights Act: timeline update",
        "url": (
            "https://www.gov.uk/government/publications/"
            "implementing-the-plan-to-make-work-pay-and-employment-rights-act/"
            "plan-to-make-work-pay-and-employment-rights-act-timeline-update"
        ),
        "page_as_at": "2026-10-22",
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Updated 22 October 2026. Confirms the harassment measures for "
            "30 October 2026, tribunal limits on 1 October 2026, and the "
            "unfair-dismissal qualifying period and removal of the "
            "compensatory-award cap on 1 January 2027. It says breach of "
            "employment contract claims in Scotland change on 9 November 2026. "
            "That instrument was not opened. It says future dates remain "
            "subject to parliamentary processes. Non-disclosure-agreement "
            "regulations are listed for September 2027 and were not opened."
        ),
    },
    {
        "id": "acas-sexual-harassment",
        "title": "Acas: sexual harassment law changes",
        "url": ACAS_URL,
        "page_as_at": ACAS_UPDATED,
        "last_verified": LAST_VERIFIED,
        "body_opened": True,
        "notes": (
            "Last updated 26 August 2026. From 30 October 2026 the page "
            "describes a move from 'reasonable steps' to 'all reasonable "
            "steps', and lists preparation examples. Those examples are not "
            "regulations under section 40B. The page's worked examples are "
            "not applied to a pack. Acas is not a substitute for the statute."
        ),
    },
]
