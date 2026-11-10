"""Shared synthetic packs. Calderwell Borough Council is fictional."""

from __future__ import annotations

import copy

AS_OF = "2026-11-10"


def pack(**overrides) -> dict:
    base = {
        "synthetic": True,
        "work_order_id": "SYN-WO-4601",
        "sector": "housing",
        "organisation": "Calderwell Borough Council",
        "social_housing_in_england": True,
        "aware_at": "2026-11-10T09:30:00+00:00",
        "asset": {
            "asset_id": "SYN-ASSET-0142",
            "description": "Bathroom extract fan",
            "location": "SYN street label, not a real address",
            "location_id": "SYN-LOC-0142",
            "last_service_on": "2026-08-01",
        },
        "work_order": {
            "summary": "Tenant reports black mould around the extract fan.",
            "priority_on_record": "routine",
            "status_on_record": "open",
            "opened_on": "2026-11-09",
        },
        "site_access": {
            "as_of": "2026-11-01",
            "entry_rule": "tenant_present",
            "notes": "Tenant must be at home. Do not enter if nobody is in.",
        },
        "safety_records": [
            {
                "record_id": "SYN-SAFE-01",
                "kind": "asbestos",
                "status": "current",
                "as_of": "2026-09-01",
            }
        ],
    }
    for key, value in overrides.items():
        if key in {"asset", "work_order", "site_access"} and isinstance(value, dict):
            merged = dict(base[key])
            merged.update(value)
            base[key] = merged
        else:
            base[key] = value
    return copy.deepcopy(base)


def review(**overrides) -> dict:
    base = {
        "decision": "technician_confirm_asset_and_safety",
        "actor_role": "Field technician",
        "actor_id": "SYN-TECH-046",
        "asset_id": "SYN-ASSET-0142",
        "safety_context_read": True,
        "acknowledge_gaps": True,
        "acknowledge_safety_hold": True,
        "acknowledge_stale": True,
    }
    base.update(overrides)
    return base
