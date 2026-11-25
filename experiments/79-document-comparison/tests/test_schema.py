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
    assert manifest["agent"]["id"] == "exp-79-document-comparison"
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
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


def test_tool_schemas_do_not_offer_an_edit_or_a_send():
    forbidden = {
        "edit",
        "edit_document",
        "approve",
        "approve_document",
        "publish",
        "publish_document",
        "send",
        "send_document",
        "give_legal_advice",
        "document_approved",
        "published",
        "sent",
    }
    names = (
        "compare_tool.schema.json",
        "confirm_tool.schema.json",
        "route_tool.schema.json",
        "interpretation_tool.schema.json",
    )
    for name in names:
        schema = json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert forbidden.isdisjoint(schema["properties"])
    confirm = json.loads((ROOT / "schema" / "confirm_tool.schema.json").read_text(encoding="utf-8"))
    assert confirm["properties"]["item"]["const"] == "version-pair"
    assert confirm["properties"]["decision"]["const"] == "confirm-versions"
    route = json.loads((ROOT / "schema" / "route_tool.schema.json").read_text(encoding="utf-8"))
    assert route["properties"]["item"]["const"] == "route-seen"
