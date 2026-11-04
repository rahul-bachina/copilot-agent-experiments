"""Shared bundle loader. Tests mutate a copy."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-11-04"


def load_bundle() -> dict:
    return json.loads((ROOT / "examples" / "sample_bundle.json").read_text(encoding="utf-8"))


def bundle() -> dict:
    return copy.deepcopy(load_bundle())


def signoff(**overrides) -> dict:
    base = json.loads((ROOT / "examples" / "sample_signoff.json").read_text(encoding="utf-8"))
    base.update(overrides)
    return base
