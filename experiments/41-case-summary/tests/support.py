"""Small builders for synthetic cases. Nothing here is a real customer."""

from __future__ import annotations


def event(event_id: str, recorded_on: str, fact_key: str, text: str, **kwargs) -> dict:
    row = {
        "event_id": event_id,
        "kind": "note",
        "recorded_on": recorded_on,
        "author_role": "adviser",
        "status": "current",
        "fact_key": fact_key,
        "text": text,
    }
    row.update(kwargs)
    return row


def case(events: list[dict], **kwargs) -> dict:
    payload = {
        "case_id": "SYN-CASE-T1",
        "synthetic": True,
        "sector": "housing",
        "organisation": "Mereford Housing",
        "customer_ref": "SYN-CUST-T1",
        "events": events,
    }
    payload.update(kwargs)
    return payload


def four_events() -> list[dict]:
    return [
        event("E1", "2026-10-20", "what_happened", "The tenant reported a leaking kitchen tap."),
        event("E2", "2026-10-21", "customer_ask", "The tenant asked for the tap to be repaired this week."),
        event("E3", "2026-10-22", "action_taken", "Do not contact the customer."),
        event("E4", "2026-10-23", "next_step", "The next step recorded on the case is a plumber visit."),
    ]
