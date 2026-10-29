"""Shared synthetic tickets. Aldermere is fictional."""

from __future__ import annotations

import copy

AS_OF = "2026-10-29"


def ticket(**overrides) -> dict:
    base = {
        "synthetic": True,
        "ticket_id": "SYN-1042",
        "channel": "portal",
        "as_of": AS_OF,
        "requester": {"staff_id": "SYN-STAFF-014", "signed_in": True},
        "subject_account": {"staff_id": "SYN-STAFF-014"},
        "identity_check": {
            "method": "entra_session",
            "result": "passed",
            "checked_by": "channel",
            "as_of": AS_OF,
        },
        "device": {"asset_tag": "SYN-LAP-220", "change_requested": False},
        "summary": "VPN client shows error 809 on the office laptop.",
        "diagnostics": {
            "os": "Windows 11",
            "error_code": "809",
            "network_connected": True,
            "free_text": "",
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged = copy.deepcopy(base[key])
            merged.update(value)
            base[key] = merged
        else:
            base[key] = value
    return base
