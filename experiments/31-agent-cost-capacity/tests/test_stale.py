"""A stale rate card and a stale pin are flagged. The date is not rewritten."""

from tests.support import run, sample


def test_fresh_sample_is_within_ninety_days():
    report = run()
    card = report["rate_card"]
    assert card["effective_date"] == "2026-10-01"
    assert card["age_days"] == 33
    assert card["stale"] is False
    opened = [row for row in report["sources"] if row["stale_applicable"]]
    assert opened
    assert all(row["stale"] is False for row in opened)
    assert all(row["reopened_for_this_experiment"] is True for row in opened)
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert boundary["stale_applicable"] is False
    assert boundary["reopened_for_this_experiment"] is False


def test_old_as_of_marks_the_card_and_the_pins_and_still_shows_the_arithmetic():
    report = run(as_of="2027-05-01")
    assert report["rate_card"]["stale"] is True
    assert report["do_not_rely"] is True
    assert report["totals"]["cost"] == "4.3500"
    assert report["rates_validated"] is False
    assert report["forecast"]["validated"] is False
    opened = [row for row in report["sources"] if row["stale_applicable"]]
    assert all(row["stale"] is True for row in opened)
    boundary = next(row for row in report["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    assert any(row["id"] == "rate_card_stale" for row in report["anomalies"])


def test_future_rate_card_is_not_applied():
    _bundle, card = sample()
    card["effective_date"] = "2026-12-01"
    report = run(rate_card=card)
    assert report["rate_card"]["not_yet_effective"] is True
    assert report["totals"]["cost"] is None
    assert report["agents"]
    assert all(row["cost"] is None for row in report["agents"])
    assert report["do_not_rely"] is True
    assert any(row["id"] == "rate_card_not_yet_effective" for row in report["anomalies"])
    assert not any(row["id"] == "rate_missing" for row in report["anomalies"])


def test_caller_threshold_can_mark_a_thirty_three_day_card_stale():
    report = run()
    from src.report import evaluate
    from tests.support import sample as load_sample

    bundle, card = load_sample()
    marked = evaluate(bundle, card, as_of="2026-11-03", stale_after_days=30)
    assert marked["rate_card"]["stale"] is True
    assert marked["totals"]["cost"] == "4.3500"
    assert report["rate_card"]["stale"] is False
