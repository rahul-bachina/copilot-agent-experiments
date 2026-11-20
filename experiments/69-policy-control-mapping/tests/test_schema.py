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
    assert manifest["agent"]["id"] == "exp-69-policy-control-mapping"
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for name in (
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ):
        assert manifest["high_risk_actions"][name]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False
    validate(manifest, schema)


def test_tool_schemas_do_not_offer_a_grc_write():
    for name in ("map_tool.schema.json", "approval_tool.schema.json"):
        schema = json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        blob = json.dumps(schema)
        assert "write_grc" not in blob
        assert "mark_control_met" not in blob
    approval = json.loads((ROOT / "schema" / "approval_tool.schema.json").read_text(encoding="utf-8"))
    assert approval["properties"]["decision"]["const"] == "approved"
    assert approval["properties"]["control_met"]["const"] is False
    assert approval["properties"]["gap_closed"]["const"] is False
    assert approval["properties"]["policy_edited"]["const"] is False
    assert approval["properties"]["grc_written"]["const"] is False
