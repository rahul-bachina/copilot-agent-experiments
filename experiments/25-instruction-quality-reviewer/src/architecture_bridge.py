"""Cross-check a structured use case with Experiment 14. Do not select a platform.

Experiment 14's decision table is called only when the bundle includes a use
case. Free text in the instructions is not passed in as the narrative that
drives the rules. platform_selected stays null.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

EXP14_SRC = Path(__file__).resolve().parents[2] / "14-agent-architecture-advisor" / "src"


def cross_check(use_case: dict[str, Any] | None) -> dict[str, Any]:
    if not use_case:
        return {
            "called": False,
            "experiment": "14",
            "reason": "No use case was supplied. Experiment 14 was not called.",
            "recommended_autonomy": None,
            "a3_recommended": False,
            "platform_selected": None,
            "any_option_selected": False,
            "deployed": False,
            "rules_fired": [],
            "work_shape": None,
        }
    if str(EXP14_SRC) not in sys.path:
        sys.path.insert(0, str(EXP14_SRC))
    from rules import normalise, score

    case, notes = normalise(use_case)
    result = score(case)
    level = result["recommended_autonomy"]
    if level not in {"A0", "A1", "A2"} or result.get("a3_recommended"):
        raise RuntimeError("Experiment 14 returned an autonomy level this catalogue does not allow")
    selected = [option["id"] for option in result["options"] if option.get("selected")]
    return {
        "called": True,
        "experiment": "14",
        "reason": "Experiment 14 scored the structured use case. It did not select a platform.",
        "recommended_autonomy": level,
        "a3_recommended": False,
        "platform_selected": None,
        "any_option_selected": bool(selected),
        "deployed": False,
        "rules_fired": list(result["rules_fired"]),
        "work_shape": result["work_shape"],
        "normalise_notes": notes,
    }
