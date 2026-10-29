"""Customer-facing content is not drafted.

Proceeds of Crime Act 2002, section 333A, was opened on 29 October 2026.
Subsection (1) covers disclosing that a disclosure under that Part has been
made, where that is likely to prejudice an investigation. Subsection (3)
covers disclosing that an investigation is being contemplated or carried out.
This module does not decide whether an offence would be committed. It refuses
to produce any customer-facing text, including a form of words that avoids
the statutory terms.

Sections 333B, 333C, and 333D are named in section 333A(5) and were not opened.
They are not applied.
"""

from __future__ import annotations


def empty_customer_facing(*, message_requested: bool) -> dict:
    """The only customer-facing object this agent returns."""

    return {
        "drafted": False,
        "text": None,
        "audience": "none",
        "message_requested": message_requested,
        "request_echoed": False,
        "may_be_sent_by_agent": False,
        "reason": (
            "Proceeds of Crime Act 2002, section 333A. This agent does not "
            "draft customer-facing content about a suspicion, a disclosure, "
            "or an investigation. It does not decide whether a disclosure "
            "would be likely to prejudice an investigation."
        ),
    }


def assert_no_customer_text(draft: dict) -> None:
    """Raise if a later edit put words on the customer channel."""

    facing = draft.get("customer_facing") or {}
    if facing.get("drafted") or facing.get("text") or facing.get("may_be_sent_by_agent"):
        raise RuntimeError("customer-facing content was drafted")
    if facing.get("request_echoed"):
        raise RuntimeError("a requested customer message was echoed")
