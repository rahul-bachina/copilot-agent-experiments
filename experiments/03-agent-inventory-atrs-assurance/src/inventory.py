"""Load an inventory record. The record is an input, not an approval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from catalogue import (
    LIFECYCLE_STATUSES,
    PROCESSING_REGIMES,
    SECTORS,
    SIGNIFICANT_EFFECTS,
    TRI_STATE,
)

REQUIRED_KEYS = (
    "inventory_id",
    "name",
    "sector",
    "lifecycle_status",
    "autonomy_level",
    "organisation_name",
    "source_reviewed_on",
)

TRI_STATE_KEYS = (
    "processes_personal_data",
    "special_category_data",
    "profiling",
    "meaningful_human_involvement",
    "explicit_consent",
    "article_9_2_g",
    "contract_or_authorised_by_law",
    "safeguard_information",
    "safeguard_representations",
    "safeguard_human_intervention",
    "safeguard_contest",
)


class InventoryError(ValueError):
    """The inventory record is not in the shape this core accepts."""


def load_json(path: Path | str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise InventoryError("Inventory JSON must be an object")
    return validate_record(payload)


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in REQUIRED_KEYS if not _present(record.get(key))]
    if missing:
        raise InventoryError("Missing inventory fields: " + ", ".join(missing))
    if record["sector"] not in SECTORS:
        raise InventoryError("sector must be public, fca_firm, or other")
    if record["lifecycle_status"] not in LIFECYCLE_STATUSES:
        raise InventoryError("lifecycle_status is not a known status")
    autonomy = record["autonomy_level"]
    if autonomy not in {"A0", "A1", "A2", "A3"}:
        raise InventoryError("autonomy_level must be A0, A1, A2, or A3")
    regime = record.get("processing_regime", "unknown")
    if regime not in PROCESSING_REGIMES:
        raise InventoryError("processing_regime is not recognised")
    effect = record.get("significant_effect", "unknown")
    if effect not in SIGNIFICANT_EFFECTS:
        raise InventoryError("significant_effect is not recognised")
    for key in TRI_STATE_KEYS:
        if key in record and record[key] not in TRI_STATE:
            raise InventoryError(f"{key} must be yes, no, or unknown")
    reviewed = record["source_reviewed_on"]
    if not isinstance(reviewed, str) or len(reviewed) != 10:
        raise InventoryError("source_reviewed_on must be an ISO date")
    return record


def _present(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))
