"""Least-privilege tool schema. No send, no write, no release, no exemption."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))


def test_tools_cannot_write_send_release_or_apply_an_exemption():
    names = []
    for tool in TOOLS["tools"]:
        names.append(tool["name"])
        assert tool["writes"] is False
        assert tool["sends"] is False
        assert tool["releases"] is False
        assert tool["accepts_into_queue"] is False
        assert tool["persists_file_body"] is False
        assert tool["applies_exemption"] is False
        for banned in ("send", "release", "disclose", "approve_exemption"):
            assert banned not in tool["name"]
    assert names == [
        "build_evidence_pack",
        "record_export_approval",
        "produce_export_index",
    ]


def test_the_agent_cannot_record_its_own_approval_or_export():
    approval = next(tool for tool in TOOLS["tools"] if tool["name"] == "record_export_approval")
    export = next(tool for tool in TOOLS["tools"] if tool["name"] == "produce_export_index")
    assert approval["callable_by_agent"] is False
    assert approval["approver"] == "Evidence pack approver"
    assert export["callable_by_agent"] is False
    assert export["approver"] == "Evidence pack approver"
    build = next(tool for tool in TOOLS["tools"] if tool["name"] == "build_evidence_pack")
    assert build["callable_by_agent"] is True
    assert build["human_approval_to_rely_on_output"] is True
    assert build["human_approval_to_run"] is False
