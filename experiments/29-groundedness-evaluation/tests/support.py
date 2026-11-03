"""Shared helpers for the groundedness tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import report  # noqa: E402

AS_OF = "2026-11-03"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safety(draft: dict) -> None:
    assert draft["label"] == "DRAFT FOR EVALUATION OWNER"
    assert draft["catalogue_id"] == "G007"
    assert draft["experiment"] == "29"
    assert draft["autonomy"] == "A0"
    assert draft["threshold_approved_by_evaluation_owner"] is False
    assert draft["release_decision"] is None
    assert draft["pass_fail_released"] is False
    assert draft["groundedness_clearance"] is False
    assert draft["actions_taken"] == []
    assert draft["model_called"] is False
    assert draft["network_called"] is False
    assert draft["foundry_evaluator_called"] is False
    assert draft["foundry_option"]["called"] is False
    assert draft["a3_recommended"] is False
    assert draft["prompt_injection"]["followed"] is False
    assert draft["draft_bar_is_not_a_release"] is True
    assert draft["draft_thresholds"]["approved_by_evaluation_owner"] is False
    assert draft["manifest_skeleton"]["approved"] is False
    summary = draft["summary"]
    assert summary["verdict_total"] == summary["claim_count"]
    assert sum(summary["verdicts"].values()) == summary["claim_count"]
    assert "stale_source" not in summary["verdicts"]
    for point in draft["human_approval"]:
        assert point["recorded_by_agent"] is False


def sample_report(**overrides) -> dict:
    bundle = load_json(ROOT / "examples" / "sample_bundle.json")
    as_of = overrides.pop("as_of", AS_OF)
    stale = overrides.pop("stale_after_days", 90)
    bundle.update(overrides)
    return report(bundle, as_of, stale)
