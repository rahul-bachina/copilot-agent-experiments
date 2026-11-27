"""Call Experiment 02 and Experiment 08. Do not copy their rules.

Experiment 02's injection list is called and then checked with this
starter's negation window. Its DISP clock is not applied. Energy and water
complaints are not DISP complaints.

Experiment 08 counts UK identifiers. The matched values are not stored.

Experiment 13's council triage is not called. A bill question is not a
council catalogue match. The handover record uses the same fields.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    from negate import affirmed
else:
    from .negate import affirmed

EXPERIMENTS = Path(__file__).resolve().parents[2]
CALLER = "exp-84-energy-water-customer-agent"

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
    "customer",
    "siblings",
    "paraphrases",
    "amounts",
    "fairness",
    "intake",
    "disp_clock",
    "front_door",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load_loose(folder: str, filename: str, module_name: str):
    if module_name in _cache:
        return _cache[module_name]
    saved = {name: sys.modules.get(name) for name in _COLLIDING}
    saved_path = list(sys.path)
    path = EXPERIMENTS / folder / "src" / filename
    if not path.is_file():
        raise NeighbourMissing(folder)
    sys.path.insert(0, str(path.parent))
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


def complaint_signals(text: str) -> dict:
    """Call Experiment 02. Do not apply a DISP clock or a DISP route."""

    module = _load_loose(
        "02-consumer-duty-complaint-intake",
        "intake.py",
        "exp02_intake_for_uk12",
    )
    raw = list(module.detect_injection(text or ""))
    view = module.analyse(text or "")
    affirmed_signals = [phrase for phrase in raw if affirmed(text or "", phrase)]
    return {
        "called": True,
        "experiment_id": "exp-02-consumer-duty-complaint-intake",
        "detect_injection_called": True,
        "analyse_called": True,
        "intake_called": False,
        "disp_clock_applied": False,
        "disp_route_applied": False,
        "disp_meets": bool(view.get("meets")),
        "injection_signals_affirmed": affirmed_signals,
        "quotes_stored": False,
    }


def identifier_counts(text: str, *, on: date) -> dict:
    gateway = _load_loose(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_uk12",
    )
    proposal = gateway.propose(
        text or "",
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
    for finding in (proposal.get("audit_log") or {}).get("findings") or []:
        if not finding.get("applied"):
            continue
        count += 1
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
    return {
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
        "count": count,
        "types": types,
        "output_is_anonymised": False,
        "values_stored": False,
        "redacted_text_copied": False,
        "described_as_anonymised": False,
    }
