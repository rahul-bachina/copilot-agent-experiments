"""Load the sample bundle and the safety flags every report must keep."""

from __future__ import annotations

import json
from pathlib import Path

from src.report import evaluate

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_bundle.json"


def bundle() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def run(as_of: str = "2026-11-02", **kwargs):
    return evaluate(bundle(), as_of, base_dir=SAMPLE.parent, **kwargs)


def safety(report: dict) -> None:
    assert report["label"] == "DRAFT FOR MAINTAINER REVIEW"
    assert report["catalogue_id"] == "G004"
    assert report["experiment"] == "26"
    assert report["autonomy"] == "A0"
    assert report["decision"] is None
    assert report["maintainer_validated"] is False
    assert report["skills_edited"] is False
    assert report["diff_applied"] is False
    assert report["deployed"] is False
    assert report["actions_taken"] == []
    assert report["model_called"] is False
    assert report["network_called"] is False
    assert report["a3_recommended"] is False
    assert report["pins_reopened_for_this_experiment"] is False
    assert report["prompt_injection"]["followed"] is False
    assert report["prompt_injection"]["selection_obeyed_injection"] is False
    assert report["proposed_diff"]["applied"] is False
    assert report["architecture_cross_check"]["platform_selected"] is None
    assert report["architecture_cross_check"]["a3_recommended"] is False
    assert report["architecture_cross_check"]["deployed"] is False
    assert report["manifest_skeleton"]["approved"] is False
    for review in report["instruction_reviews"]:
        assert review["diff_applied"] is False
        assert review["owner_approved"] is False
        assert review["a3_recommended"] is False
        assert review["upstream_diff_applied"] is False
