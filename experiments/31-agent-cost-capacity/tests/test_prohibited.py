"""The process cannot validate rates or change a quota, a budget, or a subscription."""

from __future__ import annotations

import subprocess
import sys

import pytest

from src.prohibited import (
    ProhibitedAction,
    change_budget,
    change_quota,
    change_subscription,
    validate_forecast,
    validate_rates,
)
from tests.support import ROOT


@pytest.mark.parametrize(
    "function",
    [validate_rates, validate_forecast, change_quota, change_budget, change_subscription],
)
def test_prohibited_functions_raise(function):
    with pytest.raises(ProhibitedAction):
        function()


@pytest.mark.parametrize(
    "flag",
    ["--validate-rates", "--validate-forecast", "--change-quota", "--change-budget", "--change-subscription"],
)
def test_cli_flag_exits_without_writing(flag, tmp_path):
    output = tmp_path / "report.json"
    completed = subprocess.run(
        [
            sys.executable,
            "src/report.py",
            "--bundle",
            "examples/sample_bundle.json",
            "--rate-card",
            "examples/sample_rate_card.json",
            "--as-of",
            "2026-11-03",
            flag,
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    assert output.exists() is False
    assert completed.stdout == ""
