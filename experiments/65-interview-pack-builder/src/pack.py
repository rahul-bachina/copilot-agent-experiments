"""Draft an interview pack from a synthetic person specification.

The recruiter approves the questions and the rubric on a separate object,
bound to the hash of that text. The agent does not contact candidates,
schedule interviews, score or rank anyone, or make a hiring decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    from distress import distress_present
    from injection import scan as scan_injection
    from intents import intents_in
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        retention_labels,
    )
    from mask import mask_text
    from negate import affirmed
    from probes import (
        EXAMPLE_NOTE,
        categories_in,
        occupational_requirement,
        positive_action_general,
        positive_action_recruitment,
    )
    from reuse import redact_uk_identifiers, wording_flags
    from sources import ICO, OPENED_ON, pin_rows, statutory_note
else:
    from .distress import distress_present
    from .injection import scan as scan_injection
    from .intents import intents_in
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        retention_labels,
    )
    from .mask import mask_text
    from .negate import affirmed
    from .probes import (
        EXAMPLE_NOTE,
        categories_in,
        occupational_requirement,
        positive_action_general,
        positive_action_recruitment,
    )
    from .reuse import redact_uk_identifiers, wording_flags
    from .sources import ICO, OPENED_ON, pin_rows, statutory_note

LABEL = (
    "DRAFT INTERVIEW PACK. NOT FOR USE UNTIL THE RECRUITER APPROVES THE "
    "QUESTIONS AND THE RUBRIC. NOT LEGAL ADVICE. THE AGENT DOES NOT CONTACT "
    "CANDIDATES, SCHEDULE INTERVIEWS, SCORE OR RANK ANYONE, OR MAKE A HIRING DECISION."
)
CATALOGUE_ID = "H008"
EXPERIMENT_ID = "exp-65-interview-pack-builder"
AUTONOMY = "A1"
STARTER_ADJUSTMENT = (
    "Please tell us if you need a change to the interview arrangements so you "
    "can take part. You do not need to tell us about your health or your diagnosis."
)
_PAY = re.compile(
    r"\b(?:you|the candidate|applicants?) must pay\b|\bat your own cost\b|"
    r"\bpay for (?:your|the) (?:adjustment|interpreter|support)\b",
    re.I,
)
_SICKNESS = re.compile(r"\b(?:sick days|sickness days|sickness absence)\b", re.I)
_STYLES = {"competency", "strengths"}


class InterviewPackForbidden(RuntimeError):
    """Contact, scheduling, scoring, ranking, and hiring are not tools."""


class NotSynthetic(ValueError):
    """The caller did not mark the inputs as synthetic."""


def contact_candidate(*_args, **_kwargs) -> None:
    raise InterviewPackForbidden("The agent does not contact candidates.")


def schedule_interview(*_args, **_kwargs) -> None:
    raise InterviewPackForbidden("The agent does not schedule interviews.")


def score_candidate(*_args, **_kwargs) -> None:
    raise InterviewPackForbidden("The agent does not score candidates.")


def rank_candidates(*_args, **_kwargs) -> None:
    raise InterviewPackForbidden("The agent does not rank candidates.")


def make_hiring_decision(*_args, **_kwargs) -> None:
    raise InterviewPackForbidden("The agent does not make a hiring decision.")


def _parse_day(value: object) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _mask(text: str) -> str:
    masked, _counts = mask_text(text)
    return masked


def _person(directory: dict, ref: object) -> dict | None:
    if not isinstance(directory, dict) or directory.get("synthetic") is not True:
        return None
    if not isinstance(ref, str):
        return None
    people = directory.get("people")
    if not isinstance(people, list):
        return None
    for person in people:
        if isinstance(person, dict) and person.get("ref") == ref:
            return person
    return None


def _blank() -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "opened_on": OPENED_ON,
        "legal_advice": False,
        "human_approval": None,
        "approved_for_use": False,
        "contacted": False,
        "scheduled": False,
        "scored": False,
        "ranked": False,
        "hiring_decision": False,
        "candidates_contacted": False,
        "interviews_scheduled": False,
        "candidates_scored": False,
        "candidates_ranked": False,
        "discrimination_decided": False,
        "section_15_decided": False,
        "section_20_decided": False,
        "section_20_met": False,
        "occupational_requirement_decided": False,
        "positive_action_decided": False,
        "health_question_decided": False,
        "right_to_work_checked": False,
        "coerced": False,
        "instructions_followed": False,
        "invented_criteria": False,
        "cue_copied": False,
        "output_is_anonymised": False,
        "may_be_relied_on": False,
        "performed_by_agent": False,
    }


def _force(result: dict) -> dict:
    result["label"] = LABEL
    result["catalogue_id"] = CATALOGUE_ID
    result["autonomy"] = AUTONOMY
    result["legal_advice"] = False
    result["approved_for_use"] = bool(result.get("approved_for_use"))
    result["contacted"] = False
    result["scheduled"] = False
    result["scored"] = False
    result["ranked"] = False
    result["hiring_decision"] = False
    result["candidates_contacted"] = False
    result["interviews_scheduled"] = False
    result["candidates_scored"] = False
    result["candidates_ranked"] = False
    result["discrimination_decided"] = False
    result["section_15_decided"] = False
    result["section_20_decided"] = False
    result["section_20_met"] = False
    result["occupational_requirement_decided"] = False
    result["positive_action_decided"] = False
    result["health_question_decided"] = False
    result["right_to_work_checked"] = False
    result["coerced"] = False
    result["instructions_followed"] = False
    result["invented_criteria"] = False
    result["cue_copied"] = False
    result["output_is_anonymised"] = False
    result["may_be_relied_on"] = False
    if result.get("prompt_injection"):
        result["prompt_injection"]["followed"] = False
    return result


def _criteria(raw: object) -> tuple[list[dict] | None, bool]:
    """Return (rows, unparseable). None rows means the field could not be read.

    An empty list is a real empty list. It is not a stand-in for a bad value.
    """

    if raw is None:
        return [], False
    if not isinstance(raw, list):
        return None, True
    rows: list[dict] = []
    unparseable = False
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            unparseable = True
            continue
        cid = item.get("id")
        text = item.get("text")
        if not isinstance(cid, str) or not cid.strip() or not isinstance(text, str) or not text.strip():
            unparseable = True
            continue
        if cid.strip() in seen:
            unparseable = True
            continue
        seen.add(cid.strip())
        rows.append({"id": cid.strip(), "text": text.strip()})
    return rows, unparseable


def _question_text(style: str, criterion: str) -> str:
    if style == "competency":
        return (
            f"Tell us about a time you did this work: {criterion} "
            "What did you do, and what was the result?"
        )
    return f"What draws you to this work: {criterion} How have you used it?"


def _add_route(routes: list[dict], kind: str, reason: str) -> None:
    if any(row["kind"] == kind for row in routes):
        return
    routes.append(
        {
            "route_id": f"HR-{len(routes) + 1}",
            "kind": kind,
            "reason": reason,
            "decided": False,
            "hr_seen": False,
            "excerpt_copied": False,
        }
    )


def _hash_questions(questions: list[dict]) -> str:
    payload = [
        {
            "question_id": row["question_id"],
            "criterion_id": row["criterion_id"],
            "text": row["text"],
            "style": row["style"],
            "wording_flags": row.get("wording_flags") or [],
        }
        for row in questions
    ]
    return _sha(_canonical(payload))


def _hash_rubric(rubric: dict) -> str:
    payload = {
        "unreadable": rubric.get("unreadable"),
        "scale": rubric.get("scale"),
        "rows": rubric.get("rows"),
        "below_guide_minimum": rubric.get("below_guide_minimum"),
    }
    return _sha(_canonical(payload))


def route_hash(route: dict) -> str:
    return _sha(
        _canonical(
            {
                "route_id": route["route_id"],
                "kind": route["kind"],
                "reason": route["reason"],
            }
        )
    )


def _hash_pack(result: dict) -> str:
    payload = {
        "questions_hash": result.get("questions_hash"),
        "rubric_hash": result.get("rubric_hash"),
        "adjustment_prompts": [
            row.get("text") for row in result.get("adjustment_prompts") or []
        ],
        "panel_rules": (result.get("panel_guidance") or {}).get("rules"),
        "exclusions": result.get("exclusions"),
        "hr_kinds": [row.get("kind") for row in result.get("hr_routes") or []],
        "retention_labels": result.get("retention_labels"),
        "legal_hold": result.get("legal_hold"),
        "marking": result.get("marking"),
    }
    return _sha(_canonical(payload))


def _scale(guide: dict) -> tuple[list[str] | None, dict]:
    info = {
        "unreadable": False,
        "missing": False,
        "minimum": None,
        "minimum_source": None,
        "minimum_unreadable": False,
        "minimum_out_of_range": False,
        "anchors_unreadable": False,
        "anchors": {},
    }
    raw = guide.get("scale")
    if raw is None:
        info["missing"] = True
        info["unreadable"] = True
        return None, info
    if (
        not isinstance(raw, list)
        or not raw
        or not all(isinstance(item, str) and item.strip() for item in raw)
    ):
        info["unreadable"] = True
        return None, info
    scale = [item.strip() for item in raw]
    anchors = guide.get("anchors")
    if anchors is None:
        info["anchors"] = {}
    elif not isinstance(anchors, dict):
        info["anchors_unreadable"] = True
        info["anchors"] = {}
    else:
        cleaned = {}
        for key, value in anchors.items():
            if isinstance(key, str) and isinstance(value, str) and value.strip():
                cleaned[key] = value.strip()
            else:
                info["anchors_unreadable"] = True
        info["anchors"] = cleaned
    minimum = guide.get("minimum_anchor_points")
    if minimum is None:
        info["minimum"] = len(scale)
        info["minimum_source"] = "scale_length"
    elif isinstance(minimum, bool) or not isinstance(minimum, int):
        info["minimum_unreadable"] = True
    elif minimum < 1 or minimum > 20:
        info["minimum_out_of_range"] = True
    else:
        info["minimum"] = minimum
        info["minimum_source"] = "guide"
    return scale, info


def _rubric_for(questions: list[dict], scale: list[str] | None, info: dict) -> dict:
    if scale is None:
        return {
            "unreadable": True,
            "complete": False,
            "below_guide_minimum": False,
            "scale": None,
            "row_count": None,
            "scores_a_candidate": False,
            "rows": [],
            "minimum_anchor_points": None,
            "minimum_source": info.get("minimum_source"),
            "minimum_unreadable": info.get("minimum_unreadable"),
            "minimum_out_of_range": info.get("minimum_out_of_range"),
            "anchors_unreadable": info.get("anchors_unreadable"),
            "coerced": False,
        }
    rows = []
    below = False
    for question in questions:
        anchors = []
        present = 0
        for point in scale:
            text = info["anchors"].get(point)
            missing = not isinstance(text, str)
            if not missing:
                present += 1
            anchors.append(
                {
                    "point": point,
                    "text": None if missing else text,
                    "missing": missing,
                    "invented": False,
                }
            )
        minimum = info.get("minimum")
        short = minimum is None or present < minimum or (isinstance(minimum, int) and minimum > len(scale))
        if short:
            below = True
        rows.append(
            {
                "question_id": question["question_id"],
                "criterion_id": question["criterion_id"],
                "anchors": anchors,
                "anchors_present": present,
                "scores_a_candidate": False,
            }
        )
    if info.get("minimum_unreadable") or info.get("minimum_out_of_range") or info.get("anchors_unreadable"):
        below = True
    return {
        "unreadable": False,
        "complete": not below and all(not anchor["missing"] for row in rows for anchor in row["anchors"]),
        "below_guide_minimum": below,
        "scale": scale,
        "row_count": len(rows),
        "scores_a_candidate": False,
        "rows": rows,
        "minimum_anchor_points": info.get("minimum"),
        "minimum_source": info.get("minimum_source"),
        "minimum_unreadable": info.get("minimum_unreadable"),
        "minimum_out_of_range": info.get("minimum_out_of_range"),
        "anchors_unreadable": info.get("anchors_unreadable"),
        "coerced": False,
        "starter_rule": info.get("minimum_source") == "scale_length",
    }


def _prompts(guide: dict, routes: list[dict]) -> tuple[list[dict], dict]:
    raw = guide.get("adjustment_prompts")
    info = {
        "organisation_supplied": False,
        "unreadable": False,
        "missing": False,
        "starter_used": False,
        "cost_shifted": False,
        "below_opened_rule": False,
    }
    texts: list[str] = []
    if raw is None:
        info["missing"] = True
    elif not isinstance(raw, list):
        info["unreadable"] = True
    else:
        info["organisation_supplied"] = True
        for item in raw:
            if isinstance(item, str) and item.strip():
                texts.append(item.strip())
            else:
                info["unreadable"] = True
    kept: list[dict] = []
    for text in texts:
        if _PAY.search(text):
            info["cost_shifted"] = True
            info["below_opened_rule"] = True
            _add_route(
                routes,
                "section_20_cost",
                "Section 20(7) says A is not entitled to require a disabled person to pay A's costs of complying with the duty. This starter does not decide that the duty arose.",
            )
            continue
        if "disability_health" in categories_in(text):
            _add_route(
                routes,
                "section_60",
                "Section 60(1) covers a health question before an offer. Section 60(6) is not decided here.",
            )
            continue
        kept.append(
            {
                "text": _mask(text),
                "source": "guide",
                "organisation_supplied": True,
                "section_20_met": False,
            }
        )
    if not kept:
        info["starter_used"] = True
        info["organisation_supplied"] = False
        kept.append(
            {
                "text": STARTER_ADJUSTMENT,
                "source": "starter",
                "organisation_supplied": False,
                "section_20_met": False,
                "note": "The guide did not supply a usable prompt. This sentence is a starter prompt. It is not the organisation's policy.",
            }
        )
    return kept, info


def _panel(guide: dict) -> dict:
    raw = guide.get("note_taking")
    if raw is None:
        return {
            "rules": [],
            "missing": True,
            "unreadable": False,
            "source": None,
            "invented": False,
        }
    if not isinstance(raw, list):
        return {
            "rules": [],
            "missing": True,
            "unreadable": True,
            "source": None,
            "invented": False,
        }
    rules = []
    unreadable = False
    for item in raw:
        if isinstance(item, str) and item.strip():
            rules.append(_mask(item.strip()))
        else:
            unreadable = True
    return {
        "rules": rules,
        "missing": len(rules) == 0,
        "unreadable": unreadable,
        "source": "guide" if rules else None,
        "invented": False,
    }


def _collect_text(request: dict) -> str:
    parts: list[str] = []
    job = request.get("job") if isinstance(request.get("job"), dict) else {}
    for key in ("text", "title", "invitation"):
        value = job.get(key)
        if isinstance(value, str):
            parts.append(value)
    invitation = request.get("invitation")
    if isinstance(invitation, str):
        parts.append(invitation)
    notes = request.get("notes")
    if isinstance(notes, str):
        parts.append(notes)
    spec = request.get("person_specification")
    if isinstance(spec, dict):
        for key in ("essential", "desirable"):
            raw = spec.get(key)
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        parts.append(item["text"])
    proposals = request.get("proposed_questions")
    if isinstance(proposals, list):
        for item in proposals:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
    return "\n".join(parts)


def draft_pack(request: dict, guide: dict, directory: dict, as_of: str) -> dict:
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    result = _blank()
    result["as_of"] = as_of if isinstance(as_of, str) else None
    question_date = _parse_day(as_of)
    result["question_date_unreadable"] = question_date is None
    embedded = request.get("question_date")
    result["question_date_conflict"] = (
        isinstance(embedded, str) and embedded != as_of
    ) or (embedded not in (None, as_of) and not isinstance(embedded, str))
    if request.get("synthetic") is not True or not isinstance(guide, dict) or guide.get("synthetic") is not True:
        result["outcome"] = "not_synthetic"
        result["question_count"] = None
        result["body_copied"] = False
        return _force(result)
    if question_date is None:
        result["outcome"] = "unreadable"
        result["question_count"] = None
        result["coerced"] = False
        return _force(result)

    corpus = _collect_text(request)
    result["prompt_injection"] = scan_injection(corpus)
    result["self_declared_role_ignored"] = "self_role" in result["prompt_injection"]["signals"]
    result["self_declared_clearance_ignored"] = "self_clearance" in result["prompt_injection"]["signals"]
    requester = _person(directory, request.get("recruiter_ref"))
    result["requester_ref"] = requester.get("ref") if requester else None
    result["requester_role"] = requester.get("role") if requester else None
    result["requester_in_directory"] = requester is not None
    ceiling = requester.get("clearance") if requester else None
    if not isinstance(ceiling, str):
        ceiling = None
    job = request.get("job") if isinstance(request.get("job"), dict) else {}
    meta_marking = job.get("marking") if isinstance(job.get("marking"), str) else None
    page = content_markings(corpus)
    labels = ([meta_marking] if meta_marking else []) + page
    result["marking"] = higher_marking([label for label in labels if isinstance(label, str)])
    result["marking_from_content"] = page
    result["marking_unreadable"] = meta_marking is not None and meta_marking not in {
        "OFFICIAL",
        "OFFICIAL-SENSITIVE",
        "SECRET",
        "TOP SECRET",
    }
    held = legal_hold(job.get("legal_hold"), corpus)
    result["legal_hold"] = held
    labels_kept, retention_bad = retention_labels(job.get("retention_labels"), corpus)
    result["retention_labels"] = labels_kept
    result["retention_unreadable"] = retention_bad
    if above_ceiling(result["marking"], ceiling) or ceiling is None:
        result["outcome"] = "above_clearance" if requester else "requester_unknown"
        result["question_count"] = None
        result["body_copied"] = False
        result["clearance"] = ceiling
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        if distress_present(corpus):
            result["outcome"] = "human_route"
            result["distress_routed"] = True
            result["cue_copied"] = False
        return _force(result)
    result["clearance"] = ceiling
    result["body_copied"] = True
    result["distress_routed"] = False
    if distress_present(corpus):
        result["outcome"] = "human_route"
        result["distress_routed"] = True
        result["cue_copied"] = False
        result["question_count"] = None
        result["questions"] = []
        result["body_copied"] = False
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        _mask_report(result, corpus)
        return _force(result)

    prohibited = intents_in(corpus)
    result["prohibited_requests"] = prohibited
    if prohibited:
        result["outcome"] = "prohibited_request"
        result["question_count"] = None
        result["questions"] = []
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        _mask_report(result, corpus)
        return _force(result)

    review_due = _parse_day(guide.get("review_due"))
    in_force = _parse_day(guide.get("in_force_from"))
    guide_info = {
        "id": guide.get("id") if isinstance(guide.get("id"), str) else None,
        "dates_unreadable": False,
        "stale": False,
        "not_yet_in_force": False,
        "style": None,
        "style_unreadable": False,
    }
    if guide.get("review_due") is not None and review_due is None:
        guide_info["dates_unreadable"] = True
    if guide.get("in_force_from") is not None and in_force is None:
        guide_info["dates_unreadable"] = True
    if review_due is not None and question_date >= review_due:
        guide_info["stale"] = True
    if in_force is not None and question_date < in_force:
        guide_info["not_yet_in_force"] = True
    style = guide.get("style")
    if style not in _STYLES:
        guide_info["style_unreadable"] = True
    else:
        guide_info["style"] = style
    result["guide"] = guide_info

    spec = request.get("person_specification")
    if not isinstance(spec, dict):
        result["outcome"] = "unreadable"
        result["question_count"] = None
        result["criteria_unparseable"] = True
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        _mask_report(result, corpus)
        return _force(result)
    essential, essential_bad = _criteria(spec.get("essential"))
    desirable, desirable_bad = _criteria(spec.get("desirable"))
    result["criteria_unparseable"] = essential_bad or desirable_bad or essential is None
    ask_desirable = guide.get("ask_desirable")
    result["ask_desirable_unreadable"] = "ask_desirable" in guide and not isinstance(ask_desirable, bool)
    use_desirable = ask_desirable is True
    if essential is None or guide_info["style_unreadable"]:
        result["outcome"] = "unreadable"
        result["question_count"] = None
        result["questions"] = []
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        _finish_common(result, question_date, corpus, guide, [])
        return _force(result)
    if not essential and essential_bad:
        result["outcome"] = "unreadable"
        result["question_count"] = None
        result["questions"] = []
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        _finish_common(result, question_date, corpus, guide, [])
        return _force(result)
    if not essential:
        result["outcome"] = "no_criteria"
        result["question_count"] = 0
        result["questions"] = []
        result["pins"] = pin_rows(question_date)
        result["statutory_note"] = statutory_note(question_date)
        _finish_common(result, question_date, corpus, guide, [])
        return _force(result)

    chosen = list(essential)
    if use_desirable and desirable:
        chosen.extend(desirable)
    result["desirable_count"] = len(desirable or [])
    result["desirable_asked"] = bool(use_desirable and desirable)

    routes: list[dict] = []
    exclusions: list[dict] = []
    questions: list[dict] = []
    wording = wording_flags(corpus)
    result["wording_flags"] = wording
    result["wording_source"] = "exp-64-job-description-quality"
    result["probe_note"] = EXAMPLE_NOTE

    def exclude(reason: str, categories: list[str], criterion_id: object, source: str) -> None:
        exclusions.append(
            {
                "reason": reason,
                "categories": categories,
                "criterion_id": criterion_id if isinstance(criterion_id, str) else None,
                "source": source,
                "included": False,
                "excerpt_copied": False,
            }
        )

    for criterion in chosen:
        text = criterion["text"]
        probe_rows = categories_in(text)
        if occupational_requirement(text):
            _add_route(
                routes,
                "schedule_9",
                "Schedule 9 paragraph 1(1) is the occupational-requirement test. This starter does not decide that it is met.",
            )
            exclude("occupational_requirement", probe_rows or ["schedule_9"], criterion["id"], "criterion")
            continue
        if probe_rows:
            if "disability_health" in probe_rows:
                _add_route(
                    routes,
                    "section_60",
                    "Section 60(1) covers a health question before an offer. Section 60(6) is not decided here.",
                )
                if _SICKNESS.search(text):
                    _add_route(
                        routes,
                        "section_15",
                        "Section 15(1) is about unfavourable treatment because of something arising in consequence of disability. This starter does not decide it.",
                    )
            exclude("protected_characteristic", probe_rows, criterion["id"], "criterion")
            continue
        flags = [row["phrase"] for row in wording_flags(text)]
        questions.append(
            {
                "question_id": "Q-" + re.sub(r"[^A-Za-z0-9-]", "", criterion["id"])[:40],
                "criterion_id": criterion["id"],
                "criterion_text": _mask(text),
                "text": _mask(_question_text(style, text)),
                "style": style,
                "tied_to_criterion": True,
                "source": "drafted",
                "wording_flags": flags,
                "scores_a_candidate": False,
            }
        )

    proposals = request.get("proposed_questions")
    reviewed = []
    if proposals is None:
        result["proposals_unreadable"] = False
    elif not isinstance(proposals, list):
        result["proposals_unreadable"] = True
    else:
        result["proposals_unreadable"] = False
        known = {row["id"] for row in chosen}
        for item in proposals:
            if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                result["proposals_unreadable"] = True
                continue
            text = item["text"]
            cid = item.get("criterion_id") if isinstance(item.get("criterion_id"), str) else None
            cats = categories_in(text)
            if distress_present(text):
                reviewed.append({"criterion_id": cid, "included": False, "reason": "distress", "excerpt_copied": False})
                continue
            if occupational_requirement(text):
                _add_route(
                    routes,
                    "schedule_9",
                    "Schedule 9 paragraph 1(1) is the occupational-requirement test. This starter does not decide that it is met.",
                )
                exclude("occupational_requirement", cats, cid, "proposed")
                continue
            if cats:
                if "disability_health" in cats:
                    _add_route(
                        routes,
                        "section_60",
                        "Section 60(1) covers a health question before an offer. Section 60(6) is not decided here.",
                    )
                    if _SICKNESS.search(text):
                        _add_route(
                            routes,
                            "section_15",
                            "Section 15(1) is about unfavourable treatment because of something arising in consequence of disability. This starter does not decide it.",
                        )
                exclude("protected_characteristic", cats, cid, "proposed")
                continue
            if cid not in known:
                exclude("untied", [], cid, "proposed")
                continue
            reviewed.append(
                {
                    "criterion_id": cid,
                    "included": False,
                    "reason": "pack questions are drafted from the criteria",
                    "excerpt_copied": False,
                }
            )
    result["reviewed_proposals"] = reviewed

    if occupational_requirement(corpus):
        _add_route(
            routes,
            "schedule_9",
            "Schedule 9 paragraph 1(1) is the occupational-requirement test. This starter does not decide that it is met.",
        )
    if positive_action_general(corpus):
        _add_route(
            routes,
            "section_158",
            "Section 158(2) is general positive action. Section 158(4) excludes action within section 159(3). This starter does not decide that either section permits the text.",
        )
    if positive_action_recruitment(corpus):
        _add_route(
            routes,
            "section_159",
            "Section 159(4) limits positive action in recruitment or promotion. This starter does not decide that the section permits the text.",
        )
    if "disability_health" in categories_in(corpus):
        _add_route(
            routes,
            "section_60",
            "Section 60(1) covers a health question before an offer. Section 60(6) is not decided here.",
        )

    invitation = request.get("invitation") if isinstance(request.get("invitation"), str) else ""
    job_invitation = job.get("invitation") if isinstance(job.get("invitation"), str) else ""
    invitation_cost = bool(_PAY.search(invitation) or _PAY.search(job_invitation))
    if invitation_cost:
        _add_route(
            routes,
            "section_20_cost",
            "Section 20(7) says A is not entitled to require a disabled person to pay A's costs of complying with the duty. This starter does not decide that the duty arose.",
        )
    result["invitation_cost"] = invitation_cost

    result["input_probe_categories"] = categories_in(corpus)
    result["exclusions"] = exclusions
    result["hr_routes"] = routes
    result["questions"] = questions
    result["question_count"] = len(questions)
    result["every_question_tied"] = all(row["tied_to_criterion"] and row["criterion_id"] for row in questions)
    tied_ids = {row["id"] for row in chosen}
    result["criteria_invented"] = any(row["criterion_id"] not in tied_ids for row in questions)
    result["outcome"] = "draft"
    result["right_to_work_statement_present"] = affirmed(corpus, "right to work") and (
        "nationality" not in categories_in(corpus)
    )
    _finish_common(result, question_date, corpus, guide, questions)
    return _force(result)


def _finish_common(result: dict, question_date: date, corpus: str, guide: dict, questions: list[dict]) -> None:
    routes = result.setdefault("hr_routes", [])
    prompts, prompt_info = _prompts(guide, routes)
    if result.get("invitation_cost"):
        prompt_info["cost_shifted"] = True
        prompt_info["below_opened_rule"] = True
    result["adjustment_prompts"] = prompts
    result["adjustment"] = prompt_info
    result["panel_guidance"] = _panel(guide)
    result["hr_routes"] = routes
    scale, info = _scale(guide)
    rubric = _rubric_for(questions, scale, info)
    result["rubric"] = rubric
    result["questions_hash"] = _hash_questions(questions)
    result["rubric_hash"] = _hash_rubric(rubric)
    result["questions_decision"] = None
    result["rubric_decision"] = None
    pins = pin_rows(question_date)
    result["pins"] = pins
    result["pins_not_confirmed"] = any(not row["confirmed_for_question_date"] for row in pins)
    result["statutory_note"] = statutory_note(question_date)
    result["ico"] = {
        "recruitment_page_final": ICO["recruitment_page"]["final"],
        "recruitment_page_status": ICO["recruitment_page"]["status"],
        "code_status": ICO["employment_practices_code"]["status"],
        "fee_relied_on": False,
    }
    guide_info = result.get("guide") or {}
    result["sources_current"] = not (
        result["pins_not_confirmed"]
        or guide_info.get("stale")
        or guide_info.get("not_yet_in_force")
        or guide_info.get("dates_unreadable")
    )
    result["pack_hash"] = _hash_pack(result)
    _mask_report(result, corpus)


def _mask_report(result: dict, corpus: str) -> None:
    _masked, local = mask_text(corpus)
    uk = redact_uk_identifiers(corpus)
    output_blob = json.dumps(
        {
            "questions": result.get("questions"),
            "adjustment_prompts": result.get("adjustment_prompts"),
            "panel_guidance": result.get("panel_guidance"),
            "exclusions": result.get("exclusions"),
        },
        ensure_ascii=False,
    )
    _out_masked, output_counts = mask_text(output_blob)
    result["masking"] = {
        "input_counts": local["counts"],
        "output_still_matched": output_counts["counts"],
        "uk_identifier_types": uk["types"],
        "uk_identifier_count": uk["count"],
        "values_stored": False,
        "output_is_anonymised": False,
        "experiment_08_called": True,
        "experiment_08_id": uk["experiment_id"],
        "body_copied": result.get("body_copied"),
        "described_as_anonymised": False,
    }


def _reject(pack: dict, reason: str) -> dict:
    pack["blocked_reason"] = reason
    pack["human_approval"] = None
    pack["approved_for_use"] = False
    return _force(pack)


def _prepare(pack: dict, decision: dict) -> dict | None:
    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    updated = deepcopy(pack)
    if not isinstance(decision, dict):
        return _reject(updated, "decision_unreadable")
    return updated


def record_questions_approval(pack: dict, directory: dict, decision: dict) -> dict:
    updated = _prepare(pack, decision)
    if updated.get("blocked_reason") == "decision_unreadable" and updated.get("human_approval") is None and decision is not None and not isinstance(decision, dict):
        return updated
    if not isinstance(decision, dict):
        return updated
    if updated.get("outcome") != "draft":
        return _reject(updated, updated.get("outcome") or "not_a_draft")
    if decision.get("item") != "questions" or decision.get("decision") not in {"accept", "reject"}:
        return _reject(updated, "item_mismatch")
    if decision.get("pack_hash") != updated.get("pack_hash"):
        return _reject(updated, "pack_hash_mismatch")
    person = _person(directory, decision.get("approver_ref"))
    if person is None or person.get("role") != "recruiter":
        return _reject(updated, "not_a_recruiter")
    recomputed = _hash_questions(updated.get("questions") or [])
    if decision.get("questions_hash") != updated.get("questions_hash") or decision.get("questions_hash") != recomputed:
        return _reject(updated, "questions_hash_mismatch")
    updated["questions_decision"] = decision["decision"]
    updated["questions_decided_by"] = person["ref"]
    updated["blocked_reason"] = None
    updated["human_approval"] = None
    updated["approved_for_use"] = False
    return _force(updated)


def record_rubric_approval(pack: dict, directory: dict, decision: dict) -> dict:
    updated = deepcopy(pack) if isinstance(pack, dict) else pack
    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    updated = deepcopy(pack)
    if not isinstance(decision, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "draft":
        return _reject(updated, updated.get("outcome") or "not_a_draft")
    if decision.get("item") != "rubric" or decision.get("decision") not in {"accept", "reject"}:
        return _reject(updated, "item_mismatch")
    if decision.get("pack_hash") != updated.get("pack_hash"):
        return _reject(updated, "pack_hash_mismatch")
    person = _person(directory, decision.get("approver_ref"))
    if person is None or person.get("role") != "recruiter":
        return _reject(updated, "not_a_recruiter")
    rubric = updated.get("rubric") or {}
    if rubric.get("unreadable") is True:
        return _reject(updated, "rubric_unreadable")
    recomputed = _hash_rubric(rubric)
    if decision.get("rubric_hash") != updated.get("rubric_hash") or decision.get("rubric_hash") != recomputed:
        return _reject(updated, "rubric_hash_mismatch")
    updated["rubric_decision"] = decision["decision"]
    updated["rubric_decided_by"] = person["ref"]
    updated["blocked_reason"] = None
    updated["human_approval"] = None
    updated["approved_for_use"] = False
    return _force(updated)


def record_hr_seen(pack: dict, directory: dict, seen: dict) -> dict:
    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    updated = deepcopy(pack)
    if not isinstance(seen, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "draft":
        return _reject(updated, updated.get("outcome") or "not_a_draft")
    if seen.get("item") != "hr-route" or seen.get("decision") != "seen":
        return _reject(updated, "item_mismatch")
    if seen.get("pack_hash") != updated.get("pack_hash"):
        return _reject(updated, "pack_hash_mismatch")
    person = _person(directory, seen.get("approver_ref"))
    if person is None or person.get("role") != "hr_partner":
        return _reject(updated, "not_an_hr_partner")
    route = None
    for row in updated.get("hr_routes") or []:
        if row.get("route_id") == seen.get("route_id"):
            route = row
            break
    if route is None:
        return _reject(updated, "route_mismatch")
    if seen.get("route_hash") != route_hash(route):
        return _reject(updated, "route_hash_mismatch")
    route["hr_seen"] = True
    route["decided"] = False
    route["seen_by"] = person["ref"]
    updated["blocked_reason"] = None
    updated["human_approval"] = None
    updated["approved_for_use"] = False
    updated["pack_hash"] = _hash_pack(updated)
    return _force(updated)


def _needs_boolean(updated: dict, approval: dict) -> str | None:
    guide = updated.get("guide") or {}
    if guide.get("dates_unreadable") or guide.get("stale") or guide.get("not_yet_in_force"):
        if approval.get("guide_seen") is not True:
            return "guide_not_seen"
    if updated.get("pins_not_confirmed") and approval.get("pins_seen") is not True:
        return "pins_not_seen"
    if updated.get("question_date_conflict") or updated.get("question_date_unreadable"):
        if approval.get("question_date_seen") is not True:
            return "question_date_not_seen"
    if updated.get("retention_unreadable") or updated.get("marking_unreadable"):
        if approval.get("labels_unreadable_seen") is not True:
            return "labels_not_seen"
    rubric = updated.get("rubric") or {}
    if rubric.get("below_guide_minimum") and approval.get("rubric_gap_seen") is not True:
        return "rubric_gap_not_seen"
    if (updated.get("adjustment") or {}).get("below_opened_rule") and approval.get("adjustment_seen") is not True:
        return "adjustment_not_seen"
    return None


def record_pack_approval(pack: dict, directory: dict, approval: dict) -> dict:
    if not isinstance(pack, dict):
        raise TypeError("pack must be an object")
    updated = deepcopy(pack)
    if not isinstance(approval, dict):
        return _reject(updated, "decision_unreadable")
    if updated.get("outcome") != "draft":
        return _reject(updated, updated.get("outcome") or "not_a_draft")
    if approval.get("item") != "pack" or approval.get("decision") != "approve":
        return _reject(updated, "item_mismatch")
    if approval.get("pack_hash") != updated.get("pack_hash") or approval.get("pack_hash") != _hash_pack(updated):
        return _reject(updated, "pack_hash_mismatch")
    person = _person(directory, approval.get("approver_ref"))
    if person is None or person.get("role") != "recruiter":
        return _reject(updated, "not_a_recruiter")
    if updated.get("questions_decision") != "accept":
        return _reject(updated, "questions_not_accepted")
    if updated.get("rubric_decision") != "accept":
        return _reject(updated, "rubric_not_accepted")
    if not updated.get("questions"):
        return _reject(updated, "no_questions")
    if (updated.get("rubric") or {}).get("unreadable") is True:
        return _reject(updated, "rubric_unreadable")
    for route in updated.get("hr_routes") or []:
        if route.get("hr_seen") is not True:
            return _reject(updated, "hr_route_not_seen")
    gate = _needs_boolean(updated, approval)
    if gate:
        return _reject(updated, gate)
    if updated.get("questions_hash") != _hash_questions(updated.get("questions") or []):
        return _reject(updated, "questions_hash_mismatch")
    if updated.get("rubric_hash") != _hash_rubric(updated.get("rubric") or {}):
        return _reject(updated, "rubric_hash_mismatch")
    updated["human_approval"] = {
        "approver_ref": person["ref"],
        "directory_role": "recruiter",
        "item": "pack",
        "pack_hash": updated["pack_hash"],
        "questions_hash": updated["questions_hash"],
        "rubric_hash": updated["rubric_hash"],
        "performed_by_agent": False,
    }
    updated["approved_for_use"] = True
    updated["blocked_reason"] = None
    updated["contacted"] = False
    updated["scheduled"] = False
    updated["scored"] = False
    updated["ranked"] = False
    updated["hiring_decision"] = False
    return _force(updated)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one synthetic interview pack. Experiment 65.")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = draft_pack(_load(args.request), _load(args.guide), _load(args.directory), args.as_of)
    except NotSynthetic:
        return 2
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return 2
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
