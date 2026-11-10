"""Tool contracts stay read-only."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_cannot_publish():
    schema = _schema("review_tool.schema.json")
    decisions = set(schema["properties"]["decision"]["enum"])
    assert decisions == {"confirm_gap", "reject_gap", "defer"}
    assert schema["additionalProperties"] is False
    assert "email" not in schema["properties"]
    assert "publish" not in schema["properties"]
    assert schema["properties"]["actor"]["enum"] == ["knowledge_manager"]


def test_detect_schema_is_read_only():
    schema = _schema("detect_tool.schema.json")
    assert schema["additionalProperties"] is False
    description = schema["description"].lower()
    assert "does not publish" in description
    assert schema["properties"]["synthetic"]["const"] is True
    assert "human_approval" not in schema["properties"]
    assert "published" not in schema["properties"]
