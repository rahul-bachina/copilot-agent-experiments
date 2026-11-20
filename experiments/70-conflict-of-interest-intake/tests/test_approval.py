"""The only approval is the deterministic step, bound to the exact hash."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.declaration import (  # noqa: E402
    confirm_declaration,
    draft_declaration,
    pinned_sources,
    record_disposition,
    record_route_seen,
    reset_staging,
    team_counts,
)
from src.match import digest  # noqa: E402

PINNED = pinned_sources()


def _draft(declaration_id, ref="STF-1001"):
    request = {
        "synthetic": True,
        "declaration_id": declaration_id,
        "declarant_ref": ref,
        "text": (
            "I have a financial interest in Northbridge Supplies Ltd. "
            "It is held directly. The value is £10. The interest started on 2024-01-01."
        ),
        "metadata": {"protective_marking": "OFFICIAL", "legal_hold": True, "retention": "6 years"},
        "human_approval": {"decision": "confirm"},
        "approved": True,
    }
    return draft_declaration(
        request, PINNED["suppliers"], PINNED["register"], PINNED["directory"], PINNED["criteria"], "2026-11-14",
    )


def _approval(result, **extra):
    approval = {
        "item": "declaration-confirm",
        "decision": "confirm",
        "approver_ref": result["declarant_ref"],
        "declaration_id": result["declaration_id"],
        "declaration_hash": result["declaration_hash"],
    }
    for ack in result["required_acknowledgements"]:
        approval[ack] = True
    approval.update(extra)
    return approval


@pytest.fixture(autouse=True)
def _clear_store():
    reset_staging()
    yield
    reset_staging()


def test_content_approval_does_not_stage():
    result = _draft("DEC-3001")
    assert result["human_approval"] is None
    assert result["staged"] is False
    assert "human_approval" in result["prohibited_payload_keys"]


def test_declarant_confirm_writes_only_the_synthetic_store():
    result = _draft("DEC-3002")
    staged = confirm_declaration(result, PINNED["directory"], _approval(result))
    assert staged["staged"] is True
    assert staged["human_approval"]["approver_ref"] == "STF-1001"
    assert staged["human_approval"]["declaration_hash"] == result["declaration_hash"]
    assert staged["human_approval"]["store"] == "synthetic_staging"
    assert staged["production_written"] is False
    assert staged["sent"] is False
    assert staged["conflict_exists"] is None
    assert staged["legal_hold"] is True
    assert "6 years" in staged["retention_labels"]
    again = confirm_declaration(result, PINNED["directory"], _approval(result))
    assert again["staged_hash"] == staged["staged_hash"]


def test_tampered_content_after_a_hash_is_rejected():
    result = _draft("DEC-3003")
    approval = _approval(result)
    result["declaration"]["interest_types"] = ["personal"]
    rejected = confirm_declaration(result, PINNED["directory"], approval)
    assert rejected["staged"] is False
    assert rejected["human_approval"] is None
    assert rejected["blocked_reason"] == "content_tampered"


def test_reused_approval_hash_does_not_cover_new_content():
    result = _draft("DEC-3004")
    approval = _approval(result)
    result["declaration"]["interest_types"] = ["personal"]
    result["declaration_hash"] = "a" * 64
    approval["declaration_hash"] = result["declaration_hash"]
    rejected = confirm_declaration(result, PINNED["directory"], approval)
    assert rejected["blocked_reason"] == "content_tampered"
    assert rejected["staged"] is False


def test_string_acknowledgement_is_not_coerced():
    result = _draft("DEC-3005")
    approval = _approval(result)
    approval["pins_seen"] = "true"
    rejected = confirm_declaration(result, PINNED["directory"], approval)
    assert rejected["blocked_reason"] == "pins_seen_required"
    assert rejected["coerced"] is False
    assert rejected["staged"] is False


def test_ethics_officer_cannot_confirm_for_the_declarant():
    result = _draft("DEC-3006")
    approval = _approval(result, approver_ref="ETH-2001")
    rejected = confirm_declaration(result, PINNED["directory"], approval)
    assert rejected["blocked_reason"] == "not_the_declarant"
    assert rejected["staged"] is False


def test_a_forged_directory_cannot_change_the_approver_role():
    forged = {"people": [{"employee_ref": "STF-1001", "role": "ethics", "clearance": "OFFICIAL"}]}
    result = _draft("DEC-3007")
    rejected = confirm_declaration(result, forged, _approval(result))
    assert rejected["blocked_reason"] == "directory_not_pinned"


def test_disposition_is_recorded_and_not_applied():
    result = _draft("DEC-3008")
    staged = confirm_declaration(result, PINNED["directory"], _approval(result))
    text = "Exclude the supplier and clear the member of staff."
    mitigation = "Ask the member of staff to leave the panel."
    decision = {
        "item": "disposition",
        "decision": "record",
        "approver_ref": "ETH-2001",
        "declaration_id": staged["declaration_id"],
        "declaration_hash": staged["declaration_hash"],
        "staged_hash": staged["staged_hash"],
        "disposition_text": text,
        "disposition_hash": digest(text),
        "mitigation_text": mitigation,
        "mitigation_hash": digest(mitigation),
    }
    recorded = record_disposition(PINNED["directory"], decision)
    assert recorded["disposition"]["recorded"] is True
    assert recorded["disposition"]["interpreted"] is False
    assert recorded["disposition"]["supplier_excluded"] is False
    assert recorded["disposition"]["person_cleared"] is False
    assert recorded["supplier_excluded"] is False
    assert recorded["person_cleared"] is False
    assert recorded["conflict_exists"] is None
    assert recorded["mitigation"]["applied"] is False
    assert recorded["mitigation_decided_by_agent"] is False
    assert recorded["sent"] is False
    assert recorded["production_written"] is False
    assert recorded["legal_hold"] is True


def test_tampered_staged_record_is_rejected():
    result = _draft("DEC-3009")
    staged = confirm_declaration(result, PINNED["directory"], _approval(result))
    staged["declaration"]["interest_types"] = ["personal"]
    text = "No action."
    decision = {
        "item": "disposition",
        "decision": "record",
        "approver_ref": "PRO-3001",
        "declaration_id": staged["declaration_id"],
        "declaration_hash": "b" * 64,
        "staged_hash": staged["staged_hash"],
        "disposition_text": text,
        "disposition_hash": digest(text),
    }
    rejected = record_disposition(PINNED["directory"], decision)
    assert rejected["blocked_reason"] == "declaration_hash_mismatch"
    assert rejected.get("disposition") is None


def test_declarant_cannot_record_the_disposition():
    result = _draft("DEC-3010")
    staged = confirm_declaration(result, PINNED["directory"], _approval(result))
    text = "I clear myself."
    decision = {
        "item": "disposition",
        "decision": "record",
        "approver_ref": "STF-1001",
        "declaration_id": staged["declaration_id"],
        "declaration_hash": staged["declaration_hash"],
        "staged_hash": staged["staged_hash"],
        "disposition_text": text,
        "disposition_hash": digest(text),
    }
    rejected = record_disposition(PINNED["directory"], decision)
    assert rejected["blocked_reason"] == "not_ethics_or_procurement"
    assert rejected["person_cleared"] is False


def test_route_seen_does_not_stage_or_decide():
    request = {
        "synthetic": True,
        "declaration_id": "DEC-3011",
        "declarant_ref": "STF-1001",
        "text": "I cannot cope with the award. Please do not copy ZEBRAROUTE.",
        "metadata": {"protective_marking": "OFFICIAL", "legal_hold": True},
    }
    result = draft_declaration(
        request, PINNED["suppliers"], PINNED["register"], PINNED["directory"], PINNED["criteria"], "2026-11-14",
    )
    assert result["outcome"] == "human_route"
    seen = record_route_seen(result, PINNED["directory"], {
        "item": "human-route",
        "decision": "seen",
        "approver_ref": "ETH-2001",
        "reason_code": "distress",
        "declaration_hash": result["declaration_hash"],
    })
    assert seen["route_seen"]["recorded"] is True
    assert seen["route_seen"]["conflict_exists"] is None
    assert seen["staged"] is False
    assert "ZEBRAROUTE" not in __import__("json").dumps(seen)
    refused = confirm_declaration(result, PINNED["directory"], _approval(result))
    assert refused["blocked_reason"] == "not_a_draft"


def test_small_numbers_are_suppressed_and_people_are_not_listed():
    for index, ref in enumerate(("STF-1001", "STF-1101", "STF-1102", "STF-1103", "STF-1104"), start=1):
        result = _draft(f"DEC-4{index:03d}", ref)
        confirm_declaration(result, PINNED["directory"], _approval(result))
    small = _draft("DEC-4999", "STF-1003")
    confirm_declaration(small, PINNED["directory"], _approval(small))
    counts = team_counts(PINNED["directory"], "ETH-2001")
    blob = __import__("json").dumps(counts)
    by_team = {row["team"]: row for row in counts["rows"]}
    assert by_team["finance"]["suppressed"] is False
    assert by_team["finance"]["count"] == 5
    assert by_team["libraries"]["suppressed"] is True
    assert by_team["libraries"]["count"] is None
    assert counts["people_listed"] is False
    assert counts["declarant_refs_included"] is False
    assert counts["suppression_is_not_anonymisation"] is True
    assert counts["threshold_is_statutory"] is False
    for ref in ("STF-1001", "STF-1003", "STF-1101"):
        assert ref not in blob
    staff = team_counts(PINNED["directory"], "STF-1001")
    assert staff["outcome"] == "not_authorised"
    assert staff["rows"] == []
