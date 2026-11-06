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
        "customer_confirm_address_draft",
        "customer_confirm_appointment_draft",
        "handler_take_handover",
        "handler_approve_correspondence_for_own_send",
        "reject_draft",
    }
    forbidden = {
        "reset_password",
        "take_payment",
        "close_complaint",
        "change_tariff",
        "change_contract",
        "send_message",
        "write_record",
    }
    assert decisions.isdisjoint(forbidden)
    assert schema["additionalProperties"] is False
    assert "email" not in schema["properties"]
    assert "recipient" not in schema["properties"]


def test_reply_schema_does_not_grant_a_write():
    schema = _schema("reply_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not change" in description
    assert "does not send" in description
    properties = schema["properties"]
    assert "text" in properties
    assert "human_approval" not in properties
    assert "message_sent" not in properties
