"""Tool contracts stay read-only."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_has_no_grant_or_send():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "human_decides_included",
        "human_decides_not_included",
        "human_requests_more_information",
        "reject_explanation",
    }
    forbidden = {
        "grant_entitlement",
        "refuse_entitlement",
        "change_entitlement",
        "waive_exclusion",
        "send_message",
        "write_record",
        "apply_section_69",
        "find_unfair_term",
    }
    assert decisions.isdisjoint(forbidden)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["actor"]["const"] == "entitlement_owner"
    assert "email" not in schema["properties"]
    assert "recipient" not in schema["properties"]
    assert "does not grant" in schema["description"]


def test_explain_schema_does_not_grant_a_write():
    schema = _schema("explain_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].casefold()
    assert "does not grant" in description
    assert "does not send" in description
    properties = schema["properties"]
    assert "question" in properties
    assert "human_approval" not in properties
    assert "grant_entitlement" not in properties
    assert properties["synthetic"]["const"] is True
