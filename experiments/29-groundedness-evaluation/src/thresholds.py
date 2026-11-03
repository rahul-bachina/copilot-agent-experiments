"""Draft thresholds. The evaluation owner has not approved them.

A caller may supply numbers for this run. The report scores against those
numbers and still leaves threshold_approved_by_evaluation_owner false.
"""

from __future__ import annotations

from typing import Any

DRAFT_DEFAULTS: dict[str, Any] = {
    "min_supported_rate": 1.0,
    "max_non_supported_claims": 0,
    "max_stale_claims": 0,
    "stale_after_days": 180,
}

_ALLOWED = frozenset(DRAFT_DEFAULTS)


def resolve(raw: Any) -> tuple[dict[str, Any], list[str]]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("draft_thresholds must be an object.")
    ignored: list[str] = []
    cleaned: dict[str, Any] = {}
    for key, value in raw.items():
        if key not in _ALLOWED:
            ignored.append(str(key))
            continue
        cleaned[key] = value
    out = dict(DRAFT_DEFAULTS)
    out.update(cleaned)
    rate = out["min_supported_rate"]
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 <= float(rate) <= 1:
        raise ValueError("min_supported_rate must be a number from 0 to 1.")
    for key in ("max_non_supported_claims", "max_stale_claims", "stale_after_days"):
        value = out[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{key} must be a non-negative integer.")
    out["min_supported_rate"] = float(rate)
    out["approved_by_evaluation_owner"] = False
    out["source"] = "caller" if cleaned else "draft_default"
    return out, ignored
