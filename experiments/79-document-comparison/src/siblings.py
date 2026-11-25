"""Call Experiments 12, 08, 33, and 29. Do not copy their rules.

Experiment 12 inventories the text. Files are not confirmed and no purpose
is confirmed. Experiment 08 counts UK identifiers. The redacted text is not
stored. Experiment 33's normalise and resolve_span check a pinpoint quote.
Experiment 29's extract_numbers and extract_dates read figures. Experiment 38
uses those same neighbours for insurance wordings. This starter does not call
Experiment 38 compare(), which is a closed topic list for policy wordings.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import date, datetime
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]
CALLER = "exp-79-document-comparison"

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
    intake = _load_loose("12-document-intake", "intake.py", "exp12_intake_for_o004")
    gateway = _load_loose("08-uk-pii-redaction-gateway", "gateway.py", "exp08_gateway_for_o004")
    exp33 = _package("exp79_exp33", "33-case-bundle-summariser", ("injection", "citations"))
    exp29 = _package("exp79_exp29", "29-groundedness-evaluation", ("tokens", "score"))
    for name in ("normalise", "resolve_span"):
        if not hasattr(exp33["citations"], name):
            raise NeighbourMissing(f"Experiment 33 citations.{name}")
    for name in ("extract_numbers", "extract_dates"):
        if not hasattr(exp29["score"], name):
            raise NeighbourMissing(f"Experiment 29 score.{name}")
    bundle = {
        "intake": intake.intake,
        "propose": gateway.propose,
        "normalise": exp33["citations"].normalise,
        "resolve_span": exp33["citations"].resolve_span,
        "extract_numbers": exp29["score"].extract_numbers,
        "extract_dates": exp29["score"].extract_dates,
        "experiment_38_compare_called": False,
    }
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


def intake_versions(files: list[dict], *, on: date) -> dict:
    if not files:
        return {
            "called": False,
            "reason": "no_files",
            "experiment_id": "exp-12-document-intake",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "content_recorded": False,
        }
    batch = {"synthetic": True, "batch_id": "document-comparison", "files": files[:12]}
    draft = neighbours()["intake"](batch, as_of=on)
    rows = []
    for row in draft.get("files") or []:
        pii = row.get("pii") or {}
        rows.append(
            {
                "file_id": row.get("file_id"),
                "read_status": row.get("read_status"),
                "date_status": row.get("date_status"),
                "finding_count": pii.get("finding_count"),
                "content_recorded": False,
            }
        )
    flags = draft.get("flags") or {}
    return {
        "called": True,
        "experiment_id": "exp-12-document-intake",
        "catalogue_id": draft.get("catalogue_id"),
        "files_confirmed": False,
        "purpose_confirmed": False,
        "handed_off": False,
        "accepted_into_queue": flags.get("accepted_into_queue"),
        "content_recorded": False,
        "prompt_injection_followed": False,
        "files": rows,
    }
