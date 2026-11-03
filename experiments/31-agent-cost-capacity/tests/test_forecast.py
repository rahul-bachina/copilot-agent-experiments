"""The forecast states its band and does not invent a Microsoft range."""

from tests.support import run, sample


def test_sample_forecast_repeats_the_period_when_the_horizon_matches():
    report = run()
    forecast = report["forecast"]
    assert forecast["point"] == "4.3500"
    assert forecast["low"] == "3.4800"
    assert forecast["high"] == "5.2200"
    assert forecast["band"] == "0.2000"
    assert forecast["band_source"] == "caller"
    assert forecast["observed_days"] == 31
    assert forecast["horizon_days"] == 31
    assert forecast["cases_point"] == "250"
    assert forecast["statistical_interval"] is False
    assert forecast["microsoft_estimate"] is False
    assert forecast["validated"] is False
    assert forecast["do_not_rely"] is False
    assert forecast["coverage_end"] == "2027-01-29"
    assert forecast["horizon_end"] == "2026-12-01"
    assert forecast["flags"] == []


def test_default_band_is_labelled_as_the_starter_default():
    bundle, _card = sample()
    del bundle["forecast"]["band"]
    report = run(bundle)
    assert report["forecast"]["band"] == "0.2000"
    assert report["forecast"]["band_source"] == "starter_default"
    assert report["forecast"]["low"] == "3.4800"


def test_uncovered_horizon_is_not_relied_on():
    _bundle, card = sample()
    card["validity_days"] = 10
    report = run(rate_card=card)
    assert report["forecast"]["do_not_rely"] is True
    assert any(row["id"] == "forecast_rate_uncovered" for row in report["forecast"]["flags"])
    assert report["do_not_rely"] is True
    assert report["totals"]["cost"] == "4.3500"


def test_unspecified_validity_marks_the_forecast():
    _bundle, card = sample()
    del card["validity_days"]
    report = run(rate_card=card)
    assert any(row["id"] == "forecast_validity_unspecified" for row in report["forecast"]["flags"])
    assert report["forecast"]["do_not_rely"] is True
