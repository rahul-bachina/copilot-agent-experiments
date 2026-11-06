"""Prohibited actions raise, and the command flags do not write a draft."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import (
    CompareForbidden,
    contact_broker,
    decide_coverage,
    draft_endorsement,
    recommend_autonomy_a3,
    recommend_buy_sell_renew,
    release_evaluation,
    write_policy_admin,
)

FLAGS = (
    "--favourable",
    "--recommend",
    "--draft-endorsement",
    "--contact-broker",
    "--write-pas",
    "--decide-coverage",
)


def test_prohibited_functions_raise():
    for function in (
        recommend_buy_sell_renew,
        draft_endorsement,
        contact_broker,
        write_policy_admin,
        decide_coverage,
        recommend_autonomy_a3,
        release_evaluation,
    ):
        try:
            function()
        except CompareForbidden:
            continue
        raise AssertionError(function.__name__)


def test_command_flags_exit_without_a_draft():
    sample = ROOT / "examples" / "sample_pack.json"
    for flag in FLAGS:
        completed = subprocess.run(
            [sys.executable, "src/compare.py", "--pack", str(sample), "--as-of", "2026-11-06", flag],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 2
        assert completed.stdout == ""
