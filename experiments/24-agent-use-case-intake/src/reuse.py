"""Call Experiments 03, 14, and 19 without copying their decisions.

Each neighbour keeps its own module names. Those names collide, so a
neighbour is loaded under a private name. Modules that were already
imported are put back afterwards. Already-bound functions inside the
neighbour keep their own references.

Experiment 03's manifest generator imports PyYAML and jsonschema. This
module does not load it.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "catalogue",
    "injection",
    "screening",
    "rules",
    "drafts",
    "inventory",
    "lifecycle",
    "manifest_generator",
    "manifest_skeleton",
    "advise",
)

_rules = None
_screening = None
_drafts = None
_exp14_sources = None
_exp19_sources = None
_exp03_catalogue = None


def _load(folder: str, filename: str, module_name: str):
    saved = {name: sys.modules[name] for name in _COLLIDING if name in sys.modules}
    src = EXPERIMENTS / folder / "src"
    path = src / filename
    if not path.is_file():
        raise FileNotFoundError(folder)
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


def experiment_14_sources():
    global _exp14_sources
    if _exp14_sources is None:
        _exp14_sources = _load(
            "14-agent-architecture-advisor",
            "sources.py",
            "exp14_sources_for_intake",
        )
    return _exp14_sources


def experiment_19_sources():
    global _exp19_sources
    if _exp19_sources is None:
        _exp19_sources = _load(
            "19-privacy-impact-assessment",
            "sources.py",
            "exp19_sources_for_intake",
        )
    return _exp19_sources


def experiment_03_catalogue():
    global _exp03_catalogue
    if _exp03_catalogue is None:
        _exp03_catalogue = _load(
            "03-agent-inventory-atrs-assurance",
            "catalogue.py",
            "exp03_catalogue_for_intake",
        )
    return _exp03_catalogue


def _rules_module():
    global _rules
    if _rules is None:
        _rules = _load(
            "14-agent-architecture-advisor",
            "rules.py",
            "exp14_rules_for_intake",
        )
    return _rules


def _screening_module():
    global _screening
    if _screening is None:
        _screening = _load(
            "19-privacy-impact-assessment",
            "screening.py",
            "exp19_screening_for_intake",
        )
    return _screening


def _drafts_module():
    global _drafts
    if _drafts is None:
        _drafts = _load(
            "03-agent-inventory-atrs-assurance",
            "drafts.py",
            "exp03_drafts_for_intake",
        )
    return _drafts


def score_autonomy(case: dict) -> dict:
    """Experiment 14's table. ``a3_recommended`` is false. Nothing is selected."""

    rules = _rules_module()
    normalised, notes = rules.normalise(case)
    scored = rules.score(normalised)
    level = scored["recommended_autonomy"]
    if level not in {"A0", "A1", "A2"} or scored.get("a3_recommended") is not False:
        raise RuntimeError("Experiment 14 recommended a level this catalogue does not allow")
    return {
        "experiment": "14-agent-architecture-advisor",
        "catalogue_id": "G002",
        "called": True,
        "manifest_generator_called": False,
        "platform_selected": None,
        "recommended_autonomy": level,
        "a3_recommended": False,
        "work_shape": scored["work_shape"],
        "rules_fired": list(scored["rules_fired"]),
        "normalise_notes": notes,
        "options": [
            {
                "id": option["id"],
                "suitability": option["suitability"],
                "selected": False,
            }
            for option in scored["options"]
        ],
        "actions_taken": [],
    }


def screen_dpia(answers: dict | None, article_35_1_view: str) -> dict:
    """Experiment 19's screen. ``dpia_required`` stays null."""

    screening = _screening_module()
    view = article_35_1_view if article_35_1_view in {"yes", "no", "unknown"} else "unknown"
    block = answers if isinstance(answers, dict) else {}
    result = screening.screen(block, article_35_1_view=view)
    if result.get("dpia_required") is not None or result.get("dpia_required_decided_by_this_tool") is not False:
        raise RuntimeError("Experiment 19 returned a DPIA determination. This intake will not use it.")
    indicated = bool(result.get("indicated_on_recorded_answers"))
    screen_result = result.get("screen_result")
    if indicated and screen_result in {
        "article_35_3_recorded",
        "ico_list_recorded",
        "article_35_1_view_recorded",
    }:
        likely = True
    elif screen_result == "recorded_answers_do_not_indicate":
        likely = False
    else:
        likely = None
    return {
        "experiment": "19-privacy-impact-assessment",
        "catalogue_id": "L006",
        "called": True,
        "screen_result": screen_result,
        "indicated_on_recorded_answers": indicated,
        "dpia_likely_needed": likely,
        "dpia_required": None,
        "dpia_required_decided_by_this_tool": False,
        "reading": result.get("reading"),
        "actions_taken": [],
        "note": (
            "Passed through Experiment 19. A false likely-needed flag means every "
            "recorded answer on that screen was no. It is not a decision that "
            "Article 35(1) does not apply."
        ),
    }


def draft_assurance(record: dict) -> dict:
    """Experiment 03 applicability and DUAA screen. Nothing is submitted."""

    drafts = _drafts_module()
    atrs = drafts.draft_atrs(record)
    duaa = drafts.screen_duaa(record)
    applicability = atrs.get("applicability") or {}
    if atrs.get("approved") is not False or atrs.get("submission_status") != "not_submitted":
        raise RuntimeError("Experiment 03 returned an ATRS record this intake will not use")
    if duaa.get("lawful") is not None or duaa.get("approved") is not False:
        raise RuntimeError("Experiment 03 returned a DUAA determination this intake will not use")
    return {
        "experiment": "03-agent-inventory-atrs-assurance",
        "catalogue_id": "G010",
        "called": True,
        "manifest_generator_called": False,
        "atrs_approved": False,
        "atrs_submission_status": "not_submitted",
        "may_be_emailed_to_dsit": False,
        "applicability_code": applicability.get("code"),
        "applicability_note": applicability.get("note"),
        "mandatory_scope_decided_by_experiment_03": applicability.get("mandatory_scope_decided_by_this_tool"),
        "duaa_screen_result": duaa.get("screen_result"),
        "duaa_lawful": None,
        "duaa_determination": duaa.get("determination"),
        "actions_taken": [],
        "note": (
            "Experiment 03 drafted the applicability note and the DUAA screen. "
            "The field-by-field ATRS template is not copied here. The manifest "
            "generator was not called."
        ),
    }


def neighbour_pins() -> dict[str, str]:
    """Dates the neighbours recorded. This intake does not rewrite them."""

    exp14 = experiment_14_sources().LAST_VERIFIED
    exp19 = experiment_19_sources().SOURCES_PINNED_ON
    exp03 = experiment_03_catalogue().ATRS_RETRIEVED_ON
    if isinstance(exp19, date):
        exp19 = exp19.isoformat()
    return {
        "experiment_14_last_verified": str(exp14),
        "experiment_19_sources_pinned_on": str(exp19),
        "experiment_03_atrs_retrieved_on": str(exp03),
    }


def experiment_14_stale(as_of: date, stale_after_days: int) -> bool:
    rows = experiment_14_sources().currency(as_of.isoformat(), stale_after_days)
    return any(row.get("stale") for row in rows)
