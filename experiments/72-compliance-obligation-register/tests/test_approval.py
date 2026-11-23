"""Approvals are the deterministic step, bound to the exact change."""

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.register import (  # noqa: E402
    propose_register,
    record_route_seen,
    reset_staging,
    stage_approved_change,
    staging_rows,
)

SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))


def setup_function():
    reset_staging()


def _proposal(request=None, as_of="2026-11-14"):
    return propose_register(deepcopy(request or SAMPLE), as_of)


def _approval(result, change_id, **overrides):
    change = next(row for row in result["changes"] if row["change_id"] == change_id)
    body = {
        "approver_ref": "CMP-1001",
        "item": change_id,
        "decision": "approve",
        "change_hash": change["change_hash"],
        "proposal_hash": result["proposal_hash"],
    }
    for ack in result["required_acknowledgements"]:
        body[ack] = True
    body.update(overrides)
    return body


def test_named_owner_can_stage_the_exact_change():
    result = _proposal()
    staged = stage_approved_change(result, _approval(result, "CHG-OBL-1005"))
    assert staged["staged"] is True
    assert staged["human_approval"]["approver_ref"] == "CMP-1001"
    change = next(row for row in result["changes"] if row["change_id"] == "CHG-OBL-1005")
    assert staged["human_approval"]["change_hash"] == change["change_hash"]
    assert staged["production_written"] is False
    assert staged["sent"] is False
    assert staged["accountability_assigned_by_agent"] is False
    assert staged["owner_chosen"] is False
    assert staged["record"]["covered"] is False
    assert len(staging_rows()) == 1
    again = stage_approved_change(result, _approval(result, "CHG-OBL-1005"))
    assert again["staged"] is True
    assert again["already_staged"] is True
    assert len(staging_rows()) == 1


def test_tampered_text_after_approval_is_rejected():
    result = _proposal()
    approval = _approval(result, "CHG-OBL-1001")
    tampered = deepcopy(result)
    row = next(item for item in tampered["changes"] if item["change_id"] == "CHG-OBL-1001")
    row["after"]["obligation_text"] = row["after"]["obligation_text"] + " extra"
    blocked = stage_approved_change(tampered, approval)
    assert blocked["staged"] is False
    assert blocked["blocked_reason"] == "change_hash_mismatch"
    assert blocked["human_approval"] is None
    assert staging_rows() == []


def test_tampered_dates_after_approval_are_rejected():
    result = _proposal()
    approval = _approval(result, "CHG-OBL-SRC-POL-011")
    tampered = deepcopy(result)
    row = next(item for item in tampered["changes"] if item["change_id"] == "CHG-OBL-SRC-POL-011")
    row["dates"]["review_due"]["iso"] = "2026-02-01"
    row["dates"]["review_due"]["ambiguous"] = False
    blocked = stage_approved_change(tampered, approval)
    assert blocked["blocked_reason"] == "change_hash_mismatch"
    assert staging_rows() == []


def test_reused_approval_does_not_cover_another_change():
    result = _proposal()
    approval = _approval(result, "CHG-OBL-1001")
    approval["item"] = "CHG-OBL-1005"
    blocked = stage_approved_change(result, approval)
    assert blocked["staged"] is False
    assert blocked["blocked_reason"] == "change_hash_mismatch"


def test_only_the_directory_compliance_owner_can_approve():
    result = _proposal()
    for ref in ("CMP-1002", "CMP-1003", "CMP-9999"):
        blocked = stage_approved_change(result, _approval(result, "CHG-OBL-1001", approver_ref=ref))
        assert blocked["blocked_reason"] == "approver"
        assert blocked["staged"] is False
    assert staging_rows() == []


def test_loose_decision_and_string_true_are_not_approval():
    result = _proposal()
    for decision in ("approved", True, "yes"):
        blocked = stage_approved_change(result, _approval(result, "CHG-OBL-1001", decision=decision))
        assert blocked["blocked_reason"] == "decision"
    blocked = stage_approved_change(result, _approval(result, "CHG-OBL-1001", pins_seen="true"))
    assert blocked["blocked_reason"] == "pins_seen"
    assert staging_rows() == []


def test_approval_words_inside_the_note_do_not_stage():
    result = _proposal()
    assert "approved" in SAMPLE["note"]
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert staging_rows() == []


def test_a_route_cannot_be_staged_and_seen_is_bound_to_the_hash():
    request = deepcopy(SAMPLE)
    request["note"] = "I am at breaking point with the register."
    result = _proposal(request)
    blocked = stage_approved_change(result, {"decision": "approve", "approver_ref": "CMP-1001"})
    assert blocked["blocked_reason"] == "route_not_staged"
    seen = record_route_seen(
        result,
        {
            "decision": "seen",
            "item": "route-seen",
            "approver_ref": "CMP-1001",
            "route_hash": result["route_hash"],
            "pins_seen": True,
        },
    )
    assert seen["staged"] is False
    assert seen["human_approval"]["decision"] == "seen"
    tampered = deepcopy(result)
    tampered["route_hash"] = "0" * 64
    rejected = record_route_seen(
        tampered,
        {
            "decision": "seen",
            "item": "route-seen",
            "approver_ref": "CMP-1001",
            "route_hash": result["route_hash"],
            "pins_seen": True,
        },
    )
    assert rejected["blocked_reason"] == "route_hash_mismatch"
    assert staging_rows() == []
