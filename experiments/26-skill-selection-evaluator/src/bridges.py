"""Call Experiments 25, 14, and 03 without letting their module names clash.

Experiment 25 scores each skill file as an instruction bundle. Experiment 14
scores a structured use case when one was supplied and does not select a
platform. Experiment 03 drafts an unapproved manifest skeleton when none was
supplied. PyYAML and jsonschema are not installed by this experiment. When
they are missing, the stand-in from Experiment 25 is used. It still refuses
approval and still refuses autonomy A3.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

EXP25_SRC = Path(__file__).resolve().parents[2] / "25-instruction-quality-reviewer" / "src"

_CONFLICTS = (
    "architecture_bridge",
    "checklist",
    "diffing",
    "injection",
    "manifest_bridge",
    "manifest_yaml",
    "review",
    "sources",
)

_API: dict[str, Any] = {}


def instruction_review(skill_text: str, skill_path: str, reviewed_on: str | None, as_of: str, manifest: dict[str, Any] | None) -> dict[str, Any]:
    """One Experiment 25 reading of a skill file. The diff there is not applied."""
    review = _api()["review"]
    bundle: dict[str, Any] = {
        "bundle_id": Path(skill_path).stem or "skill",
        "title": Path(skill_path).stem or "skill",
        "documents": [
            {
                "path": skill_path,
                "kind": "skill",
                "text": skill_text,
            }
        ],
    }
    if reviewed_on:
        bundle["documents"][0]["reviewed_on"] = reviewed_on
    if manifest:
        bundle["manifest"] = manifest
    try:
        report = review(bundle, as_of)
    except Exception as exc:  # noqa: BLE001 — a review failure must not edit a skill
        return {
            "called": True,
            "experiment": "25",
            "path": skill_path,
            "error": f"{exc.__class__.__name__}: {exc}",
            "owner_approved": False,
            "diff_applied": False,
            "a3_recommended": False,
            "percent": None,
            "band": None,
            "blocking": [],
        }
    return {
        "called": True,
        "experiment": "25",
        "path": skill_path,
        "error": None,
        "owner_approved": False,
        "diff_applied": bool(report.get("diff_applied")),
        "instructions_edited": bool(report.get("instructions_edited")),
        "a3_recommended": bool(report.get("a3_recommended")),
        "percent": (report.get("score") or {}).get("percent"),
        "band": (report.get("score") or {}).get("band"),
        "blocking": list(report.get("blocking") or []),
        "do_not_rely": bool(report.get("do_not_rely")),
    }


def architecture_cross_check(use_case: dict[str, Any] | None) -> dict[str, Any]:
    if not use_case:
        return {
            "called": False,
            "experiment": "14",
            "reason": "No use case was supplied. Experiment 14 was not called.",
            "recommended_autonomy": None,
            "a3_recommended": False,
            "platform_selected": None,
            "any_option_selected": False,
            "deployed": False,
            "rules_fired": [],
            "work_shape": None,
        }
    cross_check = _api()["cross_check"]
    result = cross_check(use_case)
    result["platform_selected"] = None
    result["a3_recommended"] = False
    result["deployed"] = False
    return result


def manifest_skeleton(bundle_id: str, title: str, as_of: str, needed: bool) -> dict[str, Any]:
    if not needed:
        return {
            "generated": False,
            "experiment_03_called": False,
            "approved": False,
            "may_be_relied_on": False,
            "validation_passed": False,
            "autonomy_level": None,
            "yaml": None,
            "errors": [],
            "reason": "A manifest was supplied. Experiment 03 was not asked to replace it.",
        }
    draft = _api()["draft_skeleton"]
    skeleton = draft(
        bundle_id=bundle_id or "skill-catalogue",
        title=title or "Skill catalogue",
        as_of=as_of,
        autonomy_level="A0",
        approve=False,
    )
    skeleton["generated"] = True
    skeleton["approved"] = False
    skeleton["may_be_relied_on"] = False
    if skeleton.get("autonomy_level") == "A3":
        skeleton["yaml"] = None
        skeleton["autonomy_level"] = None
        skeleton["errors"] = list(skeleton.get("errors") or []) + [
            "Autonomy A3 was discarded. This catalogue does not keep it."
        ]
    return skeleton


def _api() -> dict[str, Any]:
    if _API:
        return _API
    saved = {name: sys.modules.pop(name) for name in _CONFLICTS if name in sys.modules}
    sys.path.insert(0, str(EXP25_SRC))
    try:
        review_mod = importlib.import_module("review")
        arch_mod = importlib.import_module("architecture_bridge")
        manifest_mod = importlib.import_module("manifest_bridge")
        _API["review"] = review_mod.review
        _API["cross_check"] = arch_mod.cross_check
        _API["draft_skeleton"] = manifest_mod.draft_skeleton
    finally:
        try:
            sys.path.remove(str(EXP25_SRC))
        except ValueError:
            pass
        for name in _CONFLICTS:
            sys.modules.pop(name, None)
        sys.modules.update(saved)
    return _API
