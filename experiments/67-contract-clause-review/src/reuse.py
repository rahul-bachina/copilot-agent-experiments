"""Call Experiments 08, 12, and 27 under private module names.

Experiment 27 review() is not called. A legal contract is not a tool contract.
The helpers reused from that experiment are strip_prohibited and signals_in_text.
Experiment 12 intake() does not confirm the file. Experiment 08 propose() does
not return a reversible vault. Redacted values are not stored by this module.
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
    "review",
    "reuse",
    "clauses",
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
    "architecture_bridge",
    "instruction_bridge",
    "manifest_bridge",
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


def _isolated(function):
    saved_path = list(sys.path)
    saved_modules = dict(sys.modules)
    try:
        return function()
    finally:
        sys.path[:] = saved_path
        extra = [name for name in list(sys.modules) if name not in saved_modules]
        for name in extra:
            sys.modules.pop(name, None)
        for name, module in saved_modules.items():
            sys.modules[name] = module


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_clause_review",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def intake_module():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_clause_review",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module


def tool_contract_injection():
    module = _load(
        "27-tool-contract-review",
        "injection.py",
        "exp27_injection_for_clause_review",
    )
    if not hasattr(module, "strip_prohibited") or not hasattr(module, "signals_in_text"):
        raise NeighbourMissing("27-tool-contract-review")
    return module


def redact_uk_identifiers(text: str, *, rules_as_of: date | None) -> dict:
    """Types and a redacted body. The banner and the matched values are not returned."""

    def _run():
        return propose()(
            text,
            caller="exp-67-contract-clause-review",
            now=datetime(rules_as_of.year, rules_as_of.month, rules_as_of.day) if rules_as_of else None,
            rules_as_of=rules_as_of,
            apply_model_suggestions=False,
            reversible=False,
        )

    proposal = _isolated(_run)
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 reported anonymised output. This starter will not use it.")
    redacted = str(proposal.get("redacted_text") or "")
    banner, _sep, body = redacted.partition("\n")
    shown = body if banner.startswith("[REDACTION PROPOSAL") else redacted
    types: list[str] = []
    count = 0
    for finding in (proposal.get("audit_log") or {}).get("findings") or []:
        if not finding.get("applied"):
            continue
        count += 1
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
    return {
        "text": shown,
        "types": types,
        "count": count,
        "output_is_anonymised": False,
        "values_stored": False,
        "rules_stale": bool((proposal.get("audit_log") or {}).get("rules_stale")),
        "rules_pinned_on": (proposal.get("audit_log") or {}).get("rules_pinned_on"),
    }


def strip_request(payload: dict) -> tuple[dict, list[str]]:
    module = tool_contract_injection()
    cleaned, ignored = module.strip_prohibited(payload)
    if not isinstance(cleaned, dict):
        raise ValueError("request must be an object")
    return cleaned, list(ignored)


def tool_contract_signals(text: str) -> list[str]:
    module = tool_contract_injection()
    found = module.signals_in_text(text)
    return list(found) if isinstance(found, list) else []


def intake_contract(text: str, *, contract_id: str, document_date: str | None, as_of: date) -> dict:
    """Inventory the text. Confirmation flags are forced false."""

    module = intake_module()
    file_row: dict = {
        "file_id": "contract",
        "filename": "synthetic-contract.txt",
        "media_type": "text/plain",
        "content": text,
    }
    if document_date:
        file_row["document_date"] = document_date
    batch = {
        "synthetic": True,
        "batch_id": contract_id[:80] or "unspecified",
        "files": [file_row],
    }

    def _run():
        return module.intake(batch, as_of=as_of, rules_as_of=as_of)

    draft = _isolated(_run)
    files = draft.get("files") or []
    first = files[0] if files else {}
    pii = first.get("pii") or {}
    injection = draft.get("prompt_injection") or {}
    return {
        "called": True,
        "experiment_id": draft.get("experiment_id"),
        "label": draft.get("label"),
        "files_confirmed": False,
        "purpose_confirmed": False,
        "handed_off": False,
        "read_status": first.get("read_status"),
        "date_status": first.get("date_status"),
        "injection_detected": bool(injection.get("detected")),
        "pii_finding_count": pii.get("finding_count"),
        "pii_types": list(pii.get("entity_types") or []),
        "catalogue_stale": bool(draft.get("catalogue_stale")),
        "content_recorded": False,
        "output_is_anonymised": False,
        "agent_may_release": False,
    }
