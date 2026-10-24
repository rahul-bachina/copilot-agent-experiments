"""Read the synthetic Dataverse CSV fixtures back into inventory records."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from inventory import validate_record

HEADER_FILE = "agent_inventory.csv"
NARRATIVE_FILE = "agent_narrative.csv"


def load_directory(directory: Path | str) -> list[dict[str, Any]]:
    directory = Path(directory)
    rows = list(_read(directory / HEADER_FILE))
    narratives: dict[str, dict[str, str]] = {}
    for item in _read(directory / NARRATIVE_FILE):
        narratives.setdefault(item["inventory_id"], {})[item["field"]] = item["value"]
    reads: dict[str, list[dict[str, Any]]] = {}
    never: dict[str, list[dict[str, Any]]] = {}
    for item in _read(directory / "data_access.csv"):
        if item["direction"] == "read":
            reads.setdefault(item["inventory_id"], []).append(
                {
                    "resource": item["resource"],
                    "justification": item["justification"],
                    "may_contain_personal_data": item["may_contain_personal_data"] == "True",
                }
            )
        elif item["direction"] == "never":
            never.setdefault(item["inventory_id"], []).append(
                {"resource": item["resource"], "reason": item["justification"]}
            )
    tools: dict[str, list[dict[str, str]]] = {}
    for item in _read(directory / "tools.csv"):
        tools.setdefault(item["inventory_id"], []).append(
            {"tool": item["tool"], "action": item["action"], "access_level": item["access_level"]}
        )
    risks: dict[str, list[dict[str, str]]] = {}
    for item in _read(directory / "risks.csv"):
        risks.setdefault(item["inventory_id"], []).append(
            {
                "id": item["risk_id"],
                "risk": item["risk"],
                "likelihood": item["likelihood"],
                "impact": item["impact"],
                "residual_risk": item["residual_risk"],
            }
        )
    events: dict[str, list[dict[str, Any]]] = {}
    for item in _read(directory / "lifecycle_events.csv"):
        events.setdefault(item["inventory_id"], []).append(
            {
                "from_status": item["from_status"],
                "to_status": item["to_status"],
                "requested_by": item["requested_by"],
                "reason": item["reason"],
                "applied": item["applied"] == "True",
                "approved_by_this_tool": item["approved_by_this_tool"] == "True",
                "external_approval_id": item["external_approval_id"],
                "approver_role": item["approver_role"],
                "external_decision": item["external_decision"],
            }
        )

    records = []
    for row in rows:
        record: dict[str, Any] = {key: value for key, value in row.items() if value != ""}
        record.update(narratives.get(row["inventory_id"], {}))
        record["data_reads"] = reads.get(row["inventory_id"], [])
        record["never_access"] = never.get(row["inventory_id"], [])
        record["tools"] = tools.get(row["inventory_id"], [])
        record["risk_rows"] = risks.get(row["inventory_id"], [])
        record["recorded_events"] = events.get(row["inventory_id"], [])
        records.append(validate_record(record))
    return records


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
