"""Least-privilege tool schema. No queue, no send, no write, no release."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))


def test_tools_cannot_write_send_release_or_queue():
    names = []
    for tool in TOOLS["tools"]:
        names.append(tool["name"])
        assert tool["writes"] is False
        assert tool["sends"] is False
        assert tool["releases"] is False
        assert tool["accepts_into_queue"] is False
        assert tool["persists_file_body"] is False
        for banned in ("send", "release", "commit", "approve", "reject"):
            assert banned not in tool["name"]
    assert names == [
        "inventory_documents",
        "record_user_confirmation",
        "record_reviewer_decision",
    ]


def test_the_agent_cannot_record_its_own_approval():
    confirmation = next(tool for tool in TOOLS["tools"] if tool["name"] == "record_user_confirmation")
    decision = next(tool for tool in TOOLS["tools"] if tool["name"] == "record_reviewer_decision")
    assert confirmation["callable_by_agent"] is False
    assert confirmation["approver"] == "Intake user"
    assert decision["callable_by_agent"] is False
    assert decision["approver"] == "Intake reviewer"
    inventory = next(tool for tool in TOOLS["tools"] if tool["name"] == "inventory_documents")
    assert inventory["callable_by_agent"] is True
    assert inventory["human_approval_to_rely_on_output"] is True
    assert inventory["human_approval_to_run"] is False
