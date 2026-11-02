"""Precision and recall on a hand-built confusion, and parsing of real SKILL.md files."""

from pathlib import Path

from src.metrics import per_class
from src.skill_parse import skill_from_markdown


def test_precision_and_recall_on_a_known_confusion():
    rows = [
        {"expected_class": "alpha", "predicted_class": "alpha"},
        {"expected_class": "alpha", "predicted_class": "beta"},
        {"expected_class": "beta", "predicted_class": "beta"},
        {"expected_class": "none", "predicted_class": "alpha"},
        {"expected_class": "human", "predicted_class": "human"},
    ]
    by_class = {row["class"]: row for row in per_class(rows, ["alpha", "beta"])}
    assert by_class["alpha"]["true_positive"] == 1
    assert by_class["alpha"]["false_positive"] == 1
    assert by_class["alpha"]["false_negative"] == 1
    assert by_class["alpha"]["precision"] == 50.0
    assert by_class["alpha"]["recall"] == 50.0
    assert by_class["beta"]["true_positive"] == 1
    assert by_class["beta"]["false_positive"] == 1
    assert by_class["beta"]["recall"] == 100.0
    assert by_class["none"]["false_negative"] == 1
    assert by_class["human"]["precision"] == 100.0


def test_repository_skill_files_parse():
    root = Path(__file__).resolve().parents[3]
    relative = [
        "experiments/01-foi-complaint-triage/skills/triage-submission/SKILL.md",
        "experiments/08-uk-pii-redaction-gateway/skills/propose-redaction/SKILL.md",
        "experiments/12-document-intake/skills/inventory-documents/SKILL.md",
        "experiments/05-awaabs-law-hazard-triage/skills/case-review/SKILL.md",
        "experiments/03-agent-inventory-atrs-assurance/skills/draft-assurance-pack/SKILL.md",
        "experiments/25-instruction-quality-reviewer/skills/score-instruction-quality/SKILL.md",
    ]
    for path in relative:
        skill = skill_from_markdown((root / path).read_text(encoding="utf-8"), path)
        assert skill.id
        assert skill.description
        assert skill.kind == "skill"


def test_trigger_phrases_heading_is_read_when_front_matter_has_none():
    text = """---
name: desk-topic
description: >
  Answer a question about a parking permit renewal.
---

# Desk topic

## Trigger phrases

- renew a parking permit
- Do not use this topic to take a payment.
"""
    skill = skill_from_markdown(text, "desk-topic.md")
    assert skill.triggers == [
        "renew a parking permit",
        "Do not use this topic to take a payment.",
    ]
