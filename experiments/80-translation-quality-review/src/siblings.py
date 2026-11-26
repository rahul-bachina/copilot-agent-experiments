"""Call Experiment 79 alignment and Experiment 08 masking. Do not copy them.

Experiment 79 align() pairs segments. Its mask_text covers phone numbers,
email addresses, dates of birth, postal addresses, and personal names.
Experiment 08 propose() counts UK identifiers. Matched values are not stored.
The redacted text is not copied into the review.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]
CALLER = "exp-80-translation-quality-review"

_COLLIDING = (
    "sources",
    "injection",
    "cues",
    "mask",
    "marking",
    "negate",
    "dates",
    "catalogue",
    "intake",
    "checklist",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "citations",
    "tokens",
    "score",
    "summarise",
    "compare",
    "siblings",
    "material",
    "align",
    "paraphrases",
    "checks",
    "risk",
    "review",
    "seeded",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _package(alias: str, folder: str, modules: tuple[str, ...]) -> dict:
    src = EXPERIMENTS / folder / "src"
    if not src.is_dir():
        raise NeighbourMissing(folder)
    package = types.ModuleType(alias)
    package.__path__ = [str(src)]  # type: ignore[attr-defined]
    package.__package__ = alias
    sys.modules[alias] = package
    loaded = {}
    saved = {name: sys.modules.get(name) for name in _COLLIDING}
    try:
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        for name in modules:
            path = src / f"{name}.py"
            spec = importlib.util.spec_from_file_location(
                f"{alias}.{name}",
                path,
                submodule_search_locations=[str(src)],
            )
            if spec is None or spec.loader is None:
                raise NeighbourMissing(f"{folder}/src/{name}.py")
            module = importlib.util.module_from_spec(spec)
            module.__package__ = alias
            sys.modules[f"{alias}.{name}"] = module
            spec.loader.exec_module(module)
            loaded[name] = module
    finally:
        for name in _COLLIDING:
            sys.modules.pop(name, None)
        for name, saved_module in saved.items():
            if saved_module is not None:
                sys.modules[name] = saved_module
    return loaded


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
    exp79 = _package(
        "exp80_exp79",
        "79-document-comparison",
        ("negate", "dates", "mask", "marking", "siblings", "align"),
    )
    gateway = _load_loose(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_o006",
    )
    align = exp79["align"]
    for name in ("align", "tokens", "jaccard", "score_pairs"):
        if not hasattr(align, name):
            raise NeighbourMissing(f"Experiment 79 align.{name}")
    bundle = {
        "align": align.align,
        "tokens": align.tokens,
        "jaccard": align.jaccard,
        "score_pairs": align.score_pairs,
        "mask_text": exp79["mask"].mask_text,
        "suppress_small_counts": exp79["mask"].suppress_small_counts,
        "people_count_spans": exp79["mask"].people_count_spans,
        "empty_mask": exp79["mask"].empty_mask,
        "parse_date": exp79["dates"].parse_date,
        "as_date": exp79["dates"].as_date,
        "with_question_date": exp79["dates"].with_question_date,
        "content_markings": exp79["marking"].content_markings,
        "metadata_markings": exp79["marking"].metadata_markings,
        "higher_marking": exp79["marking"].higher_marking,
        "above_ceiling": exp79["marking"].above_ceiling,
        "legal_hold": exp79["marking"].legal_hold,
        "retention_labels": exp79["marking"].retention_labels,
        "affirmed": exp79["negate"].affirmed,
        "regex_affirmed": exp79["negate"].regex_affirmed,
        "regex_present": exp79["negate"].regex_present,
        "sentences": exp79["negate"].sentences,
        "propose": gateway.propose,
        "experiment_38_compare_called": False,
    }
    _cache["bundle"] = bundle
    return bundle


def identifier_counts(text: str, *, on: date) -> dict:
    """Count UK identifiers. Do not store the matched text."""

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
    }
