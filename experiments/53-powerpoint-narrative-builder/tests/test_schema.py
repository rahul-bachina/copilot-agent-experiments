"""Tool contracts stay least-privilege, and permissions.yaml matches the manifest."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def test_permissions_yaml_matches_the_manifest_and_the_schema():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
    schema = json.loads((REPO / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "permissions.yaml").read_text(encoding="utf-8"))
    Draft7Validator(schema).validate(manifest)
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
    assert all(item["enabled"] is False for item in manifest["high_risk_actions"]["additional_high_risk"])


def test_tool_schemas_reject_a_share_and_an_extra_field():
    outline = json.loads((ROOT / "schema" / "outline_tool.schema.json").read_text(encoding="utf-8"))
    approval = json.loads((ROOT / "schema" / "approval_tool.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(outline)
    Draft7Validator.check_schema(approval)
    assert outline["additionalProperties"] is False
    assert approval["additionalProperties"] is False
    assert "share" not in json.dumps(approval["properties"]["decision"]["enum"])
    validator = Draft7Validator(approval)
    errors = list(
        validator.iter_errors(
            {
                "decision": "share_deck",
                "actor_role": "presenter",
                "actor_id": "SYN-PRES-053",
                "pack_id": "SYN-DECK-5301",
                "outline_seen": True,
                "citations_approved": [],
                "accessibility_seen": True,
                "markings_seen": True,
            }
        )
    )
    assert errors
