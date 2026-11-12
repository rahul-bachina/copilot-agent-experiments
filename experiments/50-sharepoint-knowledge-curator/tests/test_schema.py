"""Tool contracts stay least-privilege, and permissions.yaml matches the manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_curate_schema_cannot_set_an_approval_or_a_deletion():
    schema = _schema("curate_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["properties"]["synthetic"]["const"] is True
    assert "human_approval" not in schema["properties"]
    description = schema["description"].lower()
    assert "does not delete" in description
    assert "does not unpublish" in description
    assert "does not change permissions" in description


def test_approval_schema_has_no_delete_or_unpublish():
    schema = _schema("approval_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {"approve_actions", "reject_actions", "defer"}
    assert decisions.isdisjoint({"delete", "unpublish", "move", "change_permissions", "publish"})
    assert schema["additionalProperties"] is False
    assert schema["properties"]["actor_role"]["const"] == "Site owner"


def test_stub_schema_is_not_a_tenant_write():
    schema = _schema("stub_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not call sharepoint" in description
    assert "does not call microsoft graph" in description
    assert "does not delete" in description


def test_permissions_yaml_matches_the_manifest_and_the_schema():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
    import yaml
    from jsonschema import Draft7Validator

    schema = json.loads((REPO / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "permissions.yaml").read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(manifest)
    assert manifest["autonomy"]["level"] == "A1"
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for action in (
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ):
        assert manifest["high_risk_actions"][action]["enabled"] is False
