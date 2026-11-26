"""Skill frontmatter is one line and says when to use the skill."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_descriptions_are_single_line_and_say_when():
    paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert len(paths) >= 4
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        end = text.index("\n---", 4)
        front = text[4:end]
        assert "\nname: " not in "\n" + front or front.startswith("name:")
        description = next(line for line in front.splitlines() if line.startswith("description:"))
        assert "\n" not in description
        assert description.startswith("description: ")
        assert "Use when" in description
        assert "Azure AI " + "Foundry" not in text
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")
