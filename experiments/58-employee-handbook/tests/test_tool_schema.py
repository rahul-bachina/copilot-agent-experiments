"""Tool schema: the agent can answer. It cannot decide, send, write, or approve."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schema_keeps_side_effects_off_the_agent():
    schema = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    by_name = {tool["name"]: tool for tool in schema["tools"]}
    answer = by_name["answer_handbook_question"]
    assert answer["callable_by_agent"] is True
    assert answer["writes"] is False
    assert answer["sends"] is False
    assert answer["decides_entitlement"] is False
    assert answer["calls_sharepoint"] is False
    for name in ("decide_entitlement", "send_answer", "write_record", "approve_source"):
        assert by_name[name]["callable_by_agent"] is False
        assert by_name[name]["always_raises"] is True
    assert by_name["acknowledge_answer"]["callable_by_agent"] is False
