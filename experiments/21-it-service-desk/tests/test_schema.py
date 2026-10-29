"""Tool schemas do not offer an execution field.

The check uses the standard library. CI installs only pytest.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_desk_schema_has_no_side_effect_field():
    schema = _schema("desk_tool.schema.json")
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["additionalProperties"] is False
    assert "synthetic" in schema["required"]
    properties = schema["properties"]
    for banned in (
        "password_reset",
        "execute",
        "grant_access",
        "send_message",
        "human_approval",
    ):
        assert banned not in properties
    assert properties["identity_check"]["additionalProperties"] is False


def test_review_schema_allows_only_the_four_decisions():
    schema = _schema("review_tool.schema.json")
    assert schema["additionalProperties"] is False
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "user_confirm_standard_fix",
        "user_confirm_device_change",
        "analyst_take_handover",
        "reject_draft",
    }
    assert "reset_password" not in decisions
    assert "execute_fix" not in decisions
