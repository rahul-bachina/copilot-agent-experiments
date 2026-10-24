"""Source and document currency. No network.

A source is stale when the as-of date is more than stale_after_days after
last_verified. Equal to the threshold is still within it. "Older than" is strict.
"""

from __future__ import annotations

from datetime import date, datetime


def parse_iso(value: str) -> date:
    """Parse an ISO date. Raise ValueError if it is not one."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def assess_source(source: dict, as_of: date, stale_after_days: int) -> dict:
    """Return the currency row for one pinned source."""
    if stale_after_days < 0:
        raise ValueError("stale_after_days must be zero or positive")
    verified = parse_iso(source["last_verified"])
    age_days = (as_of - verified).days
    if age_days < 0:
        currency = "as_of_before_verification"
    elif age_days > stale_after_days:
        currency = "stale"
    else:
        currency = "within_threshold"
    return {
        "source_id": source["id"],
        "title": source["title"],
        "url": source["url"],
        "page_published": source["page_published"],
        "page_last_updated": source["page_last_updated"],
        "last_verified": source["last_verified"],
        "age_days": age_days,
        "stale_after_days": stale_after_days,
        "currency": currency,
        "body_opened": source["body_opened"],
        "pdf_opened": source["pdf_opened"],
        "notes": source["notes"],
    }


def assess_catalogue(sources: list[dict], as_of: date, stale_after_days: int) -> list[dict]:
    """Currency row for every pinned source, catalogue order."""
    return [assess_source(source, as_of, stale_after_days) for source in sources]


def assess_document_date(
    document_date: str | None,
    as_of: date,
    stale_after_days: int,
) -> dict:
    """Flag a policy whose own date is older than the document threshold."""
    if not document_date:
        return {
            "document_date": None,
            "age_days": None,
            "stale_after_days": stale_after_days,
            "currency": "undated",
        }
    parsed = parse_iso(document_date)
    age_days = (as_of - parsed).days
    if age_days < 0:
        currency = "document_date_after_as_of"
    elif age_days > stale_after_days:
        currency = "stale"
    else:
        currency = "within_threshold"
    return {
        "document_date": document_date,
        "age_days": age_days,
        "stale_after_days": stale_after_days,
        "currency": currency,
    }
