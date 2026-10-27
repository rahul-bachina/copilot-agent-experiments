"""Draft a permissions manifest for the proposed agent. Never approve it.

The draft is built by Experiment 03's generator and checked against
schemas/agent-manifest.schema.json. Autonomy A3 is not passed in.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    from injection import signals_in_text
else:
    from .injection import signals_in_text

EXP03_SRC = (
    Path(__file__).resolve().parents[2] / "03-agent-inventory-atrs-assurance" / "src"
)

_CONSEQUENTIAL = (
    ("production_write", "Change a production record"),
    ("external_send", "Send externally"),
    ("spend", "Spend or transact"),
    ("approve_or_reject", "Approve or reject"),
    ("regulated_decision", "Make a regulated decision"),
)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    return slug or "draft-use-case"


def _record(case: dict[str, Any], level: str, as_of: str) -> dict[str, Any]:
    if level not in {"A0", "A1", "A2"}:
        raise ValueError("The skeleton generator accepts A0, A1, or A2 only.")
    title = case["title"]
    org = case["organisation"]["name"]
    description = case["data"]["description"]
    if signals_in_text(title):
        title = "Proposed agent"
    if signals_in_text(org):
        org = "Not copied"
    if signals_in_text(description):
        description = ""
    personal = case["data"]["personal_data"] or case["data"]["special_category"]
    never = [
        {
            "resource": "A channel that can send or publish",
            "reason": "This skeleton does not enable a send.",
        },
        {
            "resource": "A production system of record",
            "reason": "This skeleton does not enable a production write.",
        },
    ]
    if case["data"]["classification"] == "secret_or_above":
        never.append(
            {
                "resource": "Material recorded as secret or above",
                "reason": "This catalogue does not put that material into an agent.",
            }
        )
    risks = []
    recorded = case["risk"]["level"]
    if recorded in {"Low", "Medium", "High"}:
        band = recorded
    elif recorded == "high":
        band = "High"
    elif recorded == "low":
        band = "Low"
    else:
        band = "Medium"
    risks.append(
        {
            "id": "U1",
            "risk": "The draft is treated as a decision to build or as an approved manifest",
            "likelihood": band,
            "impact": "High",
            "residual_risk": "Medium",
        }
    )
    for key, label in _CONSEQUENTIAL:
        if case["actions"][key] or (key == "regulated_decision" and case["risk"]["significant_automated_decision"]):
            risks.append(
                {
                    "id": "U-" + key.replace("_", "-"),
                    "risk": label + " was asked for. The skeleton leaves it disabled.",
                    "likelihood": "Medium",
                    "impact": "High",
                    "residual_risk": "Medium",
                }
            )
    public = (
        "Draft manifest for a proposed agent. The architect has not confirmed a platform. "
        "The advisor has not deployed anything. "
        + (description or "No data description was copied.")
    )
    return {
        "inventory_id": _slug(case["case_id"]),
        "name": (title or "Proposed agent")[:100],
        "version": "0.0.1",
        "team": (org or "Not recorded")[:200],
        "contact_email": "architecture-draft@example.com",
        "experiment_path": "experiments/14-agent-architecture-advisor",
        "autonomy_level": level,
        "public_description": public,
        "source_reviewed_on": as_of,
        "special_category_data": "yes" if case["data"]["special_category"] else "no",
        "processes_personal_data": "yes" if personal else "no",
        "lawful_basis": (
            "Not chosen. A DPO confirms an Article 6 basis before processing."
            if personal
            else "No personal data was recorded. The architect confirms that is true."
        ),
        "data_reads": [
            {
                "resource": description or "Use case data described by the architect",
                "justification": "Copied from the structured use case. Not re-justified here.",
                "may_contain_personal_data": personal,
            }
        ],
        "never_access": never,
        "risk_rows": risks,
    }


def draft_skeleton(
    case: dict[str, Any],
    level: str,
    as_of: str,
    approve: bool = False,
) -> dict[str, Any]:
    if approve:
        return {
            "validation_passed": False,
            "approved": False,
            "may_be_relied_on": False,
            "autonomy_level": None,
            "errors": ["The permissions-manifest generator cannot mark a manifest approved."],
            "yaml": None,
        }
    if str(EXP03_SRC) not in sys.path:
        sys.path.insert(0, str(EXP03_SRC))
    from manifest_generator import generate_manifest

    record = _record(case, level, as_of)
    result = generate_manifest(record, as_of, approve=False)
    manifest = result.get("manifest") or {}
    autonomy = None
    if isinstance(manifest, dict):
        autonomy = (manifest.get("autonomy") or {}).get("level")
    if autonomy == "A3":
        return {
            "validation_passed": False,
            "approved": False,
            "may_be_relied_on": False,
            "autonomy_level": None,
            "errors": ["The skeleton came back as A3. It was discarded."],
            "yaml": None,
        }
    approved = False
    if isinstance(manifest, dict):
        approved = manifest.get("draft_control", {}).get("approved") is True
    return {
        "validation_passed": bool(result.get("validation_passed")) and not approved and autonomy in {"A0", "A1", "A2"},
        "approved": False,
        "may_be_relied_on": False,
        "autonomy_level": autonomy,
        "errors": list(result.get("errors") or []),
        "yaml": result.get("yaml"),
    }
