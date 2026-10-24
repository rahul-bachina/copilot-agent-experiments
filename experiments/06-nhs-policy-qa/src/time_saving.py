"""Score a paired time observation. Elapsed time comes from harness timestamps.

A self-reported "minutes saved" field is rejected. An item whose answer is
wrong, or whose citations are not grounded, is excluded from the median.
A fast wrong answer is not a saving. This module does not collect observations.
"""

from __future__ import annotations

from datetime import datetime

SELF_REPORT_KEYS = frozenset(
    {
        "minutes_saved",
        "minutes_saved_self_report",
        "self_reported_minutes",
        "self_reported_minutes_saved",
        "hours_saved",
    }
)


def _parse_timestamp(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp {value!r} needs a timezone")
    return parsed


def elapsed_seconds(arm: dict) -> float:
    start = _parse_timestamp(arm["shown_at"])
    end = _parse_timestamp(arm["submitted_at"])
    delta = (end - start).total_seconds()
    if delta < 0:
        raise ValueError("submitted_at is earlier than shown_at")
    return delta


def _has_self_report(row: dict) -> bool:
    return any(key in row for key in SELF_REPORT_KEYS)


def median(values: list[float]) -> float | None:
    """Middle value. For an even count, the mean of the two middle values."""
    if not values:
        return None
    ordered = sorted(values)
    count = len(ordered)
    mid = count // 2
    if count % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def score_observations(rows: list[dict]) -> dict:
    """Primary endpoint: median of (manual seconds minus agent seconds) on grounded items."""
    rejected: list[str] = []
    excluded: list[str] = []
    included: list[dict] = []
    for row in rows:
        row_id = row["id"]
        if _has_self_report(row):
            rejected.append(row_id)
            continue
        grounded = row.get("agent_outcome_correct") is True and row.get("citations_grounded") is True
        if not grounded:
            excluded.append(row_id)
            continue
        manual_seconds = elapsed_seconds(row["manual"])
        agent_seconds = elapsed_seconds(row["agent"])
        included.append(
            {
                "id": row_id,
                "manual_seconds": manual_seconds,
                "agent_seconds": agent_seconds,
                "difference_seconds": manual_seconds - agent_seconds,
            }
        )
    differences = [item["difference_seconds"] for item in included]
    return {
        "method": (
            "Elapsed seconds are computed from harness timestamps (shown_at, submitted_at). "
            "Self-reported minutes are rejected. Items that are not grounded are excluded."
        ),
        "primary_endpoint": (
            "Median paired difference in elapsed seconds (manual minus agent) "
            "on items where the agent outcome is correct and the citations are grounded."
        ),
        "not_a_staff_study": True,
        "nhs_trial_figure_not_used": True,
        "n_included": len(included),
        "n_rejected_self_report": len(rejected),
        "n_excluded_ungrounded": len(excluded),
        "rejected_self_report_ids": rejected,
        "excluded_ungrounded_ids": excluded,
        "median_seconds_saved_on_grounded_items": median(differences),
        "included": included,
    }
