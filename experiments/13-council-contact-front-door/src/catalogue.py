"""Synthetic published pages for an invented council.

Northmarsh Borough Council is not a real authority. Nothing here is a
resident's record. A page body is the only sentence the front door may quote.
"""

from __future__ import annotations

import re
from datetime import date

COUNCIL = {
    "id": "northmarsh-borough-council",
    "name": "Northmarsh Borough Council",
    "fictional": True,
}

STALE_AFTER_DAYS = 180

_BIN = r"\b(bin|bins|rubbish|dustbin|dustbins|wheelie|recycling)\b"
_MISSED = r"(missed bin|not been collected|was not collected|wasn't collected)"


def _search(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def _example_ward_bins(text: str) -> bool:
    return _search(r"\bexample ward\b", text) and _search(_BIN, text) and not _search(_MISSED, text)


def _other_bins(text: str) -> bool:
    return _search(_BIN, text) and not _search(r"\bexample ward\b", text) and not _search(_MISSED, text)


def _missed(text: str) -> bool:
    return _search(_MISSED, text)


def _library(text: str) -> bool:
    return _search(r"\blibrar(y|ies)\b", text)


def _how_to_pay(text: str) -> bool:
    return _search(
        r"(how (do i |to )?pay (my )?council tax|ways to pay council tax|council tax payment)",
        text,
    )


def _reduction(text: str) -> bool:
    return _search(r"council tax (reduction|support)", text)


def _housing(text: str) -> bool:
    return _search(r"(housing register|council house|social housing|\bhomeless\b)", text)


def _parking(text: str) -> bool:
    return _search(r"\bmarket square\b", text) and _search(r"(car park|parking|tariff)", text)


def _pothole(text: str) -> bool:
    return _search(r"\b(pothole|potholes|pot hole|pot holes)\b", text)


def _blue_badge(text: str) -> bool:
    return _search(r"\bblue badge\b", text)


ARTICLES: tuple[dict, ...] = (
    {
        "id": "waste-example-ward",
        "title": "Example Ward bin day",
        "service_area": "waste",
        "queue": "waste",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/bins/example-ward",
        "last_reviewed": "2026-09-02",
        "match": _example_ward_bins,
        "body": (
            "Example Ward household bins are collected on Wednesday. "
            "Put the bin out by 7:00. This page does not say whether a particular "
            "collection was missed, and it does not list any other ward."
        ),
    },
    {
        "id": "waste-day-depends-on-ward",
        "title": "Bin days depend on the ward",
        "service_area": "waste",
        "queue": "waste",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/bins",
        "last_reviewed": "2026-09-02",
        "match": _other_bins,
        "body": (
            "Bin days depend on the ward. This page does not give a day unless the "
            "ward is named and is one this page lists. The only listed ward is "
            "Example Ward. This page does not confirm a missed collection."
        ),
    },
    {
        "id": "waste-missed-collection",
        "title": "Report a missed collection",
        "service_area": "waste",
        "queue": "waste",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/bins/missed",
        "last_reviewed": "2026-08-20",
        "match": _missed,
        "body": (
            "To report a missed household collection, use the council's published "
            "form before 12:00 on the next working day. Sending a report does not "
            "by itself book a return visit. A person checks the report. This page "
            "does not say that a named collection was missed."
        ),
    },
    {
        "id": "library-hours",
        "title": "Northmarsh Library opening hours",
        "service_area": "libraries",
        "queue": "libraries",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/libraries/hours",
        "last_reviewed": "2026-07-06",
        "match": _library,
        "body": (
            "Northmarsh Library is open Tuesday, Wednesday, Thursday and Friday "
            "from 9:30 to 17:00, and Saturday from 10:00 to 13:00. It is closed "
            "on Sunday and Monday. This page does not reserve a book or a computer."
        ),
    },
    {
        "id": "council-tax-how-to-pay",
        "title": "How to pay council tax",
        "service_area": "revenues",
        "queue": "revenues",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/council-tax/pay",
        "last_reviewed": "2026-06-15",
        "match": _how_to_pay,
        "body": (
            "Council tax can be paid by direct debit, on the council's published "
            "payment page, or at a Post Office with a barcoded bill. This page "
            "does not show a balance, set a reduction, or take a payment."
        ),
    },
    {
        "id": "council-tax-reduction-contact",
        "title": "Contact the team about council tax reduction",
        "service_area": "revenues",
        "queue": "revenues",
        "kind": "statutory_contact",
        "url": "https://www.northmarsh.example.gov.uk/council-tax/reduction",
        "last_reviewed": "2026-09-01",
        "match": _reduction,
        "body": (
            "To ask about council tax reduction, contact the revenues team on the "
            "number published on the council's own page. A person decides whether "
            "a reduction applies. This page does not calculate a reduction and "
            "does not decide an application."
        ),
    },
    {
        "id": "housing-register-contact",
        "title": "Contact housing options",
        "service_area": "housing",
        "queue": "housing_options",
        "kind": "statutory_contact",
        "url": "https://www.northmarsh.example.gov.uk/housing/register",
        "last_reviewed": "2026-09-12",
        "match": _housing,
        "body": (
            "To ask about the housing register, contact the housing options team. "
            "A person decides an application. This page does not place you "
            "on the register and does not offer a home."
        ),
    },
    {
        "id": "parking-market-square",
        "title": "Market Square car park tariff",
        "service_area": "parking",
        "queue": "parking",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/parking/market-square",
        "last_reviewed": "2026-05-28",
        "match": _parking,
        "body": (
            "Market Square car park, Monday to Saturday 8:00 to 18:00: the "
            "published tariff is £1.40 an hour, up to 4 hours. Sunday is free on "
            "this page. This page does not issue, cancel, or waive a penalty charge."
        ),
    },
    {
        "id": "pothole-report",
        "title": "Report a pothole",
        "service_area": "highways",
        "queue": "highways",
        "kind": "routine",
        "url": "https://www.northmarsh.example.gov.uk/roads/potholes",
        "last_reviewed": "2026-01-10",
        "match": _pothole,
        "body": (
            "Potholes on roads the council maintains can be reported on the "
            "published form. This page does not say when a repair will happen, "
            "and it does not cover motorways or trunk roads."
        ),
    },
    {
        "id": "blue-badge-contact",
        "title": "Contact the team about a Blue Badge",
        "service_area": "customer_services",
        "queue": "customer_services",
        "kind": "statutory_contact",
        "url": "https://www.northmarsh.example.gov.uk/blue-badge",
        "last_reviewed": "2026-08-01",
        "match": _blue_badge,
        "body": (
            "To ask about a Blue Badge, contact the team named on the council's "
            "own page. A person decides an application. This page does not say "
            "that a badge will be issued."
        ),
    },
)


def article_by_id(article_id: str) -> dict:
    for article in ARTICLES:
        if article["id"] == article_id:
            return article
    raise KeyError(article_id)


def match_articles(text: str) -> list[dict]:
    if not text:
        return []
    return [article for article in ARTICLES if article["match"](text)]


def age_days(earlier: date, later: date) -> int:
    return (later - earlier).days


def is_stale(last_reviewed: date, as_of: date, stale_after_days: int) -> bool:
    """A future review date is not quotable. Equal to the threshold is current."""
    age = age_days(last_reviewed, as_of)
    return age < 0 or age > stale_after_days
