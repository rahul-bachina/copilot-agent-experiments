"""Lifecycle proposals. A status changes only when a person has already decided.

This module never mints an approval id and never sets approved_by_this_tool.
"""

from __future__ import annotations

import copy
from typing import Any

from catalogue import GENERATED_ID_PREFIX, GOVERNANCE_OWNER_ROLE, LIFECYCLE_STATUSES


class ProhibitedAction(RuntimeError):
    """The caller asked this tool to approve, send, or publish."""


def propose_status_change(
    record: dict[str, Any],
    target_status: str,
    reason: str,
    requested_by: str,
) -> dict[str, Any]:
    """Return a proposal. The inventory record is not modified."""
    if target_status not in LIFECYCLE_STATUSES:
        raise ValueError("target_status is not a known lifecycle status")
    if not reason or not reason.strip():
        raise ValueError("A proposal needs a reason a person can read")
    if target_status == record["lifecycle_status"]:
        raise ValueError("The record is already in that status")
    return {
        "inventory_id": record["inventory_id"],
        "from_status": record["lifecycle_status"],
        "to_status": target_status,
        "reason": reason.strip(),
        "requested_by": requested_by,
        "applied": False,
        "approved": False,
        "approved_by_this_tool": False,
        "approver_required": GOVERNANCE_OWNER_ROLE,
        "actions_taken": [],
    }


def apply_status_change(
    record: dict[str, Any],
    proposal: dict[str, Any],
    approval: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply a proposal only when an external governance-owner decision is supplied.

    Returns the original record when the decision is missing or is not an
    approval. The returned event never says this tool approved the change.
    """
    if approval is not None and approval.get("minted_by") == "g010":
        raise ProhibitedAction("This tool does not mint approvals")
    event: dict[str, Any] = {
        "inventory_id": record.get("inventory_id"),
        "from_status": proposal.get("from_status"),
        "to_status": proposal.get("to_status"),
        "reason": proposal.get("reason"),
        "requested_by": proposal.get("requested_by"),
        "applied": False,
        "approved": False,
        "approved_by_this_tool": False,
        "external_decision": None,
        "external_approval_id": None,
        "approver_role": None,
        "rejection": None,
        "actions_taken": [],
    }
    rejection = _rejection_reason(record, proposal, approval)
    if rejection:
        event["rejection"] = rejection
        if isinstance(approval, dict) and approval.get("decision") == "reject":
            event["external_decision"] = "reject"
            event["external_approval_id"] = approval.get("approval_id")
            event["approver_role"] = approval.get("approver_role")
        return record, event

    assert isinstance(approval, dict)
    updated = copy.deepcopy(record)
    updated["lifecycle_status"] = proposal["to_status"]
    updated["lifecycle_change_approved_by_this_tool"] = False
    event["applied"] = True
    event["external_decision"] = "approve"
    event["external_approval_id"] = approval["approval_id"]
    event["approver_role"] = approval["approver_role"]
    return updated, event


def _rejection_reason(
    record: dict[str, Any],
    proposal: dict[str, Any],
    approval: dict[str, Any] | None,
) -> str | None:
    if proposal.get("inventory_id") != record.get("inventory_id"):
        return "Proposal is for a different inventory record"
    if proposal.get("from_status") != record.get("lifecycle_status"):
        return "Proposal does not start from the current status"
    if proposal.get("to_status") not in LIFECYCLE_STATUSES:
        return "Target status is not known"
    if not isinstance(approval, dict):
        return "No external decision was supplied"
    if approval.get("source") != "external":
        return "Decision source must be external. This tool does not supply one."
    approval_id = approval.get("approval_id")
    if not isinstance(approval_id, str) or not approval_id.strip():
        return "External decision has no approval id"
    if approval_id.startswith(GENERATED_ID_PREFIX):
        return "Approval ids with the generator prefix are rejected"
    if approval.get("approver_role") != GOVERNANCE_OWNER_ROLE:
        return "Approver role must be Governance owner"
    if approval.get("inventory_id") != record.get("inventory_id"):
        return "External decision is for a different inventory record"
    if approval.get("to_status") != proposal.get("to_status"):
        return "External decision is for a different target status"
    if approval.get("approved_by_this_tool") is True:
        return "A decision cannot claim it was approved by this tool"
    decision = approval.get("decision")
    if decision == "reject":
        return "Governance owner rejected the change"
    if decision != "approve":
        return "External decision must be approve or reject"
    decided_on = approval.get("decided_on")
    if not isinstance(decided_on, str) or len(decided_on) != 10:
        return "External decision needs an ISO date in decided_on"
    return None
