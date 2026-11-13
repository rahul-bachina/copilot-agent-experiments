"""Skills declare when to use them, on one line, without a routing weight."""

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
    return fields


def test_each_skill_has_a_single_line_description_and_an_approval_gate():
    paths = sorted(SKILLS.glob("*/SKILL.md"))
    assert [path.parent.name for path in paths] == [
        "explain-a-ranked-hit",
        "find-in-confirmed-locations",
        "flag-safeguarding-hit",
        "record-location-selection",
    ]
    harness = (ROOT / "docs" / "github-copilot-harness.md").read_text(encoding="utf-8")
    comparison = (ROOT / "docs" / "harness-comparison.md").read_text(encoding="utf-8")
    assert "Microsoft Copilot harness" in harness
    assert "unverified" in harness.lower()
    assert "unverified" in comparison.lower()
    retired = "Azure AI" + " Foundry"
    assert retired not in harness
    assert retired not in comparison
    for path in paths:
        text = path.read_text(encoding="utf-8")
        fields = _front_matter(text)
        assert fields["name"] == path.parent.name
        assert fields["description"].startswith("Use when")
        assert "\n" not in fields["description"]
        assert len(fields["description"]) > 40
        assert "approval" in text.lower() or "human_approval" in text or "confirmed" in text.lower()
        assert retired not in text
        lowered = text.lower()
        assert "routing weight" not in lowered
        assert "trigger phrase" not in lowered
        assert "does not" in lowered


def test_smoke_report_counts_each_case_once():
    report = __import__("json").loads((ROOT / "eval" / "smoke_report.json").read_text(encoding="utf-8"))
    summary = report["summary"]
    assert report["mode"] == "deterministic"
    assert report["not_a_model_evaluation"] is True
    assert summary["passed"] + summary["failed"] + summary["errors"] == summary["total_cases"]
    ids = [case["case_id"] for case in report["cases"]]
    assert len(ids) == len(set(ids)) == summary["total_cases"]
    assert summary["total_cases"] == 18
    assert summary["failed"] == 0
    assert summary["errors"] == 0
