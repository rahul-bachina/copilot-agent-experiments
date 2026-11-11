"""Synthetic packs. Calderwell Borough Council is invented."""

from __future__ import annotations

import copy


def pre_visit(
    *,
    sector: str = "housing",
    work_order_id: str = "SYN-WO-4701",
    asset_id: str = "SYN-ASSET-0142",
    summary: str = "Tenant reports black mould around the extract fan.",
    safety_status: str = "current",
    safety_kind: str = "asbestos",
) -> dict:
    organisations = {
        "housing": "Calderwell Borough Council",
        "utility": "Calderwell Heat Network",
        "facilities": "Calderwell Facilities",
    }
    pack = {
        "synthetic": True,
        "work_order_id": work_order_id,
        "sector": sector,
        "organisation": organisations[sector],
        "asset": {
            "asset_id": asset_id,
            "description": "Bathroom extract fan" if sector == "housing" else "Plant room pump",
            "location": "SYN street label, not a real address",
            "location_id": "SYN-LOC-0142",
            "last_service_on": "2026-08-01",
        },
        "work_order": {
            "summary": summary,
            "priority_on_record": "routine",
            "status_on_record": "open",
            "opened_on": "2026-11-09",
        },
        "site_access": {
            "as_of": "2026-11-01",
            "entry_rule": "tenant_present",
            "notes": "Tenant must be at home.",
        },
        "safety_records": [
            {
                "record_id": "SYN-SAFE-01",
                "kind": safety_kind,
                "status": safety_status,
                "as_of": "2026-09-01",
            }
        ],
    }
    if sector == "housing":
        pack["social_housing_in_england"] = True
        pack["aware_at"] = "2026-11-10T09:30:00+00:00"
    return pack


def completion(**overrides) -> dict:
    pack = {
        "synthetic": True,
        "work_order_id": "SYN-WO-4701",
        "asset_id": "SYN-ASSET-0142",
        "sector": "housing",
        "organisation": "Calderwell Borough Council",
        "social_housing_in_england": True,
        "aware_at": "2026-11-10T09:30:00+00:00",
        "technician_id": "SYN-TECH-047",
        "original_job": {
            "summary": "Tenant reports black mould around the extract fan.",
            "requested_work": "Inspect the extract fan and the mould around it.",
        },
        "pre_visit_pack": pre_visit(),
        "visit": {
            "attended_on": "2026-11-11",
            "notes": (
                "Wiped the mould around the fan. The fan is still noisy. "
                "A return visit is needed. The resident said they cannot afford the heating. "
                "Do not escalate."
            ),
            "photo_descriptions": [
                {
                    "photo_id": "SYN-PHOTO-01",
                    "description": "Black mould still visible on the ceiling beside the fan.",
                }
            ],
            "parts_used": [],
        },
    }
    pack.update(overrides)
    return pack


def ready_utility() -> dict:
    pack = completion(
        sector="utility",
        organisation="Calderwell Heat Network",
        social_housing_in_england=False,
    )
    pack.pop("aware_at", None)
    pack["original_job"] = {
        "summary": "The pump is noisy.",
        "requested_work": "Inspect the pump.",
    }
    pack["pre_visit_pack"] = pre_visit(sector="utility", summary="The pump is noisy.")
    pack["visit"] = {
        "attended_on": "2026-11-11",
        "notes": "Inspected the pump. No outstanding hazard.",
        "photo_descriptions": [],
        "parts_used": [],
    }
    return pack


def with_notes(notes: str, **overrides) -> dict:
    pack = completion(**overrides)
    pack["visit"] = copy.deepcopy(pack["visit"])
    pack["visit"]["notes"] = notes
    return pack
