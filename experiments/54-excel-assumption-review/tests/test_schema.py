"""Tool contracts stay least-privilege, and permissions.yaml matches the manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))


def test_review_schema_cannot_edit_or_judge():
    schema = _schema("review_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["properties"]["synthetic"]["const"] is True
    props = schema["properties"]
    for forbidden in (
        "human_approval",
        "workbook_modified",
        "assumption_judged",
        "benchmark",
        "findings_accepted",
        "graph_called",
    ):
        assert forbidden not in props
    assert "does not edit the workbook" in schema["description"].lower()


def test_confirm_schema_is_scope_only():
    schema = _schema("confirm_tool.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["properties"]["decision"]["const"] == "confirm_workbook_ranges_and_formulas"
    assert "findings_accepted" not in schema["properties"]
    assert "email" not in schema["properties"]
    assert "does not edit the workbook" in schema["description"].lower()
    assert "does not accept the findings" in schema["description"].lower()


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
