"""Old advice is shown and marked. The 20-week marker is not a breach finding."""

from src.assemble import assemble
from tests.support import AS_OF, bundle


def test_advice_older_than_the_window_is_stale_and_still_quoted():
    source = bundle()
    source["reports"][0]["dated"] = "2026-01-01"
    draft = assemble(source, as_of=AS_OF, stale_after_days=90)
    stale = next(row for row in draft["stale_reports"] if row["report_id"] == "R-PAR-01")
    assert stale["problem"] == "stale"
    assert draft["do_not_rely"] is True
    line = draft["sections"]["A"]["lines"][0]
    assert line["stale"] is True
    assert line["quote"].startswith("Child A likes drawing")
    assert draft["needs_decided"] is False


def test_a_future_report_date_is_not_copied():
    source = bundle()
    source["reports"][0]["dated"] = "2026-12-01"
    draft = assemble(source, as_of=AS_OF)
    assert draft["sections"]["A"]["lines"] == []
    assert any(row["problem"] == "future" for row in draft["stale_reports"])
    assert draft["do_not_rely"] is True
    assert "likes drawing" not in draft["sections"]["A"]["heading"]


def test_the_twenty_week_marker_does_not_find_a_breach():
    source = bundle()
    source["request_received"] = "2026-01-01"
    draft = assemble(source, as_of=AS_OF)
    marker = draft["timescale"]
    assert marker["days_since_request"] == 307
    assert marker["twenty_weeks_as_days"] == 140
    assert marker["twenty_week_marker_passed"] is True
    assert marker["breach_found"] is False
    assert marker["exceptions_applied"] is False
    assert marker["draft_consultation_started"] is False
    assert draft["sent_to_parents"] is False


def test_a_pinned_page_older_than_the_window_is_not_relied_on():
    draft = assemble(bundle(), as_of="2027-05-04", stale_after_days=90)
    opened = [row for row in draft["sources"] if row["stale_applicable"]]
    assert opened
    assert all(row["stale"] is True for row in opened)
    boundary = next(row for row in draft["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    code = next(row for row in draft["sources"] if row["id"] == "ico-childrens-code")
    assert code["stale"] is False
    assert code["reopened_for_this_experiment"] is False
    assert draft["do_not_rely"] is True
    assert draft["placed_quotes"] == 7
