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
        "explain-kyc-checklist",
        "review-kyc-file",
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
        assert "KYC reviewer" in text
        assert "approval" in text.lower()
        assert "record_reviewer_confirmation" in text
        assert "final_risk_rating" in text or "risk rating" in text.lower()
        assert retired not in text


def test_tool_schema_does_not_let_the_agent_approve_or_send():
    tools = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))["tools"]
    by_name = {tool["name"]: tool for tool in tools}
    assert by_name["review_kyc_file"]["callable_by_agent"] is True
    assert by_name["review_kyc_file"]["approves_customer"] is False
    assert by_name["review_kyc_file"]["sends"] is False
    for name in ("record_reviewer_confirmation", "approve_customer", "assign_risk_rating", "file_sar", "send_to_customer"):
        assert by_name[name]["callable_by_agent"] is False
