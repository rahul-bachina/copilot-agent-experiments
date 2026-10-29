"""Shared fixtures for Experiment 22."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(ROOT))

from src.investigate import investigate  # noqa: E402


def load_example(name: str = "sample_alert.json") -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def draft_sample(as_of: str = "2026-10-29", **overrides) -> dict:
    case = load_example()
    case.update(overrides)
    return investigate(case, as_of=date.fromisoformat(as_of))
