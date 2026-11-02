"""Propose description rewrites. Do not write them to disk."""

from __future__ import annotations

import difflib
from typing import Any

try:
    from .skill_parse import Skill
except ImportError:  # python src/report.py puts this directory on sys.path
    from skill_parse import Skill

VAGUE_PHRASES = (
    "help with anything",
    "general assistant",
    "various tasks",
    "as appropriate",
    "if it seems right",
    "use your judgement",
    "use your judgment",
    "and more",
    "etc.",
)

MIN_DESCRIPTION_TOKENS = 4
MIN_DESCRIPTION_CHARACTERS = 40


def describe_quality(skill: Skill, confusable_with: list[str]) -> dict[str, Any]:
    vague = [phrase for phrase in VAGUE_PHRASES if phrase in skill.description.lower()]
    token_count = len(skill.tokens)
    missing = (not skill.description.strip()) or (
        token_count < MIN_DESCRIPTION_TOKENS and not skill.triggers and len(skill.description.strip()) < MIN_DESCRIPTION_CHARACTERS
    )
    if not skill.description.strip():
        missing = True
    ambiguous = bool(vague) or bool(confusable_with)
    reasons = []
    if not skill.description.strip():
        reasons.append("The description is empty.")
    elif missing:
        reasons.append(
            "The description has fewer than 4 content tokens and no trigger phrase, and it is shorter than 40 characters."
        )
    for phrase in vague:
        reasons.append(f"Vague phrase: {phrase}.")
    if confusable_with:
        names = ", ".join(confusable_with)
        reasons.append(f"The description or the triggers overlap with {names}.")
    return {
        "skill_id": skill.id,
        "path": skill.path,
        "missing": missing,
        "ambiguous": ambiguous,
        "vague_phrases": vague,
        "confusable_with": confusable_with,
        "reasons": reasons,
        "needs_rewrite": missing or ambiguous,
    }


def propose(skills: list[Skill], findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Append a rewrite block. The original description is not otherwise edited."""
    by_id = {skill.id: skill for skill in skills}
    files = []
    chunks = []
    for finding in findings:
        if not finding["needs_rewrite"]:
            continue
        skill = by_id[finding["skill_id"]]
        suggested = _suggested(
            skill,
            finding["confusable_with"],
            finding["missing"] or bool(finding["vague_phrases"]),
            finding.get("extra_sentence") or "",
        )
        original = skill.text if skill.text.endswith("\n") else skill.text + "\n"
        block = (
            "\n## Proposed description rewrite\n\n"
            "Not applied. The maintainer validates routing tests and decides whether to keep this sentence.\n\n"
            f"Suggested description: {suggested}\n"
        )
        proposed = original.rstrip() + "\n" + block
        diff = "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                proposed.splitlines(keepends=True),
                fromfile="a/" + skill.path,
                tofile="b/" + skill.path,
            )
        )
        files.append(
            {
                "path": skill.path,
                "skill_id": skill.id,
                "suggested_description": suggested,
                "diff": diff,
                "applied": False,
            }
        )
        if diff:
            chunks.append(diff)
    return {"applied": False, "diff": "".join(chunks), "files": files}


def _suggested(skill: Skill, others: list[str], replace: bool, extra: str) -> str:
    if replace:
        sentence = (
            f"{skill.id} does one named job. State that job, the trigger phrases, "
            "and the requests that must go to a person."
        )
    else:
        sentence = skill.description.strip().rstrip(".") + "."
    if others:
        sentence = sentence.rstrip(".") + ". Do not use this skill for " + ", ".join(others) + "."
    if extra:
        sentence = sentence.rstrip(".") + ". " + extra.strip()
    return sentence
