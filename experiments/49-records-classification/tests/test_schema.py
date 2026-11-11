"""Tool contracts stay least-privilege, and permissions.yaml matches the manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_classify_schema_cannot_set_an_approval_or_a_disposal():
    schema = _schema("classify_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["properties"]["synthetic"]["const"] is True
    assert "human_approval" not in schema["properties"]
    description = schema["description"].lower()
    assert "does not delete" in description
    assert "does not dispose" in description
    assert "does not downgrade" in description


def test_confirmation_schema_has_no_dispose_or_downgrade():
    schema = _schema("confirmation_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "confirm_classification",
        "change_classification",
        "reject_proposal",
    }
    assert decisions.isdisjoint({"dispose", "delete", "move", "downgrade", "apply_labels"})
    assert schema["additionalProperties"] is False
    assert "every_field_confirmed" in schema["required"]


def test_label_schema_is_a_stub_and_not_a_tenant_write():
    schema = _schema("label_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not call microsoft purview" in description
    assert "does not delete" in description
    assert schema["properties"]["confirmed_draft"]["description"]


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
