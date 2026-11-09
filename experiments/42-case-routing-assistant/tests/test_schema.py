"""Tool contracts stay read-only and do not offer a reroute."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_has_no_reroute_or_close_decision():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {
        "adviser_confirm_proposed_route",
        "adviser_accept_human_queue",
        "queue_owner_approve_rule_change",
        "reject_proposal",
    }
    forbidden = {
        "reroute",
        "close",
        "escalate",
        "change_routing_rules",
        "set_priority",
        "send",
        "decide_entitlement",
        "label_vulnerable",
    }
    assert decisions.isdisjoint(forbidden)
    assert schema["additionalProperties"] is False


def test_routing_schema_does_not_grant_a_write():
    schema = _schema("routing_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert "queue" not in schema["properties"]
    assert "priority" not in schema["properties"]
    assert schema["properties"]["synthetic"]["const"] is True
