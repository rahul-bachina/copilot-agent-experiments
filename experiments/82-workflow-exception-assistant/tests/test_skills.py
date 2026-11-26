"""Skill files: one description line, and when to use the skill."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    raw = text[4:end]
    assert "\n" not in raw.split("description:", 1)[1].split("\n", 1)[0]
    loaded: dict[str, str] = {}
    for line in raw.splitlines():
        key, separator, value = line.partition(":")
        assert separator == ":"
        loaded[key.strip()] = value.strip()
    assert isinstance(loaded["description"], str)
    assert "\n" not in loaded["description"]
    return loaded


def test_skills_say_when_to_use_them():
    names = sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md"))
    assert names == [
        "diagnose-workflow-exception",
        "record-owner-decision",
        "record-route-seen",
    ]
    for name in names:
        meta = _frontmatter(SKILLS / name / "SKILL.md")
        assert meta["name"] == name
        lowered = meta["description"].lower()
        assert "use when" in lowered
        assert "trigger phrase" not in lowered
        assert "routing weight" not in lowered
        assert "classic orchestration" not in lowered


def test_permissions_file_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")
