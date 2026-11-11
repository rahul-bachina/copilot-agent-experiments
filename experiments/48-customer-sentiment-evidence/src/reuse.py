"""Load Experiment 07, Experiment 08, and Experiment 20. Do not copy them.

Paths are put on ``sys.path`` only while a sibling module is imported, then
restored. A missing folder is an error. This starter does not carry a second copy.
"""

from __future__ import annotations

import importlib
import sys
from datetime import datetime
from pathlib import Path

CALLER = "exp-48-customer-sentiment-evidence"

_propose = None
_cluster = None
_wilson = None
_round6 = None
_classify = None


def _experiments_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _src(folder: str) -> Path:
    src = _experiments_root() / folder / "src"
    if not src.is_dir():
        raise RuntimeError(
            f"{folder} is required beside this experiment. "
            "This starter does not carry its own copy."
        )
    return src


def _import_sibling(folder: str, module_name: str):
    """Import ``module_name`` from a sibling ``src`` without keeping that name."""

    src = _src(folder)
    src_s = str(src)
    saved_path = list(sys.path)
    saved = sys.modules.get(module_name)
    sys.path.insert(0, src_s)
    sys.modules.pop(module_name, None)
    try:
        module = importlib.import_module(module_name)
    finally:
        sys.path[:] = saved_path
        if saved is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = saved
    return module


def propose():
    global _propose
    if _propose is None:
        _propose = _import_sibling("08-uk-pii-redaction-gateway", "gateway").propose
    return _propose


def cluster_responses():
    global _cluster
    if _cluster is None:
        _cluster = _import_sibling("07-consultation-themes", "clusters").cluster_responses
    return _cluster


def wilson_interval():
    global _wilson, _round6
    if _wilson is None:
        stats = _import_sibling("07-consultation-themes", "stats")
        _wilson = stats.wilson_interval
        _round6 = stats.round6
    return _wilson


def round6(value: float) -> float:
    wilson_interval()
    return _round6(value)


def classify_financial(text: str) -> dict:
    """Experiment 20 ``classify`` for one financial-services complaint.

    Experiment 20's ``classify`` imports its own ``reuse`` module. That name
    is restored afterwards so this file stays the ``reuse`` callers imported.
    """

    global _classify
    if _classify is None:
        src = _src("20-complaints-root-cause-mi")
        saved_path = list(sys.path)
        saved = {name: sys.modules.get(name) for name in ("reuse", "classify")}
        sys.path.insert(0, str(src))
        sys.modules.pop("reuse", None)
        sys.modules.pop("classify", None)
        try:
            module = importlib.import_module("classify")
            _classify = module.classify
        finally:
            sys.path[:] = saved_path
            for name, previous in saved.items():
                if previous is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = previous
    return _classify("financial_services", text, {})


def redact(text: str, *, now: datetime) -> dict:
    """Propose identifier redactions. Do not keep a reversible map or a model span."""

    proposal = propose()(
        text,
        caller=CALLER,
        now=now,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 returned an anonymisation claim")
    if proposal["release"]["agent_may_release"] is not False:
        raise RuntimeError("Experiment 08 returned a release")
    redacted = proposal["redacted_text"]
    body = redacted.split("\n", 1)[1] if "\n" in redacted else redacted
    findings = proposal["audit_log"]["findings"]
    types = sorted({item["entity_type"] for item in findings if item.get("applied", True)})
    return {
        "text": body,
        "finding_count": len(findings),
        "entity_types": types,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "reversible_requested": False,
        "model_suggestions_applied": False,
    }
