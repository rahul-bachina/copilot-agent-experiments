"""A stale pin or an old alert is flagged and is not cleared."""

from datetime import date, timedelta

from tests.support import load_example

from src.investigate import investigate
from src.sources import DEFAULT_STALE_AFTER_DAYS, SOURCES_PINNED_ON


def test_the_sample_date_is_inside_the_window():
    draft = investigate(load_example(), as_of=date(2026, 10, 29))
    assert draft["sources_stale"] is False
    assert draft["rules_current"] is True
    assert draft["alert_context_stale"] is False
    assert all(row["applied_as_a_decision"] is False for row in draft["sources"])


def test_equal_to_the_threshold_is_not_stale():
    as_of = SOURCES_PINNED_ON + timedelta(days=DEFAULT_STALE_AFTER_DAYS)
    draft = investigate(load_example(), as_of=as_of)
    assert draft["sources_stale"] is False


def test_past_the_threshold_is_stale_and_still_does_not_file():
    draft = investigate(load_example(), as_of=date(2027, 4, 1))
    assert draft["sources_stale"] is True
    assert draft["rules_current"] is False
    assert draft["sar_filed"] is False
    assert draft["mlro_decision"] is None
    assert draft["customer_facing"]["text"] is None


def test_an_old_alert_is_flagged_and_a_future_hop_is_not_placed():
    case = load_example()
    case["alert"]["raised_at"] = "2026-01-01T00:00:00+00:00"
    case["alert"]["hops"][0]["at"] = "2026-11-01T00:00:00+00:00"
    draft = investigate(case, as_of=date(2026, 10, 29))
    assert draft["alert_context_stale"] is True
    future = [event for event in draft["evidence_timeline"] if event["future"]]
    assert future
    assert all(event["placed"] is False for event in future)
