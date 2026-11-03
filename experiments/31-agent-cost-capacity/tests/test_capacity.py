"""Headroom is a report. The quota limit stays where the caller put it."""

from tests.support import run, sample


def test_sample_headroom_uses_each_meter_once():
    report = run()
    credits = next(row for row in report["capacity"] if row["quota_id"] == "env-credits")
    assert credits["used"] == "255"
    assert credits["headroom"] == "745"
    assert credits["headroom_ratio"] == "0.745000"
    assert credits["changed"] is False
    assert credits["added_rollup"] is False
    assert credits["flags"] == []
    assert report["quota_changed"] is False
    assert report["budget_changed"] is False
    assert report["subscription_changed"] is False


def test_over_quota_is_a_flag_and_not_a_new_limit():
    bundle, _card = sample()
    bundle["quotas"][0]["limit"] = "100"
    report = run(bundle)
    credits = report["capacity"][0]
    assert credits["limit"] == "100"
    assert credits["used"] == "255"
    assert credits["headroom"] == "-155"
    assert "over_quota" in credits["flags"]
    assert "tight_headroom" not in credits["flags"]
    assert report["quota_changed"] is False


def test_tight_headroom_is_separate_from_over_quota():
    bundle, _card = sample()
    bundle["quotas"][0]["limit"] = "280"
    report = run(bundle)
    credits = report["capacity"][0]
    assert credits["flags"] == ["tight_headroom"]
    assert report["quota_changed"] is False


def test_spike_needs_three_unit_costs_on_the_same_platform():
    bundle, _card = sample()
    bundle["agents"] = [
        {
            "agent_id": agent_id,
            "name": agent_id,
            "platform": "copilot_studio_standard",
            "cases": cases,
            "copilot_credits": credits,
            "tokens": {"input": 10, "output": 10},
        }
        for agent_id, credits, cases in (
            ("a", "1", 100),
            ("b", "1", 100),
            ("c", "1", 100),
            ("d", "100", 10),
        )
    ]
    bundle["period_rollup"] = {"copilot_credits": "103", "cost": "1.0300"}
    report = run(bundle)
    spikes = [row for row in report["anomalies"] if row["id"] == "spike"]
    assert [row["agent_id"] for row in spikes] == ["d"]
    assert report["totals"]["cost"] == "1.0300"


def test_one_agent_on_a_platform_is_not_called_a_spike():
    report = run()
    assert not any(row["id"] == "spike" for row in report["anomalies"])
