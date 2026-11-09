"""Tool contracts stay read-only."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_has_no_send_or_write_decision():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "representative_approve_for_own_send",
        "representative_request_revision",
        "reject_draft",
    }
    forbidden = {
        "send_message",
        "write_case",
        "offer_redress",
        "close_case",
        "promise_outcome",
        "send",
    }
    assert decisions.isdisjoint(forbidden)
    assert schema["additionalProperties"] is False
    assert "email" not in schema["properties"]
    assert "recipient" not in schema["properties"]
    assert schema["properties"]["recipient_role"]["enum"] == ["customer-on-case"]


def test_draft_schema_does_not_grant_a_send():
    schema = _schema("draft_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not send" in description
    assert "does not write" in description
    properties = schema["properties"]
    assert "text" in properties
    assert "human_approval" not in properties
    assert "message_sent" not in properties
    assert properties["synthetic"]["const"] is True
