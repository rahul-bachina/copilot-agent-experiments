"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _frontmatter(relative: str) -> str:
    text = _text(relative)
    return text.split("---", 2)[1]


def test_each_skill_has_a_single_line_description_that_says_when():
    for relative in (
        "skills/read-agent-pack/SKILL.md",
        "skills/draft-regression-cases/SKILL.md",
        "skills/show-draft-pr/SKILL.md",
    ):
        front = _frontmatter(relative)
        descriptions = [line for line in front.splitlines() if line.startswith("description:")]
        assert len(descriptions) == 1
        assert "Use when" in descriptions[0]
        assert not descriptions[0].rstrip().endswith(">")
        body = _text(relative)
        assert "not the GitHub Copilot service" in body or "not a GitHub Copilot service skill" in body
        assert "memory" in body.lower()
        assert "do not use it" in body.lower() or "do not store" in body.lower()
        assert "A3" in body


def test_draft_skill_does_not_weight_trigger_phrases():
    text = _text("skills/draft-regression-cases/SKILL.md").lower()
    assert "routing weight" in text
    assert "does not assign a routing weight" in text
    assert "maintainer_approved` false" in text or "maintainer_approved` stays false" in text


def test_harness_docs_do_not_invent_billing_and_keep_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    studio = _text("copilot-studio/README.md")
    for text in (comparison, harness, studio):
        assert "not the GitHub Copilot service" in text
        assert "3 November 2026" in text
        assert "Azure AI " + "Foundry" not in text
    foundry = _text("docs/foundry.md")
    assert "Microsoft Foundry" in foundry
    assert "not been done" in foundry or "does not" in foundry
    assert "unverified" in foundry.lower()
    assert "Azure AI " + "Foundry" not in foundry
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "prompt shields",
        "Unverified",
        "Entra Agent ID",
    ):
        assert label in security or label.lower() in security.lower()
