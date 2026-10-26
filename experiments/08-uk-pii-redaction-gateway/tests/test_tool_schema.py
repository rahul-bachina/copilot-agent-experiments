"""Least-privilege tool schema. No release, no send, no write."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))


def test_tools_cannot_release_send_or_write():
    names = []
    for tool in TOOLS["tools"]:
        names.append(tool["name"])
        assert tool["writes"] is False
        assert tool["sends"] is False
        assert tool["releases"] is False
        assert tool["persists_raw_values"] is False
        assert "release" not in tool["name"]
        assert "send" not in tool["name"]
    assert names == ["propose_redaction", "record_reviewer_decision"]


def test_the_agent_cannot_record_its_own_approval():
    decision = next(tool for tool in TOOLS["tools"] if tool["name"] == "record_reviewer_decision")
    assert decision["callable_by_agent"] is False
    assert decision["approver"] == "Privacy reviewer"
    propose = next(tool for tool in TOOLS["tools"] if tool["name"] == "propose_redaction")
    assert propose["callable_by_agent"] is True
    assert propose["human_approval_to_rely_on_output"] is True
