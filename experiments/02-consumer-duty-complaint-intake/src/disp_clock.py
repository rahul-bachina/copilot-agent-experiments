#!/usr/bin/env python3
"""Deterministic DISP timescale calculator. England and Wales edition.

Dates are computed here, in code. A language model must not supply them.

The Handbook text was read on 24 October 2026. DISP 1.6 on that date showed
a future version dated 25 October 2027. This module does not encode that
future text.

This is a calculation aid for a complaints handler. It is not a decision,
and it is not legal advice.
"""

from __future__ import annotations

import argparse
import json
import sys
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")

# Handbook pages opened on 24 October 2026.
REFERENCES: dict[str, str] = {
    "DISP 1.5": "https://handbook.fca.org.uk/handbook/disp1/disp1s5",
    "DISP 1.6": "https://www.handbook.fca.org.uk/handbook/DISP/1/6.html",
    "DISP 2.8": "https://www.handbook.fca.org.uk/handbook/DISP/2/8.html",
    "business day": "https://handbook.fca.org.uk/glossary/G120",
    "complaint": "https://handbook.fca.org.uk/glossary/G197",
    "PRIN 2A.1": "https://www.handbook.fca.org.uk/handbook/PRIN/2A/1.html",
    "England and Wales bank holidays": "https://www.gov.uk/bank-holidays",
}

ROUTES = ("general", "psd", "emd", "mixed")
PSD_ROUTES = ("psd", "emd", "mixed")


@dataclass(frozen=True)
class Deadline:
    """One calculated date and the rule it comes from."""

    name: str
    on: date | None
    rule: str
    operative: bool
    note: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "on": self.on.isoformat() if self.on else None,
            "rule": self.rule,
            "operative": self.operative,
            "note": self.note,
        }


def easter_sunday(year: int) -> date:
    """Gregorian Computus. Anonymous algorithm, valid for Gregorian years."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = ((h + ell - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _first_monday(year: int, month: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(0 - first.weekday()) % 7)


def _last_monday(year: int, month: int) -> date:
    last = date(year, month, monthrange(year, month)[1])
    return last - timedelta(days=(last.weekday() - 0) % 7)


def statutory_england_and_wales_bank_holidays(year: int) -> frozenset[date]:
    """Standing England and Wales bank holidays for one calendar year.

    Built from the pattern published on GOV.UK (weekends move to a substitute
    weekday, normally the following Monday, with the Christmas/Boxing Day
    collision). One-off proclaimed days are not included. A bank holiday that
    was moved by proclamation (for example early May 2020, or the late spring
    bank holiday in 2022) is returned on its usual Monday unless the caller
    passes an override.

    Weekend Christmas Day or Boxing Day stays in the set. Those dates are
    already non-business days because they are a Saturday or Sunday.
    """
    days: set[date] = set()
    easter = easter_sunday(year)
    days.add(easter - timedelta(days=2))  # Good Friday
    days.add(easter + timedelta(days=1))  # Easter Monday
    days.add(_first_monday(year, 5))
    days.add(_last_monday(year, 5))
    days.add(_last_monday(year, 8))

    new_year = date(year, 1, 1)
    days.add(new_year)
    if new_year.weekday() == 5:
        days.add(date(year, 1, 3))
    elif new_year.weekday() == 6:
        days.add(date(year, 1, 2))

    christmas = date(year, 12, 25)
    boxing = date(year, 12, 26)
    days.add(christmas)
    days.add(boxing)
    if christmas.weekday() == 5:
        # Christmas Saturday, Boxing Sunday: Monday and Tuesday.
        days.add(date(year, 12, 27))
        days.add(date(year, 12, 28))
    elif christmas.weekday() == 6:
        # Christmas Sunday, Boxing Monday: Christmas substitute is Tuesday.
        days.add(date(year, 12, 27))
    elif boxing.weekday() == 5:
        # Christmas Friday, Boxing Saturday: substitute Monday.
        days.add(date(year, 12, 28))
    elif boxing.weekday() == 6:
        days.add(date(year, 12, 28))
    return frozenset(days)


def weekday_bank_holidays(year: int) -> frozenset[date]:
    """Statutory bank holidays that fall on a weekday, including substitutes."""
    return frozenset(
        day for day in statutory_england_and_wales_bank_holidays(year) if day.weekday() < 5
    )


def _as_dates(values: Iterable[date] | None) -> set[date]:
    return set(values or ())


def england_wales_closed_days(
    around: date,
    extra_non_business_days: Iterable[date] = (),
    cancelled_bank_holidays: Iterable[date] = (),
) -> set[date]:
    """Bank holidays for the years a clock starting at `around` can touch."""
    closed: set[date] = set()
    for year in range(around.year - 1, around.year + 3):
        closed.update(statutory_england_and_wales_bank_holidays(year))
    closed.update(extra_non_business_days)
    closed.difference_update(cancelled_bank_holidays)
    return closed


def is_england_wales_business_day(day: date, closed: set[date]) -> bool:
    """Glossary 'business day' (1)(a) for something done in England and Wales.

    Any day which is not a Saturday or Sunday, Christmas Day, Good Friday or
    a bank holiday in that part of the United Kingdom. Christmas Day and
    Good Friday are bank holidays in England and Wales, so they are in
    `closed` as well as being excluded by the glossary words.
    """
    return day.weekday() < 5 and day not in closed


def add_business_days(start: date, count: int, is_open) -> date:
    """The date `count` open days after `start`. `start` itself is not counted."""
    if count < 1:
        raise ValueError("count must be at least 1")
    current = start
    remaining = count
    guard = 0
    while remaining:
        current += timedelta(days=1)
        guard += 1
        if guard > 3660:
            raise RuntimeError("business-day walk exceeded 10 years")
        if is_open(current):
            remaining -= 1
    return current


def add_calendar_months(start: date, months: int) -> date:
    """Corresponding date, or the last day of the month if that day does not exist."""
    if months < 0:
        raise ValueError("months must be >= 0")
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    last_day = monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day))


def receipt_date(received_on: date | datetime) -> tuple[date, str | None]:
    """London calendar date of receipt, and a note if the input was naive."""
    if isinstance(received_on, datetime):
        if received_on.tzinfo is None:
            return received_on.date(), (
                "A naive datetime was treated as a calendar date with no zone "
                "conversion. Pass a timezone-aware datetime so a receipt near "
                "midnight is read in Europe/London."
            )
        return received_on.astimezone(LONDON).date(), None
    if isinstance(received_on, date):
        return received_on, None
    raise TypeError("received_on must be a date or datetime")


def fos_referral_deadline(response_sent_on: date) -> date:
    """Last day to refer on the reading that the six-month anniversary is in time.

    DISP 2.8.2R(1): the Ombudsman cannot consider a complaint referred more
    than six months after the date the final response, redress determination
    or summary resolution communication was sent. Referral on the anniversary
    is not 'more than' six months after that date.
    """
    return add_calendar_months(response_sent_on, 6)


def longstop_dates(
    event_complained_of: date | None,
    complainant_aware_on: date | None,
) -> dict:
    """DISP 2.8.2R(2). Does not apply the exceptions in DISP 2.8.2R(3) to (5)."""
    six_year = (
        add_calendar_months(event_complained_of, 72) if event_complained_of else None
    )
    three_year = (
        add_calendar_months(complainant_aware_on, 36) if complainant_aware_on else None
    )
    candidates = [day for day in (six_year, three_year) if day is not None]
    later = max(candidates) if candidates else None
    return {
        "six_years_after_event": six_year.isoformat() if six_year else None,
        "three_years_after_awareness": three_year.isoformat() if three_year else None,
        "later_of_the_two": later.isoformat() if later else None,
        "rule": "DISP 2.8.2R(2)",
        "awareness_is_a_human_judgement": complainant_aware_on is None,
        "exceptions_not_applied": [
            "DISP 2.8.2R(3) exceptional circumstances, which the Ombudsman decides",
            "DISP 2.8.2R(4) Ombudsman Transitional Order",
            "DISP 2.8.2R(5) respondent consent, which cannot be withdrawn once given",
            "The written-acknowledgement saving in DISP 2.8.2R(2)",
        ],
    }


def calculate_disp_clock(
    received_on: date | datetime,
    route: str = "general",
    *,
    exceptional_circumstances: bool = False,
    extra_non_business_days: Iterable[date] = (),
    cancelled_bank_holidays: Iterable[date] = (),
    psp_closed_dates: Iterable[date] | None = None,
    response_sent_on: date | None = None,
    event_complained_of: date | None = None,
    complainant_aware_on: date | None = None,
) -> dict:
    """Calculate DISP clocks for one complaint.

    `route` is a classification the handler has confirmed. This function does
    not decide it.

    `exceptional_circumstances` is a human flag for DISP 1.6.2AR(2). It is
    ignored for a general complaint. The default is false.

    `psp_closed_dates` are days the payment service provider is not open for
    business as required for the execution of a payment transaction. That is
    the business day in glossary limb (3), which applies in DISP 1.6.2A and
    DISP 2.8. Pass None if the firm's opening calendar is not known. The
    15-day and 35-day dates are then a non-operative reference count on the
    England and Wales bank-holiday calendar.
    """
    if route not in ROUTES:
        raise ValueError(f"route must be one of {ROUTES}")
    if exceptional_circumstances and route == "general":
        exceptional_note = (
            "exceptional_circumstances was set on a general complaint. "
            "DISP 1.6.2AR(2) applies to an EMD complaint or a PSD complaint. "
            "The eight-week date was not extended."
        )
        exceptional_circumstances = False
    else:
        exceptional_note = None

    received, receipt_note = receipt_date(received_on)
    closed = england_wales_closed_days(
        received, extra_non_business_days, cancelled_bank_holidays
    )

    def handbook_open(day: date) -> bool:
        return is_england_wales_business_day(day, closed)

    summary_on = add_business_days(received, 3, handbook_open)
    eight_weeks_on = received + timedelta(weeks=8)

    psp_known = psp_closed_dates is not None
    psp_closed = _as_dates(psp_closed_dates)

    def psp_open(day: date) -> bool:
        return day not in psp_closed

    if route in PSD_ROUTES:
        if psp_known:
            day_15 = add_business_days(received, 15, psp_open)
            day_35 = add_business_days(received, 35, psp_open)
            psd_operative = True
            psd_calendar = "caller-supplied PSP opening days"
        else:
            day_15 = add_business_days(received, 15, handbook_open)
            day_35 = add_business_days(received, 35, handbook_open)
            psd_operative = False
            psd_calendar = (
                "england-and-wales reference only; not the DISP 1.6.2A business day"
            )
    else:
        day_15 = None
        day_35 = None
        psd_operative = False
        psd_calendar = None

    deadlines: list[Deadline] = [
        Deadline(
            name="Summary resolution route closes",
            on=summary_on,
            rule="DISP 1.5.1R",
            operative=True,
            note=(
                "Close of the third business day following the day of receipt. "
                "The day of receipt is not counted. 'Close of business' is not "
                "given an hour in DISP 1.5, so this is a date. The route applies "
                "only if the complainant has indicated acceptance (DISP 1.5.2AR). "
                "This function does not decide acceptance. A summary resolution "
                "communication must still be sent (DISP 1.5.4R)."
            ),
        ),
        Deadline(
            name="Prompt acknowledgement",
            on=None,
            rule="DISP 1.6.1R",
            operative=True,
            note=(
                "A prompt written acknowledgement is required. DISP 1.6.1R does "
                "not set a number of days. No acknowledgement deadline has been invented."
            ),
        ),
    ]

    if route == "general":
        deadlines.append(
            Deadline(
                name="Final or other written response",
                on=eight_weeks_on,
                rule="DISP 1.6.2R",
                operative=True,
                note=(
                    "By the end of eight weeks after receipt. Eight weeks is "
                    "fifty-six days. The date is not moved if it falls on a "
                    "weekend or bank holiday. DISP 1.6.4R can disapply DISP 1.6.2R "
                    "where the complainant has already accepted a qualifying "
                    "response in writing. That is a human judgement, and it does "
                    "not apply here unless the handler records it outside this clock."
                ),
            )
        )
    else:
        part = "the PSD or EMD part" if route == "mixed" else "this complaint"
        deadlines.append(
            Deadline(
                name="Eight-week written response",
                on=eight_weeks_on,
                rule="DISP 1.6.2R",
                operative=route == "mixed",
                note=(
                    "DISP 1.6.2R is subject to DISP 1.6.2AR. "
                    + (
                        "For a mixed complaint the eight-week clock still applies "
                        "to the part that is not an EMD or PSD complaint, unless "
                        "the firm chooses to treat the whole complaint under "
                        "DISP 1.6.2AR. This function does not make that choice."
                        if route == "mixed"
                        else "DISP 1.6.2R does not set the final-response deadline for an EMD or PSD complaint."
                    )
                ),
            )
        )
        holding = exceptional_circumstances
        deadlines.append(
            Deadline(
                name="15-business-day final response" if not holding else "Holding response",
                on=day_15,
                rule="DISP 1.6.2AR(1)" if not holding else "DISP 1.6.2AR(2)(a)",
                operative=psd_operative,
                note=(
                    f"Counted for {part}. Fifteen business days after the day of "
                    f"receipt. Calendar used: {psd_calendar}. "
                    + (
                        "Operative only because the caller supplied PSP closed dates."
                        if psp_known
                        else "Not operative until the handler supplies the days the PSP is closed."
                    )
                    + (
                        " A human has flagged exceptional circumstances, so this "
                        "date is the holding-response deadline, not the final response."
                        if holding
                        else " This is the final-response deadline unless a human flags exceptional circumstances."
                    )
                ),
            )
        )
        deadlines.append(
            Deadline(
                name="35-business-day final response",
                on=day_35,
                rule="DISP 1.6.2AR(2)(b)",
                operative=psd_operative and exceptional_circumstances,
                note=(
                    "Available only in exceptional circumstances beyond the firm's "
                    "control, which a human must decide and record. The holding "
                    "response has to give the reasons and this deadline. "
                    f"Calendar used: {psd_calendar}."
                ),
            )
        )

    if route in ("psd", "emd") and psp_known:
        final_on = day_35 if exceptional_circumstances else day_15
        final_rule = "DISP 1.6.2AR(2)(b)" if exceptional_circumstances else "DISP 1.6.2AR(1)"
    elif route == "general":
        final_on = eight_weeks_on
        final_rule = "DISP 1.6.2R"
    else:
        final_on = None
        final_rule = "see deadlines; mixed complaint has more than one clock"

    # DISP 2.8.1R: the complainant may go to the Ombudsman once the relevant
    # period has elapsed and no qualifying response has been sent. The firm's
    # 'by the end of' day is still available to the firm, so the elapsed date
    # used here is the following day. For an unknown PSP calendar the PSD
    # figure is not operative.
    fos_from = None
    fos_from_operative = False
    fos_rule = "DISP 2.8.1R(2)"
    if route == "general" and final_on is not None:
        fos_from = final_on + timedelta(days=1)
        fos_from_operative = True
    elif route in ("psd", "emd") and psp_known and final_on is not None:
        fos_from = final_on + timedelta(days=1)
        fos_from_operative = True
        fos_rule = "DISP 2.8.1R(2A)"
    elif route == "mixed":
        fos_rule = "DISP 2.8.1R(2) and DISP 2.8.1R(2A)"

    notes = [
        "Calculated in code from the rules cited. A model must not replace these dates.",
        "Not a decision to uphold, reject, close, or pay redress. Not legal advice.",
        "Business day for DISP 1.5 is Handbook glossary 'business day' (1)(a): not a Saturday, Sunday, Christmas Day, Good Friday or a bank holiday in England and Wales.",
        "Business day for DISP 1.6.2A and for the business-day periods in DISP 2.8 is glossary limb (3): a day the payment service provider is open for business as required for the execution of a payment transaction. Bank holidays are not that definition.",
        "Proclaimed one-off bank holidays, and bank holidays moved by proclamation, are included only if the caller passes them.",
        "This calendar is England and Wales. Do not use it for a complaint handled on the Scottish or Northern Ireland bank-holiday calendar.",
        "DISP 1.6, as retrieved on 24 October 2026, showed a future version dated 25 October 2027. That future text is not encoded.",
    ]
    if receipt_note:
        notes.append(receipt_note)
    if exceptional_note:
        notes.append(exceptional_note)
    if route == "mixed":
        notes.append(
            "DISP 1.6.2A applies to the EMD or PSD part. The firm may choose to "
            "treat the whole complaint under DISP 1.6.2AR. A human makes that choice."
        )

    result = {
        "received_on": received.isoformat(),
        "calendar": "england-and-wales",
        "route": route,
        "exceptional_circumstances": exceptional_circumstances and route in PSD_ROUTES,
        "psp_opening_calendar_supplied": psp_known,
        "deadlines": [item.as_dict() for item in deadlines],
        "operative_final_response_due_on": final_on.isoformat() if final_on else None,
        "operative_final_response_rule": final_rule,
        "fos": {
            "may_refer_from_if_no_qualifying_response": (
                fos_from.isoformat() if fos_from else None
            ),
            "may_refer_from_operative": fos_from_operative,
            "rule_if_firm_has_not_responded": fos_rule,
            "six_month_last_day_to_refer": (
                fos_referral_deadline(response_sent_on).isoformat()
                if response_sent_on
                else None
            ),
            "six_month_rule": "DISP 2.8.2R(1)",
            "six_month_runs_from": (
                response_sent_on.isoformat() if response_sent_on else None
            ),
            "longstop": longstop_dates(event_complained_of, complainant_aware_on),
        },
        "handler_must_confirm": [
            "That the matter is a complaint, using the Handbook glossary definition",
            "The route: general, PSD, EMD, or mixed",
            "Whether the complainant has accepted a response, before anyone relies on the three-business-day route",
            "Whether exceptional circumstances under DISP 1.6.2AR(2) exist, before anyone relies on day 35",
            "The PSP's real opening days, before anyone relies on a 15-day or 35-day date",
            "The London date of receipt, if the source timestamp is near midnight",
        ],
        "final_response_must_cover": [
            "DISP 1.6.2R(1)(d) or DISP 1.6.4R(3): the Financial Ombudsman Service standard explanatory leaflet",
            "The Financial Ombudsman Service website address",
            "That the complainant may refer the complaint to the Financial Ombudsman Service",
            "The wording in DISP 1 Annex 3R on whether the respondent consents to waive the DISP 2.8.2R or DISP 2.8.7R time limits. This module does not reproduce that wording.",
        ],
        "notes": notes,
        "references": REFERENCES,
    }
    return result


def reference_psp_closed_dates(
    received_on: date,
    *,
    extra_non_business_days: Iterable[date] = (),
    cancelled_bank_holidays: Iterable[date] = (),
    span_days: int = 400,
) -> set[date]:
    """Closed dates if a PSP asserts it is shut on E&W weekends and bank holidays.

    This is an assertion the handler makes about the firm. It is not what the
    glossary says a DISP 1.6.2A business day is.
    """
    closed = england_wales_closed_days(
        received_on, extra_non_business_days, cancelled_bank_holidays
    )
    cursor = received_on
    end = received_on + timedelta(days=span_days)
    while cursor <= end:
        if cursor.weekday() >= 5:
            closed.add(cursor)
        cursor += timedelta(days=1)
    return closed


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Use YYYY-MM-DD, not {value!r}"
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calculate DISP clocks. Deterministic. Does not call a model."
    )
    parser.add_argument("--received", type=_parse_date, required=True)
    parser.add_argument("--route", choices=ROUTES, default="general")
    parser.add_argument(
        "--exceptional-circumstances",
        action="store_true",
        help="Human flag for the DISP 1.6.2AR(2) extension. Does not apply to a general complaint.",
    )
    parser.add_argument(
        "--psp-use-england-wales-calendar",
        action="store_true",
        help=(
            "Assert that this PSP is closed on England and Wales weekends and "
            "bank holidays, and treat the 15/35 dates as operative on that assertion."
        ),
    )
    parser.add_argument("--response-sent", type=_parse_date)
    parser.add_argument("--event", type=_parse_date, dest="event_complained_of")
    parser.add_argument("--aware", type=_parse_date, dest="complainant_aware_on")
    parser.add_argument(
        "--extra-closed",
        type=_parse_date,
        action="append",
        default=[],
        help="Extra England and Wales non-business day, repeatable. Use for a proclaimed bank holiday.",
    )
    parser.add_argument(
        "--cancel-bank-holiday",
        type=_parse_date,
        action="append",
        default=[],
        help="Statutory bank holiday that was moved or did not happen, repeatable.",
    )
    args = parser.parse_args(argv)

    psp_closed = None
    if args.psp_use_england_wales_calendar:
        psp_closed = reference_psp_closed_dates(
            args.received,
            extra_non_business_days=args.extra_closed,
            cancelled_bank_holidays=args.cancel_bank_holiday,
        )

    result = calculate_disp_clock(
        args.received,
        args.route,
        exceptional_circumstances=args.exceptional_circumstances,
        extra_non_business_days=args.extra_closed,
        cancelled_bank_holidays=args.cancel_bank_holiday,
        psp_closed_dates=psp_closed,
        response_sent_on=args.response_sent,
        event_complained_of=args.event_complained_of,
        complainant_aware_on=args.complainant_aware_on,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
