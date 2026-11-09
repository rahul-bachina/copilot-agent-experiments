"""Statutory-clock handling.

Freedom of Information and environmental-information periods are cited and
not calculated. A subject-access period is not stated, because Article 12A
was not opened. An Awaab's Law clock is delegated to Experiment 05, and the
officer-approval flags are forced off so no deadline is operative.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

CLOCK_EXPERIMENT = "exp-05-awaabs-law-hazard-triage"

_FOI = (
    "Freedom of Information Act 2000, section 10(1), subject to subsections (2) and (3): "
    "comply promptly and in any event not later than the twentieth working day following "
    "the date of receipt. Section 10(6) defines a working day by reference to a bank holiday "
    "in any part of the United Kingdom. The day is not calculated here."
)
_EIR = (
    "Environmental Information Regulations 2004, regulation 5(2): as soon as possible and "
    "no later than 20 working days after the date of receipt. Regulation 2 was not opened. "
    "The day is not calculated here."
)
_SAR = (
    "UK GDPR Article 12(3) points to Article 12A for the applicable time period. "
    "Article 12A was not opened on 9 November 2026. No number of days is stated."
)
_AWAABS = (
    "Experiment 05 calculates the illustrations. This assistant does not pass officer approval, "
    "so the clock is not operative and is not a route."
)
_DISP = (
    "DISP was not opened on 9 November 2026. Experiment 02 was not called. "
    "No complaint timescale is calculated."
)
_UNVERIFIED = (
    "No statutory period was opened for this kind. The case still goes to a person. "
    "The period is unverified in this folder."
)

CITATIONS = {
    "foi": ("foia_s10", _FOI),
    "eir": ("eir_reg5", _EIR),
    "sar": ("uk_gdpr_art_12", _SAR),
    "awaabs": ("experiment_05", _AWAABS),
    "disp": ("not_opened_disp", _DISP),
}


def _load_clock():
    clock_src = (
        Path(__file__).resolve().parents[2] / "05-awaabs-law-hazard-triage" / "src"
    )
    if not clock_src.is_dir():
        raise RuntimeError(
            "Experiment 05 is required at experiments/05-awaabs-law-hazard-triage. "
            "This assistant does not carry its own clock."
        )
    inserted = str(clock_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import statutory_clock as clock_module

    return clock_module


def _parse_aware(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("awareness time must be timezone-aware")
    return parsed


def cite(kind: str) -> dict:
    source_id, text = CITATIONS.get(kind, ("not_opened", _UNVERIFIED))
    return {
        "kind": kind,
        "source_id": source_id,
        "text": text,
        "date_calculated": False,
        "experiment_02_called": False,
        "experiment_05_called": False,
    }


def awaabs_view(fields: dict | None, as_of: date) -> dict:
    """Call Experiment 05 only when the structured fields are present.

    Officer approval in the payload is ignored. Illustrations are not copied.
    """

    base = {
        "called": False,
        "experiment": CLOCK_EXPERIMENT,
        "officer_approved_category_passed": False,
        "officer_approved_clock_passed": False,
        "payload_claimed_officer_approval": False,
        "any_operative_deadline": False,
        "applied_as_a_route": False,
        "deadline_ids": [],
        "error": None,
    }
    if not isinstance(fields, dict):
        base["error"] = "fields_not_supplied"
        return base
    claimed = bool(fields.get("officer_approved_category") or fields.get("officer_approved_clock"))
    base["payload_claimed_officer_approval"] = claimed
    aware = fields.get("aware_at")
    family = fields.get("hazard_family")
    category = fields.get("category")
    if not aware or not family or not category:
        base["error"] = "fields_not_supplied"
        return base
    try:
        clock = _load_clock()
        result = clock.calculate_statutory_clock(
            _parse_aware(str(aware)),
            str(family),
            str(category),
            social_home_in_england=bool(fields.get("social_home_in_england")),
            officer_approved_category=False,
            officer_approved_clock=False,
            as_of=as_of,
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        base["error"] = type(exc).__name__
        return base
    deadlines = result.get("deadlines") or []
    base.update(
        {
            "called": True,
            "any_operative_deadline": result.get("operative") is True,
            "deadline_ids": [row.get("id") for row in deadlines if row.get("id")],
            "in_force": result.get("in_force"),
            "officer_approved_category_on_result": result.get("officer_approved_category"),
            "officer_approved_clock_on_result": result.get("officer_approved_clock"),
        }
    )
    return base
