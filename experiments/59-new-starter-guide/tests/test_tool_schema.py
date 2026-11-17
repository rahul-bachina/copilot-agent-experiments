"""Tool schema: the agent can draft. It cannot provision, send, or approve."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schema_keeps_side_effects_off_the_agent():
    schema = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    by_name = {tool["name"]: tool for tool in schema["tools"]}
    draft = by_name["draft_starter_guide"]
    assert draft["callable_by_agent"] is True
    assert draft["writes"] is False
    assert draft["sends"] is False
    assert draft["requests_equipment"] is False
    assert draft["creates_accounts"] is False
    assert draft["grants_access"] is False
    assert draft["enrols_training"] is False
    assert draft["collects_special_category_data"] is False
    for name in (
        "request_equipment",
        "create_account",
        "grant_access",
        "enrol_training",
        "send_externally",
        "write_hr_record",
        "collect_special_category",
    ):
        assert by_name[name]["callable_by_agent"] is False
        assert by_name[name]["always_raises"] is True
    assert by_name["approve_checklist"]["callable_by_agent"] is False
    assert by_name["share_checklist"]["callable_by_agent"] is False
