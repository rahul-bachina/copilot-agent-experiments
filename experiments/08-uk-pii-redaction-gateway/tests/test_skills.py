"""The GitHub Copilot harness skills declare metadata and the existing approval gates."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MANIFEST = ROOT / "agent-manifest.yaml"

REQUIRED_SKILLS = (
    "explain-redaction-finding",
    "propose-redaction",
)


def _front_matter(text: str) -> dict[str, str]:
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    block = text[4:end]
    fields: dict[str, str] = {}
    current = None
    lines: list[str] = []
    for line in block.splitlines():
        if line.startswith("name:") or line.startswith("description:"):
            if current:
                fields[current] = " ".join(lines).strip()
            current, _, rest = line.partition(":")
            lines = [rest.strip()]
        elif current:
            lines.append(line.strip())
    if current:
        fields[current] = " ".join(lines).strip()
    return fields


def _manifest_actions(section_name: str) -> list[str]:
    """Read action strings from one mapping under human_approval, and no further."""
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(f"  {section_name}:"))
    indent = len(lines[start]) - len(lines[start].lstrip(" "))
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.strip() and not line.lstrip().startswith("#"):
            this = len(line) - len(line.lstrip(" "))
            if this <= indent:
                break
        body.append(line)
    return re.findall(r'action:\s*"([^"]+)"', "\n".join(body))


def test_each_skill_has_name_description_and_an_approval_gate():
    paths = sorted(SKILLS.glob("*/SKILL.md"))
    assert [path.parent.name for path in paths] == list(REQUIRED_SKILLS)
    for path in paths:
        text = path.read_text(encoding="utf-8")
        fields = _front_matter(text)
        assert fields["name"] == path.parent.name
        description = fields["description"].lstrip("> ").strip()
        assert len(description) > 40
        assert ":" not in description
        assert "Tool contract" in text
        assert "Approval gates" in text
        assert "Privacy reviewer" in text
        assert "not the GitHub Copilot service" in text
        retired = "Azure AI" + " Foundry"
        assert retired not in text


def test_skill_approval_actions_match_the_manifest():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in SKILLS.glob("*/SKILL.md"))
    mandatory = _manifest_actions("approval_points")
    optional = _manifest_actions("no_approval_required")
    assert mandatory == [
        "Approve the redacted output before release",
        "Accept or reject each model suggestion before it is treated as a redaction",
        "Decide whether a reversible token vault may be stored",
        "Release or send the redacted output",
    ]
    assert optional == [
        "View the redaction proposal",
        "Re-run detection on the same text",
    ]
    for action in mandatory + optional:
        assert action in combined
    propose = (SKILLS / "propose-redaction" / "SKILL.md").read_text(encoding="utf-8")
    assert "does not add an approval step" in propose
    assert "output_is_anonymised" in propose
    assert "agent_may_release" in propose
    assert "src/gateway.py" in propose


def test_harness_docs_name_the_core_and_do_not_invent_a_licence():
    harness = (ROOT / "docs" / "github-copilot-harness.md").read_text(encoding="utf-8")
    comparison = (ROOT / "docs" / "harness-comparison.md").read_text(encoding="utf-8")
    assert "not the GitHub Copilot service" in harness
    assert "src/gateway.py" in harness
    assert "src/identifiers.py" in comparison
    assert "agent-manifest.yaml" in comparison
    assert "Copilot Credits" in comparison
    assert "unverified" in comparison.lower()
    assert "preview" in comparison.lower()
    retired = "Azure AI" + " Foundry"
    assert retired not in harness
    assert retired not in comparison
