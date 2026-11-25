"""Statutory clocks. Recognition only. Nothing is marked as met.

Freedom of Information Act 2000 section 10(1) says the twentieth working day.
Working day, in section 10(6), also excludes Christmas Day, Good Friday, and
bank holidays. This module counts Monday to Friday only. It does not apply
those holidays, and it does not produce a statutory due date.

UK GDPR Article 12A(1) says the applicable time period is one month, subject
to an extension. This module does not decide that a stated period met it.
"""

from __future__ import annotations

from datetime import date

if __package__ in {None, ""}:
    from dates import add_months, twentieth_weekday_following
else:
    from .dates import add_months, twentieth_weekday_following


def read_period(value: object) -> dict:
    """A positive int is information. Anything else is not turned into 0."""

    if value is None or value == "":
        return {"present": False, "days": None, "accepted": False, "reason": "missing", "coerced": False}
    if isinstance(value, bool) or type(value) is not int:
        return {"present": True, "days": None, "accepted": False, "reason": "not_an_integer", "coerced": False}
    if value <= 0:
        return {
            "present": True,
            "days": None,
            "accepted": False,
            "reason": "not_a_positive_period",
            "coerced": False,
        }
    return {"present": True, "days": value, "accepted": True, "reason": None, "coerced": False}


def foi_clock(received: date | None, stated_working_days: object) -> dict:
    period = read_period(stated_working_days)
    weekday = None
    if received is not None:
        weekday = twentieth_weekday_following(received).isoformat()
    above = bool(period["accepted"] and period["days"] is not None and period["days"] > 20)
    return {
        "recognised": True,
        "statute": "Freedom of Information Act 2000 section 10(1)",
        "verified_text": "twentieth working day following the date of receipt",
        "weekday_count_20": weekday,
        "bank_holidays_applied": False,
        "not_the_statutory_day": True,
        "statutory_due_date": None,
        "stated_working_days": period,
        "stated_working_days_above_20": above,
        "not_a_finding_of_breach": True,
        "clock_met": False,
        "decided": False,
    }


def sar_clock(received: date | None, stated_days: object) -> dict:
    period = read_period(stated_days)
    anniversary = None
    if received is not None:
        anniversary = add_months(received, 1)["date"]
    above = bool(period["accepted"] and period["days"] is not None and period["days"] > 31)
    return {
        "recognised": True,
        "statute": "UK GDPR Article 12A(1), read with Article 12(3)",
        "verified_text": "the period of one month beginning with the relevant time, subject to paragraph 3",
        "anniversary_not_a_due_date": anniversary,
        "extension_in_paragraph_3_not_applied": True,
        "statutory_due_date": None,
        "stated_days": period,
        "stated_days_above_31": above,
        "not_a_finding_of_breach": True,
        "clock_met": False,
        "decided": False,
    }


def empty_clock() -> dict:
    return {
        "recognised": False,
        "statutory_due_date": None,
        "clock_met": False,
        "decided": False,
        "coerced": False,
    }
