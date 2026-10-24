"""Least-privilege tool schemas. No publish, send, or write field."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema"


def _load(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def test_schemas_reject_unknown_fields_and_have_no_side_effect_property():
    for name in ("intake_tool.schema.json", "analysis_tool.schema.json"):
        schema = _load(name)
        assert schema["additionalProperties"] is False
        properties = schema["properties"]
        for banned in ("publish", "send", "external_send", "write", "production_write"):
            assert banned not in properties


def test_approval_cannot_carry_a_publish_field():
    schema = _load("analysis_tool.schema.json")
    approval = schema["properties"]["approval"]
    assert approval["additionalProperties"] is False
    assert "publish" not in approval["properties"]
    assert "framework_approved" in approval["properties"]
