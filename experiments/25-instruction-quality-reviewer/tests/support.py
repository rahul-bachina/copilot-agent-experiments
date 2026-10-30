"""Shared loaders for the instruction-reviewer tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "instructions"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.review import review  # noqa: E402

AS_OF = "2026-10-30"
MANIFEST = {
    "tools": {
        "allowed": [{"tool": "read_policy_file"}],
        "writes": {"enabled": False},
        "sends": {"enabled": False},
    },
    "autonomy": {"level": "A0"},
    "human_approval": {
        "approval_points": [
            {"action": "Approve prompt changes", "approver": "Agent owner", "mandatory": True}
        ]
    },
}
USE_CASE = {
    "case_id": "halebridge-policy",
    "title": "Halebridge policy questions",
    "organisation": {
        "name": "Halebridge Borough Council",
        "sector": "local_authority",
        "licences": {
            "copilot_studio": "yes",
            "microsoft_365_copilot": "unknown",
            "power_automate": "unknown",
            "foundry": "unknown",
        },
    },
    "users": {"audience": "internal_staff", "channel": "teams"},
    "data": {
        "description": "Published staff policies",
        "personal_data": False,
        "classification": "official",
        "volume": "bounded",
        "residency": "uk",
    },
    "actions": {"read": True, "draft": True},
    "risk": {
        "level": "low",
        "requested_autonomy": "A0",
        "named_approver": True,
        "approver_role": "Agent owner",
    },
    "narrative": "Staff ask about published policies. A person still owns the answer.",
}


def text_of(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def bundle_for(name: str, *, manifest=MANIFEST, reviewed_on="2026-10-30", extra=None) -> dict:
    body = {
        "bundle_id": Path(name).stem,
        "title": Path(name).stem,
        "documents": [
            {
                "path": name,
                "kind": "system_prompt",
                "reviewed_on": reviewed_on,
                "text": text_of(name),
            }
        ],
    }
    if manifest is not None:
        body["manifest"] = manifest
    if extra:
        body.update(extra)
    return body


def run(name: str, **kwargs) -> dict:
    as_of = kwargs.pop("as_of", AS_OF)
    return review(bundle_for(name, **kwargs), as_of)


def safety(report: dict) -> None:
    assert report["label"] == "DRAFT FOR AGENT OWNER REVIEW"
    assert report["autonomy"] == "A0"
    assert report["catalogue_id"] == "G003"
    assert report["decision"] is None
    assert report["owner_approved"] is False
    assert report["diff_applied"] is False
    assert report["instructions_edited"] is False
    assert report["deployed"] is False
    assert report["actions_taken"] == []
    assert report["model_called"] is False
    assert report["network_called"] is False
    assert report["a3_recommended"] is False
    assert report["prompt_injection"]["followed"] is False
    assert report["proposed_diff"]["applied"] is False
    assert report["manifest_skeleton"]["approved"] is False
    assert report["architecture_cross_check"]["platform_selected"] is None
    assert report["architecture_cross_check"]["a3_recommended"] is False
    assert report["architecture_cross_check"]["deployed"] is False
    assert report["pins_reopened_for_this_experiment"] is False
    ids = [check["id"] for check in report["checks"]]
    assert ids == ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]


def result_map(report: dict) -> dict[str, str]:
    return {check["id"]: check["result"] for check in report["checks"]}


def dataset() -> list[dict]:
    path = ROOT / "eval" / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))
