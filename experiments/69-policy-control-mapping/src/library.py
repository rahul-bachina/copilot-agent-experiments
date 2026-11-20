"""The pinned control library is the only library used for a mapping.

A library passed by the caller is compared with the file in fixtures/.
Differences are flagged. They are not applied. An expected strength that is
not in the closed list is not coerced to must.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from statements import STRENGTHS, biased
else:
    from .statements import STRENGTHS, biased

PINNED_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "library.json"
IDENTIFIER = re.compile(r"^ISO/IEC 27001:2022 A\.\d+\.\d+$")


def load_pinned() -> dict:
    with PINNED_PATH.open(encoding="utf-8") as handle:
        library = json.load(handle)
    problems = library_problems(library)
    if problems:
        raise ValueError("pinned library failed its own checks: " + ", ".join(problems))
    return library


def library_problems(library: dict) -> list[str]:
    problems: list[str] = []
    if not isinstance(library, dict):
        return ["library_not_object"]
    controls = library.get("controls")
    if not isinstance(controls, list) or not controls:
        return ["library_has_no_controls"]
    seen: set[str] = set()
    for control in controls:
        if not isinstance(control, dict):
            problems.append("control_not_object")
            continue
        control_id = control.get("control_id")
        if not isinstance(control_id, str) or not control_id:
            problems.append("control_id_unreadable")
            continue
        if control_id in seen:
            problems.append(f"duplicate:{control_id}")
        seen.add(control_id)
        if control.get("expected_strength") not in STRENGTHS:
            problems.append(f"unparseable_expected_strength:{control_id}")
        identifier = control.get("external_identifier")
        if identifier not in (None, "") and not (isinstance(identifier, str) and IDENTIFIER.fullmatch(identifier)):
            problems.append(f"external_text_not_identifier:{control_id}")
        blob = " ".join(
            str(control.get(key) or "")
            for key in ("title", "objective", "external_identifier", "notes")
        )
        if "the organization shall" in blob.casefold() or "the organisation shall" in blob.casefold():
            problems.append(f"standard_text_present:{control_id}")
        if biased(blob):
            problems.append(f"biased_criterion:{control_id}")
    return problems


def differences(supplied: dict | None, pinned: dict) -> list[dict]:
    """Field-by-field differences. The pinned control is not replaced."""

    if supplied is None:
        return []
    if not isinstance(supplied, dict):
        return [{"kind": "supplied_library_not_object", "applied": False, "coerced": False}]
    rows: list[dict] = []
    pinned_controls = {
        control["control_id"]: control
        for control in pinned.get("controls") or []
        if isinstance(control, dict) and isinstance(control.get("control_id"), str)
    }
    supplied_controls = supplied.get("controls")
    if not isinstance(supplied_controls, list):
        return [{"kind": "supplied_controls_unreadable", "coerced": False}]
    seen: set[str] = set()
    for control in supplied_controls:
        if not isinstance(control, dict):
            rows.append({"kind": "supplied_control_not_object", "applied": False, "coerced": False})
            continue
        control_id = control.get("control_id")
        if not isinstance(control_id, str):
            rows.append({"kind": "supplied_control_id_unreadable", "coerced": False, "applied": False})
            continue
        seen.add(control_id)
        current = pinned_controls.get(control_id)
        if current is None:
            rows.append({"kind": "supplied_control_not_in_pinned", "control_id": control_id, "applied": False, "coerced": False})
            if biased(" ".join(str(control.get(key) or "") for key in ("title", "objective", "notes"))):
                rows.append({"kind": "biased_criterion", "control_id": control_id, "applied": False, "coerced": False})
            continue
        for field in ("title", "objective", "expected_strength", "external_identifier"):
            if control.get(field) != current.get(field):
                strength = control.get("expected_strength")
                rows.append(
                    {
                        "kind": "field_differs",
                        "control_id": control_id,
                        "field": field,
                        "applied": False,
                        "coerced": False,
                        "unparseable_expected_strength": field == "expected_strength" and strength not in STRENGTHS,
                    }
                )
        if control.get("signal_groups") != current.get("signal_groups"):
            rows.append(
                {
                    "kind": "field_differs",
                    "control_id": control_id,
                    "field": "signal_groups",
                    "applied": False,
                    "coerced": False,
                }
            )
        blob = " ".join(str(control.get(key) or "") for key in ("title", "objective", "notes"))
        if biased(blob):
            rows.append({"kind": "biased_criterion", "control_id": control_id, "applied": False, "coerced": False})
    for control_id in pinned_controls:
        if control_id not in seen:
            rows.append({"kind": "pinned_control_missing_from_supplied", "control_id": control_id, "applied": False, "coerced": False})
    return rows
