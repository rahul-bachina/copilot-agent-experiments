"""Shared loaders for the tool-contract reviewer tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "fixtures" / "contracts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.review import review  # noqa: E402

AS_OF = "2026-11-02"
MANIFEST = {
    "tools": {
        "allowed": [{"tool": "getCase"}],
        "writes": {"enabled": False},
        "sends": {"enabled": False},
    },
    "autonomy": {"level": "A0"},
    "high_risk_actions": {
        "production_record_change": {"enabled": False},
        "external_send": {"enabled": False},
    },
}
USE_CASE = {
    "case_id": "halebridge-case-read",
    "title": "Read one housing case identifier",
    "organisation": {
        "name": "Halebridge Borough Council",
        "sector": "local_authority",
        "licences": {"copilot_studio": "yes", "foundry": "unknown"},
    },
    "users": {"audience": "internal_staff", "channel": "teams"},
    "data": {
        "description": "One synthetic case identifier and a status",
        "classification": "official",
        "volume": "bounded",
        "residency": "uk",
    },
    "actions": {"read": True, "draft": True},
    "risk": {
        "requested_autonomy": "A0",
        "named_approver": True,
        "approver_role": "Security/API owner",
    },
    "narrative": "A housing officer reads one case status. A person still owns the case.",
}


def contract(name: str) -> dict:
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def bundle_for(name: str, *, manifest=MANIFEST, reviewed_on="2026-11-02", kind=None, extra=None) -> dict:
    body = {
        "bundle_id": Path(name).stem,
        "title": Path(name).stem,
        "reviewed_on": reviewed_on,
        "contract": contract(name),
    }
    if kind:
        body["contract_kind"] = kind
    if manifest is not None:
        body["manifest"] = manifest
    if extra:
        body.update(extra)
    return body


def run(name: str, **kwargs) -> dict:
    as_of = kwargs.pop("as_of", AS_OF)
    return review(bundle_for(name, **kwargs), as_of)


def safety(report: dict) -> None:
    assert report["label"] == "DRAFT FOR SECURITY/API OWNER REVIEW"
    assert report["autonomy"] == "A0"
    assert report["catalogue_id"] == "G005"
    assert report["decision"] is None
    assert report["owner_approved"] is False
    assert report["contract_approved"] is False
    assert report["diff_applied"] is False
    assert report["contract_modified"] is False
    assert report["policy_published"] is False
    assert report["deployed"] is False
    assert report["actions_taken"] == []
    assert report["model_called"] is False
    assert report["network_called"] is False
    assert report["a3_recommended"] is False
    assert report["prompt_injection"]["followed"] is False
    assert report["proposed_diff"]["applied"] is False
    assert report["proposed_diff"]["published"] is False
    assert report["manifest_skeleton"]["approved"] is False
    assert report["architecture_cross_check"]["platform_selected"] is None
    assert report["architecture_cross_check"]["a3_recommended"] is False
    assert report["architecture_cross_check"]["deployed"] is False
    assert report["instruction_review"]["owner_approved"] is False
    assert report["instruction_review"]["diff_applied"] is False
    assert report["instruction_review"]["a3_recommended"] is False
    assert report["instruction_review"]["followed"] is False
    ids = [check["id"] for check in report["checks"]]
    assert ids == ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]


def result_map(report: dict) -> dict[str, str]:
    return {check["id"]: check["result"] for check in report["checks"]}
