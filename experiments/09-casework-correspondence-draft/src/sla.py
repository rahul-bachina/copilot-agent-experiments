"""Casework reply clock.

Cabinet Office, Guide to Handling Correspondence, September 2024, paragraph 9,
PDF retrieved 26 October 2026:

- Departments and agencies should set a deadline, with ministerial agreement,
  for ministerial and public correspondence.
- That deadline should not exceed 20 working days.
- The clock (the first working day) starts the day after the correspondence
  is received.

Paragraph 20: a holding reply does not clear the case or count towards
performance. The original deadline remains. This module does not move the
date because a letter asks for a holding reply.

Paragraph 21 times a transfer request, and the other department's reply to
that request, from the transfer. This module does not send a transfer, so
those dates are not calculated.

Paragraph 40: FOI performance is recorded separately from correspondence.
The Government Correspondence Hub, retrieved 26 October 2026, also says
correspondence is separate from FOI, SAR, and complaints processes. When the
letter is on an information-rights route, this clock does not produce a due
date. It does not calculate a Freedom of Information Act deadline. Experiment
01 is the FOI triage starter.

The Guide is written for government departments and agencies. A council's own
published target is not given the 20-working-day ceiling. The caller passes
regime "council" and the council's number. This module does not invent a
council statutory deadline.

The Guide does not define "working day". See working_days.py.
"""

from __future__ import annotations

from datetime import date, timedelta

from working_days import closed_days_covering, nth_working_day_from

GUIDE_TITLE = "Guide to Handling Correspondence"
GUIDE_EDITION = "September 2024"
GUIDE_URL = (
    "https://assets.publishing.service.gov.uk/media/66d99762608fb761b681111d/"
    "Guide_to_Handling_Correspondence_-_September_2024__1_.pdf"
)
GUIDE_RETRIEVED_ON = "2026-10-26"
HUB_URL = "https://www.gov.uk/guidance/government-correspondence-hub"
HUB_RETRIEVED_ON = "2026-10-26"
CEILING_WORKING_DAYS = 20

COUNTING_RULE = (
    "The first working day is the first England and Wales working day on or "
    "after the calendar day after receipt. Cabinet Office Guide to Handling "
    "Correspondence, September 2024, paragraph 9. PDF retrieved 26 October 2026. "
    "The Guide does not define working day. This count uses the England and "
    "Wales bank-holiday calendar in working_days.py."
)


def reply_due_on(received_on: date, working_days: int, closed: set[date] | None = None) -> date:
    """Due date for a confirmed target. Day 1 is the day after receipt, if open."""
    if working_days < 1:
        raise ValueError("working_days must be at least 1")
    if closed is None:
        horizon = received_on + timedelta(days=working_days * 2 + 30)
        closed = closed_days_covering([received_on, horizon])
    return nth_working_day_from(received_on + timedelta(days=1), working_days, closed)


def calculate_casework_sla(
    received_on: date,
    *,
    regime: str,
    target_working_days: int | None,
    target_confirmed: bool,
    channel_confirmed: bool,
    information_rights: bool,
    extra_closed: tuple[date, ...] = (),
    cancel_bank_holiday: tuple[date, ...] = (),
) -> dict:
    """Return a clock result. A date is operative only when a person has confirmed it."""
    if regime not in {"central_government", "council"}:
        raise ValueError("regime must be central_government or council")

    horizon = received_on + timedelta(days=80)
    closed = closed_days_covering([received_on, horizon], extra_closed, cancel_bank_holiday)
    ceiling_applies = regime == "central_government"

    result = {
        "regime": regime,
        "target_working_days": target_working_days,
        "target_confirmed": target_confirmed,
        "channel_confirmed": channel_confirmed,
        "operative": False,
        "operative_due_on": None,
        "reference_due_on": None,
        "ceiling_working_days": CEILING_WORKING_DAYS if ceiling_applies else None,
        "ceiling_applies": ceiling_applies,
        "reason": None,
        "counting_rule": COUNTING_RULE,
        "holding_reply_clears_deadline": False,
        "holding_reply_note": (
            "Guide paragraph 20, retrieved 26 October 2026. A holding reply does "
            "not clear the case. This clock does not move the date, and the agent "
            "does not send a holding reply."
        ),
        "transfer_clocks_calculated": False,
        "transfer_note": (
            "Guide paragraph 21 times a transfer request (within one working day) "
            "and the receiving department's response (three working days for "
            "ministerial correspondence, five for public correspondence) from the "
            "transfer. This agent does not send a transfer, so those dates are "
            "not calculated. Paragraph 24's three-working-day contribution is "
            "also not calculated."
        ),
        "calendar": (
            "England and Wales bank holidays, plus any extra closed dates the "
            "author passed. Scotland and Northern Ireland are not encoded."
        ),
        "guide": {
            "title": GUIDE_TITLE,
            "edition": GUIDE_EDITION,
            "url": GUIDE_URL,
            "retrieved_on": GUIDE_RETRIEVED_ON,
            "paragraphs": [9, 20, 21, 40],
        },
        "correspondence_hub": {
            "url": HUB_URL,
            "retrieved_on": HUB_RETRIEVED_ON,
            "note": (
                "The hub says departments will aim to respond within 20 working "
                "days, and that correspondence is separate from FOI, SAR, and "
                "complaints processes. Page last updated 25 September 2026 on "
                "the copy retrieved 26 October 2026."
            ),
        },
    }

    if information_rights:
        result["reason"] = "information_rights_clock_is_separate"
        result["information_rights_note"] = (
            "Guide paragraph 40: FOI performance is recorded separately from "
            "correspondence. This clock is not a Freedom of Information Act or "
            "subject-access deadline. Experiment 01 triages those requests. "
            "No correspondence due date is returned, so it cannot be mistaken "
            "for the statutory clock."
        )
        return result

    if regime == "council" and target_working_days is None:
        result["reason"] = "council_target_not_supplied"
        result["council_note"] = (
            "The September 2024 Guide is for government departments and agencies. "
            "It is not applied as a council's statutory deadline. Pass the "
            "council's own published target."
        )
        return result

    if target_working_days is None:
        result["reason"] = "target_not_confirmed"
        result["reference_due_on"] = reply_due_on(
            received_on, CEILING_WORKING_DAYS, closed
        ).isoformat()
        result["reference_note"] = (
            "20 working days is the Guide paragraph 9 ceiling, shown as a "
            "reference only. It is not this department's confirmed target."
        )
        return result

    if target_working_days < 1:
        result["reason"] = "invalid_target"
        return result

    if ceiling_applies and target_working_days > CEILING_WORKING_DAYS:
        result["reason"] = "exceeds_cabinet_office_ceiling"
        result["ceiling_note"] = (
            "Guide paragraph 9 says the deadline should not exceed 20 working "
            "days. A longer target is not returned as a date."
        )
        return result

    reference = reply_due_on(received_on, target_working_days, closed).isoformat()
    result["reference_due_on"] = reference

    if not target_confirmed or not channel_confirmed:
        result["reason"] = "target_or_channel_not_confirmed"
        result["reference_note"] = (
            "The date is arithmetic from the inputs. It is not operative until "
            "the author confirms both the channel and the target."
        )
        return result

    result["operative"] = True
    result["operative_due_on"] = reference
    if regime == "council":
        result["council_note"] = (
            "Operative only as the council target the author confirmed. The "
            "Cabinet Office 20-working-day ceiling is not applied as a council rule."
        )
    return result
