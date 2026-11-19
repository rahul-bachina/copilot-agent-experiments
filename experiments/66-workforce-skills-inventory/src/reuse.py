"""Call Experiments 08, 61, and 62 under private module names.

Shared names are restored after each load. Redacted values are not stored
by this module. A learning plan is not an enrolment. A vacancy note is not
a selection and is not built from inferred skills.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "words",
    "mask",
    "marking",
    "inventory",
    "reuse",
    "gateway",
    "detectors",
    "identifiers",
    "model_assist",
    "plan",
    "explore",
    "handbook",
    "answer",
    "compare",
    "normalise",
    "siblings",
    "phrases",
    "scan",
    "gaps",
    "knowledge",
)

_cache: dict[str, object] = {}


class NeighbourMissing(RuntimeError):
    """A neighbouring experiment is not beside this folder."""


def _load(folder: str, filename: str, module_name: str):
    if module_name in _cache:
        return _cache[module_name]
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
    _cache[module_name] = module
    return module


def propose():
    module = _load(
        "08-uk-pii-redaction-gateway",
        "gateway.py",
        "exp08_gateway_for_skills",
    )
    if not hasattr(module, "propose"):
        raise NeighbourMissing("08-uk-pii-redaction-gateway")
    return module.propose


def redact_uk_identifiers(text: str) -> dict:
    """Types and redacted body. Matched values are not returned."""

    proposal = propose()(
        text,
        caller="exp-66-workforce-skills-inventory",
        apply_model_suggestions=False,
        reversible=False,
    )
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
        "called": True,
        "experiment_id": "exp-08-uk-pii-redaction-gateway",
    }


def _read_json(folder: str, name: str) -> dict:
    path = EXPERIMENTS / folder / name
    if not path.is_file():
        raise NeighbourMissing(folder)
    return json.loads(path.read_text(encoding="utf-8"))


def learning_plan(goals: str, as_of: str) -> dict:
    """Experiment 61, only from text the caller already confirmed.

    enrolled stays false. The plan is not a performance rating and not a
    promotion factor. This function does not record an approval.
    """

    module = _load("61-learning-path-planner", "plan.py", "exp61_plan_for_skills")
    if not hasattr(module, "draft_plan"):
        raise NeighbourMissing("61-learning-path-planner")
    catalogue = _read_json("61-learning-path-planner", "fixtures/catalogue.json")
    framework = _read_json("61-learning-path-planner", "fixtures/framework.json")
    directory = _read_json("61-learning-path-planner", "fixtures/directory.json")
    request = {
        "synthetic": True,
        "employee_ref": "EMP-1001",
        "goals": goals,
    }
    plan = module.draft_plan(request, catalogue, framework, directory, as_of)
    return {
        "called": True,
        "experiment_id": "exp-61-learning-path-planner",
        "outcome": plan.get("outcome"),
        "enrolled": False,
        "human_approval": None,
        "used_as_a_performance_or_promotion_factor": False,
        "step_count": len(plan.get("steps") or plan.get("plan") or []),
        "values_copied": False,
    }


def mobility_note(stated_experience: str, as_of: str) -> dict:
    """Experiment 62, from the employee's stated experience only.

    Inferred skills are not passed in. selection_made is copied from that
    result and is not turned into a decision here.
    """

    module = _load("62-internal-mobility-explorer", "explore.py", "exp62_explore_for_skills")
    if not hasattr(module, "explore"):
        raise NeighbourMissing("62-internal-mobility-explorer")
    root = "62-internal-mobility-explorer"
    vacancies = _read_json(root, "fixtures/vacancies.json")
    rules = _read_json(root, "fixtures/eligibility.json")
    framework = _read_json(root, "fixtures/framework.json")
    directory = _read_json(root, "fixtures/directory.json")
    request = {
        "synthetic": True,
        "employee_ref": "EMP-4101",
        "experience": stated_experience,
    }
    note = module.explore(request, vacancies, rules, framework, directory, as_of)
    flags = note.get("flags") or {}
    return {
        "called": True,
        "experiment_id": "exp-62-internal-mobility-explorer",
        "outcome": note.get("outcome"),
        "applied": flags.get("applied"),
        "nominated": flags.get("nominated"),
        "shortlisted": flags.get("shortlisted"),
        "contacted": flags.get("contacted"),
        "selection_made": flags.get("selection_made"),
        "eligibility_decided": flags.get("eligibility_decided"),
        "used_as_a_selection_factor": False,
        "inferred_skills_passed": False,
        "vacancy_ids": [row.get("vacancy_id") for row in (note.get("relevant") or []) if isinstance(row, dict)],
        "values_copied": False,
    }
