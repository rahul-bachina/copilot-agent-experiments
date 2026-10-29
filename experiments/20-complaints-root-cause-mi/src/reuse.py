"""Load Experiment 02 analyse() and Experiment 08 propose() from this repo.

This folder does not copy either implementation.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

CALLER = "exp-20-complaints-root-cause-mi"

_analyse = None
_propose = None


def _experiments_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_module(folder: str, filename: str, unique_name: str):
    src = _experiments_root() / folder / "src"
    if not src.is_dir():
        raise RuntimeError(
            f"{folder} is required beside this experiment. "
            "This starter does not carry its own copy."
        )
    inserted = str(src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    # Drop a previously imported module of the same file name from another experiment.
    sys.modules.pop(filename[:-3], None)
    module = importlib.import_module(filename[:-3])
    sys.modules[unique_name] = module
    return module


def analyse():
    """Experiment 02's lexicon. Not a second copy of the phrases."""

    global _analyse
    if _analyse is None:
        module = _load_module(
            "02-consumer-duty-complaint-intake",
            "intake.py",
            "exp02_intake",
        )
        _analyse = module.analyse
    return _analyse


def propose():
    """Experiment 08's gateway. Model suggestions stay off at the call site."""

    global _propose
    if _propose is None:
        module = _load_module(
            "08-uk-pii-redaction-gateway",
            "gateway.py",
            "exp08_gateway",
        )
        _propose = module.propose
    return _propose


def redact(text: str, *, now) -> dict:
    """Propose redactions. Do not request a reversible map or a model span."""

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
    audit = proposal["audit_log"]
    return {
        "text": body,
        "finding_count": len(audit["findings"]),
        "input_sha256": audit["input_sha256"],
        "output_is_anonymised": False,
        "agent_may_release": False,
        "reversible_requested": False,
        "model_suggestions_applied": False,
    }
