"""Tool schemas stay least privilege, and the manifest validates."""

import json
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, validate

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def test_permissions_manifest_matches_the_schema():
    schema = json.loads((REPO / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    manifest = yaml.safe_load((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    permissions = yaml.safe_load((ROOT / "permissions.yaml").read_text(encoding="utf-8"))
    assert manifest == permissions
    validate(manifest, schema)
    assert manifest["autonomy"]["level"] == "A1"
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for name in ("approve_reject", "regulated_decision", "production_record_change", "external_send", "spend_transact"):
        assert manifest["high_risk_actions"][name]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False


def test_tool_schemas_reject_external_sharing():
    propose = json.loads((ROOT / "schema" / "propose_tool.schema.json").read_text(encoding="utf-8"))
    approve = json.loads((ROOT / "schema" / "approve_tool.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(propose)
    Draft7Validator.check_schema(approve)
    assert propose["additionalProperties"] is False
    assert "share_externally" not in propose["properties"]
    assert approve["properties"]["external_share_approved"]["const"] is False
