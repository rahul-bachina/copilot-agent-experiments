"""The tool contract is least privilege. The agent cannot call the confirmation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tool_schema_keeps_writes_and_sends_off():
    payload = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    by_name = {tool["name"]: tool for tool in payload["tools"]}
    draft = by_name["draft_employee_case"]
    assert draft["callable_by_agent"] is True
    assert draft["writes"] is False
    assert draft["sends"] is False
    assert draft["decides_outcome"] is False
    assert draft["contacts_employee"] is False
    assert draft["contacts_manager"] is False
    assert draft["persists_narrative"] is False
    confirm = by_name["record_hr_confirmation"]
    assert confirm["callable_by_agent"] is False
    assert confirm["writes"] is False
    for name in (
        "decide_outcome",
        "advise_on_merits",
        "contact_employee",
        "contact_manager",
        "write_hr_system",
    ):
        tool = by_name[name]
        assert tool["always_raises"] is True
        assert tool["callable_by_agent"] is False
        assert tool["writes"] is False
        assert tool["sends"] is False
