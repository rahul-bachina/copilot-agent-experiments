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
        assert "do not use it" in text.lower()
        assert "A3" in text
        assert "handler" in text.lower() or "evaluation owner" in text.lower()


def test_harness_docs_name_the_framework_and_not_the_retired_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    for text in (comparison, harness, _text("README.md"), _text("copilot-studio/README.md")):
        assert "not the GitHub Copilot service" in text
        assert "5 November 2026" in text
        retired = "Azure AI " + "Foundry"
        assert retired not in text
        assert "classic orchestration" not in text.lower()
        assert "weighted trigger" not in text.lower()
    assert "Microsoft Foundry" in _text("docs/foundry.md")
    assert "not opened" in _text("docs/foundry.md").lower() or "not called" in _text("docs/foundry.md").lower()
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "prompt shields",
        "unverified",
        "Claims handler",
    ):
        assert label.lower() in security.lower()


def test_permissions_manifest_matches_the_agent_manifest():
    assert _text("permissions.yaml") == _text("agent-manifest.yaml")
    text = _text("agent-manifest.yaml")
    assert 'level: "A1"' in text
    assert "enabled: false" in text
    assert "Claims handler" in text
    retired = "Azure AI " + "Foundry"
    assert retired not in text


def test_tools_do_not_grant_an_outcome():
    tools = _text("schema/tools.json")
    assert '"declines_claim": false' in tools
    assert '"writes_claims_system": false' in tools
    assert '"callable_by_agent": false' in tools
