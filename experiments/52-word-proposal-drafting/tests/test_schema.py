"""Tool contracts stay least-privilege, and permissions.yaml matches the manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_draft_schema_cannot_submit_or_set_a_price():
    schema = _schema("draft_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["properties"]["synthetic"]["const"] is True
    props = schema["properties"]
    for forbidden in ("submitted", "price", "amount", "human_approval", "recipient", "email"):
        assert forbidden not in props
    description = schema["description"].lower()
    assert "does not submit" in description


def test_review_schema_has_no_submit_or_recipient():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "author_accept_complete_draft",
        "author_request_revision",
        "reject_draft",
    }
    assert decisions.isdisjoint({"submit_bid", "send_proposal", "upload_to_portal"})
    assert schema["additionalProperties"] is False
    assert "complete_draft_seen" in schema["required"]
    assert "email" not in schema["properties"]
    assert "recipient" not in schema["properties"]
    description = schema["description"].lower()
    assert "does not submit" in description


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
