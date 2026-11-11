"""Tool contracts stay read-only, and the manifest matches permissions.yaml."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_has_no_publish_or_contact():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {"confirm_sample_frame_and_limitations", "reject_pack"}
    forbidden = {
        "publish",
        "publish_pack",
        "contact_customer",
        "conclude_about_individual",
        "approve_board_report",
        "submit_return",
        "write_production_record",
    }
    assert decisions.isdisjoint(forbidden)
    assert schema["additionalProperties"] is False


def test_evidence_schema_does_not_grant_a_publication():
    schema = _schema("evidence_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not publish" in description
    assert "does not contact" in description
    assert "does not conclude" in description
    assert "human_approval" not in schema["properties"]
    assert schema["properties"]["synthetic"]["const"] is True


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
