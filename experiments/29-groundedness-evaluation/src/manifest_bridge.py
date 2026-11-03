"""Ask Experiment 03 for an unapproved skeleton, or use a local stand-in.

The generator cannot mark a manifest approved. Autonomy A3 produces no
manifest. PyYAML and jsonschema are not part of this experiment's install.
When they are missing, the stand-in keeps the same refusals and does not
claim the schema was checked.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

EXP03_SRC = Path(__file__).resolve().parents[2] / "03-agent-inventory-atrs-assurance" / "src"


def draft_skeleton(
    *,
    bundle_id: str,
    title: str,
    as_of: str,
    autonomy_level: str,
    approve: bool = False,
) -> dict[str, Any]:
    if approve:
        return _refused(
            "An approve flag was passed. Experiment 03 was not called.",
            "The permissions-manifest generator cannot mark a manifest approved.",
        )
    if autonomy_level == "A3" or autonomy_level not in {"A0", "A1", "A2"}:
        return _refused(
            "The requested autonomy is not A0, A1, or A2.",
            "Autonomy A3 is not permitted in this catalogue. No manifest was drafted.",
        )
    try:
        if str(EXP03_SRC) not in sys.path:
            sys.path.insert(0, str(EXP03_SRC))
        from manifest_generator import generate_manifest
    except ImportError as exc:
        return _stand_in(
            autonomy_level,
            called=False,
            reason=(
                "Experiment 03 was not called. PyYAML and jsonschema are not installed "
                f"in this environment ({exc.__class__.__name__}: {exc}). "
                "The stand-in is not schema-validated."
            ),
        )
    record = _record(bundle_id, title, autonomy_level)
    try:
        result = generate_manifest(record, as_of, approve=False)
    except Exception as exc:  # noqa: BLE001 — a generator failure must not approve anything
        stand_in = _stand_in(
            autonomy_level,
            called=True,
            reason=(
                "Experiment 03 was called and raised "
                f"{exc.__class__.__name__}. The stand-in was used instead. {exc}"
            ),
        )
        stand_in["errors"] = [str(exc)]
        return stand_in
    manifest = result.get("manifest") if isinstance(result.get("manifest"), dict) else {}
    level = (manifest.get("autonomy") or {}).get("level")
    approved_flag = (manifest.get("draft_control") or {}).get("approved") is True
    if level == "A3" or approved_flag:
        return {
            "requested": True,
            "experiment_03_called": True,
            "generator": "experiment-03",
            "document_status": "draft",
            "approved": False,
            "may_be_relied_on": False,
            "validation_passed": False,
            "autonomy_level": None,
            "high_risk_actions_enabled": False,
            "yaml": None,
            "errors": ["The skeleton was discarded because it was approved or it was autonomy A3."],
            "reason": "Experiment 03 returned a skeleton this checker will not keep.",
        }
    return {
        "requested": True,
        "experiment_03_called": True,
        "generator": "experiment-03",
        "document_status": "draft",
        "approved": False,
        "may_be_relied_on": False,
        "validation_passed": bool(result.get("validation_passed")) and level in {"A0", "A1", "A2"},
        "autonomy_level": level,
        "high_risk_actions_enabled": False,
        "yaml": result.get("yaml"),
        "errors": list(result.get("errors") or []),
        "reason": "Experiment 03 drafted a skeleton. approved is false.",
    }


def not_requested() -> dict[str, Any]:
    return {
        "requested": False,
        "experiment_03_called": False,
        "generator": "not-requested",
        "document_status": "draft",
        "approved": False,
        "may_be_relied_on": False,
        "validation_passed": False,
        "autonomy_level": None,
        "high_risk_actions_enabled": False,
        "yaml": None,
        "errors": [],
        "reason": "No skeleton was requested.",
    }


def _refused(reason: str, error: str) -> dict[str, Any]:
    return {
        "requested": True,
        "experiment_03_called": False,
        "generator": "refused",
        "document_status": "draft",
        "approved": False,
        "may_be_relied_on": False,
        "validation_passed": False,
        "autonomy_level": None,
        "high_risk_actions_enabled": False,
        "yaml": None,
        "errors": [error],
        "reason": reason,
    }


def _stand_in(level: str, called: bool, reason: str) -> dict[str, Any]:
    return {
        "requested": True,
        "experiment_03_called": called,
        "generator": "local-stand-in" if not called else "experiment-03",
        "document_status": "draft",
        "approved": False,
        "may_be_relied_on": False,
        "validation_passed": False,
        "autonomy_level": level,
        "high_risk_actions_enabled": False,
        "yaml": None,
        "errors": [],
        "reason": reason,
    }


def _record(bundle_id: str, title: str, level: str) -> dict[str, Any]:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in bundle_id).strip("-") or "draft"
    return {
        "inventory_id": slug[:80],
        "name": (title or "Groundedness evaluation")[:100],
        "version": "0.0.1",
        "team": "Not recorded",
        "contact_email": "groundedness-evaluation@example.com",
        "experiment_path": "experiments/29-groundedness-evaluation",
        "autonomy_level": level,
        "public_description": (
            "Draft manifest skeleton for a groundedness report. The evaluation "
            "owner has not approved the thresholds and has not recorded a release."
        ),
        "source_reviewed_on": "2026-11-03",
        "special_category_data": "no",
        "processes_personal_data": "no",
        "lawful_basis": "Not chosen. A DPO confirms an Article 6 basis before processing.",
        "data_reads": [
            {
                "resource": "Synthetic Q&A bundle supplied for this draft",
                "justification": "The skeleton records the read. It does not copy the answers.",
                "may_contain_personal_data": False,
            }
        ],
        "never_access": [
            {
                "resource": "A Microsoft Foundry evaluation deployment",
                "reason": "This skeleton does not call the groundedness evaluator.",
            },
            {
                "resource": "A production system of record",
                "reason": "This skeleton does not enable a production write.",
            },
        ],
        "risk_rows": [
            {
                "id": "U1",
                "risk": "The draft is treated as an approved manifest or a release decision",
                "likelihood": "Medium",
                "impact": "High",
                "residual_risk": "Medium",
            }
        ],
    }
