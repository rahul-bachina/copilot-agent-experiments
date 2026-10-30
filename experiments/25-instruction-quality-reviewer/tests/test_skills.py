"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_each_skill_names_the_harness_and_refuses_memory_and_a3():
    for relative in (
        "skills/read-instructions/SKILL.md",
        "skills/score-instruction-quality/SKILL.md",
        "skills/propose-instruction-diff/SKILL.md",
    ):
        text = _text(relative)
        assert text.startswith("---\n")
        assert "name:" in text
        assert "not the GitHub Copilot service" in text
        assert "memory" in text.lower()
        assert "do not use it" in text.lower() or "is not used" in text.lower()
        assert "A3" in text
        assert "do not apply" in text.lower() or "do not edit" in text.lower()


def test_propose_skill_does_not_tell_the_agent_to_apply_the_diff():
    text = _text("skills/propose-instruction-diff/SKILL.md").lower()
    assert "you do not apply the diff" in text
    assert "applied` is false" in text or "applied` is still false" in text


def test_harness_docs_keep_both_licensing_sentences_and_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    for text in (comparison, harness):
        assert "not the GitHub Copilot service" in text
        assert "27 October 2026" in text
        assert "lets you use Copilot Studio to build" in text
        assert "not included" in text
        assert "Azure AI " + "Foundry" not in text
    assert "Microsoft Foundry" in _text("docs/foundry.md")
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "prompt shields",
        "Unverified",
    ):
        assert label in security or label.lower() in security.lower()
