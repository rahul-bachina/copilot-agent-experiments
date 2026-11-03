"""The harness notes stay inside the boundary the code already enforces."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_each_skill_has_a_single_line_use_when_description():
    skills = list((ROOT / "skills").glob("*/SKILL.md"))
    assert len(skills) == 3
    for path in skills:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        front = text.split("---", 2)[1]
        descriptions = [line for line in front.splitlines() if line.startswith("description:")]
        assert descriptions == [descriptions[0]]
        assert descriptions[0].startswith("description: Use when ")
        assert ">" not in descriptions[0]
        assert "not the GitHub Copilot service" in text
        assert "do not use it" in text.lower()
        assert "A3" in text
        assert "quota" in text.lower()


def test_harness_docs_keep_both_licensing_sentences_and_the_brand():
    comparison = _text("docs/harness-comparison.md")
    harness = _text("docs/github-copilot-harness.md")
    for text in (comparison, harness, _text("README.md")):
        assert "not the GitHub Copilot service" in text
        assert "3 November 2026" in text
        assert "lets you use Copilot Studio to build" in text
        assert "not included" in text
        assert "not merged" in text
        assert "Azure AI Foundry" not in text
        assert "classic orchestration" not in text.lower()
        assert "weighted trigger" not in text.lower()
    assert "Microsoft Foundry" in _text("docs/foundry.md")
    security = _text("docs/security-and-permissions.md")
    for label in (
        "Conditional Access",
        "Key Vault",
        "Purview",
        "Application Insights",
        "prompt shields",
        "Unverified",
        "FinOps owner",
    ):
        assert label in security or label.lower() in security.lower()


def test_sources_pin_matches_the_pages_that_were_opened():
    from src.sources import SOURCES

    opened = [row for row in SOURCES if row["stale_applicable"]]
    assert len(opened) == 5
    assert all(row["last_verified"] == "2026-11-03" for row in opened)
    assert all(row["reopened_for_this_experiment"] is True for row in opened)
    notes = "\n".join(row["notes"] for row in opened)
    assert "not the GitHub Copilot service" in notes
    assert "starts billing after publish" in notes
    assert "from the moment you start building" in notes
    assert "No rate is copied" in notes or "No rate is copied".lower() in notes.lower() or "No rate is copied" in notes
    blob = "\n".join(row["notes"] for row in SOURCES)
    assert "£" not in blob
    assert "$" not in blob
    boundary = next(row for row in SOURCES if row["id"] == "catalogue-boundary")
    assert boundary["stale_applicable"] is False
