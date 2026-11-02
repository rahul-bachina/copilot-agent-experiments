"""The reviewer manifest stays inside the A0 boundary."""

from pathlib import Path

from src.yaml_reader import load_yaml

MANIFEST = Path(__file__).resolve().parents[1] / "agent-manifest.yaml"


def test_reviewer_manifest_is_a0_and_cannot_write_or_send():
    document = load_yaml(MANIFEST.read_text(encoding="utf-8"))
    assert document["agent"]["id"] == "exp-27-tool-contract-review"
    assert document["autonomy"]["level"] == "A0"
    assert document["autonomy"]["auto_actions_enabled"] is False
    assert document["tools"]["writes"]["enabled"] is False
    assert document["tools"]["sends"]["enabled"] is False
    high = document["high_risk_actions"]
    for name in (
        "approve_reject",
        "regulated_decision",
        "production_record_change",
        "external_send",
        "spend_transact",
    ):
        assert high[name]["enabled"] is False
    assert all(item["enabled"] is False for item in high["additional_high_risk"])
    approvers = [point["approver"] for point in document["human_approval"]["approval_points"]]
    assert "Security/API owner" in approvers


def test_tools_schema_disables_writes_sends_and_publish():
    import json

    schema = json.loads((MANIFEST.parent / "schema" / "tools.json").read_text(encoding="utf-8"))
    by_name = {tool["name"]: tool for tool in schema["tools"]}
    assert by_name["review_tool_contract"]["writes"] is False
    assert by_name["review_tool_contract"]["sends"] is False
    assert by_name["review_tool_contract"]["publishes_policy"] is False
    for name in ("record_owner_approval", "apply_contract_diff", "publish_policy", "deploy_contract"):
        assert by_name[name]["callable_by_agent"] is False
        assert by_name[name]["always_raises"] is True
