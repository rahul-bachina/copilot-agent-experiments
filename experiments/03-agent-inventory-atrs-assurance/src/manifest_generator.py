"""Draft an agent-manifest.yaml from an inventory record and validate it.

The generator cannot mark the manifest approved. Passing approve=True raises.
An inventory row that asks for autonomy A3 produces no manifest.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator

from catalogue import AUTONOMY_LEVELS
from lifecycle import ProhibitedAction

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "schemas" / "agent-manifest.schema.json"
)


def generate_manifest(
    record: dict[str, Any],
    as_of: str,
    approve: bool = False,
) -> dict[str, Any]:
    if approve:
        raise ProhibitedAction(
            "The permissions-manifest generator cannot mark a manifest approved."
        )
    result: dict[str, Any] = {
        "document_status": "draft",
        "approved": False,
        "approved_by": None,
        "may_be_relied_on": False,
        "validation_passed": False,
        "manifest": None,
        "yaml": None,
        "errors": [],
        "actions_taken": [],
    }
    if record.get("autonomy_level") not in AUTONOMY_LEVELS:
        result["errors"].append(
            "Autonomy A3 is not permitted in this catalogue. No manifest was drafted."
            if record.get("autonomy_level") == "A3"
            else "Autonomy level is not A0, A1, or A2. No manifest was drafted."
        )
        return result

    manifest = _build(record, as_of)
    text = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)
    loaded = yaml.safe_load(text)
    errors = _validate(loaded)
    result["yaml"] = text
    result["manifest"] = loaded
    result["errors"] = errors
    result["validation_passed"] = not errors
    result["approved"] = False
    if loaded.get("draft_control", {}).get("approved") is not False:
        raise ProhibitedAction("Draft control lost the not-approved flag")
    return result


def repo_schema() -> dict[str, Any]:
    import json

    with open(SCHEMA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def _validate(manifest: dict[str, Any]) -> list[str]:
    validator = Draft7Validator(repo_schema(), format_checker=Draft7Validator.FORMAT_CHECKER)
    return [error.message for error in sorted(validator.iter_errors(manifest), key=str)]


def _build(record: dict[str, Any], as_of: str) -> dict[str, Any]:
    level = record["autonomy_level"]
    last_review, next_review, review_note = _review_dates(record, as_of)
    description = _description(record)
    return {
        "draft_control": {
            "document_status": "draft",
            "approved": False,
            "approved_by": None,
            "may_be_relied_on": False,
            "note": (
                "Generated from an inventory record. This file is not an "
                "approval of the agent, the lifecycle status, or the manifest."
            ),
        },
        "agent": {
            "id": record["inventory_id"],
            "name": record["name"][:100],
            "version": record.get("version") or "0.0.0",
            "description": description,
            "owner": record.get("team") or "Not recorded in the inventory",
            "contact": record.get("contact_email") or "not-recorded@example.com",
            "repository": "https://github.com/rahul-bachina/copilot-agent-experiments",
            "experiment_path": record.get("experiment_path")
            or "experiments/03-agent-inventory-atrs-assurance",
        },
        "autonomy": {
            "level": level,
            "level_description": _level_description(level),
            "constraints": [
                "This manifest is a draft from the inventory generator",
                "The generator does not approve lifecycle status, publishing, or sending",
                "High-risk actions are left disabled even if the inventory asked for them",
            ],
            "human_in_the_loop": True,
            "auto_actions_enabled": False,
        },
        "data_access": {
            "reads": _reads(record),
            "never_access": _never(record),
        },
        "tools": {
            "allowed": [
                {
                    "tool": "Read the inventory record supplied for this draft",
                    "provider": "Local Python",
                    "action": "Copy recorded fields into a draft manifest",
                    "access_level": "read",
                    "scope": "The single inventory record passed to the generator",
                    "justification": "The draft cannot be built without the record the caller supplied",
                    "human_approval_required": False,
                    "output_requires_human_review": True,
                }
            ],
            "writes": {
                "enabled": False,
                "note": "The generator does not write Dataverse or any other production record.",
            },
            "sends": {
                "enabled": False,
                "note": "The generator does not send email or publish an ATRS record.",
            },
        },
        "human_approval": {
            "description": (
                "A governance owner approves every lifecycle status change "
                "outside this generator. The generator cannot record that approval."
            ),
            "approval_points": [
                {
                    "action": "Change the lifecycle status of the inventoried agent",
                    "approver": "Governance owner",
                    "mandatory": True,
                    "rationale": "Catalogue control for G010. The generator only drafts.",
                },
                {
                    "action": "Rely on this manifest in a tenant",
                    "approver": "Governance owner",
                    "mandatory": True,
                    "rationale": "A generated file is not a sign-off.",
                },
            ],
            "no_approval_required": [
                {
                    "action": "Generate this draft from an inventory record",
                    "rationale": "The draft has no external effect.",
                }
            ],
        },
        "uk_gdpr": {
            "lawful_basis": {
                "primary": _basis(record),
                "description": (
                    "Copied from the inventory where a basis was recorded. "
                    "The generator does not choose a basis. A DPO confirms it "
                    "before any processing."
                ),
            },
            "special_category_data": {
                "may_process": record.get("special_category_data") == "yes",
                "lawful_basis_special": "Not asserted by this generator.",
                "safeguards": [
                    "No Article 9 condition is claimed here",
                    "The draft is not written to a production record",
                ],
            },
            "data_minimisation": [
                "One inventory record per draft",
                "Narrative text is copied, not enriched",
            ],
            "retention": {
                "agent_retention": "None in this generator. The draft is returned to the caller.",
            },
            "data_residency": {
                "region": "UK",
                "note": "A deployment choice. This generator does not call a model.",
            },
        },
        "risk_assessment": {
            "methodology": "Rows copied from the inventory where they were valid. Otherwise a single gap row.",
            "date_assessed": as_of,
            "risks": _risks(record),
        },
        "logging_and_audit": {
            "description": "This generator does not write a log. A deployment would need one before live use.",
            "logged_events": [
                {
                    "event": "Manifest draft generated",
                    "data_logged": ["inventory id", "as-of date", "validation result"],
                    "retention": "Not set by this generator.",
                }
            ],
        },
        "kill_switch": {
            "description": "Ways a deployment can stop use of the inventoried agent. Not tested here.",
            "methods": [
                {
                    "method": "Stop the Copilot Studio agent",
                    "action": "Set the published agent to off",
                    "who_can_activate": "Copilot Studio administrators",
                },
                {
                    "method": "Remove the Dataverse security role",
                    "action": "Take the read role off the agent identity",
                    "who_can_activate": "Power Platform administrators",
                },
            ],
        },
        "review": {
            "last_review_date": last_review,
            "next_review_date": next_review,
            "review_frequency": "Draft only. " + review_note,
            "reviewer": "Not assigned by this generator",
        },
        "high_risk_actions": {
            "approve_reject": _disabled(
                "The generator does not approve or reject an agent, a record, or a request."
            ),
            "regulated_decision": _disabled(
                "ATRS scope, DUAA engagement, and FCA inventory status are screens, not decisions."
            ),
            "production_record_change": _disabled(
                "Lifecycle status in a system of record is changed by a person, not by this draft."
            ),
            "external_send": _disabled(
                "The draft is not emailed to the ATRS team or to anyone else."
            ),
            "spend_transact": _disabled("No spend and no contract."),
            "additional_high_risk": [
                _disabled("Publish an ATRS record", "Publish an ATRS record"),
                _disabled("Mark a manifest approved", "Mark a manifest approved"),
            ],
        },
        "assumptions": {
            "description": "The organisation confirms these before anyone relies on the draft.",
            "items": [
                {
                    "id": "G1",
                    "assumption": review_note,
                    "section": "review",
                    "verify_on_deployment": True,
                },
                {
                    "id": "G2",
                    "assumption": "High-risk actions stay disabled until a person edits the manifest and the schema still passes",
                    "section": "high_risk_actions",
                    "verify_on_deployment": True,
                },
                {
                    "id": "G3",
                    "assumption": record.get("lawful_basis")
                    or "No lawful basis was recorded. A DPO has to choose one.",
                    "section": "uk_gdpr.lawful_basis",
                    "verify_on_deployment": True,
                },
            ],
        },
    }


def _disabled(rationale: str, action_name: str | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {"enabled": False, "rationale": rationale}
    if action_name:
        entry["action_name"] = action_name
    return entry


def _description(record: dict[str, Any]) -> str:
    text = record.get("public_description") or record.get("one_sentence_description") or record["name"]
    text = str(text).strip()
    prefix = "Draft manifest for the inventoried agent. "
    combined = prefix + text
    if len(combined) < 10:
        combined = prefix + "No public description was recorded."
    return combined


def _level_description(level: str) -> str:
    return {
        "A0": "Read-only analysis. Drafted from the inventory, not approved.",
        "A1": "Human approves every action. Drafted from the inventory, not approved.",
        "A2": "Human approves high-risk actions. Drafted from the inventory, not approved.",
    }[level]


def _basis(record: dict[str, Any]) -> str:
    basis = record.get("lawful_basis")
    if isinstance(basis, str) and basis.strip():
        return basis.strip()
    return "Not recorded. A DPO must confirm a basis before processing."


def _reads(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows = record.get("data_reads") or []
    drafted = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("resource"):
            continue
        drafted.append(
            {
                "resource": row["resource"],
                "access_level": "read",
                "justification": row.get("justification") or "Recorded on the inventory. Not re-justified here.",
                "may_contain_personal_data": bool(row.get("may_contain_personal_data")),
            }
        )
    if drafted:
        return drafted
    return [
        {
            "resource": "Inventory record supplied for this draft",
            "access_level": "read",
            "justification": "The generator reads only the record it was given",
            "may_contain_personal_data": record.get("processes_personal_data") == "yes",
        }
    ]


def _never(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows = record.get("never_access") or []
    drafted = []
    for row in rows:
        if isinstance(row, dict) and row.get("resource") and row.get("reason"):
            drafted.append({"resource": row["resource"], "reason": row["reason"]})
    drafted.append(
        {
            "resource": "A channel that can send or publish",
            "reason": "The generator has no send and no ATRS submission step",
        }
    )
    return drafted


def _risks(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in record.get("risk_rows") or []:
        if not isinstance(row, dict):
            continue
        if row.get("likelihood") not in {"Low", "Medium", "High"}:
            continue
        if row.get("impact") not in {"Low", "Medium", "High"}:
            continue
        if row.get("residual_risk") not in {"Low", "Medium", "High"}:
            continue
        if not row.get("id") or not row.get("risk"):
            continue
        rows.append(
            {
                "id": str(row["id"]),
                "risk": str(row["risk"]),
                "likelihood": row["likelihood"],
                "impact": row["impact"],
                "controls": ["Copied from the inventory. This generator has not accepted the risk."],
                "residual_risk": row["residual_risk"],
                "owner": "Not assigned by this generator",
            }
        )
    if rows:
        return rows
    return [
        {
            "id": "R0",
            "risk": "The inventory had no usable risk rows, so this draft is incomplete",
            "likelihood": "Medium",
            "impact": "Medium",
            "controls": ["A person adds the organisation's own risk rows before reliance"],
            "residual_risk": "Medium",
            "owner": "Not assigned by this generator",
        }
    ]


def _review_dates(record: dict[str, Any], as_of: str) -> tuple[str, str, str]:
    try:
        reviewed = date.fromisoformat(record["source_reviewed_on"])
        note = "Next review is 365 days after the inventory review date. That interval is not a legal period."
    except (TypeError, ValueError):
        reviewed = date.fromisoformat(as_of)
        note = "The inventory had no usable review date. The dates are the as-of date of this draft."
    return reviewed.isoformat(), (reviewed + timedelta(days=365)).isoformat(), note
