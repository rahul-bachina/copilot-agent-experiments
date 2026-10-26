"""Shared paths for Experiment 03 tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inventory import load_json  # noqa: E402


def load_record(inventory_id: str) -> dict:
    return load_json(ROOT / "fixtures" / "inventory" / f"{inventory_id}.json")
