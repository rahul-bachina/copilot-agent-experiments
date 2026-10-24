"""Deterministic timeframe tests for SI 2025/1042."""

import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from statutory_clock import (  # noqa: E402
    DAMP,
    OVERCROWDING,
    calculate_statutory_clock,
)
from working_days import is_working_day, statutory_england_and_wales_bank_holidays  # noqa: E402

LONDON = ZoneInfo("Europe/London")
GATES = {
    "social_home_in_england": True,
    "officer_approved_category": True,
    "officer_approved_clock": True,
}


def by_id(clock: dict) -> dict:
    return {item["id"]: item for item in clock["deadlines"]}


def aware(year, month, day, hour=9, minute=0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=LONDON)


class TestWorkingDays:
    def test_named_days_in_2026(self):
        closed = set(statutory_england_and_wales_bank_holidays(2026))
        assert date(2026, 4, 5) == __import__("working_days").easter_sunday(2026)
        assert is_working_day(date(2026, 4, 3), closed) is False  # Good Friday
        assert is_working_day(date(2026, 4, 6), closed) is False  # Easter Monday
        assert is_working_day(date(2026, 4, 2), closed) is True
        assert is_working_day(date(2026, 5, 4), closed) is False  # early May
        assert is_working_day(date(2026, 12, 25), closed) is False
        assert is_working_day(date(2026, 12, 28), closed) is False  # Boxing Day substitute
        assert is_working_day(date(2026, 12, 29), closed) is True
        assert is_working_day(date(2026, 1, 3), closed) is False  # Saturday


class TestPhase1Clock:
    def test_significant_damp_investigation_ends_22_january(self):
        clock = calculate_statutory_clock(aware(2026, 1, 8), DAMP, "significant", **GATES)
        item = by_id(clock)["standard_investigation"]
        assert clock["in_force"] is True
        assert clock["operative"] is True
        assert item["on"] == "2026-01-22"
        assert item["operative"] is True
        assert by_id(clock)["awaiting_investigation_completion"]["operative"] is False

    def test_approval_and_social_home_are_required(self):
        clock = calculate_statutory_clock(aware(2026, 1, 8), DAMP, "significant")
        assert by_id(clock)["standard_investigation"]["on"] == "2026-01-22"
        assert clock["operative"] is False
        assert "approved the hazard category" in clock["operative_block_reason"]
        partial = calculate_statutory_clock(
            aware(2026, 1, 8),
            DAMP,
            "significant",
            officer_approved_category=True,
            officer_approved_clock=True,
        )
        assert partial["operative"] is False
        assert "social home" in partial["operative_block_reason"]

    def test_emergency_twenty_four_hours_includes_the_weekend(self):
        clock = calculate_statutory_clock(
            aware(2026, 1, 2, 16, 0), "electrical", "emergency", **GATES
        )
        item = by_id(clock)["emergency_action_condition_1"]
        assert item["at"].startswith("2026-01-03T16:00:00")
        assert item["on"] == "2026-01-03"
        assert item["operative"] is True
        assert clock["phase_id"] == "phase_1"
        assert any("Phase 2" in warning for warning in clock["warnings"])

    def test_christmas_investigation_ends_8_january_2027(self):
        clock = calculate_statutory_clock(
            aware(2026, 12, 22, 10, 0), DAMP, "significant", **GATES
        )
        assert by_id(clock)["standard_investigation"]["on"] == "2027-01-08"

    def test_summary_safety_and_twelve_weeks(self):
        clock = calculate_statutory_clock(
            aware(2026, 1, 8),
            DAMP,
            "significant",
            investigation_completed_on=date(2026, 1, 16),
            supplementary_preventative_work_identified=True,
            not_reasonably_practicable_to_begin=True,
            **GATES,
        )
        items = by_id(clock)
        assert items["written_summary"]["on"] == "2026-01-21"
        assert items["written_summary"]["operative"] is True
        assert "9(1)" in items["written_summary"]["note"]
        assert items["significant_safety_work"]["on"] == "2026-01-23"
        assert items["preventative_begin_or_steps"]["on"] == "2026-01-23"
        assert items["preventative_begin_long_stop"]["on"] == "2026-04-10"
        assert items["preventative_begin_long_stop"]["operative"] is True
        assert items["preventative_completion"]["on"] is None
        assert items["preventative_completion"]["operative"] is False

    def test_twelve_weeks_is_not_a_free_choice(self):
        clock = calculate_statutory_clock(
            aware(2026, 1, 8),
            DAMP,
            "significant",
            investigation_completed_on=date(2026, 1, 16),
            supplementary_preventative_work_identified=True,
            **GATES,
        )
        long_stop = by_id(clock)["preventative_begin_long_stop"]
        assert long_stop["on"] == "2026-04-10"
        assert long_stop["operative"] is False

    def test_physical_inspection_request_resets_the_count(self):
        clock = calculate_statutory_clock(
            aware(2026, 1, 8),
            DAMP,
            "significant",
            physical_inspection_requested_on=date(2026, 1, 15),
            **GATES,
        )
        items = by_id(clock)
        assert items["standard_investigation"]["operative"] is False
        assert items["extended_investigation"]["on"] == "2026-01-29"
        assert items["extended_investigation"]["operative"] is True

    def test_part_6_disapplies_the_hard_stop(self):
        clock = calculate_statutory_clock(
            aware(2026, 1, 2, 16, 0),
            "electrical",
            "emergency",
            part_6_complied=True,
            **GATES,
        )
        item = by_id(clock)["emergency_action_condition_1"]
        assert item["operative"] is False
        assert "Part 6" in item["note"]
        assert clock["reasonable_endeavours"]["defence_made_out"] is False

    def test_condition_2_runs_from_the_investigation(self):
        started = aware(2026, 1, 5, 9, 0)
        finished = aware(2026, 1, 5, 11, 30)
        clock = calculate_statutory_clock(
            started,
            "fire_and_explosions",
            "emergency",
            emergency_condition="2",
            investigation_completed_at=finished,
            **GATES,
        )
        items = by_id(clock)
        assert items["emergency_action_condition_1"]["operative"] is False
        assert items["emergency_action_condition_2"]["at"].startswith("2026-01-06T11:30:00")
        assert items["emergency_action_condition_2"]["operative"] is True
        assert clock["in_force"] is True
        assert any("Fire Safety Order" in warning for warning in clock["warnings"])

    def test_naive_time_is_refused(self):
        with pytest.raises(ValueError, match="timezone"):
            calculate_statutory_clock(datetime(2026, 1, 8, 9, 0), DAMP, "significant", **GATES)


class TestPhasesNotInForce:
    def test_phase_2_stays_off_after_the_draft_date(self):
        clock = calculate_statutory_clock(
            aware(2026, 12, 1),
            "excess_cold",
            "significant",
            as_of=date(2026, 12, 1),
            **GATES,
        )
        assert clock["in_force"] is False
        assert clock["operative"] is False
        assert clock["phase_id"] == "phase_2"
        assert any(phase["id"] == "phase_2" for phase in clock["phases_not_in_force"])
        assert "not encoded" in clock["significant_risk_test_encoded"]

    def test_an_assertion_cannot_start_phase_2_early(self):
        clock = calculate_statutory_clock(
            aware(2026, 11, 2),
            "excess_heat",
            "significant",
            as_of=date(2026, 11, 29),
            caller_asserts_phase_2_instrument_in_force=True,
            **GATES,
        )
        assert clock["in_force"] is False
        assert any("draft" in warning for warning in clock["warnings"])

    def test_an_assertion_on_or_after_30_november_still_warns(self):
        clock = calculate_statutory_clock(
            aware(2026, 12, 1),
            "domestic_hygiene",
            "significant",
            as_of=date(2026, 12, 1),
            caller_asserts_phase_2_instrument_in_force=True,
            **GATES,
        )
        assert clock["in_force"] is True
        assert clock["operative"] is True
        assert any("does not make that draft law" in warning for warning in clock["warnings"])

    def test_phase_3_has_no_switch(self):
        clock = calculate_statutory_clock(
            aware(2026, 12, 1), "other_prescribed", "significant", **GATES
        )
        assert clock["phase_id"] == "phase_3"
        assert clock["in_force"] is False
        assert clock["operative"] is False

    def test_overcrowding_is_not_an_emergency_clock(self):
        clock = calculate_statutory_clock(
            aware(2026, 6, 1), OVERCROWDING, "emergency", **GATES
        )
        assert clock["in_force"] is False
        assert clock["operative"] is False
        assert "adequate space" in clock["scope_reason"]

    def test_before_commencement_nothing_is_in_force(self):
        clock = calculate_statutory_clock(
            aware(2025, 10, 1),
            "electrical",
            "emergency",
            as_of=date(2025, 10, 26),
            **GATES,
        )
        assert clock["in_force"] is False
        assert clock["operative"] is False


class TestToolSchema:
    def test_clock_schema_cannot_send_or_write(self):
        path = Path(__file__).parent.parent / "schema" / "clock_tool.schema.json"
        schema = json.loads(path.read_text())
        assert schema["additionalProperties"] is False
        blob = json.dumps(schema)
        for banned in ("send", "email", "write_record", "housing_system"):
            assert banned not in schema["properties"]
        assert "officer_approved_category" in schema["properties"]
        assert "send" not in blob or "does not send" in schema["description"]
