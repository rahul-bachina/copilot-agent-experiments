"""Call Experiment 08 and Experiment 12. Do not copy their rules.

Experiment 08 counts UK identifiers. The matched values are not stored.
Experiment 12 inventories rough notes. It does not accept them into a queue
or write a record. This starter does not copy either module's detectors.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]
CALLER = "exp-85-visit-notes-case-record"

_COLLIDING = (
    "sources",
    "injection",
    "cues",
    "mask",
    "marking",
    "negate",
    "dates",
    "catalogue",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "intake",
    "notes",
    "concerns",
    "grounding",
    "paraphrases",
    "siblings",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load_loose(folder: str, filename: str, module_name: str):
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
            raise NeighbourMissing(folder)
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


def neighbours() -> dict:
    if "bundle" in _cache:
        return _cache["bundle"]  # type: ignore[return-value]
    gateway = _load_loose("08-uk-pii-redaction-gateway", "gateway.py", "exp08_gateway_for_uk13")
    intake = _load_loose("12-document-intake", "intake.py", "exp12_intake_for_uk13")
    bundle = {"propose": gateway.propose, "intake": intake.intake}
    _cache["bundle"] = bundle
    return bundle


def identifier_counts(text: str, *, on: date) -> dict:
    proposal = neighbours()["propose"](
        text,
        caller=CALLER,
        now=datetime(on.year, on.month, on.day),
        rules_as_of=on,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 reported anonymised output. This starter will not use it.")
    types: list[str] = []
    count = 0
    spans: list[tuple[int, int, str]] = []
    for finding in (proposal.get("audit_log") or {}).get("findings") or []:
        if not finding.get("applied"):
            continue
        count += 1
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
        start = finding.get("start")
        end = finding.get("end")
        placeholder = finding.get("placeholder") or "[identifier]"
        if isinstance(start, int) and isinstance(end, int):
            spans.append((start, end, str(placeholder)))
    redacted = text
    for start, end, placeholder in sorted(spans, key=lambda item: item[0], reverse=True):
        if 0 <= start < end <= len(redacted):
            redacted = redacted[:start] + placeholder + redacted[end:]
    return {
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "count": count,
        "types": types,
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
        "masked": redacted,
    }


def inventory_rough_notes(text: str, *, visit_id: str, document_date: str | None, on: date) -> dict:
    """Ask Experiment 12 to inventory the note. The content is not stored from its reply."""

    batch = {
        "synthetic": True,
        "batch_id": visit_id if visit_id else "rough-notes",
        "files": [
            {
                "file_id": "rough-notes",
                "filename": "rough-notes.txt",
                "media_type": "text/plain",
                "content": text,
            }
        ],
    }
    if document_date:
        batch["files"][0]["document_date"] = document_date
    draft = neighbours()["intake"](batch, as_of=on)
    files = draft.get("files") or [{}]
    row = files[0] if files else {}
    flags = draft.get("flags") or {}
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "read_status": row.get("read_status"),
        "date_status": row.get("date_status"),
        "injection_scanned": row.get("injection_scanned"),
        "content_recorded": False,
        "accepted_into_queue": flags.get("accepted_into_queue"),
        "production_record_written": flags.get("production_record_written"),
        "class_applied": False,
    }
