#!/usr/bin/env python3
"""Evaluate skill and topic routing on a labelled set of utterances.

The same bundle and the same as-of date produce the same JSON. Utterance
text cannot set maintainer_validated, edit a skill, or choose the route.
Autonomy A3 is never the recommendation of this evaluator. The maintainer
validates routing tests.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from bridges import architecture_cross_check, instruction_review, manifest_skeleton
    from injection import skill_text_injection, split_sentences, strip_prohibited
    from metrics import agreement, confusable_pairs, per_class
    from rewrites import describe_quality, propose
    from router import class_of, route_utterance
    from skill_parse import SkillParseError, skill_from_markdown, skill_from_object
    from sources import DEFAULT_STALE_AFTER_DAYS, currency
    from tokens import token_set
else:
    from .bridges import architecture_cross_check, instruction_review, manifest_skeleton
    from .injection import skill_text_injection, split_sentences, strip_prohibited
    from .metrics import agreement, confusable_pairs, per_class
    from .rewrites import describe_quality, propose
    from .router import class_of, route_utterance
    from .skill_parse import SkillParseError, skill_from_markdown, skill_from_object
    from .sources import DEFAULT_STALE_AFTER_DAYS, currency
    from .tokens import token_set

LABEL = "DRAFT FOR MAINTAINER REVIEW"
CATALOGUE_ID = "G004"
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]


class ProhibitedAction(RuntimeError):
    """The evaluator was asked to validate, edit, or deploy."""


def evaluate(
    bundle: dict[str, Any],
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    approve: bool = False,
    apply: bool = False,
    edit_skills: bool = False,
    deploy: bool = False,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    if approve or apply or edit_skills or deploy:
        raise ProhibitedAction(
            "The evaluator cannot validate routing tests, edit a skill, apply a diff, or deploy. "
            "The maintainer decides."
        )
    date.fromisoformat(as_of)
    cleaned, ignored_keys = strip_prohibited(bundle)
    if not isinstance(cleaned, dict):
        raise ValueError("The bundle must be a JSON object.")
    base = base_dir or Path.cwd()
    skills, description_injection = _skills(cleaned, base)
    manifest = cleaned.get("manifest") if isinstance(cleaned.get("manifest"), dict) else None
    utterances = _utterances(cleaned, {skill.id for skill in skills})
    routed = []
    for item in utterances:
        outcome = route_utterance(skills, item["text"])
        predicted = outcome["predicted"]
        routed.append(
            {
                "id": item["id"],
                "text": item["text"],
                "kind": item["kind"],
                "expected": item["expected"],
                "expected_class": class_of(item["expected"]),
                "predicted": predicted,
                "predicted_class": class_of(predicted),
                "passed": predicted == item["expected"],
                "reason": outcome["reason"],
                "scores": outcome["scores"],
                "scoring_text": outcome["scoring_text"],
                "injection_detected": outcome["injection_detected"],
                "forced_skills": outcome["forced_skills"],
                "selection_obeyed_injection": False,
                "prohibited": outcome["prohibited"],
            }
        )
    classes = per_class(routed, [skill.id for skill in skills])
    pairs = confusable_pairs(skills, routed)
    confusable_with = _confusable_index(pairs)
    findings = [describe_quality(skill, confusable_with.get(skill.id, [])) for skill in skills]
    missed: dict[str, list[str]] = {}
    for row in routed:
        if row["expected"].startswith("skill:") and not row["passed"]:
            missed.setdefault(row["expected_class"], []).append(row["id"])
    for finding, injection in zip(findings, description_injection):
        finding["description_injection"] = injection
        if injection["detected"]:
            finding["ambiguous"] = True
            finding["needs_rewrite"] = True
            finding["reasons"].append(
                "The description or a trigger tries to force selection. That text was not used as a trigger."
            )
        missed_ids = missed.get(finding["skill_id"], [])
        finding["unselected_labelled_ids"] = missed_ids
        if missed_ids:
            finding["ambiguous"] = True
            finding["needs_rewrite"] = True
            finding["extra_sentence"] = (
                "Add the words a person would actually use. These labelled utterances were not selected: "
                + ", ".join(missed_ids)
                + "."
            )
            finding["reasons"].append(
                "Labelled utterances were not selected: " + ", ".join(missed_ids) + "."
            )
    proposed = propose(skills, findings)
    sources = currency(as_of, stale_after_days)
    skill_stale = _skill_staleness(skills, as_of, stale_after_days)
    sources_stale = any(row["stale"] for row in sources)
    skills_stale = any(row["stale"] for row in skill_stale)
    do_not_rely = sources_stale or skills_stale
    reviews = [
        instruction_review(skill.text, skill.path, skill.reviewed_on, as_of, manifest)
        for skill in skills
    ]
    for review in reviews:
        review["upstream_diff_applied"] = bool(review.get("diff_applied"))
        review["diff_applied"] = False
        review["owner_approved"] = False
        review["a3_recommended"] = False
    use_case = cleaned.get("use_case") if isinstance(cleaned.get("use_case"), dict) else None
    architecture = architecture_cross_check(use_case)
    skeleton = manifest_skeleton(
        str(cleaned.get("bundle_id") or ""),
        str(cleaned.get("title") or ""),
        as_of,
        needed=manifest is None,
    )
    injection_rows = [row for row in routed if row["injection_detected"]]
    prohibited_rows = [row for row in routed if row["prohibited"]]
    score = agreement(routed)
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "26",
        "autonomy": "A0",
        "bundle_id": str(cleaned.get("bundle_id") or ""),
        "title": str(cleaned.get("title") or ""),
        "as_of": as_of,
        "stale_after_days": stale_after_days,
        "decision": None,
        "maintainer_validated": False,
        "skills_edited": False,
        "diff_applied": False,
        "deployed": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "a3_recommended": False,
        "pins_reopened_for_this_experiment": False,
        "do_not_rely": do_not_rely,
        "routing_rules": {
            "trigger_weight": 5,
            "token_weight": 1,
            "minimum_description_tokens": 2,
            "tie_routes_to": "human",
            "prohibited_action_routes_to": "human",
            "injection_without_request_routes_to": "human",
            "no_match_routes_to": "none",
            "selection_obeyed_injection": False,
        },
        "agreement": score,
        "per_class": classes,
        "skills": [skill.to_public() for skill in skills],
        "utterances": routed,
        "routing_tests": _tests(routed),
        "no_skill": [row["id"] for row in routed if row["predicted"] == "none"],
        "human": [row["id"] for row in routed if row["predicted"] == "human"],
        "refusal": [row["id"] for row in routed if row["reason"] == "prohibited_action"],
        "confusable_pairs": pairs,
        "description_findings": findings,
        "proposed_diff": proposed,
        "prompt_injection": {
            "detected": bool(injection_rows) or any(item["detected"] for item in description_injection),
            "followed": False,
            "selection_obeyed_injection": False,
            "utterance_ids": [row["id"] for row in injection_rows],
            "forced_skills_ignored": sorted({name for row in injection_rows for name in row["forced_skills"]}),
            "prohibited_payload_keys_ignored": ignored_keys,
        },
        "prohibited_actions": {
            "count": len(prohibited_rows),
            "all_routed_to_human": all(row["predicted"] == "human" for row in prohibited_rows),
            "items": [
                {"id": row["id"], "predicted": row["predicted"], "kinds": row["prohibited"]}
                for row in prohibited_rows
            ],
        },
        "stale": {
            "skills": skill_stale,
            "sources_stale": sources_stale,
            "skills_stale": skills_stale,
            "do_not_rely": do_not_rely,
        },
        "sources": sources,
        "instruction_reviews": reviews,
        "architecture_cross_check": architecture,
        "manifest_skeleton": skeleton,
        "human_approval": _approval_points(do_not_rely, skeleton),
    }


def _approval_points(do_not_rely: bool, skeleton: dict[str, Any]) -> list[dict[str, Any]]:
    points = [
        {
            "action": "Validate routing tests",
            "approver": "Maintainer",
            "mandatory": True,
            "rationale": "Catalogue control for G004. The maintainer validates routing tests.",
        },
        {
            "action": "Accept or reject each description rewrite before it is kept",
            "approver": "Maintainer",
            "mandatory": True,
            "rationale": "The proposed diff stays unapplied. The evaluator does not edit a skill.",
        },
    ]
    if skeleton.get("generated"):
        points.append(
            {
                "action": "Rely on the manifest skeleton",
                "approver": "Governance owner",
                "mandatory": True,
                "rationale": "approved is false. The skeleton is not a sign-off.",
            }
        )
    if do_not_rely:
        points.append(
            {
                "action": "Re-open a pinned page or a review date before relying on a citation",
                "approver": "Maintainer",
                "mandatory": True,
                "rationale": "At least one date is older than the threshold, or a review date is missing.",
            }
        )
    return points


def _tests(routed: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "expected": row["expected"],
            "predicted": row["predicted"],
            "passed": row["passed"],
            "reason": row["reason"],
        }
        for row in routed
    ]


def _confusable_index(pairs: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for pair in pairs:
        left, right = pair["skills"]
        index.setdefault(left, []).append(right)
        index.setdefault(right, []).append(left)
    for key in index:
        index[key] = sorted(set(index[key]))
    return index


def _skills(bundle: dict[str, Any], base_dir: Path) -> tuple[list[Any], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    raw = bundle.get("skills")
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError("Each skill must be an object.")
            items.append(item)
    for rel in bundle.get("skill_repo_paths") or []:
        items.append({"repo_path": str(rel), "kind": "skill"})
    if not items:
        raise ValueError("The bundle needs at least one skill or topic.")
    skills = []
    injections = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        skill = _one_skill(item, index, base_dir)
        if skill.id in seen:
            raise ValueError(f"Duplicate skill id: {skill.id}")
        seen.add(skill.id)
        injection = skill_text_injection(skill.description, skill.triggers)
        if injection["detected"]:
            kept = [
                sentence
                for sentence in split_sentences(skill.description)
                if sentence not in injection["sentences"]
            ]
            skill.description = " ".join(kept).strip()
            skill.tokens = token_set(skill.description)
            skill.triggers = [trigger for trigger in skill.triggers if trigger not in injection["triggers"]]
        skills.append(skill)
        injections.append(injection)
    order = sorted(range(len(skills)), key=lambda position: skills[position].id)
    skills = [skills[position] for position in order]
    injections = [injections[position] for position in order]
    return skills, injections


def _one_skill(item: dict[str, Any], index: int, base_dir: Path):
    reviewed = item.get("reviewed_on")
    try:
        if item.get("repo_path"):
            path = REPO_ROOT / str(item["repo_path"])
            if not path.is_file():
                raise ValueError(f"Skill file not found: {item['repo_path']}")
            return skill_from_markdown(
                path.read_text(encoding="utf-8"),
                str(item["repo_path"]),
                reviewed_on=None if reviewed is None else str(reviewed),
                kind=str(item["kind"]) if item.get("kind") else None,
            )
        if item.get("text"):
            return skill_from_object(item, f"inline-{index}.md")
        relative = item.get("text_path") or item.get("path")
        if not relative:
            return skill_from_object(item, f"inline-{index}.md")
        path = _resolve(str(relative), base_dir)
        return skill_from_markdown(
            path.read_text(encoding="utf-8"),
            str(relative),
            reviewed_on=None if reviewed is None else str(reviewed),
            kind=str(item["kind"]) if item.get("kind") else None,
        )
    except SkillParseError as exc:
        raise ValueError(str(exc)) from exc


def _resolve(relative: str, base_dir: Path) -> Path:
    path = Path(relative)
    if path.is_absolute() and path.is_file():
        return path
    for root in (base_dir, EXPERIMENT_ROOT, REPO_ROOT):
        candidate = root / path
        if candidate.is_file():
            return candidate
    raise ValueError(f"Skill file not found: {relative}")


def _utterances(bundle: dict[str, Any], skill_ids: set[str]) -> list[dict[str, Any]]:
    raw = bundle.get("utterances")
    if not isinstance(raw, list) or not raw:
        raise ValueError("The bundle needs a labelled utterances list.")
    rows = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Each utterance must be an object.")
        utterance_id = str(item.get("id") or "")
        if not utterance_id or utterance_id in seen:
            raise ValueError("Each utterance needs its own id.")
        seen.add(utterance_id)
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Utterance {utterance_id} needs text.")
        expected = str(item.get("expected") or "")
        _check_expected(expected, skill_ids, utterance_id)
        kind = str(item.get("kind") or "ordinary")
        rows.append({"id": utterance_id, "text": text, "expected": expected, "kind": kind})
    return rows


def _check_expected(expected: str, skill_ids: set[str], utterance_id: str) -> None:
    if expected in {"none", "human"}:
        return
    if expected.startswith("skill:"):
        skill_id = expected.split(":", 1)[1]
        if skill_id in skill_ids:
            return
    raise ValueError(f"Utterance {utterance_id} has an expected route that is not in the catalogue: {expected}")


def _skill_staleness(skills: list[Any], as_of: str, stale_after_days: int) -> list[dict[str, Any]]:
    as_of_date = date.fromisoformat(as_of)
    rows = []
    for skill in skills:
        row: dict[str, Any] = {"skill_id": skill.id, "path": skill.path, "reviewed_on": skill.reviewed_on}
        if not skill.reviewed_on:
            row["stale"] = True
            row["age_days"] = None
            row["reason"] = "No review date was supplied."
        else:
            reviewed = date.fromisoformat(str(skill.reviewed_on))
            age = (as_of_date - reviewed).days
            row["age_days"] = age
            row["stale"] = age > stale_after_days
            row["reason"] = "Older than the threshold." if row["stale"] else "Inside the threshold."
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a skill-routing report. Do not edit a skill.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--edit-skills", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args(argv)
    if args.approve or args.apply or args.edit_skills or args.deploy:
        print(
            "The evaluator cannot validate routing tests, edit a skill, apply a diff, or deploy. "
            "The maintainer decides.",
            file=sys.stderr,
        )
        return 2
    bundle_path = Path(args.bundle)
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    report = evaluate(
        bundle,
        args.as_of,
        stale_after_days=args.stale_after_days,
        base_dir=bundle_path.parent,
    )
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
