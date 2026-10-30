"""Shared fixtures for Experiment 23."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(ROOT))

from src.precheck import precheck  # noqa: E402


def load_example(name: str = "sample_web.json") -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def draft_sample(as_of: str = "2026-10-30", **overrides) -> dict:
    promotion = load_example()
    promotion.update(overrides)
    return precheck(promotion, as_of=date.fromisoformat(as_of))


def by_id(draft: dict) -> dict[str, dict]:
    return {row["id"]: row for row in draft["checklist"]}
