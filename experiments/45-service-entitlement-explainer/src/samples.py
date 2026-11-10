"""Shared fixture loader. Aldermere is fictional."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
AS_OF = "2026-11-10"


def load_plan(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def request(plan: str = "home_plan.json", **overrides) -> dict:
    base = load_plan(plan)
    body = {
        "synthetic": True,
        "request_id": "SYN-ENT-4501",
        "organisation": base["organisation"],
        "sector": base["sector"],
        "customer_reference": "SYN-CUST-4501",
        "question": base["sample_question"],
        "contract": copy.deepcopy(base["contract"]),
        "rules_table": copy.deepcopy(base["rules_table"]),
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(body.get(key), dict):
            merged = copy.deepcopy(body[key])
            merged.update(value)
            body[key] = merged
        else:
            body[key] = value
    return body
