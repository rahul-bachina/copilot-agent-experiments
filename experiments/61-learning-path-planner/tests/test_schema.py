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
    assert manifest["autonomy"]["level"] == "A1"
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


def test_tool_schemas_do_not_offer_enrolment_or_spend():
    draft = json.loads((ROOT / "schema" / "draft_tool.schema.json").read_text(encoding="utf-8"))
    approve = json.loads((ROOT / "schema" / "approve_tool.schema.json").read_text(encoding="utf-8"))
    review = json.loads((ROOT / "schema" / "adjustment_tool.schema.json").read_text(encoding="utf-8"))
    for schema in (draft, approve, review):
        Draft7Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
    assert "enrol" not in draft["properties"]
    assert "spend" not in draft["properties"]
    assert "book" not in approve["properties"]
    assert approve["properties"]["enrolled"]["const"] is False
    assert approve["properties"]["spent_gbp"]["type"] == "null"
    assert review["properties"]["adjustment_decided"]["const"] is False
