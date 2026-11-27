"""Call Experiment 08 and Experiment 12. Do not copy their detector rules.

Experiment 01 is not called. Its triage path can call a model.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]
CALLER = "exp-83-subject-access-request-assistant"

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
    "sar",
    "siblings",
    "paraphrases",
    "deadline",
    "exemptions",
    "redact",
    "foi",
    "intake",
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


def _gateway():
    return _load_loose("08-uk-pii-redaction-gateway", "gateway.py", "exp08_gateway_for_uk11")


def _intake():
    return _load_loose("12-document-intake", "intake.py", "exp12_intake_for_uk11")


def identifier_spans(text: str, *, on: date) -> list[tuple[int, int, str]]:
    proposal = _gateway().propose(
        text,
        caller=CALLER,
        now=datetime(on.year, on.month, on.day),
        rules_as_of=on,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 reported anonymised output. This starter will not use it.")
    spans = []
    for finding in (proposal.get("audit_log") or {}).get("findings") or []:
        if not finding.get("applied"):
            continue
        start = finding.get("start")
        end = finding.get("end")
        placeholder = finding.get("placeholder") or "[uk identifier]"
        if isinstance(start, int) and isinstance(end, int):
            spans.append((start, end, str(placeholder)))
    return spans


def intake_summary(files: list[dict], *, on: date) -> dict:
    """Inventory the batch. Confirmation flags from Experiment 12 stay false."""

    if not files:
        return {
            "called": False,
            "reason": "no_files",
            "files_confirmed": False,
            "handed_off": False,
            "output_is_anonymised": False,
        }
    if len(files) > 12:
        return {
            "called": False,
            "reason": "above_intake_file_cap",
            "files_confirmed": False,
            "handed_off": False,
            "output_is_anonymised": False,
        }
    module = _intake()
    batch = {
        "synthetic": True,
        "batch_id": "sar-intake",
        "requested_purpose": "sar_bundle",
        "files": files,
    }
    try:
        draft = module.intake(batch, as_of=on)
    except (TypeError, ValueError) as exc:
        return {
            "called": False,
            "reason": type(exc).__name__,
            "files_confirmed": False,
            "handed_off": False,
            "output_is_anonymised": False,
        }
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "reason": None,
        "files_confirmed": draft.get("files_confirmed") is True,
        "purpose_confirmed": draft.get("purpose_confirmed") is True,
        "handed_off": (draft.get("routing") or {}).get("handed_off") is True,
        "file_count": len(draft.get("files") or []),
        "output_is_anonymised": False,
        "content_recorded_by_intake": False,
    }
