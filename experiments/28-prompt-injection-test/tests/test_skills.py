"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_each_skill_names_the_harness_and_refuses_memory_and_a3():
    for relative in (
        "skills/load-suite/SKILL.md",
        "skills/run-sandbox/SKILL.md",
        "skills/draft-findings/SKILL.md",
    ):
        text = _text(relative)
        assert text.startswith("---\n")
        assert "name:" in text
        assert "not the GitHub Copilot service" in text
        assert "memory" in text.lower()
        assert "do not use it" in text.lower()
        assert "A3" in text
        assert "do not assess" in text.lower()
        assert "do not publish" in text.lower() or "you do not publish" in text.lower()


def test_draft_skill_does_not_tell_the_agent_to_remediate():
    text = _text("skills/draft-findings/SKILL.md").lower()
    assert "you do not apply it" in text
    assert "remediation_applied` stays false" in text


def test_harness_docs_do_not_invent_billing_and_keep_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    studio = _text("copilot-studio/README.md")
    for text in (comparison, harness, studio):
        assert "not the GitHub Copilot service" in text
        assert "2 November 2026" in text
        assert "not opened" in text.lower()
        assert "Azure AI " + "Foundry" not in text
    foundry = _text("docs/foundry.md")
    assert "Microsoft Foundry" in foundry
    assert "Attack Success Rate" in foundry
    assert "does not call" in foundry
    assert "Azure AI " + "Foundry" not in foundry
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "prompt shields",
        "Unverified",
    ):
        assert label in security or label.lower() in security.lower()
