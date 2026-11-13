from support import reviewed


def test_the_pin_date_is_current_and_the_window_edge_still_reviews():
    current = reviewed(as_of="2026-11-13")
    assert current["stale"]["rules_current"] is True
    assert current["outcome"] == "review_for_model_owner"
    edge = reviewed(as_of="2027-05-12")
    assert edge["outcome"] == "review_for_model_owner"
    assert edge["guidance"]["current"] is True


def test_one_day_past_the_window_withholds_the_review():
    report = reviewed(as_of="2027-05-13")
    assert report["outcome"] == "stale_sources"
    assert report["stale"]["rules_current"] is False
    assert report["guidance"]["current"] is False
    assert report["ranges_inspected"] == []
    assert report["findings_withheld"] is True
    assert report["sensitivity"] is None
    assert report["questions"] == []
    assert report["human_approval"] is None
    assert report["protective_marking"] == "OFFICIAL-SENSITIVE"
    assert report["retention_label"] == "legal-hold"
    assert report["network_called"] is False
