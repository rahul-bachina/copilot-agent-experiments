"""Approved routing rules for the invented Northmere contact centre.

A rule is used only when the queue owner has approved it and the approval
is inside the stale window. Matching is a keyword test on the rule text.
"""

from __future__ import annotations

import re
from datetime import date

APPROVED_ON = date(2026, 11, 1)
STALE_RULE_ON = date(2025, 1, 1)


def _rule(
    rule_id: str,
    queue: str,
    patterns: tuple[str, ...],
    *,
    owner_approved: bool,
    approved_on: date,
    topic: str,
) -> dict:
    return {
        "id": rule_id,
        "queue": queue,
        "topic": topic,
        "owner_approved": owner_approved,
        "approved_on": approved_on,
        "approved_by_role": "queue_owner" if owner_approved else None,
        "patterns": tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns),
    }


RULES: tuple[dict, ...] = (
    _rule(
        "rule-waste",
        "q-waste",
        (r"\bmissed bin\b", r"\bbin collection\b", r"\brecycling collection\b", r"\bwaste collection\b"),
        owner_approved=True,
        approved_on=APPROVED_ON,
        topic="waste",
    ),
    _rule(
        "rule-repairs",
        "q-repairs",
        (r"\bbroken boiler\b", r"\bleaking tap\b", r"\bkitchen tap\b", r"\brepair the (?:tap|boiler|door)\b"),
        owner_approved=True,
        approved_on=APPROVED_ON,
        topic="repairs",
    ),
    _rule(
        "rule-council-tax-payment-method",
        "q-revenues-enquiry",
        (
            r"\bhow (?:do|can) i pay (?:my )?council tax\b",
            r"\bcouncil tax direct debit\b",
        ),
        owner_approved=True,
        approved_on=APPROVED_ON,
        topic="council_tax_payment_method",
    ),
    _rule(
        "rule-opening-hours",
        "q-general",
        (r"\bopening hours\b", r"\bwhat time do you open\b", r"\bwhen are you open\b"),
        owner_approved=True,
        approved_on=APPROVED_ON,
        topic="opening_hours",
    ),
    _rule(
        "rule-library-card",
        "q-general",
        (r"\blibrary card\b",),
        owner_approved=True,
        approved_on=STALE_RULE_ON,
        topic="library_card",
    ),
    _rule(
        "rule-parking-draft",
        "q-general",
        (r"\bparking permit\b",),
        owner_approved=False,
        approved_on=APPROVED_ON,
        topic="parking",
    ),
)


def is_stale(approved_on: date, as_of: date, *, window_days: int) -> bool:
    """Older than the window is stale. Equal to the window is still current."""
    return (as_of - approved_on).days > window_days


def match_rules(text: str, as_of: date, *, window_days: int) -> dict:
    current: list[dict] = []
    stale: list[dict] = []
    unapproved: list[dict] = []
    for rule in RULES:
        if not any(pattern.search(text or "") for pattern in rule["patterns"]):
            continue
        view = {
            "id": rule["id"],
            "queue": rule["queue"],
            "topic": rule["topic"],
            "owner_approved": rule["owner_approved"],
            "approved_on": rule["approved_on"].isoformat(),
        }
        if not rule["owner_approved"]:
            unapproved.append(view)
        elif is_stale(rule["approved_on"], as_of, window_days=window_days):
            stale.append(view)
        else:
            current.append(view)
    queues = {item["queue"] for item in current}
    return {
        "current": current,
        "stale": stale,
        "unapproved": unapproved,
        "conflict": len(queues) > 1,
        "queue": next(iter(queues)) if len(queues) == 1 else None,
    }
