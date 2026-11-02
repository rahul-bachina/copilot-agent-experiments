"""The permissions manifest stays at autonomy A0."""

from pathlib import Path


def test_manifest_is_a0_and_names_the_maintainer():
    text = Path(__file__).resolve().parents[1].joinpath("agent-manifest.yaml").read_text(encoding="utf-8")
    assert 'id: "exp-26-skill-selection-evaluator"' in text
    assert 'level: "A0"' in text
    assert "auto_actions_enabled: false" in text
    assert "The maintainer validates routing tests" in text
    assert "writes:" in text
    assert "sends:" in text
    assert "enabled: false" in text
    assert "A3" in text
    assert "Microsoft Foundry" in text
    assert "Azure AI " + "Foundry" not in text


def test_tool_schema_disables_writes_sends_and_validation():
    import json

    tools = json.loads(
        Path(__file__).resolve().parents[1].joinpath("schema", "tools.json").read_text(encoding="utf-8")
    )
    by_name = {tool["name"]: tool for tool in tools["tools"]}
    assert by_name["evaluate_skill_routing"]["writes"] is False
    assert by_name["evaluate_skill_routing"]["sends"] is False
    assert by_name["evaluate_skill_routing"]["edits_skills"] is False
    assert by_name["record_maintainer_validation"]["callable_by_agent"] is False
    assert by_name["record_maintainer_validation"]["always_raises"] is True
    assert by_name["apply_description_diff"]["always_raises"] is True
    assert by_name["deploy_agent"]["always_raises"] is True
    assert by_name["send_routing_report"]["always_raises"] is True
