"""Shared synthetic packs. Northmere Digital Services is fictional."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-11-13"


def load_sample() -> dict:
    return json.loads((ROOT / "examples" / "sample_pack.json").read_text(encoding="utf-8"))


def pack(**overrides) -> dict:
    base = load_sample()
    for key, value in overrides.items():
        base[key] = value
    return copy.deepcopy(base)


def approval(**overrides) -> dict:
    base = {
        "decision": "presenter_approve_outline_and_citations",
        "actor_role": "presenter",
        "actor_id": "SYN-PRES-053",
        "pack_id": "SYN-DECK-5301",
        "outline_seen": True,
        "citations_approved": ["KEY", "Q2", "Q3"],
        "gaps_seen": True,
        "accessibility_seen": True,
        "markings_seen": True,
    }
    base.update(overrides)
    return base
