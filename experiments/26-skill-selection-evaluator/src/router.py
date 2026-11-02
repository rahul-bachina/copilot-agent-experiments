"""Score one utterance against a skill list. Do not call a model.

A declared trigger phrase is a substring match on the normalised utterance.
Description overlap counts only when at least two content tokens from the
description appear as whole tokens. A tie routes to a person. A prohibited
action routes to a person even when a trigger also matches. A skill named
inside a prompt-injection sentence gets no bonus.
"""

from __future__ import annotations

from typing import Any

try:
    from .injection import analyse_utterance
    from .skill_parse import Skill
    from .tokens import content_tokens, normalise_phrase, token_set
except ImportError:  # python src/report.py puts this directory on sys.path
    from injection import analyse_utterance
    from skill_parse import Skill
    from tokens import content_tokens, normalise_phrase, token_set

TRIGGER_WEIGHT = 5
TOKEN_WEIGHT = 1
MIN_TOKEN_HITS = 2

ROUTE_NONE = "none"
ROUTE_HUMAN = "human"


def route_utterance(skills: list[Skill], text: str) -> dict[str, Any]:
    analysed = analyse_utterance(text)
    scoring_text = analysed["scoring_text"]
    normalised = normalise_phrase(scoring_text)
    tokens = set(content_tokens(scoring_text))
    rows = []
    for skill in skills:
        score, trigger_hits, token_hits, zero_reason = _score(skill, normalised, tokens)
        rows.append(
            {
                "skill_id": skill.id,
                "score": score,
                "trigger_hits": trigger_hits,
                "token_hits": token_hits,
                "zero_reason": zero_reason,
            }
        )
    rows.sort(key=lambda row: (-row["score"], row["skill_id"]))
    predicted, reason = _choose(rows, analysed)
    forced = list(analysed["forced_skills"])
    return {
        "predicted": predicted,
        "reason": reason,
        "scores": rows,
        "scoring_text": scoring_text,
        "injection_detected": analysed["injection_detected"],
        "injection_sentences": list(analysed["injection_sentences"]),
        "forced_skills": forced,
        "selection_obeyed_injection": False,
        "prohibited": list(analysed["prohibited"]),
    }


def _score(
    skill: Skill,
    normalised: str,
    tokens: set[str],
) -> tuple[int, list[str], list[str], str]:
    for negative in skill.negative_triggers:
        phrase = normalise_phrase(negative)
        if phrase and phrase in normalised:
            return 0, [], [], "negative_trigger"
    trigger_hits = []
    for trigger in skill.triggers:
        phrase = normalise_phrase(trigger)
        if phrase and phrase in normalised:
            trigger_hits.append(trigger)
    token_hits = sorted(skill.tokens & tokens)
    score = TRIGGER_WEIGHT * len(trigger_hits)
    if len(token_hits) >= MIN_TOKEN_HITS:
        score += TOKEN_WEIGHT * len(token_hits)
    if score == 0 and not trigger_hits:
        return 0, [], token_hits, ""
    if score == 0:
        return 0, trigger_hits, token_hits, ""
    return score, trigger_hits, token_hits, ""


def _choose(rows: list[dict[str, Any]], analysed: dict[str, Any]) -> tuple[str, str]:
    if analysed["prohibited"]:
        return ROUTE_HUMAN, "prohibited_action"
    if analysed["empty_after_injection"]:
        return ROUTE_HUMAN, "injection_without_request"
    positive = [row for row in rows if row["score"] > 0]
    if not positive:
        return ROUTE_NONE, "no_skill"
    best = positive[0]["score"]
    tied = [row for row in positive if row["score"] == best]
    if len(tied) > 1:
        return ROUTE_HUMAN, "ambiguous_tie"
    winner = tied[0]
    if winner["trigger_hits"]:
        return f"skill:{winner['skill_id']}", "trigger"
    return f"skill:{winner['skill_id']}", "description"


def route_label(skill_id: str) -> str:
    return f"skill:{skill_id}"


def class_of(route: str) -> str:
    if route.startswith("skill:"):
        return route.split(":", 1)[1]
    return route
