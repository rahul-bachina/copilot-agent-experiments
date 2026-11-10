"""The GitHub Copilot harness skills declare metadata and an approval gate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _front_matter(text: str) -> dict[str, str]:
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    block = text[4:end]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        key, separator, rest = line.partition(":")
        assert separator == ":", line
        assert key in {"name", "description"}
        assert rest.strip()
        assert "\n" not in rest
        fields[key] = rest.strip()
    assert list(fields) == ["name", "description"]
    return fields


def test_each_skill_has_a_single_line_description_and_an_approval_gate():
    paths = sorted(SKILLS.glob("*/SKILL.md"))
    assert [path.parent.name for path in paths] == [
        "explain-entitlement",
        "record-human-decision",
        "route-disputed-entitlement",
        "show-uncertainty",
    ]
    harness = (ROOT / "docs" / "github-copilot-harness.md").read_text(encoding="utf-8")
    comparison = (ROOT / "docs" / "harness-comparison.md").read_text(encoding="utf-8")
    assert "not the GitHub Copilot service" in harness
    assert "not the GitHub Copilot service" in comparison
    retired = "Azure AI" + " Foundry"
    assert retired not in harness
    assert retired not in comparison
    for path in paths:
        text = path.read_text(encoding="utf-8")
        fields = _front_matter(text)
        assert fields["name"] == path.parent.name
        assert fields["description"].startswith("Use when ")
        assert "\n" not in fields["description"]
        assert "Approval gates" in text
        assert "routing weights trigger" not in text.casefold()
        assert retired not in text
    assert "does not assign routing weights" in harness
    assert "does not assign routing weights" in comparison


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (
        ROOT / "agent-manifest.yaml"
    ).read_text(encoding="utf-8")
