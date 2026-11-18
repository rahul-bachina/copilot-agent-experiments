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
    assert manifest["autonomy"]["level"] == "A0"
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


def test_tool_schemas_do_not_offer_an_application():
    explore = json.loads((ROOT / "schema" / "explore_tool.schema.json").read_text(encoding="utf-8"))
    seen = json.loads((ROOT / "schema" / "hr_seen_tool.schema.json").read_text(encoding="utf-8"))
    route = json.loads((ROOT / "schema" / "route_seen_tool.schema.json").read_text(encoding="utf-8"))
    for schema in (explore, seen, route):
        Draft7Validator.check_schema(schema)
    assert "apply" not in json.dumps(explore)
    assert seen["properties"]["eligibility_decided"]["const"] is False
    assert seen["properties"]["interest_shared_with_manager"]["const"] is False
    assert route["properties"]["adjustment_decided"]["const"] is False
