"""Smoke totals count a fact once. Occurrences are not added to the fact total."""

import json
from pathlib import Path

from src.compare import compare

ROOT = Path(__file__).resolve().parents[1]


def test_running_the_sample_twice_does_not_add_the_facts_together():
    sample = json.loads((ROOT / "examples" / "sample_pack.json").read_text(encoding="utf-8"))
    first = compare(sample, "2026-11-05")
    second = compare(sample, "2026-11-05")
    assert first["counts"] == second["counts"]
    assert first["counts"]["fact_count"] == 7
    doubled = first["counts"]["fact_count"] + second["counts"]["fact_count"]
    assert doubled == 14
    assert "grand_total" not in first
    assert first["counts"]["occurrence_count"] == 26
    assert first["counts"]["occurrence_count"] + second["counts"]["occurrence_count"] != first["counts"]["fact_count"]
    assert sum(first["counts"][key] for key in ("match_count", "immaterial_count", "material_count")) == 7
