"""Tool schema: the agent can prepare a note. It cannot rate, browse, send, or write."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schema_keeps_side_effects_off_the_agent():
    schema = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    by_name = {tool["name"]: tool for tool in schema["tools"]}
    prepare = by_name["prepare_one_to_one"]
    assert prepare["callable_by_agent"] is True
    assert prepare["writes"] is False
    assert prepare["sends"] is False
    assert prepare["rates_performance"] is False
    assert prepare["reads_mailbox"] is False
    assert prepare["reads_chat"] is False
    assert prepare["calls_graph"] is False
    for name in (
        "rate_performance",
        "compare_employees",
        "recommend_disciplinary",
        "read_mailbox",
        "read_chat",
        "send_note",
        "write_personnel_record",
    ):
        assert by_name[name]["callable_by_agent"] is False
        assert by_name[name]["always_raises"] is True
    assert by_name["acknowledge_prep_note"]["callable_by_agent"] is False
