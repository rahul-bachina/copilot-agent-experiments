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
    assert manifest["agent"]["id"] == "exp-76-charity-grant-application-assistant"
    assert manifest["autonomy"]["level"] == "A1"
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is True
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


def test_tool_schemas_do_not_offer_a_submit_or_a_send():
    forbidden = {"send", "submit", "submit_application", "contact_funder", "funder_contacted", "sent"}
    for name in ("draft_tool.schema.json", "approval_tool.schema.json", "route_tool.schema.json"):
        schema = json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert forbidden.isdisjoint(schema["properties"])
    approval = json.loads((ROOT / "schema" / "approval_tool.schema.json").read_text(encoding="utf-8"))
    assert approval["properties"]["item"]["const"] == "grant-package"
    assert approval["properties"]["decision"]["const"] == "approve-draft"
    route = json.loads((ROOT / "schema" / "route_tool.schema.json").read_text(encoding="utf-8"))
    assert route["properties"]["item"]["const"] == "route-seen"
