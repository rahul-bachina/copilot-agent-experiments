"""Call Experiment 36. This module does not re-implement the normaliser.

The comparison classifies values the pack already lists. It does not choose
which source is right, query a bureau, or edit a record. Counts from Experiment
36 stay on this object. They are not added to the memo's stated-fact count.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any


class ComparisonUnavailable(RuntimeError):
    """Experiment 36 is not beside this experiment. A class is not invented."""


def _load_compare():
    src = Path(__file__).resolve().parents[2] / "36-cross-source-validation" / "src"
    if not src.is_dir():
        raise ComparisonUnavailable(
            "Experiment 36 is not beside this experiment. The memo will not invent a comparison."
        )
    alias = "exp36_b009"
    package = types.ModuleType(alias)
    package.__path__ = [str(src)]
    package.__package__ = alias
    sys.modules[alias] = package
    module = None
    for name in ("injection", "siblings", "normalise", "sources", "compare"):
        path = src / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"{alias}.{name}", path)
        if spec is None or spec.loader is None:
            raise ComparisonUnavailable(f"Could not load Experiment 36 {name}.py")
        loaded = importlib.util.module_from_spec(spec)
        loaded.__package__ = alias
        sys.modules[f"{alias}.{name}"] = loaded
        spec.loader.exec_module(loaded)
        if name == "compare":
            module = loaded
    if module is None or getattr(module, "EXPERIMENT_ID", None) != "exp-36-cross-source-validation":
        raise ComparisonUnavailable("the comparison module is not Experiment 36")
    return module


def not_called() -> dict[str, Any]:
    return {
        "called": False,
        "experiment_id": "exp-36-cross-source-validation",
        "catalogue_id": "B005",
        "reason": "no_comparisons_supplied",
        "agent_chose_source": False,
        "register_queried": False,
        "records_edited": False,
        "parties_contacted": False,
        "correct_value_written": False,
        "counts": {
            "fact_count": 0,
            "match_count": 0,
            "immaterial_count": 0,
            "material_count": 0,
            "occurrence_count": 0,
        },
        "counts_are_not_memo_facts": True,
        "facts": [],
        "material_fact_keys": [],
    }


def compare_pack(comparisons: dict[str, Any] | None, *, as_of: str, stale_after_days: int) -> dict[str, Any]:
    if comparisons is None:
        return not_called()
    if not isinstance(comparisons, dict):
        raise ValueError("comparisons must be an object")
    module = _load_compare()
    draft = module.compare(comparisons, as_of, stale_after_days, resolutions=None)
    if draft.get("experiment_id") != "exp-36-cross-source-validation":
        raise ComparisonUnavailable("the comparison result is not Experiment 36")
    if draft.get("agent_chose_source") or draft.get("register_queried") or draft.get("records_edited"):
        raise ComparisonUnavailable("Experiment 36 reported a prohibited action. It is not kept.")
    facts = []
    for fact in draft["facts"]:
        occurrences = []
        for row in fact["occurrences"]:
            citation = row["citation"]
            occurrences.append(
                {
                    "document_id": citation["document_id"],
                    "page": citation["page"],
                    "paragraph": citation["paragraph"],
                    "line_start": citation["line_start"],
                    "line_end": citation["line_end"],
                    "quote": row["quote"],
                    "used": row["used"],
                    "withheld": row["withheld"],
                }
            )
        facts.append(
            {
                "fact_key": fact["fact_key"],
                "field_type": fact["field_type"],
                "classification": fact["classification"],
                "reason": fact["reason"],
                "resolution_required": fact["resolution_required"],
                "resolved": False,
                "correct_value": None,
                "agent_chose_source": False,
                "occurrences": occurrences,
            }
        )
    return {
        "called": True,
        "experiment_id": draft["experiment_id"],
        "catalogue_id": draft["catalogue_id"],
        "reason": None,
        "agent_chose_source": False,
        "register_queried": False,
        "records_edited": False,
        "parties_contacted": False,
        "correct_value_written": False,
        "counts": dict(draft["counts"]),
        "counts_are_not_memo_facts": True,
        "counts_note": draft["counts_note"],
        "facts": facts,
        "material_fact_keys": [
            fact["fact_key"] for fact in facts if fact["classification"] == "material_discrepancy"
        ],
    }
