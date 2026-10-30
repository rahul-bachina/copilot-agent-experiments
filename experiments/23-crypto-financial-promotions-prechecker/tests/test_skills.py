"""The GitHub Copilot harness skills declare metadata and the approval gates."""

import json
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
        "build-promotion-checklist",
        "read-promotion-draft",
        "stop-before-sign-off",
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
        assert len(fields["description"]) > 40
        assert "section 21 approver" in text
        assert "approval" in text.lower()
        assert "approve_promotion" in text or path.parent.name == "stop-before-sign-off"
        assert retired not in text
    build = (SKILLS / "build-promotion-checklist" / "SKILL.md").read_text(encoding="utf-8")
    assert "approve_promotion" in build
    assert "publish_promotion" in build
    assert "draft-promotion-checklist.json" in build
    stop = (SKILLS / "stop-before-sign-off" / "SKILL.md").read_text(encoding="utf-8")
    assert "approve_promotion" in stop
    assert "publish_promotion" in stop


def test_tool_schema_does_not_let_the_agent_approve_or_publish():
    tools = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))["tools"]
    by_name = {tool["name"]: tool for tool in tools}
    assert by_name["precheck_promotion"]["callable_by_agent"] is True
    assert by_name["precheck_promotion"]["approves_promotion"] is False
    assert by_name["precheck_promotion"]["sends"] is False
    assert by_name["precheck_promotion"]["publishes"] is False
    for name in (
        "approve_promotion",
        "publish_promotion",
        "give_compliance_opinion",
    ):
        assert by_name[name]["callable_by_agent"] is False
        assert by_name[name]["always_raises"] is True
