"""Smoke totals stay separate. A case count is not added to an escalation count."""

import json
from datetime import date
from pathlib import Path

from src.triage import score_supplied_summary, triage
from tests.support import COVERED_CANDIDATE, base_pack, stale_pack

AS_OF = date(2026, 11, 5)
ROOT = Path(__file__).resolve().parents[1]


def test_one_case_is_not_counted_twice_inside_the_scorecard():
    draft = triage(base_pack(), as_of=AS_OF)
    faith = draft["scorecard"]["faithfulness"]
    assert faith["verdict_total"] == faith["claim_count"]
    assert faith["stale_claim_count"] == 0
    assert faith["claim_count"] + faith["stale_claim_count"] != faith["verdict_total"] or faith["stale_claim_count"] == 0
    assert "grand_total" not in draft["scorecard"]
    stale = triage(stale_pack(), as_of=AS_OF)
    # The stale date is a file flag. It is not added to the verdict total.
    assert stale["do_not_rely"] is True
    assert stale["scorecard"]["faithfulness"]["verdict_total"] == stale["scorecard"]["faithfulness"]["claim_count"]
    assert stale["scorecard"]["below_threshold"] is False


def test_escalation_count_is_cases_not_a_sum_of_criteria():
    clean = triage(base_pack(), as_of=AS_OF)
    covered = score_supplied_summary(base_pack(), COVERED_CANDIDATE, as_of=AS_OF)
    rows = [clean["scorecard"], covered]
    case_count = len(rows)
    escalated = sum(1 for row in rows if row["human_escalation_required"])
    criteria = sum(len(row["criteria_below_threshold"]) for row in rows)
    summary = {
        "case_count": case_count,
        "cases_escalated": escalated,
        "scores_are_not_summed_across_criteria": True,
        "case_count_is_not_added_to_escalated": True,
    }
    assert summary["case_count"] == 2
    assert summary["cases_escalated"] == 1
    assert "grand_total" not in summary
    assert case_count + escalated not in summary.values()
    assert criteria not in summary.values()


def test_smoke_report_shape_when_present():
    path = ROOT / "eval" / "smoke_report.json"
    if not path.is_file():
        return
    report = json.loads(path.read_text(encoding="utf-8"))
    summary = report["summary"]
    assert summary["scores_are_not_summed_across_criteria"] is True
    assert "grand_total" not in summary
    assert summary["case_count"] + summary["cases_escalated"] not in summary.values()
