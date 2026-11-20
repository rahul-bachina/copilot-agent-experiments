"""Publication-practice pins opened on 20 November 2026.

The briefing core does not download these pages. Statute text below is the
wording read on legislation.gov.uk that day. Section 138L was not opened.
This starter does not decide that a consultation met section 138I.
"""

from __future__ import annotations

from datetime import date

OPENED_ON = date(2026, 11, 20)
SECTION_138I_STAMP = date(2026, 11, 17)
SECTION_138I_URL = "https://www.legislation.gov.uk/ukpga/2000/8/section/138I"
SECTION_138L_OPENED = False

FCA_PUBLICATIONS_URL = "https://www.fca.org.uk/publications"
ICO_CONSULTATIONS_URL = "https://ico.org.uk/about-the-ico/consultations/"
ICO_STAKEHOLDER_URL = "https://ico.org.uk/about-the-ico/ico-and-stakeholder-consultations/"
OFGEM_PUBLICATIONS_URL = "https://www.ofgem.gov.uk/publications"
HOS_HOME_URL = "https://www.housing-ombudsman.org.uk/"
HOS_PUBLICATIONS_URL_TRIED = "https://www.housing-ombudsman.org.uk/publications/"

SECTION_138I_1 = (
    "Before making any rules, the FCA must— (a) consult the PRA, and "
    "(b) after doing so, publish a draft of the proposed rules in the way "
    "appearing to the FCA to be best calculated to bring them to the attention "
    "of the public."
)
SECTION_138I_2E = (
    "notice that representations about the proposals may be made to the FCA "
    "within a specified time."
)
SECTION_138I_3 = (
    "Before making the proposed rules, the FCA must have regard to any "
    "representations made to it in accordance with subsection (2)(e)."
)
SECTION_138I_4 = (
    "If the FCA makes the proposed rules, it must publish an account, in "
    "general terms, of—"
)
SECTION_138I_11 = "This section is subject to section 138L."
SECTION_138I_STAMP_WORDS = (
    "Financial Services and Markets Act 2000, Section 138I is up to date with "
    "all changes known to be in force on or before 17 November 2026. There are "
    "changes that may be brought into force at a future date."
)
SECTION_138I_CAVEAT = (
    "Revised legislation carried on this site may not be fully up to date."
)

FCA_OPEN_CONSULTATIONS = (
    "See our current open consultations and the deadlines for giving feedback."
)
FCA_LIST_NOTE = (
    "The publications page, opened 20 November 2026, has the headings "
    "Open consultations, Latest consultations, and Latest policy and guidance. "
    "Items on that page used the prefixes GC, CP, DP, PS, FS, and FG. "
    "The page did not expand those prefixes. The expansion is unverified."
)
OFGEM_SEARCH_NOTE = (
    "Search our publications for our policies, research, consultations, call "
    "for inputs, guidance, data, news, press releases, and blogs related to "
    "energy regulation."
)
ICO_NOTE = (
    "The consultations URL returned the title Consultation responses and the "
    "heading Consultation responses. It did not show a consultation-close rule "
    "in the text returned on 20 November 2026. No ICO close-date practice is "
    "taken from that page."
)
HOS_NOTE = (
    "The path /publications/ returned 404 on 20 November 2026 and is not cited "
    "as a publications list. The home page linked The Complaint Handling Code "
    "and The Housing Ombudsman Scheme under landlord information. Complaint "
    "Handling Code quotations used here are the pins in Experiment 20, not a "
    "fresh fetch."
)

PINS_CONFIRMED_REASON = (
    "Section 138L was not opened. The section 138I page says revised "
    "legislation may not be fully up to date, and that there are changes that "
    "may be brought into force at a future date. Currency is not confirmed. "
    "This starter does not decide that section 138I was met."
)


def statute_pin(as_of: date) -> dict:
    """The opened section, and an explicit statement that it is not applied."""

    covers = as_of <= SECTION_138I_STAMP
    return {
        "instrument": "Financial Services and Markets Act 2000",
        "section": "138I",
        "url": SECTION_138I_URL,
        "opened_on": OPENED_ON.isoformat(),
        "page_stamp": SECTION_138I_STAMP.isoformat(),
        "page_stamp_words": SECTION_138I_STAMP_WORDS,
        "caveat": SECTION_138I_CAVEAT,
        "covers_question_date": covers,
        "section_138l_opened": SECTION_138L_OPENED,
        "pins_confirmed": False,
        "pins_confirmed_reason": PINS_CONFIRMED_REASON,
        "applied": False,
        "duty_met": None,
        "quotes": {
            "138I(1)": SECTION_138I_1,
            "138I(2)(e)": SECTION_138I_2E,
            "138I(3)": SECTION_138I_3,
            "138I(4)": SECTION_138I_4,
            "138I(11)": SECTION_138I_11,
        },
        "statutory_minimum_days": None,
        "note": (
            "Subsection (2)(e) requires notice of a specified time. It does not "
            "state a number of days. No numeric statutory minimum is applied."
        ),
    }


def practice_pins() -> list[dict]:
    return [
        {
            "id": "fca-publications",
            "url": FCA_PUBLICATIONS_URL,
            "opened_on": OPENED_ON.isoformat(),
            "quote": FCA_OPEN_CONSULTATIONS,
            "note": FCA_LIST_NOTE,
        },
        {
            "id": "ico-consultations",
            "url": ICO_CONSULTATIONS_URL,
            "opened_on": OPENED_ON.isoformat(),
            "quote": None,
            "note": ICO_NOTE,
        },
        {
            "id": "ico-stakeholder",
            "url": ICO_STAKEHOLDER_URL,
            "opened_on": OPENED_ON.isoformat(),
            "quote": None,
            "note": (
                "The stakeholder consultations URL returned a title and no "
                "consultation-close rule on 20 November 2026."
            ),
        },
        {
            "id": "ofgem-publications",
            "url": OFGEM_PUBLICATIONS_URL,
            "opened_on": OPENED_ON.isoformat(),
            "quote": OFGEM_SEARCH_NOTE,
            "note": "The sentence is the search line on the publications page.",
        },
        {
            "id": "hos-home",
            "url": HOS_HOME_URL,
            "opened_on": OPENED_ON.isoformat(),
            "quote": None,
            "note": HOS_NOTE,
        },
    ]
