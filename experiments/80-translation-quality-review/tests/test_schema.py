"""Manifest, permissions file, and tool schemas."""

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SCHEMA = REPO / "schemas" / "agent-manifest.schema.json"


def test_manifest_validates_and_permissions_match():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    permissions = yaml.safe_load((ROOT / "permissions.yaml").read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema)
    assert permissions == manifest
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for name in ("approve_reject", "regulated_decision", "production_record_change", "external_send", "spend_transact"):
        assert manifest["high_risk_actions"][name]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False


def test_tool_schemas_are_closed():
    for path in sorted((ROOT / "schema").glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["additionalProperties"] is False
        assert document["type"] == "object"
        assert document["required"]
