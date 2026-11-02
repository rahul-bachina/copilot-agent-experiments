"""The runner refuses anything that leaves the sandbox or takes an action."""

import json
import subprocess
import sys

import pytest

from src.run import ProhibitedAction, apply_remediation, publish_findings, record_security_assessment, run
from tests.support import ROOT, bundle, safety


def test_functions_that_would_act_always_raise():
    with pytest.raises(ProhibitedAction):
        record_security_assessment()
    with pytest.raises(ProhibitedAction):
        apply_remediation()
    with pytest.raises(ProhibitedAction):
        publish_findings()


@pytest.mark.parametrize(
    "overrides",
    [
        {"sandbox": False},
        {"production": True},
        {"url": "https://example.invalid/agent"},
        {"endpoint": "https://example.invalid"},
        {"adapter": "live_model"},
        {"adapter": "instruction_surface", "instruction_path": "../secrets.md"},
        {"adapter": "instruction_surface", "instruction_path": "/etc/passwd"},
        {"adapter": "instruction_surface", "instruction_path": "experiments/01-foi-complaint-triage/README.md"},
        {"adapter": "instruction_surface"},
    ],
)
def test_unsafe_bundles_are_refused(overrides):
    with pytest.raises(ProhibitedAction):
        run(bundle(**overrides), "2026-11-02")


def test_cli_flags_exit_without_a_report(tmp_path):
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle()), encoding="utf-8")
    script = ROOT / "src" / "run.py"
    for flag in ("--assess", "--remediate", "--publish"):
        completed = subprocess.run(
            [sys.executable, str(script), "--bundle", str(bundle_path), "--as-of", "2026-11-02", flag],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 2
        assert completed.stdout == ""


def test_a_safe_run_still_does_not_assess():
    report = run(bundle(), "2026-11-02")
    safety(report)
    assert report["summary"]["passed"] == 20
    assert report["summary"]["failed"] == 0
    assert report["findings"] == []
    assert all(row["failure_signal_emitted"] is False for row in report["results"])
    assert all(row["action_taken"] is False for row in report["results"])
