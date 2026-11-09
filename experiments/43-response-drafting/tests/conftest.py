"""Shared synthetic cases. Harberton Service is fictional."""

from __future__ import annotations

import copy

AS_OF = "2026-11-09"


def case(**overrides) -> dict:
    base = {
        "synthetic": True,
        "case_id": "SYN-CASE-4301",
        "sector": "financial_services",
        "channel": "email",
        "text": "What are your opening hours for the contact centre?",
    }
    for key, value in overrides.items():
        base[key] = value
    return copy.deepcopy(base)


def review(**overrides) -> dict:
    base = {
        "decision": "representative_approve_for_own_send",
        "actor": "representative",
        "actor_id": "SYN-REP-043",
        "recipient_role": "customer-on-case",
    }
    base.update(overrides)
    return base
