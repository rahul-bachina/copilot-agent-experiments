"""Skill files: one description line, and when to use the skill."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    end = text.index("\n---\n", 4)
    raw = text[4:end]
    loaded: dict[str, str] = {}
    for line in raw.splitlines():
        key, separator, value = line.partition(":")
        assert separator == ":"
        loaded[key.strip()] = value.strip()
    assert isinstance(loaded["description"], str)
    assert "\n" not in loaded["description"]
    return loaded


def test_both_skills_say_when_to_use_them():
    names = sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md"))
    assert names == ["explain-leave-policy", "route-a-leave-question"]
    for name in names:
        meta = _frontmatter(SKILLS / name / "SKILL.md")
        assert meta["name"] == name
        lowered = meta["description"].lower()
        assert "use when" in lowered
        assert "trigger phrase" not in lowered
        assert "routing weight" not in lowered


def test_skills_do_not_grant_leave_or_a_rate():
    for path in SKILLS.glob("*/SKILL.md"):
        text = path.read_text(encoding="utf-8").lower()
        assert "do not decide" in text or "does not decide" in text
        assert "must not call" in text
        assert "routing weights trigger" not in text


def test_tool_schema_is_least_privilege():
    tools = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))["tools"]
    by_name = {tool["name"]: tool for tool in tools}
    explain = by_name["explain_leave_policy"]
    assert explain["writes"] is False
    assert explain["sends"] is False
    assert explain["decides_entitlement"] is False
    assert explain["books_leave"] is False
    assert explain["records_leave"] is False
    assert explain["calculates_pay"] is False
    assert explain["callable_by_agent"] is True
    for name in ("record_seen", "decide_entitlement", "book_leave", "record_leave", "calculate_pay", "approve_policy"):
        assert by_name[name]["callable_by_agent"] is False
