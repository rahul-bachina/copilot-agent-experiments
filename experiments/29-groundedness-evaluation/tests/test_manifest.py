"""The local manifest reader and the tool schema stay least privilege."""

import json

from src.manifest_yaml import load_yaml
from tests.support import ROOT


def test_this_manifest_is_a0_and_cannot_write_or_send():
    manifest = load_yaml((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["agent"]["id"] == "exp-29-groundedness-evaluation"
    assert manifest["autonomy"]["level"] == "A0"
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    point = next(
        item
        for item in manifest["human_approval"]["approval_points"]
        if item["action"] == "Approve the draft thresholds"
    )
    assert point["approver"] == "Evaluation owner"
    assert point["mandatory"] is True
    release = next(
        item
        for item in manifest["human_approval"]["approval_points"]
        if item["action"] == "Record a pass or fail release"
    )
    assert release["approver"] == "Evaluation owner"
    assert release["mandatory"] is True
    for key in (
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ):
        assert manifest["high_risk_actions"][key]["enabled"] is False
    for extra in manifest["high_risk_actions"]["additional_high_risk"]:
        assert extra["enabled"] is False


def test_tool_schema_has_no_write_and_no_network():
    tools = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    names = [item["name"] for item in tools["tools"]]
    assert names == [
        "load_passages",
        "score_claims",
        "approve_thresholds",
        "record_release",
        "call_foundry_evaluator",
    ]
    for item in tools["tools"]:
        if "writes" in item:
            assert item["writes"] is False
        if "sends" in item:
            assert item["sends"] is False
    blocked = [item for item in tools["tools"] if item.get("always_raises")]
    assert {item["name"] for item in blocked} == {
        "approve_thresholds",
        "record_release",
        "call_foundry_evaluator",
    }
    assert all(item["callable_by_agent"] is False for item in blocked)


def test_schema_pointer_is_the_shared_manifest_schema():
    text = (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")
    assert "../../../schemas/agent-manifest.schema.json" in text
