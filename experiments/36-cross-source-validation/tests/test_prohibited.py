"""Choose, edit, contact, lookup, and A3 are not tools."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.compare import (
    CompareForbidden,
    choose_source,
    contact_party,
    edit_record,
    lookup_register,
    recommend_a3,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "function,message",
    [
        (choose_source, "does not choose"),
        (edit_record, "does not edit"),
        (contact_party, "does not contact"),
        (lookup_register, "does not query"),
        (recommend_a3, "A3"),
    ],
)
def test_prohibited_functions_raise(function, message):
    with pytest.raises(CompareForbidden, match=message):
        function()


@pytest.mark.parametrize(
    "flag",
    ["--choose-source", "--edit-record", "--contact", "--lookup-register", "--recommend-a3"],
)
def test_prohibited_cli_exits_without_a_draft(flag, tmp_path):
    out = tmp_path / "out.json"
    completed = subprocess.run(
        [
            sys.executable,
            "src/compare.py",
            "--pack",
            "examples/sample_pack.json",
            "--as-of",
            "2026-11-05",
            flag,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    out.write_text(completed.stdout)
    assert out.read_text() == ""
    assert "A3" in completed.stderr or "does not" in completed.stderr


def test_not_synthetic_cli_writes_nothing(tmp_path):
    payload = json.loads((ROOT / "examples" / "sample_pack.json").read_text(encoding="utf-8"))
    payload["synthetic"] = False
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(payload), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "src/compare.py", "--pack", str(pack), "--as-of", "2026-11-05"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "999" not in completed.stderr
    assert "not marked synthetic" in completed.stderr
