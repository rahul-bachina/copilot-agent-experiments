"""Shared helpers for the prompt-injection tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.run import run  # noqa: E402

AS_OF = "2026-11-02"
REPO = ROOT.parents[1]


def safety(report: dict) -> None:
    assert report["label"] == "DRAFT FOR SECURITY REVIEWER"
    assert report["catalogue_id"] == "G006"
    assert report["experiment"] == "28"
    assert report["autonomy"] == "A0"
    assert report["decision"] is None
    assert report["reviewer_assessed"] is False
    assert report["remediation_applied"] is False
    assert report["published"] is False
    assert report["production_targeted"] is False
    assert report["actions_taken"] == []
    assert report["model_called"] is False
    assert report["network_called"] is False
    assert report["foundry_red_team_called"] is False
    assert report["a3_recommended"] is False
    assert report["sandbox"] is True
    assert report["production"] is False
    assert report["prompt_injection"]["followed"] is False
    assert report["manifest_skeleton"]["approved"] is False
    assert report["suite_version"] == "2026.1"
    for point in report["human_approval"]:
        assert point["recorded_by_runner"] is False
    for finding in report["findings"]:
        assert finding["assessed"] is False
        assert finding["remediation_applied"] is False


def bundle(**overrides) -> dict:
    body = {
        "bundle_id": "test",
        "target_id": "sandbox",
        "sandbox": True,
        "production": False,
        "adapter": "reference_safe",
        "suite_version": "2026.1",
    }
    body.update(overrides)
    return body


def run_bundle(**overrides) -> dict:
    as_of = overrides.pop("as_of", AS_OF)
    stale = overrides.pop("stale_after_days", 90)
    return run(bundle(**overrides), as_of, stale)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
