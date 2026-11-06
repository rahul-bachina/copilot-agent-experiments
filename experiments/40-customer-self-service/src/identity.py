"""Identity is a channel object. Enquiry text cannot supply it.

A passed result is honoured only for a portal_session recorded by the channel,
on the signed-in portal, for the same as-of date, where the customer and the
subject account are the same synthetic account reference.

This module does not call Microsoft Entra and it does not call a customer
identity product. It does not describe either product's sign-in behaviour.
A passed session does not authorise a password reset, a payment, or a record change.
"""

from __future__ import annotations

import re

ACCOUNT_REF = re.compile(r"^SYN-ACC-\d{4}$")
ENQUIRY_ID = re.compile(r"^SYN-ENQ-\d{4}$")
HANDLER_ID = re.compile(r"^SYN-HANDLER-\d{3}$")

SIGNED_IN_CHANNELS = frozenset({"portal"})
KNOWN_CHANNELS = SIGNED_IN_CHANNELS | frozenset({"web_chat", "phone", "email"})
SECTORS = frozenset({"energy_retail", "telecoms", "financial_services", "public_service"})


def _dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _str(value: object) -> str:
    return value if isinstance(value, str) else ""


def assess_identity(enquiry: dict, as_of: str) -> dict:
    customer = _dict(enquiry.get("customer"))
    subject = _dict(enquiry.get("subject_account"))
    check = _dict(enquiry.get("identity_check"))
    customer_ref = _str(customer.get("account_ref"))
    subject_ref = _str(subject.get("account_ref"))
    third_party = bool(customer_ref and subject_ref and customer_ref != subject_ref)
    channel = _str(enquiry.get("channel"))
    known_channel = channel if channel in KNOWN_CHANNELS else "unknown"
    sector = _str(enquiry.get("sector"))
    known_sector = sector if sector in SECTORS else "unspecified"

    if channel not in SIGNED_IN_CHANNELS:
        reason = "channel_not_signed_in"
        trusted = False
    elif customer.get("signed_in") is not True:
        reason = "session_not_signed_in"
        trusted = False
    elif check.get("method") != "portal_session" or check.get("checked_by") != "channel":
        reason = "check_not_from_channel"
        trusted = False
    elif check.get("result") != "passed":
        reason = "check_not_passed"
        trusted = False
    elif check.get("as_of") != as_of:
        reason = "identity_check_stale"
        trusted = False
    elif ACCOUNT_REF.match(customer_ref) is None or ACCOUNT_REF.match(subject_ref) is None:
        reason = "account_ref_not_synthetic"
        trusted = False
    elif third_party:
        reason = "third_party"
        trusted = False
    else:
        reason = "portal_session"
        trusted = True

    return {
        "trusted": trusted,
        "reason": reason,
        "third_party": third_party,
        "check_stale": bool(
            check.get("method") == "portal_session" and check.get("as_of") not in {None, as_of}
        ),
        "channel": known_channel,
        "sector": known_sector,
        "customer_is_subject": bool(customer_ref and subject_ref and customer_ref == subject_ref),
        "account_ref": customer_ref if ACCOUNT_REF.match(customer_ref) else None,
    }
