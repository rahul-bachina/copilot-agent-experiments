"""England and Wales working days for the correspondence clock.

The Cabinet Office Guide to Handling Correspondence (September 2024) does not
define "working day" in the text retrieved on 26 October 2026. This module
treats a working day as a day that is not a Saturday, a Sunday, or a bank
holiday in England and Wales.

The standing pattern was checked against the GOV.UK bank-holiday list
(https://www.gov.uk/bank-holidays), retrieved 26 October 2026, for the 2026
England and Wales dates on that page: 1 January, 3 April, 6 April, 4 May,
25 May, 31 August, 25 December, and 28 December (Boxing Day substitute).

One-off proclaimed days are not included. A bank holiday that was moved by
proclamation is returned on its usual Monday unless the caller passes an
override. The coronation bank holiday on 8 May 2023 is not included.
Scotland's bank holiday on 15 June 2026 is not an England and Wales bank
holiday on that page, and it is not closed here. Scotland and Northern
Ireland need a different calendar.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Iterable


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
    """Standing England and Wales bank holidays for one calendar year."""
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
        days.add(date(year, 12, 27))
        days.add(date(year, 12, 28))
    elif christmas.weekday() == 6:
        days.add(date(year, 12, 27))
    elif boxing.weekday() == 5:
        days.add(date(year, 12, 28))
    elif boxing.weekday() == 6:
        days.add(date(year, 12, 28))
    return frozenset(days)


def closed_days_covering(
    dates: Iterable[date],
    extra_non_working_days: Iterable[date] = (),
    cancelled_bank_holidays: Iterable[date] = (),
) -> set[date]:
    """Bank holidays for the years a clock touching `dates` can reach."""
    years = {day.year for day in dates}
    if not years:
        years.add(date.today().year)
    closed: set[date] = set()
    for year in range(min(years) - 1, max(years) + 2):
        closed.update(statutory_england_and_wales_bank_holidays(year))
    closed.update(extra_non_working_days)
    closed.difference_update(cancelled_bank_holidays)
    return closed


def is_working_day(day: date, closed: set[date]) -> bool:
    """Weekday that is not in the closed set."""
    return day.weekday() < 5 and day not in closed


def nth_working_day_from(start_on: date, count: int, closed: set[date]) -> date:
    """The `count`th working day, where `start_on` is day 1 if it is open.

    If `start_on` is not a working day, day 1 is the next working day.
    """
    if count < 1:
        raise ValueError("count must be at least 1")

    current = start_on
    guard = 0
    while not is_working_day(current, closed):
        current += timedelta(days=1)
        guard += 1
        if guard > 3660:
            raise RuntimeError("working-day walk exceeded 10 years")
    remaining = count - 1
    while remaining:
        current += timedelta(days=1)
        guard += 1
        if guard > 3660:
            raise RuntimeError("working-day walk exceeded 10 years")
        if is_working_day(current, closed):
            remaining -= 1
    return current
