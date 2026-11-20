"""Call Experiments 04, 08, 12, and 20 without sharing their module names.

Experiment 04 supplies pinned FCA page currency. Experiment 12 inventories
the notice and does not confirm the file. Experiment 20 supplies pinned
complaints quotations. Experiment 08 masks UK identifiers. None of them
decides that a change applies.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "currency",
    "dates",
    "injection",
    "cues",
    "mask",
    "marking",
    "match",
    "briefing",
    "reuse",
    "register",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "catalogue",
    "intake",
    "checklist",
    "classify",
    "figures",
    "narratives",
    "report",
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


def fca_modules():
    currency = _load(
        "04-fca-cryptoasset-readiness",
        "currency.py",
        "exp04_currency_for_change_briefing",
    )
    sources = _load(
        "04-fca-cryptoasset-readiness",
        "sources.py",
        "exp04_sources_for_change_briefing",
    )
    if not hasattr(currency, "assess_source") or not hasattr(sources, "source_by_id"):
        raise NeighbourMissing("04-fca-cryptoasset-readiness")
    return currency, sources


def intake_module():
    module = _load(
        "12-document-intake",
        "intake.py",
        "exp12_intake_for_change_briefing",
    )
    if not hasattr(module, "intake"):
        raise NeighbourMissing("12-document-intake")
    return module


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_change_briefing",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def mi_sources():
    module = _load(
        "20-complaints-root-cause-mi",
        "sources.py",
        "exp20_sources_for_change_briefing",
    )
    if not hasattr(module, "PRIN_2A_9_11"):
        raise NeighbourMissing("20-complaints-root-cause-mi")
    return module


def assess_fca_source(source_id: str, as_of: date) -> dict:
    def _run():
        currency, sources = fca_modules()
        catalogue = sources.source_by_id()
        if source_id not in catalogue:
            return {"source_id": source_id, "status": "not found", "applies": None}
        row = currency.assess_source(
            catalogue[source_id],
            as_of,
            sources.DEFAULT_STALE_AFTER_DAYS,
        )
        row["status"] = "pinned"
        row["applies"] = None
        row["stale_after_days_source"] = (
            "Experiment 04 DEFAULT_STALE_AFTER_DAYS. Not a statute."
        )
        row["note"] = (
            "Pinned FCA page from Experiment 04. Not a decision that this change applies."
        )
        return row

    return _isolated(_run)


def snapshot_currency(published: str | None, as_of: date) -> dict:
    def _run():
        currency, sources = fca_modules()
        try:
            row = currency.assess_document_date(
                published,
                as_of,
                sources.DEFAULT_STALE_AFTER_DAYS,
            )
        except ValueError:
            return {
                "document_date": None,
                "age_days": None,
                "stale_after_days": sources.DEFAULT_STALE_AFTER_DAYS,
                "currency": "unparseable",
                "coerced": False,
            }
        row["coerced"] = False
        row["rule"] = (
            "The publication date is compared with Experiment 04's source "
            "threshold. That threshold is this starter's rule for a snapshot. "
            "It is not a statute."
        )
        return row

    return _isolated(_run)


def redact_uk_identifiers(text: str, *, rules_as_of: date | None) -> dict:
    def _run():
        return propose()(
            text,
            caller="exp-68-regulatory-change-briefing",
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


def intake_notice(text: str, *, notice_id: str, document_date: str | None, as_of: date) -> dict:
    module = intake_module()
    file_row: dict = {
        "file_id": "notice",
        "filename": "synthetic-notice.txt",
        "media_type": "text/plain",
        "content": text,
    }
    if document_date:
        file_row["document_date"] = document_date
    batch = {
        "synthetic": True,
        "batch_id": (notice_id or "unspecified")[:80],
        "files": [file_row],
    }

    def _run():
        return module.intake(batch, as_of=as_of, rules_as_of=as_of)

    draft = _isolated(_run)
    files = draft.get("files") or []
    first = files[0] if files else {}
    injection = draft.get("prompt_injection") or {}
    return {
        "called": True,
        "experiment_id": draft.get("experiment_id"),
        "files_confirmed": False,
        "purpose_confirmed": False,
        "handed_off": False,
        "read_status": first.get("read_status"),
        "date_status": first.get("date_status"),
        "injection_detected": bool(injection.get("detected")),
        "catalogue_stale": bool(draft.get("catalogue_stale")),
        "content_recorded": False,
        "output_is_anonymised": False,
        "agent_may_release": False,
    }


def mi_context(kind: str | None, as_of: date) -> dict | None:
    """Pinned Experiment 20 quotations. They are not a finding of applicability."""

    if kind not in {"complaints", "housing", "energy"}:
        return None

    def _run():
        sources = mi_sources()
        currency, fca_sources = fca_modules()
        pinned = sources.SOURCES_PINNED_ON.isoformat()
        currency_row = currency.assess_document_date(
            pinned,
            as_of,
            fca_sources.DEFAULT_STALE_AFTER_DAYS,
        )
        rows = {
            "complaints": [
                {
                    "id": "PRIN_2A_9_11",
                    "quote": sources.PRIN_2A_9_11,
                    "url": sources.PRIN_2A_9_URL,
                }
            ],
            "housing": [
                {
                    "id": "CODE_9_4",
                    "quote": sources.CODE_9_4,
                    "url": sources.CODE_SUBMISSIONS_URL,
                }
            ],
            "energy": [
                {
                    "id": "CHR_REG_11",
                    "quote": sources.CHR_REG_11,
                    "url": sources.CHR_REG_11_URL,
                }
            ],
        }
        return {
            "experiment": "20-complaints-root-cause-mi",
            "kind": kind,
            "pinned_on": pinned,
            "currency": currency_row,
            "applies": None,
            "note": (
                "Pinned quotation from Experiment 20. Not a finding that this "
                "change applies. Not a regulatory return."
            ),
            "quotations": rows[kind],
        }

    return _isolated(_run)
