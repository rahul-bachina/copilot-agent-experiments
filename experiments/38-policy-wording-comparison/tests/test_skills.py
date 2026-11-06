"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_each_skill_has_a_single_line_use_when_description():
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert len(skills) == 3
    for path in skills:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        front = text.split("---", 2)[1]
        descriptions = [line for line in front.splitlines() if line.startswith("description:")]
        assert len(descriptions) == 1
        assert descriptions[0].startswith("description: Use when ")
        assert ">" not in descriptions[0]
        assert "not the GitHub Copilot service" in text
        assert "do not store" in text.lower() or "do not use it" in text.lower()
        assert "A3" in text
        assert "specialist" in text.lower()


def test_harness_docs_keep_the_opened_sentences_and_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    for text in (comparison, harness, _text("README.md"), _text("copilot-studio/README.md")):
        assert "not the GitHub Copilot service" in text
        assert "6 November 2026" in text
        retired = "Azure AI " + "Foundry"
        assert retired not in text
        assert "classic orchestration" not in text.lower()
        assert "weighted trigger" not in text.lower()
        assert "routing weights" in text
    assert "Microsoft Foundry" in _text("docs/foundry.md")
    assert "not opened" in _text("docs/foundry.md").lower()
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "prompt shields",
        "Unverified",
        "Wording specialist",
    ):
        assert label in security or label.lower() in security.lower()


def test_permissions_manifest_matches_the_agent_manifest():
    assert _text("permissions.yaml") == _text("agent-manifest.yaml")
    text = _text("agent-manifest.yaml")
    assert 'level: "A0"' in text
    assert "enabled: false" in text
    assert "Wording specialist" in text
    retired = "Azure AI " + "Foundry"
    assert retired not in text


def test_tool_schema_is_least_privilege():
    import json

    tools = json.loads(_text("schema/tools.json"))["tools"]
    by_name = {tool["name"]: tool for tool in tools}
    assert by_name["compare_policy_wordings"]["writes"] is False
    assert by_name["compare_policy_wordings"]["sends"] is False
    assert by_name["compare_policy_wordings"]["calls_document_intelligence"] is False
    for name in (
        "interpret_favourability",
        "recommend_buy_sell_renew",
        "draft_endorsement",
        "contact_broker",
        "write_policy_admin",
        "decide_coverage",
        "record_specialist_review",
    ):
        assert by_name[name]["callable_by_agent"] is False
