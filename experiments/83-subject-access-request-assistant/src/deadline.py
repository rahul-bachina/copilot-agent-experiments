"""Illustrate the one-month period. Do not decide that the deadline was met.

Article 12A(1) says the applicable time period is one month beginning with the
relevant time. The ICO page opened on 27 November 2026 says to count forward
to the same date in the following month, and to move a weekend or public
holiday to the next working day. Public holidays are not applied here. The
Banking and Financial Dealings Act 1971 was not opened.

Both readings are returned. Neither is selected.
"""

from __future__ import annotations

from datetime import date, timedelta

if __package__ in {None, ""}:
    from dates import add_months, as_date, day_before, parse_date, shift_weekend, with_question_date
else:
    from .dates import add_months, as_date, day_before, parse_date, shift_weekend, with_question_date


def read_structured_date(value: object, question: date) -> dict:
    if value is None or value == "":
        return {"present": False, "iso": None, "usable": False, "coerced": False, "reason": "missing"}
    reading = with_question_date(parse_date(value), question)
    usable = as_date(reading) is not None
    return {
        "present": True,
        "iso": reading.get("iso") if usable else None,
        "usable": usable,
        "ambiguous": reading.get("ambiguous") is True,
        "unparseable": reading.get("unparseable") is True,
        "future": reading.get("future") is True,
        "reason": reading.get("reason"),
        "coerced": False,
    }


def _iso(day: date | None) -> str | None:
    return day.isoformat() if isinstance(day, date) else None


def illustrate(
    *,
    received: dict,
    identity: dict,
    fee: dict,
    clarification_asked: dict,
    clarification_received: dict,
    regime: str,
    extension_candidate: bool,
    question: date,
) -> dict:
    """Return both month readings. deadline_decided stays false."""

    problems = []
    received_day = as_date({"iso": received.get("iso"), "unparseable": not received.get("usable"), "ambiguous": False})
    if received_day is None:
        problems.append("received_date_not_usable")
    identity_day = as_date({"iso": identity.get("iso"), "unparseable": not identity.get("usable"), "ambiguous": False}) if identity.get("present") else None
    fee_day = as_date({"iso": fee.get("iso"), "unparseable": not fee.get("usable"), "ambiguous": False}) if fee.get("present") else None
    for label, row in (
        ("identity", identity),
        ("fee", fee),
        ("clarification_asked", clarification_asked),
        ("clarification_received", clarification_received),
        ("received", received),
    ):
        if row.get("present") and not row.get("usable"):
            problems.append(f"{label}_not_usable")
        if row.get("future"):
            problems.append(f"{label}_future")

    law_enforcement = regime == "law_enforcement"
    relevant_parts: list[str] = []
    relevant = received_day
    if received_day is not None:
        relevant_parts.append("receipt")
    identity_applied = False
    fee_applied = False
    if not law_enforcement:
        if identity_day is not None and (relevant is None or identity_day > relevant):
            relevant = identity_day
            identity_applied = True
            relevant_parts.append("article_12a_2_b")
        elif identity_day is not None:
            relevant_parts.append("article_12a_2_b_not_later")
        if fee_day is not None and (relevant is None or fee_day > relevant):
            relevant = fee_day
            fee_applied = True
            relevant_parts.append("article_12a_2_c")
        elif fee_day is not None:
            relevant_parts.append("article_12a_2_c_not_later")
    else:
        if identity.get("present"):
            problems.append("section_52_not_opened_identity_not_applied")
        if fee.get("present"):
            problems.append("section_53_not_opened_fee_not_applied")

    ico_before = add_months(relevant, 1) if relevant is not None else None
    ico_end, weekend_moved = shift_weekend(ico_before) if ico_before is not None else (None, False)
    beginning_with = day_before(ico_before) if ico_before is not None else None
    readings_differ = (
        ico_end is not None and beginning_with is not None and ico_end != beginning_with
    )

    asked = as_date({
        "iso": clarification_asked.get("iso"),
        "unparseable": not clarification_asked.get("usable"),
        "ambiguous": False,
    }) if clarification_asked.get("present") else None
    got = as_date({
        "iso": clarification_received.get("iso"),
        "unparseable": not clarification_received.get("usable"),
        "ambiguous": False,
    }) if clarification_received.get("present") else None
    pause_applied = False
    paused_open = False
    paused_days = None
    if asked is not None and got is not None:
        if got < asked:
            problems.append("clarification_received_before_it_was_asked")
        else:
            paused_days = (got - asked).days + 1
            pause_applied = True
    elif asked is not None and got is None:
        paused_open = True
        problems.append("clarification_not_yet_received")

    illustrated = None
    if ico_end is not None and pause_applied and paused_days is not None and not paused_open:
        illustrated, _moved = shift_weekend(ico_end + timedelta(days=paused_days))
    elif ico_end is not None and not paused_open:
        illustrated = ico_end

    extended = None
    if relevant is not None and extension_candidate:
        extended_before = add_months(relevant, 3)
        extended, _moved = shift_weekend(extended_before)

    return {
        "regime": regime,
        "statute": (
            "Data Protection Act 2018 section 54, read with section 45"
            if law_enforcement
            else "UK GDPR Article 12A, read with Article 12(3)"
        ),
        "relevant_time": _iso(relevant),
        "relevant_time_parts": relevant_parts,
        "identity_date_applied": identity_applied,
        "fee_date_applied": fee_applied,
        "fee_decided_by_agent": False,
        "ico_same_date": _iso(ico_before),
        "ico_end_after_weekend_only": _iso(ico_end),
        "weekend_shift_applied": weekend_moved,
        "public_holidays_applied": False,
        "beginning_with_day_before_corresponding_date": _iso(beginning_with),
        "readings_differ": readings_differ,
        "deadline_selected": None,
        "deadline_decided": False,
        "illustrated_end_if_pause_confirmed": _iso(illustrated) if not paused_open else None,
        "clock_paused_open": paused_open,
        "pause_days_if_both_dates_usable": paused_days,
        "pause_applied_as_a_decision": False,
        "pause_is_illustrative": pause_applied or paused_open,
        "extension_candidate": extension_candidate,
        "extension_applied": False,
        "extension_notice_sent": False,
        "candidate_three_month_end": _iso(extended),
        "problems": problems,
        "coerced": False,
        "may_be_relied_on": False,
        "question_date": question.isoformat(),
    }
