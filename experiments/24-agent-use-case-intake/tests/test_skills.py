"""The harness notes stay inside the boundary the classifier already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_RETIRED_BRAND = "Azure AI" + " Foundry"


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_each_skill_names_the_harness_and_the_governance_gate():
    for relative in (
        "skills/read-proposal/SKILL.md",
        "skills/draft-classification/SKILL.md",
        "skills/explain-classification/SKILL.md",
    ):
        text = _text(relative)
        assert text.startswith("---\n")
        assert "name:" in text
        assert "description:" in text
        assert "not the GitHub Copilot service" in text
        assert "Governance team" in text
        assert "Approve or change the intake classification" in text
        assert "A3" in text
        lowered = text.lower()
        assert "memory" in lowered
        assert "do not use it" in lowered or "do not write" in lowered
        assert _RETIRED_BRAND not in text


def test_harness_docs_stay_inside_what_was_opened():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    studio = _text("copilot-studio/README.md")
    for text in (comparison, harness, studio):
        assert "not the GitHub Copilot service" in text
        assert "30 October 2026" in text
        assert _RETIRED_BRAND not in text
        assert "£" not in text
    foundry = _text("docs/foundry.md")
    assert "Microsoft Foundry" in foundry
    assert "No Foundry resource is created" in foundry
    assert _RETIRED_BRAND not in foundry
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "Entra Agent ID",
        "Unverified",
        "prompt shields",
    ):
        assert label.lower() in security.lower()
    assert _RETIRED_BRAND not in security
    flow = _text("copilot-studio/power-automate-flow.md")
    assert "provision" in flow.lower()
    assert "does not contain" in flow.lower()
    prompt = _text("copilot-studio/system-prompt.md")
    assert "DRAFT FOR THE GOVERNANCE TEAM" in prompt
    assert "A3" in prompt
    architecture = _text("docs/architecture.md")
    assert "governance team" in architecture.lower()
    assert "architecture_diagram.png" in architecture
