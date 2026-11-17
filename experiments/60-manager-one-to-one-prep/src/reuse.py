"""Call Experiments 08, 15, 41, and 51 without copying their decisions.

Neighbour modules share names. Each one is loaded under a private module
name, and the previous bindings are put back afterwards. Text returned by a
neighbour is not stored by this module.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "injection",
    "citations",
    "phrases",
    "model_boundary",
    "gateway",
    "scan",
    "extract",
    "sources",
    "marking",
    "mask",
    "concerns",
    "summarise",
)

_scan = None
_check_sentence = None
_index_events = None
_extract_message = None
_propose = None


class NeighbourMissing(RuntimeError):
    """A required experiment folder is not beside this one."""


def _load(folder: str, filename: str, module_name: str):
    saved = {name: sys.modules[name] for name in _COLLIDING if name in sys.modules}
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
        while str(src) in sys.path:
            sys.path.remove(str(src))
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        sys.modules.update(saved)
    return module


def _load_package_file(folder: str, package_name: str, filename: str):
    src = EXPERIMENTS / folder / "src"
    init = src / "__init__.py"
    if not init.is_file():
        raise NeighbourMissing(folder)
    if package_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            package_name,
            init,
            submodule_search_locations=[str(src)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(package_name)
        package = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = package
        spec.loader.exec_module(package)
    sub_name = f"{package_name}.{Path(filename).stem}"
    if sub_name in sys.modules:
        return sys.modules[sub_name]
    spec = importlib.util.spec_from_file_location(sub_name, src / filename)
    if spec is None or spec.loader is None:
        raise ImportError(sub_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[sub_name] = module
    spec.loader.exec_module(module)
    return module


def scan_indicators():
    """Experiment 15 scan(). The caller must not keep redacted_text."""
    global _scan
    if _scan is None:
        module = _load(
            "15-vulnerability-urgency-scanner",
            "scan.py",
            "exp15_scan_for_one_to_one",
        )
        if not hasattr(module, "scan"):
            raise NeighbourMissing("15-vulnerability-urgency-scanner")
        _scan = module.scan
    return _scan


def citation_tools():
    """Experiment 41 check_sentence and index_events."""
    global _check_sentence, _index_events
    if _check_sentence is None:
        module = _load_package_file(
            "41-case-summary",
            "exp41_for_one_to_one",
            "citations.py",
        )
        if not hasattr(module, "check_sentence"):
            raise NeighbourMissing("41-case-summary")
        _check_sentence = module.check_sentence
        _index_events = module.index_events
    return _check_sentence, _index_events


def extract_message():
    """Experiment 51 extract_message. Returned sentence text is not stored here."""
    global _extract_message
    if _extract_message is None:
        module = _load(
            "51-teams-channel-digest",
            "extract.py",
            "exp51_extract_for_one_to_one",
        )
        if not hasattr(module, "extract_message"):
            raise NeighbourMissing("51-teams-channel-digest")
        _extract_message = module.extract_message
    return _extract_message


def propose():
    """Experiment 08 propose(). reversible stays false."""
    global _propose
    if _propose is None:
        module = _load(
            "08-uk-pii-redaction-gateway",
            "gateway.py",
            "exp08_gateway_for_one_to_one",
        )
        if not hasattr(module, "propose"):
            raise NeighbourMissing("08-uk-pii-redaction-gateway")
        _propose = module.propose
    return _propose


def redact_uk_identifiers(text: str) -> tuple[str, list[str]]:
    """Return text with UK identifier placeholders, and the entity types.

    The banner and the matched values are not returned. Placeholders are not
    the original identifiers.
    """
    proposal = propose()(
        text,
        caller="exp-60-manager-one-to-one-prep",
        reversible=False,
    )
    redacted = str(proposal.get("redacted_text") or "")
    banner, _sep, body = redacted.partition("\n")
    shown = body if banner.startswith("[REDACTION PROPOSAL") else redacted
    findings = ((proposal.get("audit_log") or {}).get("findings")) or []
    types: list[str] = []
    for finding in findings:
        if not finding.get("applied"):
            continue
        entity = str(finding.get("entity_type") or "")
        if entity and entity not in types:
            types.append(entity)
    return shown, types


def channel_cues(text: str, display_name: str) -> dict[str, Any]:
    """Whether Experiment 51 treats one line as an action or a decision.

    The neighbour's sentence text is not copied out.
    """
    extracted = extract_message()(text, display_name=display_name)
    return {
        "action": bool(extracted.get("actions")),
        "decision": bool(extracted.get("decisions")),
        "negated": bool(extracted.get("negated")),
        "injection": bool(extracted.get("injections")),
        "text_copied": False,
    }
