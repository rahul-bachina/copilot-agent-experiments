"""The day the window ends is still current. The next day is stale."""

from datetime import date, timedelta

from src.summarise import summarise
from tests.support import case, event, four_events

AS_OF = "2026-11-09"
AS_OF_DATE = date(2026, 11, 9)


def test_day_90_is_current_and_day_91_is_not_quoted():
    current_day = (AS_OF_DATE - timedelta(days=90)).isoformat()
    stale_day = (AS_OF_DATE - timedelta(days=91)).isoformat()
    current = summarise(
        case([event("E1", current_day, "what_happened", "The tenant reported a leaking kitchen tap.")] + four_events()[1:]),
        AS_OF,
    )
    assert any(row["fact_key"] == "what_happened" and row["verdict"] == "supported" for row in current["sentences"])
    assert "stale_or_superseded_not_used" not in current["do_not_rely_reasons"]

    stale = summarise(
        case([event("E1", stale_day, "what_happened", "The tenant reported a leaking kitchen tap.")] + four_events()[1:]),
        AS_OF,
    )
    assert all(row["fact_key"] != "what_happened" for row in stale["sentences"])
    assert any(row["reason"] == "stale" for row in stale["not_used"])
    assert "The tenant reported a leaking kitchen tap." not in [
        row["text"] for row in stale["sentences"] if row["fact_key"] == "what_happened"
    ]
    assert stale["do_not_rely"] is True
    assert "stale_or_superseded_not_used" in stale["do_not_rely_reasons"]


def test_superseded_and_future_events_are_not_quoted():
    superseded = event(
        "E1",
        "2026-10-20",
        "what_happened",
        "The tenant reported a leaking kitchen tap.",
        status="superseded",
        superseded_by="E2",
    )
    draft = summarise(case([superseded] + four_events()[1:]), AS_OF)
    assert any(row["reason"] == "superseded" for row in draft["not_used"])
    assert all(row["fact_key"] != "what_happened" for row in draft["sentences"])

    future = event("E1", "2026-11-10", "what_happened", "The tenant reported a leaking kitchen tap.")
    later = summarise(case([future] + four_events()[1:]), AS_OF)
    assert any(row["reason"] == "recorded_date_after_as_of" for row in later["not_used"])


def test_a_stale_pin_sets_do_not_rely_without_hiding_a_current_note():
    events = [
        event("E1", "2027-02-20", "what_happened", "The tenant reported a leaking kitchen tap."),
        event("E2", "2027-02-21", "customer_ask", "The tenant asked for the tap to be repaired this week."),
        event("E3", "2027-02-22", "action_taken", "Do not contact the customer."),
        event("E4", "2027-02-23", "next_step", "The next step recorded on the case is a plumber visit."),
    ]
    draft = summarise(case(events), "2027-03-01")
    assert draft["pins_stale"] is True
    assert draft["checker_passed"] is True
    assert draft["do_not_rely"] is True
    assert "pins_stale" in draft["do_not_rely_reasons"]
    assert draft["summary"]["sentence_count"] == 4
    assert all(row["opened"] is False for row in draft["sources"] if row["id"] == "ico-ai-accuracy")
    assert draft["regulatory"]["ico_ai_accuracy_page_opened"] is False
    assert draft["regulatory"]["ico_ai_accuracy_quoted"] is False


def test_pin_window_day_90_is_not_stale():
    draft = summarise(case(four_events()), "2027-02-07")
    assert draft["pins_stale"] is False
    still = summarise(case(four_events()), "2027-02-08")
    assert still["pins_stale"] is True
