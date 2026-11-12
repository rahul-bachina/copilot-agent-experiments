"""The tool list is read-only."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schema_has_no_side_effects():
    schema = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    names = [tool["name"] for tool in schema["tools"]]
    assert names == ["preview_scope", "confirm_scope", "produce_digest"]
    assert schema["side_effects"] == "none"
    for tool in schema["tools"]:
        assert tool["access"] == "read"
    forbidden = set(schema["forbidden"])
    assert {"post", "reply", "react", "mention", "forward", "send"} <= forbidden
    assert "post" not in names
