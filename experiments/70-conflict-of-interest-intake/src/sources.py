"""Pages opened on 20 November 2026. The core does not download them.

Currency: the extracts did not show an "up to date on or before" date.
Sections 81 to 83 said there are currently no known outstanding effects, and
that revised legislation may not be fully up to date. Article 5 and Article 9
showed the same class of currency warning, or no banner in the extract.
Those dates are unverified. The quotes are context for the ethics team.
This starter does not decide that a conflict exists, and it does not prepare
a conflicts assessment.
"""

from __future__ import annotations

OPENED_ON = "2026-11-20"

QUOTE_81_1 = (
    "A contracting authority must take all reasonable steps to identify, and "
    "keep under review, in relation to a covered procurement any— "
    "(a) conflicts of interest, or "
    "(b) potential conflicts of interest."
)
QUOTE_81_2 = (
    "There is a conflict of interest in relation to a covered procurement if— "
    "(a) a person acting for or on behalf of the contracting authority in "
    "relation to the procurement has a conflict of interest, or "
    "(b) a Minister acting in relation to the procurement has a conflict of interest."
)
QUOTE_81_4_INTEREST = (
    "“interest” includes a personal, professional or financial interest and "
    "may be direct or indirect"
)
QUOTE_82_1 = (
    "A contracting authority must take all reasonable steps to ensure that a "
    "conflict of interest does not put a supplier at an unfair advantage or "
    "disadvantage in relation to a covered procurement."
)
QUOTE_82_4 = (
    "The contracting authority must in relation to the award— "
    "(a) treat the supplier as an excluded supplier for the purpose of— "
    "(i) assessing tenders under section 19 (competitive award), or "
    "(ii) awarding a contract under section 41 or 43 (direct award), and "
    "(b) exclude the supplier from participating in, or progressing as part of, "
    "any competitive tendering procedure."
)
QUOTE_83_1 = (
    "Before publishing a tender or transparency notice in relation to a "
    "covered procurement, a contracting authority must prepare a conflicts "
    "assessment in relation to the procurement."
)
QUOTE_83_3 = (
    "A conflicts assessment must include details of— "
    "(a) conflicts or potential conflicts of interest identified in accordance "
    "with section 81 (duty to identify), and "
    "(b) any steps the contracting authority has taken or will take for the "
    "purposes of section 82 (duty to mitigate)."
)
QUOTE_5_1_C = (
    "adequate, relevant and limited to what is necessary in relation to the "
    "purposes for which they are processed (‘data minimisation’);"
)
QUOTE_9_1 = (
    "Processing of personal data revealing racial or ethnic origin, political "
    "opinions, religious or philosophical beliefs, or trade union membership, "
    "and the processing of genetic data, biometric data for the purpose of "
    "uniquely identifying a natural person, data concerning health or data "
    "concerning a natural person's sex life or sexual orientation shall be prohibited."
)

PINS = (
    {
        "id": "pa2023-s81",
        "title": "Procurement Act 2023, section 81",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/81",
        "quotes": [QUOTE_81_1, QUOTE_81_2, QUOTE_81_4_INTEREST],
        "in_force": "24 February 2025, by S.I. 2024/716, Schedule, as amended by S.I. 2024/959, regulations 1(2) and 2(7)(a).",
        "extent_on_page": "U.K.",
        "outstanding_effects_on_page": "There are currently no known outstanding effects for the Procurement Act 2023, Section 81.",
        "currency_stamp": None,
        "currency_verified": False,
        "note": "Section 81(3) and the Minister definition were read and are not applied. This starter does not identify a conflict.",
    },
    {
        "id": "pa2023-s82",
        "title": "Procurement Act 2023, section 82",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/82",
        "quotes": [QUOTE_82_1, QUOTE_82_4],
        "in_force": "24 February 2025, by S.I. 2024/716, Schedule, as amended by S.I. 2024/959, regulations 1(2) and 2(7)(a).",
        "extent_on_page": "U.K.",
        "outstanding_effects_on_page": "There are currently no known outstanding effects for the Procurement Act 2023, Section 82.",
        "currency_stamp": None,
        "currency_verified": False,
        "note": "Section 82(4) is what a contracting authority must do in the case the section describes. This starter does not treat anyone as an excluded supplier. Sections 19, 41, and 43 were not opened.",
    },
    {
        "id": "pa2023-s83",
        "title": "Procurement Act 2023, section 83",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/83",
        "quotes": [QUOTE_83_1, QUOTE_83_3],
        "in_force": "24 February 2025, by S.I. 2024/716, Schedule, as amended by S.I. 2024/959, regulations 1(2) and 2(7)(a).",
        "extent_on_page": "U.K.",
        "outstanding_effects_on_page": "There are currently no known outstanding effects for the Procurement Act 2023, Section 83.",
        "currency_stamp": None,
        "currency_verified": False,
        "note": "Subsections (2) and (4) to (8) were read. A conflicts assessment is not prepared here. Section 80(3), section 55, and the notice types were not opened.",
    },
    {
        "id": "ukgdpr-art5",
        "title": "UK GDPR, Article 5",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/5",
        "quotes": [QUOTE_5_1_C],
        "in_force": None,
        "extent_on_page": None,
        "outstanding_effects_on_page": None,
        "currency_stamp": None,
        "currency_verified": False,
        "note": "Article 5(1)(c) is context for minimisation. The extract showed no 'up to date on or before' date. Article 5(1)(a), (b), (d), (e), (f), Article 5(2), and Article 5(3) were in the extract. Article 84B was not opened. This starter does not decide that Article 5 was met. Article 6 was not opened.",
    },
    {
        "id": "ukgdpr-art9",
        "title": "UK GDPR, Article 9",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/9",
        "quotes": [QUOTE_9_1],
        "in_force": None,
        "extent_on_page": None,
        "outstanding_effects_on_page": "There are currently no known outstanding effects by UK legislation for Regulation (EU) 2016/679, Article 9.",
        "currency_stamp": None,
        "currency_verified": False,
        "note": "Article 9(1) lists the special categories. A family relationship is not in that list. Political opinions are. Paragraphs 2 to 5 were in the extract and are not applied. This starter does not decide that a condition was met.",
    },
)


def statute_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "for_ethics_team_only": True,
        "decides_conflict": False,
        "conflicts_assessment_prepared": False,
        "article_5_met": False,
        "article_9_condition_met": False,
        "currency_verified": False,
        "pins": list(PINS),
    }
