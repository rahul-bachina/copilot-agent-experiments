"""Load Experiments 08, 12, and 33 without copying their rules.

The folders sit beside this one. A missing folder is a hard stop. This
module does not reimplement company-number prefixes, postcode shapes,
document intake, or the pinpoint span check.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


class CompareForbidden(RuntimeError):
    """The comparison has no choose, edit, contact, or register-lookup path."""


_ROOT = Path(__file__).resolve().parents[2]
_LOADED = False
_CACHE: dict = {}


def _package(alias: str, folder: str, modules: tuple[str, ...]) -> dict:
    src = _ROOT / folder / "src"
    if not src.is_dir():
        raise CompareForbidden(
            f"{folder} is not beside this experiment. This starter will not copy its rules."
        )
    package = types.ModuleType(alias)
    package.__path__ = [str(src)]
    package.__package__ = alias
    sys.modules[alias] = package
    loaded = {}
    for name in modules:
        path = src / f"{name}.py"
        spec = importlib.util.spec_from_file_location(f"{alias}.{name}", path)
        if spec is None or spec.loader is None:
            raise CompareForbidden(f"Could not load {folder}/src/{name}.py")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = alias
        sys.modules[f"{alias}.{name}"] = module
        spec.loader.exec_module(module)
        loaded[name] = module
    return loaded


def load() -> dict:
    """Import the three siblings once. Later calls return the same modules."""
    global _LOADED
    if _LOADED:
        return _CACHE
    gateway_src = _ROOT / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise CompareForbidden(
            "Experiment 08 is not beside this experiment. This starter will not invent a redactor."
        )
    if str(gateway_src) not in sys.path:
        sys.path.insert(0, str(gateway_src))
    import gateway  # type: ignore
    import identifiers  # type: ignore

    exp12 = _package("exp12_intake", "12-document-intake", ("catalogue", "injection", "intake"))
    exp33 = _package("exp33_citations", "33-case-bundle-summariser", ("injection", "citations"))
    _CACHE.update(
        {
            "propose": gateway.propose,
            "identifiers": identifiers,
            "intake": exp12["intake"].intake,
            "intake_scan": exp12["injection"].scan_text,
            "intake_merge": exp12["injection"].merge_scans,
            "intake_not_synthetic": exp12["intake"].NotSynthetic,
            "resolve_span": exp33["citations"].resolve_span,
            "citation_normalise": exp33["citations"].normalise,
            "document_block_reason": exp33["citations"].document_block_reason,
            "gateway_experiment_id": "exp-08-uk-pii-redaction-gateway",
            "intake_experiment_id": exp12["catalogue"].EXPERIMENT_ID,
            "citation_experiment_id": "exp-33-case-bundle-summariser",
        }
    )
    _LOADED = True
    return _CACHE
