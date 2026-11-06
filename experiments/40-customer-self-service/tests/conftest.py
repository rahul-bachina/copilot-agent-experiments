"""Shared synthetic enquiries. Mereford Customer Service is fictional."""

from __future__ import annotations

import copy

AS_OF = "2026-11-06"


def enquiry(**overrides) -> dict:
    base = {
        "synthetic": True,
        "enquiry_id": "SYN-ENQ-0040",
        "channel": "portal",
        "sector": "energy_retail",
        "as_of": AS_OF,
        "customer": {"account_ref": "SYN-ACC-1040", "signed_in": True},
        "subject_account": {"account_ref": "SYN-ACC-1040"},
        "identity_check": {
            "method": "portal_session",
            "result": "passed",
            "checked_by": "channel",
            "as_of": AS_OF,
        },
        "text": "How do I give you a meter reading?",
        "structured": {},
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged = copy.deepcopy(base[key])
            merged.update(value)
            base[key] = merged
        else:
            base[key] = value
    return base
