"""Statutory pins opened on 17 November 2026. Nothing here is downloaded at runtime.

A pin quotes a page that was opened. A section that was not opened is named
and is not paraphrased into a rule. Northern Ireland employment legislation
was not opened.
"""

from __future__ import annotations

from datetime import date, timedelta

OPENED_ON = date(2026, 11, 17)
STALE_AFTER_DAYS = 180
STALE_AFTER = OPENED_ON + timedelta(days=STALE_AFTER_DAYS)

ERA_S1_URL = "https://www.legislation.gov.uk/ukpga/1996/18/section/1"
ERA_S1_BANNER = "16 November 2026"
ERA_S1_1 = (
    "Where a worker begins employment with an employer, the employer shall "
    "give to the worker a written statement of particulars of employment."
)
ERA_S1_2_B = "the statement must be given not later than the beginning of the employment."
ERA_S1_2_SUBJECT = "Subject to sections 2(2) to (4)"
ERA_S1_EXTENT = "E+W+S"
ERA_S1_FOOTNOTE = (
    "The footnote on section 1(2) attributes the substitution, in force on "
    "6 April 2020, to the Employment Rights (Employment Particulars and Paid "
    "Annual Leave) (Amendment) Regulations 2018 (S.I. 2018/1378), regulations "
    "1 and 3(a). That instrument was not opened as its own page."
)
ERA_S2_UNOPENED = "Employment Rights Act 1996 sections 2(2) to 2(4) were not opened."

GOVUK_STATEMENT_URL = (
    "https://www.gov.uk/employment-contracts-and-conditions/written-statement-of-employment-particulars"
)
GOVUK_STATEMENT = (
    "The employer must provide the principal statement on the first day of "
    "employment and the wider written statement within 2 months of the start "
    "of employment."
)

IANA_S15_URL = "https://www.legislation.gov.uk/ukpga/2006/13/section/15"
IANA_S15_BANNER = "16 November 2026"
IANA_S15_EXTENT = "U.K."
IANA_S15_1 = (
    "It is contrary to this section to employ an adult subject to immigration control if—"
    "(a) he has not been granted leave to enter or remain in the United Kingdom, or "
    "(b) his leave to enter or remain in the United Kingdom— "
    "(i) is invalid, "
    "(ii) has ceased to have effect (whether by reason of curtailment, revocation, "
    "cancellation, passage of time or otherwise), or "
    "(iii) is subject to a condition preventing him from accepting the employment."
)
IANA_S15_3 = (
    "An employer is excused from paying a penalty if he shows that he complied "
    "with any prescribed requirements in relation to the employment."
)
IANA_S15_7_D = (
    "Section 15(7)(d): require action to be taken before employment begins. "
    "The words sit under section 15(7), which says an order prescribing "
    "requirements for the purposes of subsection (3) may, in particular, do so."
)

HO_GUIDE_URL = "https://www.gov.uk/government/publications/right-to-work-checks-employers-guide"
HO_GUIDE_UPDATED = "1 October 2026"
HO_GUIDE_HTML = (
    "This guidance explains what employers must do to prevent illegal working "
    "in the UK by carrying out right to work checks on people before employing "
    "them to make sure they are allowed to work."
)
HO_PDF_UNOPENED = (
    "The PDF 'Employer's guide to right to work checks: 1 October 2026' "
    "(83 pages) was not opened. No paragraph number from that PDF is cited."
)

EA_S20_URL = "https://www.legislation.gov.uk/ukpga/2010/15/section/20"
EA_S20_BANNER = "16 November 2026"
EA_S20_3 = (
    "The first requirement is a requirement, where a provision, criterion or "
    "practice of A's puts a disabled person at a substantial disadvantage in "
    "relation to a relevant matter in comparison with persons who are not "
    "disabled, to take such steps as it is reasonable to have to take to avoid "
    "the disadvantage."
)
EA_SCHEDULE_8_UNOPENED = "Schedule 8 (Part 5, work) was not opened."

EA_S39_URL = "https://www.legislation.gov.uk/ukpga/2010/15/section/39"
EA_S39_BANNER = "17 November 2026"
EA_S39_5 = "A duty to make reasonable adjustments applies to an employer."

UKGDPR_A13_URL = "https://www.legislation.gov.uk/eur/2016/679/article/13"
UKGDPR_A13_1 = (
    "Where personal data relating to a data subject are collected from the "
    "data subject, the controller shall, at the time when personal data are "
    "obtained, provide the data subject with all of the following information:"
)
UKGDPR_A13_1_A = (
    "the identity and the contact details of the controller and, where "
    "applicable, of the controller's representative"
)
UKGDPR_A13_4 = (
    "Paragraphs 1, 2 and 3 do not apply to the extent that the data subject "
    "already has the information."
)
UKGDPR_BANNER_SEEN = False
ICO_UNVERIFIED = (
    "An ICO privacy-notice page was not opened. A request on 17 November 2026 "
    "returned 404. No ICO sentence is cited."
)


def _row(
    pin_id: str,
    title: str,
    url: str,
    quotation: str,
    *,
    banner: str | None,
    extent: str | None,
    verified: bool,
    unverified: list[str],
    as_of: date,
) -> dict:
    stale = as_of > STALE_AFTER
    before_pin = as_of < OPENED_ON
    return {
        "pin_id": pin_id,
        "title": title,
        "url": url,
        "quotation": quotation,
        "opened_on": OPENED_ON.isoformat(),
        "legislation_banner": banner,
        "extent": extent,
        "verified_text": verified,
        "unverified": unverified,
        "complete": verified and not unverified,
        "stale": stale,
        "point_in_time_text_verified": False if before_pin else not stale,
        "applied_to_a_person": False,
        "may_be_relied_on": verified and not unverified and not stale and not before_pin,
    }


def pins_for(topics: set[str], as_of: date) -> list[dict]:
    """Return only the pins the checklist or the question actually needs."""

    rows: list[dict] = []
    if "statement" in topics:
        rows.append(
            _row(
                "era-1996-s1",
                "Employment Rights Act 1996, section 1",
                ERA_S1_URL,
                ERA_S1_1 + " Section 1(2)(b): " + ERA_S1_2_B,
                banner=ERA_S1_BANNER,
                extent=ERA_S1_EXTENT,
                verified=True,
                unverified=[ERA_S1_FOOTNOTE, ERA_S2_UNOPENED],
                as_of=as_of,
            )
        )
        rows.append(
            _row(
                "govuk-written-statement",
                "GOV.UK, written statement of employment particulars",
                GOVUK_STATEMENT_URL,
                GOVUK_STATEMENT,
                banner=None,
                extent=None,
                verified=True,
                unverified=[
                    "This is the GOV.UK summary. It is not the text of section 2.",
                    ERA_S2_UNOPENED,
                ],
                as_of=as_of,
            )
        )
    if "right_to_work" in topics:
        rows.append(
            _row(
                "iana-2006-s15",
                "Immigration, Asylum and Nationality Act 2006, section 15",
                IANA_S15_URL,
                IANA_S15_1 + " " + IANA_S15_3 + " " + IANA_S15_7_D,
                banner=IANA_S15_BANNER,
                extent=IANA_S15_EXTENT,
                verified=True,
                unverified=[
                    "The prescribed requirements are in an order under section 15(3). That order was not opened."
                ],
                as_of=as_of,
            )
        )
        rows.append(
            _row(
                "home-office-rtw-html",
                "Right to work checks: an employer's guide (HTML page)",
                HO_GUIDE_URL,
                HO_GUIDE_HTML,
                banner=None,
                extent=None,
                verified=True,
                unverified=[
                    f"The HTML page said last updated {HO_GUIDE_UPDATED}.",
                    HO_PDF_UNOPENED,
                ],
                as_of=as_of,
            )
        )
    if "adjustment" in topics:
        rows.append(
            _row(
                "ea-2010-s39-5",
                "Equality Act 2010, section 39(5)",
                EA_S39_URL,
                EA_S39_5,
                banner=EA_S39_BANNER,
                extent="E+W+S",
                verified=True,
                unverified=["Not applied to a person. This starter does not decide that a step is reasonable."],
                as_of=as_of,
            )
        )
        rows.append(
            _row(
                "ea-2010-s20-3",
                "Equality Act 2010, section 20(3)",
                EA_S20_URL,
                EA_S20_3,
                banner=EA_S20_BANNER,
                extent="E+W+S",
                verified=True,
                unverified=[EA_SCHEDULE_8_UNOPENED, "Sections 20(4) and 20(5) were read and are not applied to a person."],
                as_of=as_of,
            )
        )
    if "privacy" in topics:
        rows.append(
            _row(
                "ukgdpr-art-13",
                "UK GDPR, Article 13",
                UKGDPR_A13_URL,
                UKGDPR_A13_1 + ": " + UKGDPR_A13_1_A + ". " + UKGDPR_A13_4,
                banner=None,
                extent=None,
                verified=True,
                unverified=[
                    "A currency banner of the kind shown on the Act pages was not in the text returned for Article 13.",
                    ICO_UNVERIFIED,
                    "Article 6 and Article 9 are not asserted.",
                ],
                as_of=as_of,
            )
        )
    return rows
