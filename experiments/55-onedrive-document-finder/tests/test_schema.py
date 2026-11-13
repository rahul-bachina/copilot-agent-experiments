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
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for name in ("approve_reject", "regulated_decision", "production_record_change", "external_send", "spend_transact"):
        assert manifest["high_risk_actions"][name]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False


def test_tool_schemas_reject_extra_fields_and_file_changes():
    find_schema = json.loads((ROOT / "schema" / "find_tool.schema.json").read_text(encoding="utf-8"))
    ack_schema = json.loads((ROOT / "schema" / "acknowledge_tool.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(find_schema)
    Draft7Validator.check_schema(ack_schema)
    selection = {
        "confirmed": True,
        "actor_role": "Requesting user",
        "location_ids": ["LOC-HOUSING"],
        "principals": ["SYN-PRIN-USER"],
        "clearance": "OFFICIAL",
    }
    validate(
        {"synthetic": True, "index_id": "SYN-IDX-0055", "query": "housing", "selection": selection, "as_of": "2026-11-13"},
        find_schema,
    )
    try:
        validate(
            {"synthetic": True, "index_id": "SYN-IDX-0055", "query": "housing", "selection": selection, "as_of": "2026-11-13", "graph_token": "x"},
            find_schema,
        )
    except Exception as exc:
        assert "graph_token" in str(exc) or "Additional" in str(exc)
    else:
        raise AssertionError("extra field should be rejected")
    validate({"decision": "acknowledge", "actor_role": "Requesting user", "index_id": "SYN-IDX-0055"}, ack_schema)
    try:
        validate({"decision": "delete_file", "actor_role": "Requesting user", "index_id": "SYN-IDX-0055"}, ack_schema)
    except Exception:
        return
    raise AssertionError("delete_file should be rejected")
