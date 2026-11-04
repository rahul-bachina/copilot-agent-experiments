"""Skill files: one description line, and when to use it."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    raw = text[4:end]
    assert "\n" not in raw.split("description:", 1)[1].split("\n", 1)[0]
    loaded = yaml.safe_load(raw)
    assert isinstance(loaded["description"], str)
    assert "\n" not in loaded["description"]
    return loaded


def test_both_skills_say_when_to_use_them():
    names = sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md"))
    assert names == ["explain-case-proposal", "propose-employee-case-intake"]
    for name in names:
        meta = _frontmatter(SKILLS / name / "SKILL.md")
        assert meta["name"] == name
        lowered = meta["description"].lower()
        assert "use when" in lowered
        assert "trigger phrase" not in lowered
        assert "routing weight" not in lowered


def test_skills_do_not_tell_the_agent_to_confirm_or_contact():
    for path in SKILLS.glob("*/SKILL.md"):
        text = path.read_text(encoding="utf-8").lower()
        assert "callable_by_agent: false" in text or "must not call" in text
        assert "do not contact" in text
        assert "do not write" in text or "does not write" in text
