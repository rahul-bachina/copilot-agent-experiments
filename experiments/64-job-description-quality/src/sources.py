"""Pages opened on 18 November 2026. The checker does not download them again.

A pin is confirmed for a question date only when that date is on or before the
"up to date" stamp on the page. A later question date is not filled in from
today. Disability Confident was not opened. The order under the Immigration,
Asylum and Nationality Act 2006, section 15(3), was not opened.
"""

from __future__ import annotations

from datetime import date

OPENED_ON = "2026-11-18"

PINS: tuple[dict, ...] = (
    {
        "id": "ea-s13",
        "title": "Equality Act 2010, section 13",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/13",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-18",
        "quote": (
            "A person (A) discriminates against another (B) if, because of a "
            "protected characteristic, A treats B less favourably than A treats "
            "or would treat others."
        ),
        "use": "Section 13(1). This starter does not decide that less favourable treatment occurred.",
    },
    {
        "id": "ea-s19",
        "title": "Equality Act 2010, section 19",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/19",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-18",
        "quote": (
            "A person (A) discriminates against another (B) if A applies to B a "
            "provision, criterion or practice which is discriminatory in relation "
            "to a relevant protected characteristic of B's."
        ),
        "use": (
            "Section 19(1) and 19(2), including 19(2)(d). Section 19(3) lists age, "
            "disability, gender reassignment, marriage and civil partnership, race, "
            "religion or belief, sex, and sexual orientation. This starter does not "
            "apply that test."
        ),
    },
    {
        "id": "ea-s39",
        "title": "Equality Act 2010, section 39",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/39",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-18",
        "quote": (
            "An employer (A) must not discriminate against a person (B) in the "
            "arrangements A makes for deciding to whom to offer employment."
        ),
        "use": (
            "Section 39(1)(a), with 39(1)(b) and 39(1)(c) also on the page. "
            "A job advert can sit inside those arrangements. This starter does not "
            "decide that section 39 was contravened."
        ),
    },
    {
        "id": "ea-s60",
        "title": "Equality Act 2010, section 60",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/60",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-17",
        "quote": (
            "A person (A) to whom an application for work is made must not ask about "
            "the health of the applicant (B) before offering work to B, or, where A "
            "is not in a position to offer work to B, before including B in a pool "
            "of applicants from whom A intends (when in a position to do so) to "
            "select a person to whom to offer work."
        ),
        "use": (
            "Section 60(1). Section 60(6) lists purposes for which the section does "
            "not apply. This starter does not decide that any of those purposes is met. "
            "The page stamp was 17 November 2026, not 18 November."
        ),
    },
    {
        "id": "ea-s159",
        "title": "Equality Act 2010, section 159",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/159",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-15",
        "quote": (
            "But subsection (2) applies only if (a) A is as qualified as B to be "
            "recruited or promoted, (b) P does not have a policy of treating persons "
            "who share the protected characteristic more favourably in connection "
            "with recruitment or promotion than persons who do not share it, and "
            "(c) taking the action in question is a proportionate means of achieving "
            "the aim referred to in subsection (2)."
        ),
        "use": (
            "Section 159(4), read with 159(1) to 159(3). This starter does not decide "
            "that positive action is permitted. The page stamp was 15 November 2026."
        ),
    },
    {
        "id": "ea-sch9-p1",
        "title": "Equality Act 2010, Schedule 9, paragraph 1",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/schedule/9/paragraph/1",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-14",
        "quote": (
            "A person (A) does not contravene a provision mentioned in sub-paragraph (2) "
            "by applying in relation to work a requirement to have a particular protected "
            "characteristic, if A shows that, having regard to the nature or context of "
            "the work (a) it is an occupational requirement, (b) the application of the "
            "requirement is a proportionate means of achieving a legitimate aim, and "
            "(c) the person to whom A applies the requirement does not meet it (or A has "
            "reasonable grounds for not being satisfied that the person meets it)."
        ),
        "use": (
            "Schedule 9, paragraph 1(1). This starter does not decide that the paragraph "
            "is met. The page stamp was 14 November 2026."
        ),
    },
    {
        "id": "iana-s15",
        "title": "Immigration, Asylum and Nationality Act 2006, section 15",
        "url": "https://www.legislation.gov.uk/ukpga/2006/13/section/15",
        "extent": "U.K.",
        "up_to_date_on_or_before": "2026-11-16",
        "quote": (
            "It is contrary to this section to employ an adult subject to immigration "
            "control if he has not been granted leave to enter or remain in the United "
            "Kingdom, or his leave is invalid, has ceased to have effect, or is subject "
            "to a condition preventing him from accepting the employment."
        ),
        "use": (
            "Section 15(1) and 15(2), as context for why a right-to-work statement is "
            "kept. Section 15(2) allows a penalty notice. The prescribed requirements "
            "under section 15(3) were not opened. This starter does not check any "
            "person's leave and does not give a penalty. The page stamp was 16 November 2026."
        ),
    },
)


HARNESS = {
    "title": "Harnesses in Copilot Studio",
    "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
    "opened_on": OPENED_ON,
    "note": (
        "The page names the Microsoft Copilot harness, the Customer Conversation "
        "harness, and the standard harness. The Microsoft Copilot harness is described "
        "for reasoning-heavy multi-step work, with skills, memory, file creation, and "
        "a sandbox, and the prose says agents on that harness use Copilot Credits. "
        "No price is stated. The page does not use the words GitHub Copilot harness. "
        "Older wording that this harness is not the GitHub Copilot service was not on "
        "the page. That point is unverified."
    ),
}


def pin_rows(as_of: date) -> list[dict]:
    """One row per opened section. A later question date is not treated as covered."""

    rows = []
    for pin in PINS:
        stamp = date.fromisoformat(pin["up_to_date_on_or_before"])
        rows.append(
            {
                "id": pin["id"],
                "title": pin["title"],
                "url": pin["url"],
                "extent": pin["extent"],
                "up_to_date_on_or_before": pin["up_to_date_on_or_before"],
                "confirmed_for_question_date": as_of <= stamp,
                "quote": pin["quote"],
                "use": pin["use"],
            }
        )
    return rows


def statutory_note(as_of: date) -> str:
    """Fixed note. It is not legal advice and it does not decide a case."""

    unconfirmed = [
        row["id"] for row in pin_rows(as_of) if not row["confirmed_for_question_date"]
    ]
    note = (
        "Equality Act 2010 sections 13, 19, 39, 60, and 159, and Schedule 9 paragraph 1, "
        f"were read on {OPENED_ON}. Section 13(1), section 19(1) and 19(2), section 39(1), "
        "section 60(1), section 159(4), and Schedule 9 paragraph 1(1) are quoted in the pins. "
        "This review does not decide direct or indirect discrimination, does not decide that "
        "an occupational requirement or positive action is permitted, and does not decide "
        "that a health question falls within section 60(6). "
        "Immigration, Asylum and Nationality Act 2006 section 15(1) and 15(2) are context "
        "for keeping a right-to-work statement. The order under section 15(3) was not opened. "
        "No person's leave is checked and no penalty is given. "
        "The Equality Act sections opened here are marked E+W+S. Northern Ireland law is not stated. "
        "The Disability Confident scheme page was not opened. A statement the organisation's "
        "guide marks as mandated is kept because the guide says so. "
        "Findings are prompts for a person. They are not legal advice."
    )
    if unconfirmed:
        note += (
            " These pins are not confirmed for the question date, because the page stamp "
            "is earlier: " + ", ".join(unconfirmed) + "."
        )
    return note
