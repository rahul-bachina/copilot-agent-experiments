"""Load the sample bundle. Tests mutate copies."""

from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

from src.report import evaluate

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sample() -> tuple[dict, dict]:
    return load("examples/sample_bundle.json"), load("examples/sample_rate_card.json")


def run(bundle: dict | None = None, rate_card: dict | None = None, as_of: str = "2026-11-03") -> dict:
    base_bundle, base_card = sample()
    return evaluate(
        copy.deepcopy(base_bundle if bundle is None else bundle),
        copy.deepcopy(base_card if rate_card is None else rate_card),
        as_of=as_of,
    )


def money(report: dict) -> Decimal:
    return Decimal(report["totals"]["cost"])


def agent_sum(report: dict) -> Decimal:
    return sum(Decimal(row["cost"]) for row in report["agents"])
