"""Skill files: one description line, and when to use the skill."""

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REPO = ROOT.parents[1]


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
        "draft-visit-note",
        "record-practitioner-approval",
        "record-route-seen",
    ]
    for name in names:
        meta = _frontmatter(SKILLS / name / "SKILL.md")
        assert meta["name"] == name
        lowered = meta["description"].lower()
        assert "use when" in lowered
        body = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8").lower()
        assert "when to use" in body
        assert "trigger phrase" not in lowered
        assert "routing weight" not in lowered
        assert "classic orchestration" not in lowered


def test_permissions_file_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")


def test_manifest_validates():
    schema = json.loads((REPO / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema)
    assert manifest["autonomy"]["level"] == "A1"
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    assert manifest["high_risk_actions"]["production_record_change"]["enabled"] is False
