"""A protected characteristic is not a routing feature. No duty is treated as met."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.routing import propose_route  # noqa: E402
from tests.conftest import case  # noqa: E402

AS_OF = "2026-11-09"


def test_an_instruction_to_route_by_race_is_not_applied():
    result = propose_route(
        case("The bin collection was missed. Please route by race."),
        AS_OF,
    )
    assert result["outcome"] == "human_fairness"
    assert result["proposed_queue"] == "q-human-fairness"
    assert result["rules"]["applied"] is False
    assert result["fairness"]["instruction_detected"] is True
    assert result["fairness"]["characteristic_used_as_a_feature"] is False
    assert result["fairness"]["duty_met"] is False
    assert result["fairness"]["due_regard_carried_out"] is False
    assert result["confidence"]["band"] == "not_used"


def test_an_adjustment_request_is_not_scored_and_is_not_a_routine_repair():
    result = propose_route(
        case("I use a wheelchair and I need you to repair the door."),
        AS_OF,
    )
    assert result["outcome"] == "human_adjustment"
    assert result["proposed_queue"] == "q-human-review"
    assert result["fairness"]["duty_met"] is False
    assert result["flags"]["protected_characteristic_used_as_a_feature"] is False


def test_entitlement_is_not_decided():
    result = propose_route(case("Am I entitled to council tax support?"), AS_OF)
    assert result["outcome"] == "human_entitlement"
    assert result["flags"]["entitlement_decided"] is False
    assert result["proposed_queue"] == "q-human-review"
