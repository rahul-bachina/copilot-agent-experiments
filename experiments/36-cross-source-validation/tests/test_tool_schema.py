"""The tool list is least privilege. Writes, sends, and decisions stay off."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schema_keeps_decisions_off():
    tools = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))["tools"]
    by_name = {tool["name"]: tool for tool in tools}
    assert by_name["compare_sources"]["callable_by_agent"] is True
    assert by_name["compare_sources"]["writes"] is False
    assert by_name["compare_sources"]["sends"] is False
    assert by_name["compare_sources"]["calls_model"] is False
    assert by_name["compare_sources"]["calls_network"] is False
    assert by_name["compare_sources"]["chooses_source"] is False
    assert by_name["compare_sources"]["human_approval_to_resolve_material"] is True
    for name in ("choose_source", "edit_record", "contact_party", "lookup_register", "recommend_a3"):
        assert by_name[name]["callable_by_agent"] is False
        assert by_name[name]["always_raises"] is True
    assert by_name["record_reviewer_resolution"]["callable_by_agent"] is False
    assert by_name["record_reviewer_resolution"]["not_an_agent_tool"] is True
