"""The GitHub Copilot harness skills declare metadata and an approval gate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


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


def test_each_skill_has_name_description_and_an_approval_gate():
    paths = sorted(SKILLS.glob("*/SKILL.md"))
    assert [path.parent.name for path in paths] == [
        "answer-from-handbook",
        "review-employer-pack",
        "summarise-anonymised-report",
    ]
    harness = (ROOT / "docs" / "github-copilot-harness.md").read_text(encoding="utf-8")
    assert "not the GitHub Copilot service" in harness
    retired = "Azure AI" + " Foundry"
    assert retired not in harness
    for path in paths:
        text = path.read_text(encoding="utf-8")
        fields = _front_matter(text)
        assert fields["name"] == path.parent.name
        assert len(fields["description"]) > 40
        assert "HR lead" in text or "HR role" in text or "policy owner" in text
        assert "approval" in text.lower()
        assert "hr_decision" in text or "disciplinary_decision" in text
        assert "not the GitHub Copilot service" in text
        assert retired not in text
