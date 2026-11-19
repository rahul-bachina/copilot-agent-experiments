"""Pages opened on 19 November 2026. The pack builder does not download them again.

A pin is confirmed for a question date only when that date is on or before the
"up to date" stamp on the legislation.gov.uk page. A later question date is
not filled in from today. The ICO recruitment page is a draft under review.
The older employment-practices code is not treated as current guidance.
"""

from __future__ import annotations

from datetime import date

OPENED_ON = "2026-11-19"

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
        "id": "ea-s15",
        "title": "Equality Act 2010, section 15",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/15",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-18",
        "quote": (
            "A person (A) discriminates against a disabled person (B) if A treats "
            "B unfavourably because of something arising in consequence of B's "
            "disability, and A cannot show that the treatment is a proportionate "
            "means of achieving a legitimate aim."
        ),
        "use": (
            "Section 15(1). A question about sickness absence is routed, not decided. "
            "Section 15(2) was read and is not applied."
        ),
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
            "religion or belief, sex, and sexual orientation. Pregnancy and maternity "
            "are not in that list. This starter does not apply the test."
        ),
    },
    {
        "id": "ea-s20",
        "title": "Equality Act 2010, section 20",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/20",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-18",
        "quote": (
            "A person (A) who is subject to a duty to make reasonable adjustments is "
            "not (subject to express provision to the contrary) entitled to require "
            "a disabled person, in relation to whom A is required to comply with the "
            "duty, to pay to any extent A's costs of complying with the duty."
        ),
        "use": (
            "Section 20(7), read with section 20(3) to 20(6). Schedule 8, the applicable "
            "schedule for Part 5, was not opened. This starter does not decide that the "
            "duty arose or that any step was reasonable. A sentence that requires the "
            "candidate to pay is flagged against the opened text of section 20(7)."
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
            "Section 39(1)(a). Section 39(5) says a duty to make reasonable adjustments "
            "applies to an employer. An interview pack can sit inside those arrangements. "
            "This starter does not decide that section 39 was contravened."
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
            "not apply, including a question necessary to establish whether a duty to "
            "make reasonable adjustments is or will be imposed in connection with an "
            "assessment. Section 60(12) says an assessment is an interview or other "
            "process designed to give an indication of a person's suitability. "
            "Section 60(13) says whether or not a person has a disability is an aspect "
            "of that person's health. This starter does not decide that any purpose "
            "in section 60(6) is met. The page stamp was 17 November 2026."
        ),
    },
    {
        "id": "ea-s158",
        "title": "Equality Act 2010, section 158",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/158",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-19",
        "quote": (
            "This Act does not prohibit P from taking any action which is a "
            "proportionate means of achieving the aim of enabling or encouraging "
            "persons who share the protected characteristic to overcome or minimise "
            "that disadvantage, meeting those needs, or enabling or encouraging "
            "persons who share the protected characteristic to participate in that activity."
        ),
        "use": (
            "Section 158(2), read with 158(1). Section 158(4) says the section does not "
            "apply to action within section 159(3). This starter does not decide that "
            "the section permits anything. The page stamp was 19 November 2026."
        ),
    },
    {
        "id": "ea-s159",
        "title": "Equality Act 2010, section 159",
        "url": "https://www.legislation.gov.uk/ukpga/2010/15/section/159",
        "extent": "E+W+S",
        "up_to_date_on_or_before": "2026-11-18",
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
            "that positive action is permitted. The page stamp was 18 November 2026."
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
)


ICO = {
    "recruitment_page": {
        "title": "Employment practices and data protection: recruitment and selection",
        "url": "https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/recruitment-and-selection/",
        "opened_on": OPENED_ON,
        "status": "draft_under_review",
        "final": False,
        "quote": (
            "Our consultation on this draft guidance is now closed. The final version "
            "will be published in due course."
        ),
        "also_on_the_page": (
            "Due to changes made by the Data (Use and Access) Act, this guidance is "
            "under review and may be subject to change."
        ),
        "use": (
            "The page says the guidance covers the process from advertising vacancies "
            "through to deleting information about candidates. It did not set out the "
            "interview-note bullets. It is not treated as final guidance."
        ),
    },
    "employment_practices_code": {
        "title": "The employment practices code",
        "url": "https://ico.org.uk/media2/migrated/1064/the_employment_practices_code.pdf",
        "opened_on": OPENED_ON,
        "status": "unverified as current guidance",
        "final": False,
        "quote_1_5_1": (
            "Ensure that personal information that is recorded and retained following "
            "interview can be justified as relevant to, and necessary for, the recruitment "
            "process itself, or for defending the process against challenge."
        ),
        "quote_access": (
            "Ensure that all interviewers are aware that interviewees may have a right "
            "to request access to their interview notes."
        ),
        "quote_1_7_1": (
            "Establish and adhere to retention periods for recruitment records that are "
            "based on a clear business need."
        ),
        "use": (
            "Paragraphs 1.5.1 and 1.7.1 were read in the PDF. The same PDF refers to a "
            "subject-access fee of up to £10. That fee sentence is not relied on. The "
            "current HTML guidance did not repeat these paragraphs. Their status as "
            "current ICO guidance is unverified."
        ),
    },
}


HARNESS = {
    "title": "Harnesses in Copilot Studio",
    "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
    "opened_on": OPENED_ON,
    "note": (
        "The page names the Microsoft Copilot harness, the Customer Conversation "
        "harness, and the standard harness. The Microsoft Copilot harness is described "
        "for reasoning-heavy multi-step work. The prose says it supports skills and "
        "memory, file creation, and a sandbox, and that agents and workflows on that "
        "harness use Copilot Credits. The comparison table's billing cell for that "
        "harness names a billing overview and does not state a price. The Customer "
        "Conversation row says Copilot Credits (usage-based). The standard-harness "
        "billing cell points at a licensing page that was not opened. No price is "
        "stated. The page does not use the words GitHub Copilot harness. Older wording "
        "that this harness is not the GitHub Copilot service was not on the page. "
        "That point is unverified. The page text that was returned did not show a "
        "last-updated date."
    ),
}


def pin_rows(as_of: date) -> list[dict]:
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
    unconfirmed = [row["id"] for row in pin_rows(as_of) if not row["confirmed_for_question_date"]]
    note = (
        "Equality Act 2010 sections 13, 15, 19, 20, 39, 60, 158, and 159, and "
        f"Schedule 9 paragraph 1, were read on {OPENED_ON}. "
        "This pack does not decide direct discrimination, discrimination arising from "
        "disability, or indirect discrimination. It does not decide that section 20 "
        "was met, that an occupational requirement or positive action is permitted, "
        "or that a health question falls within section 60(6). "
        "Section 19(3) does not list pregnancy and maternity. "
        "Schedule 8 was not opened. Northern Ireland law is not stated. The sections "
        "opened here are marked E+W+S. "
        "The ICO page 'Employment practices and data protection: recruitment and "
        "selection' was opened the same day. It says the consultation on the draft "
        "guidance is closed and the final version will be published in due course, "
        "and that the guidance is under review because of the Data (Use and Access) "
        "Act. Paragraphs 1.5.1 and 1.7.1 of the employment practices code PDF were "
        "read. That code is unverified as current guidance. A subject-access fee "
        "mentioned in the PDF is not relied on. "
        "Interview notes are not sent anywhere by this starter. A retention label and "
        "a legal hold on the inputs are kept. They are not a disposal decision. "
        "Findings are prompts for a person. They are not legal advice."
    )
    if unconfirmed:
        note += " Pins not confirmed for the question date: " + ", ".join(unconfirmed) + "."
    return note
