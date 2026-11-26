"""Call Experiment 74's digest and Experiment 18's evidence index.

The pack hash is Experiment 74's digest of this pack's own projection.
paper_hash is not called: a board-paper projection would drop the approval
fields this pack has to bind. Experiment 18 build_pack is called for an
evidence sha256. That call does not approve an export, and its body is not
copied. Experiment 08 propose is called for a UK-identifier count. The
redacted text is not copied, and reversible stays false.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "cues",
    "mask",
    "marking",
    "negate",
    "dates",
    "sample",
    "reuse",
    "testing",
    "paraphrases",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "intake",
    "checklist",
    "diffing",
    "normalise",
    "prohibited",
    "yaml_reader",
    "statements",
    "library",
    "mapping",
    "match",
    "declaration",
    "pack",
    "pack_injection",
    "checks",
    "coordinator",
    "evidence",
    "routing",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load(folder: str, filename: str, module_name: str):
    if module_name in _cache:
        return _cache[module_name]
    saved = {name: sys.modules.get(name) for name in _COLLIDING}
    saved_path = list(sys.path)
    src = EXPERIMENTS / folder / "src"
    path = src / filename
    if not path.is_file():
        raise NeighbourMissing(folder)
    sys.path.insert(0, str(src))
    try:
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(module_name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved_path
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        for name, saved_module in saved.items():
            if saved_module is not None:
                sys.modules[name] = saved_module
    _cache[module_name] = module
    return module


def digest(payload: dict) -> str:
    """Canonical SHA-256 from Experiment 74. This file does not reimplement it."""

    module = _load(
        "74-board-governance-pack",
        "checks.py",
        "exp74_checks_for_approval_pack",
    )
    if not hasattr(module, "digest"):
        raise NeighbourMissing("74-board-governance-pack")
    return module.digest(payload)


def build_evidence_index():
    module = _load(
        "18-evidence-pack-builder",
        "pack.py",
        "exp18_pack_for_approval_pack",
    )
    if not hasattr(module, "build_pack"):
        raise NeighbourMissing("18-evidence-pack-builder")
    return module.build_pack


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_approval_pack",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def neighbour_hashes(items: list[dict], *, on: date) -> dict:
    """Ask Experiment 18 for an sha256 per item. Do not copy bodies or approve."""

    base = {
        "called": False,
        "experiment_id": "exp-18-evidence-pack-builder",
        "pack_type": "audit_request",
        "decides_approval": False,
        "export_approved": None,
        "bodies_copied": False,
        "item_sha256": {},
        "reason": None,
        "capped": False,
    }
    files = []
    for item in items:
        evidence_id = item.get("evidence_id")
        content = item.get("content")
        if not isinstance(evidence_id, str) or not isinstance(content, str):
            continue
        if any(row["item_id"] == evidence_id for row in files):
            continue
        row = {
            "item_id": evidence_id,
            "title": str(item.get("title") or evidence_id)[:120],
            "source": "synthetic-evidence",
            "source_scope": "audit_workpapers",
            "media_type": "text/plain",
            "content": content[:20000],
        }
        if isinstance(item.get("document_date"), str):
            row["document_date"] = item["document_date"]
        files.append(row)
        if len(files) >= 12:
            base["capped"] = True
            break
    if not files:
        base["reason"] = "no_items"
        return base
    saved_path = list(sys.path)
    saved_modules = {name: sys.modules.get(name) for name in _COLLIDING}
    try:
        draft = build_evidence_index()(
            {"synthetic": True, "request_id": "exp-81-evidence", "items": files},
            as_of=on,
            pack_type="audit_request",
            authorised_scopes=["audit_workpapers"],
            search_from=date(on.year - 1, on.month, on.day) if on.month != 2 or on.day != 29 else date(on.year - 1, 2, 28),
            search_to=on,
        )
    except (OSError, ValueError, TypeError, RuntimeError, ImportError) as exc:
        base["reason"] = type(exc).__name__
        return base
    finally:
        sys.path[:] = saved_path
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        for name, saved in saved_modules.items():
            if saved is not None:
                sys.modules[name] = saved
    if draft.get("export_approved") is not False:
        base["reason"] = "neighbour_reported_an_export_approval"
        base["called"] = True
        base["export_approved"] = draft.get("export_approved")
        return base
    sha = {}
    for row in draft.get("items") or []:
        if isinstance(row, dict) and isinstance(row.get("item_id"), str) and isinstance(row.get("sha256"), str):
            sha[row["item_id"]] = row["sha256"]
    base.update(
        {
            "called": True,
            "reason": None,
            "export_approved": False,
            "item_sha256": sha,
            "item_count": len(sha),
        }
    )
    return base


def identifier_counts(text: str, *, on: date) -> dict:
    base = {
        "called": False,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "count": 0,
        "types": [],
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
        "reason": None,
    }
    if not text:
        base["reason"] = "no_text"
        return base
    try:
        proposal = propose()(
            text[:8000],
            caller="exp-81-approval-pack-coordinator",
            now=datetime(on.year, on.month, on.day),
            rules_as_of=on,
            apply_model_suggestions=False,
            reversible=False,
        )
    except (OSError, ValueError, TypeError, RuntimeError, ImportError) as exc:
        base["reason"] = type(exc).__name__
        return base
    if proposal.get("anonymisation", {}).get("output_is_anonymised") is not False and proposal.get("output_is_anonymised") is not False:
        # Experiment 08 keeps output_is_anonymised false. If a future copy does not, do not use it.
        if (proposal.get("anonymisation") or {}).get("output_is_anonymised") is True or proposal.get("output_is_anonymised") is True:
            base["reason"] = "neighbour_reported_anonymised_output"
            return base
    types: list[str] = []
    count = 0
    findings = (proposal.get("audit_log") or {}).get("findings") or []
    for finding in findings:
        if not isinstance(finding, dict) or not finding.get("applied"):
            continue
        count += 1
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
    base.update({"called": True, "count": count, "types": types})
    return base
