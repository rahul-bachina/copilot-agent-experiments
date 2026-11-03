"""The checker refuses an approval, a release, and a Foundry call."""

import json
import subprocess
import sys

import pytest

from src.report import ProhibitedAction, approve_thresholds, call_foundry_evaluator, record_release, report
from tests.support import ROOT, sample_report


def test_functions_that_would_act_always_raise():
    with pytest.raises(ProhibitedAction):
        approve_thresholds()
    with pytest.raises(ProhibitedAction):
        record_release()
    with pytest.raises(ProhibitedAction):
        call_foundry_evaluator()


def test_keyword_flags_raise_before_a_report():
    bundle = json.loads((ROOT / "examples" / "sample_bundle.json").read_text(encoding="utf-8"))
    with pytest.raises(ProhibitedAction):
        report(bundle, "2026-11-03", approve=True)
    with pytest.raises(ProhibitedAction):
        report(bundle, "2026-11-03", release=True)
    with pytest.raises(ProhibitedAction):
        report(bundle, "2026-11-03", record_pass=True)
    with pytest.raises(ProhibitedAction):
        report(bundle, "2026-11-03", record_fail=True)


def test_cli_flags_exit_without_a_report(tmp_path):
    bundle_path = ROOT / "examples" / "sample_bundle.json"
    script = ROOT / "src" / "report.py"
    out = tmp_path / "out.json"
    for flag in ("--approve-thresholds", "--release", "--pass", "--fail"):
        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--bundle",
                str(bundle_path),
                "--as-of",
                "2026-11-03",
                "--output",
                str(out),
                flag,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 2
        assert completed.stdout == ""
        assert not out.exists()


def test_a_non_synthetic_bundle_is_refused():
    bundle = json.loads((ROOT / "examples" / "sample_bundle.json").read_text(encoding="utf-8"))
    bundle["synthetic"] = False
    with pytest.raises(ValueError, match="synthetic"):
        report(bundle, "2026-11-03")


def test_a_safe_run_still_does_not_release():
    draft = sample_report()
    assert draft["draft_bar_met"] is True
    assert draft["pass_fail_released"] is False
