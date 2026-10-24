"""The time-saving scorer uses timestamps and drops self-report and bad answers."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from time_saving import elapsed_seconds, score_observations  # noqa: E402


def _arm(start: str, end: str) -> dict:
    return {"shown_at": start, "submitted_at": end}


def _row(row_id: str, manual_end: str, *, correct: bool = True, grounded: bool = True, extra=None):
    row = {
        "id": row_id,
        "agent_outcome_correct": correct,
        "citations_grounded": grounded,
        "manual": _arm("2026-10-24T09:00:00+00:00", manual_end),
        "agent": _arm("2026-10-24T10:00:00+00:00", "2026-10-24T10:00:20+00:00"),
    }
    if extra:
        row.update(extra)
    return row


class TestScorer:
    def test_median_uses_only_grounded_timestamp_pairs(self):
        # Agent arm is 20 seconds. Manual ends produce differences 90, 120, 140, 160, 180, 200, 240.
        rows = [
            _row("T1", "2026-10-24T09:01:50+00:00"),
            _row("T2", "2026-10-24T09:02:20+00:00"),
            _row("T3", "2026-10-24T09:02:40+00:00"),
            _row("T4", "2026-10-24T09:03:00+00:00"),
            _row("T5", "2026-10-24T09:03:20+00:00"),
            _row("T6", "2026-10-24T09:03:40+00:00"),
            _row("T7", "2026-10-24T09:04:20+00:00"),
            _row(
                "T-SELF",
                "2026-10-24T09:30:00+00:00",
                extra={"minutes_saved_self_report": 40},
            ),
            _row("T-WRONG", "2026-10-24T09:20:00+00:00", correct=False),
        ]
        scored = score_observations(rows)
        assert scored["n_included"] == 7
        assert scored["n_rejected_self_report"] == 1
        assert scored["rejected_self_report_ids"] == ["T-SELF"]
        assert scored["n_excluded_ungrounded"] == 1
        assert scored["excluded_ungrounded_ids"] == ["T-WRONG"]
        assert scored["median_seconds_saved_on_grounded_items"] == 160
        assert scored["not_a_staff_study"] is True
        assert scored["nhs_trial_figure_not_used"] is True
        assert "T-SELF" not in {item["id"] for item in scored["included"]}

    def test_self_report_is_rejected_before_timestamps_are_read(self):
        scored = score_observations(
            [
                {
                    "id": "BARE",
                    "minutes_saved": 15,
                    "agent_outcome_correct": True,
                    "citations_grounded": True,
                }
            ]
        )
        assert scored["n_included"] == 0
        assert scored["rejected_self_report_ids"] == ["BARE"]
        assert scored["median_seconds_saved_on_grounded_items"] is None

    def test_negative_elapsed_is_rejected(self):
        with pytest.raises(ValueError):
            elapsed_seconds(
                {"shown_at": "2026-10-24T10:00:00+00:00", "submitted_at": "2026-10-24T09:00:00+00:00"}
            )
