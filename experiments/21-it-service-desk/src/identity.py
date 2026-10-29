"""Identity is a channel object. Ticket text cannot supply it.

A passed result is honoured only for an entra_session recorded by the channel,
on a signed-in portal or Teams chat, for the same as-of date, where the
requester and the subject are the same synthetic staff id.

This module does not call Microsoft Entra. It does not describe that product's
sign-in behaviour. A passed session does not authorise a password reset.
"""

from __future__ import annotations

import re

STAFF_ID = re.compile(r"^SYN-STAFF-\d{3}$")
ANALYST_ID = re.compile(r"^SYN-ANALYST-\d{3}$")
TICKET_ID = re.compile(r"^SYN-\d{4}$")
ASSET_TAG = re.compile(r"^SYN-[A-Z]+-\d{3}$")

SIGNED_IN_CHANNELS = frozenset({"portal", "teams_chat"})
KNOWN_CHANNELS = SIGNED_IN_CHANNELS | frozenset({"phone", "email"})


def _dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _str(value: object) -> str:
    return value if isinstance(value, str) else ""


def assess_identity(ticket: dict, as_of: str) -> dict:
    requester = _dict(ticket.get("requester"))
    subject = _dict(ticket.get("subject_account"))
    check = _dict(ticket.get("identity_check"))
    req_id = _str(requester.get("staff_id"))
    sub_id = _str(subject.get("staff_id"))
    third_party = bool(req_id and sub_id and req_id != sub_id)
    channel = _str(ticket.get("channel"))
    known_channel = channel if channel in KNOWN_CHANNELS else "unknown"

    session_shape = (
        check.get("method") == "entra_session"
        and check.get("checked_by") == "channel"
        and check.get("result") == "passed"
        and requester.get("signed_in") is True
        and STAFF_ID.match(req_id) is not None
        and STAFF_ID.match(sub_id) is not None
    )
    check_stale = bool(session_shape and check.get("as_of") != as_of)

    if channel not in SIGNED_IN_CHANNELS:
        reason = "channel_not_signed_in"
        trusted = False
    elif requester.get("signed_in") is not True:
        reason = "session_not_signed_in"
        trusted = False
    elif check.get("method") != "entra_session" or check.get("checked_by") != "channel":
        reason = "check_not_from_channel"
        trusted = False
    elif check.get("result") != "passed":
        reason = "check_not_passed"
        trusted = False
    elif check.get("as_of") != as_of:
        reason = "identity_check_stale"
        trusted = False
    elif STAFF_ID.match(req_id) is None or STAFF_ID.match(sub_id) is None:
        reason = "staff_id_not_synthetic"
        trusted = False
    elif third_party:
        reason = "third_party"
        trusted = False
    else:
        reason = "entra_session"
        trusted = True

    return {
        "trusted": trusted,
        "reason": reason,
        "third_party": third_party,
        "check_stale": check_stale,
        "channel": known_channel,
        "requester_is_subject": bool(req_id and sub_id and req_id == sub_id),
        "requester_staff_id": req_id if STAFF_ID.match(req_id) else None,
    }
