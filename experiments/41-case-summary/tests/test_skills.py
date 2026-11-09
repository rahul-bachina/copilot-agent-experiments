"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _description(text: str) -> str:
    lines = text.splitlines()
    assert lines[0] == "---"
    for line in lines[1:]:
        if line.startswith("description:"):
            raw = line.split(":", 1)[1].strip()
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            return raw
        if line == "---":
            break
    raise AssertionError("description missing")


SKILLS = (
    "skills/extract-cited-case-summary/SKILL.md",
    "skills/check-pinpoint-citations/SKILL.md",
    "skills/list-gaps-and-stale-data/SKILL.md",
)


def test_each_skill_has_a_single_line_description_that_says_when_to_use():
    for relative in SKILLS:
        text = _text(relative)
        description = _description(text)
        assert "\n" not in description
        assert description.lower().startswith("use when")
        assert "not the GitHub Copilot service" in text
        assert "memory" in text.lower()
        assert "do not use it" in text.lower()
        assert "A3" in text
        assert "do not contact the customer" in text.lower()
        assert "do not change the record" in text.lower()
        assert "record_accuracy_check" in text
        assert "not an agent tool" in text.lower()
        assert "does not assign routing weights" in text
        assert "trigger phrases" in text
        assert "generative orchestration" in text.lower()
        assert "9 November 2026" in text


def test_harness_docs_do_not_invent_billing_and_keep_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    studio = _text("copilot-studio/README.md")
    for text in (comparison, harness, studio):
        assert "not the GitHub Copilot service" in text
        assert "9 November 2026" in text
        assert "not opened" in text.lower()
        assert "does not assign routing weights" in text or "Do not give it a routing weight" in text
        assert "Azure AI " + "Foundry" not in text
    foundry = _text("docs/foundry.md")
    assert "Microsoft Foundry" in foundry
    assert "unverified" in foundry.lower()
    assert "not called" in foundry.lower() or "does not call" in foundry.lower()
    assert "Azure AI " + "Foundry" not in foundry
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "Entra Agent ID",
        "prompt shields",
        "Unverified",
    ):
        assert label in security or label.lower() in security.lower()
    assert "Article 5" in security
    assert "Article 22A" in security
    assert "HTTP 403" in security
