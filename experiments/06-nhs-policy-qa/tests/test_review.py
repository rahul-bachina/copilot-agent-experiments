"""Policy-owner review: coverage, stale policies, conflicts, unpublished change notes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from corpus import load_register, parse_date  # noqa: E402
from review import review_register  # noqa: E402

AS_OF = parse_date("2026-10-24")
REPORT = review_register(load_register(), AS_OF)


def by_topic(topic: str) -> dict:
    return next(row for row in REPORT["coverage"] if row["topic"] == topic)


class TestCoverage:
    def test_expected_statuses(self):
        assert by_topic("hr.annual_leave")["status"] == "covered_in_date"
        assert "HR-LEAVE-003" in by_topic("hr.annual_leave")["policy_ids"]
        assert "HR-LEAVE-001" in by_topic("hr.annual_leave")["also_unapproved"]
        assert by_topic("hr.sickness_absence")["status"] == "covered_in_date"
        assert by_topic("hr.flexible_working")["status"] == "covered_in_date"
        assert by_topic("finance.expenses.receipts")["status"] == "covered_in_date"
        assert by_topic("finance.expenses.alcohol")["status"] == "conflict"
        assert set(by_topic("finance.expenses.alcohol")["policy_ids"]) == {
            "FIN-EXP-004",
            "HR-HOSP-002",
        }
        assert by_topic("finance.purchase_cards")["status"] == "covered_in_date"
        assert by_topic("procurement.purchase_orders")["status"] == "covered_in_date"
        assert "PROC-PO-009" in by_topic("procurement.purchase_orders")["also_unapproved"]
        assert by_topic("procurement.conflicts_of_interest")["status"] == "covered_in_date"
        assert by_topic("it.acceptable_use")["status"] == "covered_in_date"
        assert by_topic("it.passwords")["status"] == "stale_only"
        assert by_topic("it.passwords")["also_stale"] == ["IT-PWD-002"]
        assert "IT-PWD-000" in by_topic("it.passwords")["also_unapproved"]
        assert by_topic("estates.room_booking")["status"] == "covered_in_date"
        assert by_topic("estates.lone_working")["status"] == "covered_in_date"
        assert by_topic("estates.parking")["status"] == "missing"
        assert by_topic("hr.cycle_to_work")["status"] == "draft_or_unapproved_only"

    def test_stale_list_and_quarantine(self):
        stale_ids = [row["policy_id"] for row in REPORT["stale_policies"]]
        assert stale_ids == ["IT-PWD-002"]
        assert REPORT["stale_policies"][0]["review_due"] == "2025-06-30"
        quarantined = REPORT["quarantined_clauses"]
        assert quarantined == [
            {
                "policy_id": "IT-INJECT-008",
                "clause_id": "9.9",
                "reason": "instruction_to_the_model",
            }
        ]

    def test_change_note_is_not_published(self):
        assert REPORT["published"] is False
        assert REPORT["accepted_by_policy_owner"] is False
        assert REPORT["actions_taken"] == []
        assert REPORT["model_called"] is False
        assert len(REPORT["conflicts"]) == 1
        assert REPORT["conflicts"][0]["topic"] == "finance.expenses.alcohol"
        note = REPORT["change_notes"][0]
        assert note["published"] is False
        assert note["accepted_by_policy_owner"] is False
        assert note["may_be_applied"] is False
        assert "Not published" in note["text"]
        assert "not_reimbursable" in note["text"]
        assert "reimbursable_with_director_approval" in note["text"]
