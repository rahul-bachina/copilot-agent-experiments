"""Tool schemas do not accept a decision, a send, or a case write."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"

BANNED = {
    "eligibility_decision",
    "eligibility_decided",
    "case_created",
    "message_sent",
    "send_email",
    "create_case",
    "appointment_booked",
    "payment_taken",
    "released_to_resident",
    "email",
    "phone",
    "case_id",
}


def _load(name: str) -> dict:
    return json.loads((SCHEMA / name).read_text(encoding="utf-8"))


def test_front_door_schema_is_closed_and_has_no_action_fields():
    schema = _load("front_door_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["enquiry", "as_of"]
    enquiry = schema["properties"]["enquiry"]
    assert enquiry["additionalProperties"] is False
    assert BANNED.isdisjoint(enquiry["properties"])
    assert "synthetic" in enquiry["required"]


def test_review_schema_only_allows_three_decisions():
    schema = _load("adviser_review_tool.schema.json")
    assert schema["additionalProperties"] is False
    review = schema["properties"]["review"]
    assert review["additionalProperties"] is False
    assert review["properties"]["decision"]["enum"] == [
        "accept_draft",
        "reject_draft",
        "take_handover",
    ]
    assert BANNED.isdisjoint(review["properties"])
    assert "text" not in review["properties"]
