"""Least-privilege tool schema. No decision, no publish, no write, no send."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))


def test_tools_cannot_decide_publish_write_or_send():
    names = []
    for tool in TOOLS["tools"]:
        names.append(tool["name"])
        assert tool["writes"] is False
        assert tool["sends"] is False
        assert tool["publishes_policy"] is False
        assert tool["changes_records"] is False
        assert tool["decides_discipline"] is False
        assert tool["concludes_compliance"] is False
        assert tool["contacts_acas"] is False
        assert tool["human_approval_to_rely_on_output"] is True
        for banned in ("dismiss", "send", "publish", "email"):
            assert banned not in tool["name"]
    assert names == ["review_employer_pack", "record_hr_decision"]


def test_the_agent_cannot_record_its_own_approval():
    decision = next(tool for tool in TOOLS["tools"] if tool["name"] == "record_hr_decision")
    assert decision["callable_by_agent"] is False
    assert decision["approver"] == "HR lead"
    review = next(tool for tool in TOOLS["tools"] if tool["name"] == "review_employer_pack")
    assert review["callable_by_agent"] is True
