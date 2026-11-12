"""Label sentences that already say what they are. Do not paraphrase.

A decision, a question, an action, or an item for the requesting user is the
sentence itself. An owner is a name written in that sentence. A negation in
front of the cue is not a positive match. A later retraction in the same
message drops the decisions from that message.
"""

from __future__ import annotations

import re
from typing import Any

from injection import (
    decision_cue,
    injection_codes,
    is_refusal,
    is_retraction,
    sentences,
)

_QUESTION_LABEL = re.compile(r"\bopen question\s*:", re.I)
_ACTION_FOR = re.compile(
    r"\bAction for ([A-Z][a-z]+ [A-Z][a-z]+)\s*:\s*\S",
)
_WILL = re.compile(
    r"(?<![A-Za-z])([A-Z][a-z]+ [A-Z][a-z]+) will\b",
)
_NOT_TRUE_BEFORE = re.compile(
    r"\b(?:not true that|it is not true|it's not true|it is not the case that)\b",
    re.I,
)


def _blocked(sentence: str, at: int) -> bool:
    return _NOT_TRUE_BEFORE.search(sentence[:at]) is not None


def _action_owner(sentence: str) -> tuple[str | None, bool]:
    """Return the stated owner, and whether a cue was blocked by a leading negation."""
    for pattern in (_ACTION_FOR, _WILL):
        match = pattern.search(sentence)
        if not match:
            continue
        if _blocked(sentence, match.start()):
            return None, True
        return match.group(1), False
    return None, False


def _is_question(sentence: str) -> bool:
    if sentence.rstrip().endswith("?"):
        return True
    return _QUESTION_LABEL.search(sentence) is not None


def extract_message(text: str, *, display_name: str) -> dict[str, Any]:
    """Classify one redacted message. Injection sentences are not points."""
    decisions: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    attention: list[dict[str, Any]] = []
    negated: list[dict[str, Any]] = []
    injections: list[dict[str, Any]] = []
    cancel_decisions = False
    name_fold = display_name.casefold().strip()

    for index, sentence in enumerate(sentences(text), start=1):
        codes = injection_codes(sentence)
        if codes or is_refusal(sentence):
            injections.append(
                {
                    "line": index,
                    "codes": codes or ["refused_side_effect"],
                    "followed": False,
                }
            )
            continue
        if is_retraction(sentence):
            cancel_decisions = True
            negated.append({"line": index, "positive_match": False, "reason": "retraction"})
            continue
        cue = decision_cue(sentence)
        # A question is not relabelled as a decision.
        if _is_question(sentence) and not cue:
            questions.append({"line": index, "text": sentence})
        elif cue:
            decisions.append({"line": index, "text": sentence})
        elif _is_question(sentence):
            questions.append({"line": index, "text": sentence})
        else:
            match = _DECISION_LOOKALIKE.search(sentence)
            if match:
                negated.append(
                    {"line": index, "positive_match": False, "reason": "negation_before_cue"}
                )

        owner, blocked_action = _action_owner(sentence)
        if blocked_action:
            negated.append(
                {"line": index, "positive_match": False, "reason": "negation_before_cue"}
            )
        elif owner and not is_retraction(sentence) and not injection_codes(sentence):
            actions.append({"line": index, "text": sentence, "owner": owner})

        if name_fold and name_fold in sentence.casefold() and not injection_codes(sentence):
            if not is_retraction(sentence):
                attention.append({"line": index, "text": sentence})

    if cancel_decisions:
        for row in decisions:
            negated.append(
                {
                    "line": row["line"],
                    "positive_match": False,
                    "reason": "cancelled_by_later_retraction",
                }
            )
        decisions = []

    return {
        "decisions": decisions,
        "open_questions": questions,
        "actions": actions,
        "attention": attention,
        "negated": negated,
        "injections": injections,
    }


_DECISION_LOOKALIKE = re.compile(
    r"\b(?:we decided|it was agreed|agreed that|agreed to|the decision is|decision:)\b",
    re.I,
)
