"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_each_skill_names_the_harness_and_refuses_memory_and_a3():
    for relative in (
        "skills/read-tool-contract/SKILL.md",
        "skills/score-tool-contract/SKILL.md",
        "skills/propose-contract-diff/SKILL.md",
    ):
        text = _text(relative)
        assert text.startswith("---\n")
        assert "name:" in text
        assert "not the GitHub Copilot service" in text
        assert "2 November 2026" in text
        assert "memory" in text.lower()
        assert "do not use it" in text.lower()
        assert "A3" in text
        assert "do not apply" in text.lower() or "do not edit" in text.lower() or "do not publish" in text.lower()


def test_propose_skill_does_not_tell_the_agent_to_apply_or_publish():
    text = _text("skills/propose-contract-diff/SKILL.md").lower()
    assert "you do not apply the diff" in text
    assert "you do not publish" in text
    assert "applied` is still false" in text
    assert "published` is still false" in text
    assert "set_by_api_owner" in text
    assert 'calls="20"' not in text


def test_harness_docs_keep_the_opened_pages_and_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    studio = _text("copilot-studio/README.md")
    for text in (comparison, harness, studio):
        assert "not the GitHub Copilot service" in text
        assert "2 November 2026" in text
        assert "Azure AI " + "Foundry" not in text
        assert "lets you use Copilot Studio to build" not in text
    foundry = _text("docs/foundry.md")
    assert "Microsoft Foundry" in foundry
    assert "SET_BY_API_OWNER" in foundry
    assert "300" in foundry
    assert "subscription key" in foundry
    assert "not opened for this experiment" in foundry.lower() or "was not opened" in foundry.lower()
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "prompt shields",
        "Entra Agent ID",
        "Unverified",
        "Data loss prevention",
    ):
        assert label.lower() in security.lower()
    assert "2 November 2026" in security
