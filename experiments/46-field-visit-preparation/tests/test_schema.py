"""Tool contracts stay read-only, and the manifest matches permissions.yaml."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_has_no_dispatch_or_close():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "technician_confirm_asset_and_safety",
        "supervisor_acknowledge_hold",
        "reject_brief",
    }
    forbidden = {
        "schedule_visit",
        "dispatch_technician",
        "close_work_order",
        "send_message",
        "authorise_entry",
        "clear_hold",
    }
    assert decisions.isdisjoint(forbidden)
    assert schema["additionalProperties"] is False


def test_prepare_schema_does_not_grant_a_dispatch():
    schema = _schema("prepare_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not schedule" in description
    assert "does not dispatch" in description
    assert "does not close" in description
    assert "human_approval" not in schema["properties"]
    assert schema["properties"]["synthetic"]["const"] is True


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
