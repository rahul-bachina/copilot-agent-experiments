"""Channel text is untrusted. Instructions are recorded and not followed.

A refusal is not a positive instruction. A negation in front of a cue is not
a positive decision or action. A judgement about a named person, a private or
case cue, or a message marked for a person goes to a human. The text of a
held message is not copied.
"""

from __future__ import annotations

import re
from typing import Any

_INJECTION: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", "ignore previous instructions"),
    ("ignore_instructions", "ignore all instructions"),
    ("ignore_instructions", "ignore the above"),
    ("persona_override", "you are now"),
    ("post", "post a reply"),
    ("post", "post this"),
    ("post", "post in the channel"),
    ("reply", "reply in the channel"),
    ("reply", "reply to the channel"),
    ("react", "react to this"),
    ("react", "add a reaction"),
    ("mention", "@mention"),
    ("mention", "mention everyone"),
    ("forward", "forward this"),
    ("forward", "forward the message"),
    ("system", "system prompt"),
    ("autonomy_a3", "autonomy a3"),
    ("confirm_scope", "channels are confirmed"),
    ("confirm_scope", "digest is confirmed"),
    ("confirm_scope", "period is confirmed"),
)

_SIDE_EFFECT = re.compile(
    r"\b(post a reply|post this|post in the channel|reply in the channel|"
    r"reply to the channel|react to this|add a reaction|@mention|mention everyone|"
    r"forward this|forward the message)\b",
    re.I,
)
_REFUSAL = re.compile(r"\b(do not|don't|must not|never|cannot|can't)\b", re.I)

# The negation has to come before the cue. "We decided not to" is still a decision.
_LEADING_NEGATION = re.compile(
    r"\b(?:not true that|it is not true|it's not true|never mind|"
    r"ignore the (?:earlier |previous )?decision|ignore that decision|"
    r"disregard the (?:earlier |previous )?decision|"
    r"did not decide|didn't decide|we did not|we didn't|"
    r"no decision was|there was no decision|"
    r"it is not the case that|not the case that)\b",
    re.I,
)
_RETRACTION = re.compile(
    r"\b(?:never mind|ignore the (?:earlier |previous )?decision|"
    r"disregard the (?:earlier |previous )?decision)\b",
    re.I,
)
_DECISION_CUE = re.compile(
    r"\b(?:we decided|it was agreed|agreed that|agreed to|the decision is|decision:)\b",
    re.I,
)
_NAME = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
_JUDGEMENT_WORD = re.compile(
    r"\b(performance|underperform\w*|attitude|morale|sentiment|capability|competence|"
    r"star performer|difficult to work with)\b",
    re.I,
)
# Open route, beyond a fixed performance vocabulary. A named person plus an
# evaluative copula is enough. Wording that matches neither this nor a private
# cue, and is not marked on the message, is not detected.
_EVALUATIVE = re.compile(
    r"\b(?:is|seems|appears|feels|has been|was being)\b.{0,48}\b(?:"
    r"difficult|poor|great|awful|brilliant|slow|unreliable|outstanding|"
    r"a problem|struggling|disengaged|toxic|helpful|useless|weak|excellent)\b",
    re.I,
)
_RATE_PERSON = re.compile(
    r"\b(?:what do you think of|how is [A-Z][a-z]+ doing|rate [A-Z][a-z]+|"
    r"score [A-Z][a-z]+)\b",
    re.I,
)
_PRIVATE = re.compile(
    r"\b(?:in confidence|personal matter|between us|do not share|don't share|"
    r"grievance|disciplinary|sickness|off sick|hospital|medical|diagnosis|"
    r"safeguarding|union representative|trade union)\b",
    re.I,
)
_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_ZERO_WIDTH = {ord(char): None for char in ("\u200b", "\u200c", "\u200d", "\ufeff", "\u2060")}

PROHIBITED_KEYS = frozenset(
    {
        "posted",
        "replied",
        "reacted",
        "mentioned",
        "forwarded",
        "sent",
        "human_approval",
        "scope_confirmed",
        "digest_produced",
        "channels_confirmed",
        "model_called",
        "network_called",
        "graph_called",
        "foundry_called",
        "actions_taken",
        "a3_recommended",
    }
)


def plain(text: str) -> str:
    return str(text or "").translate(_ZERO_WIDTH)


def split_comments(text: str) -> tuple[str, list[str]]:
    hidden = [plain(part) for part in _COMMENT.findall(text or "")]
    visible = _COMMENT.sub(" ", text or "")
    return plain(visible), hidden


def is_refusal(sentence: str) -> bool:
    """A refusal of a side effect is not itself the side effect.

    The refusal word has to come first, and a side effect has to be in the
    sentence. "Do not post a reply." is a refusal. "Post a reply and do not
    wait." is not. "Never mind" has no side effect, so it is not a refusal.
    """
    refusal = _REFUSAL.search(sentence)
    effect = _SIDE_EFFECT.search(sentence)
    if not refusal or not effect:
        return False
    if effect.start() < refusal.start():
        return False
    return _SIDE_EFFECT.search(sentence, effect.end()) is None


def injection_codes(text: str) -> list[str]:
    found: list[str] = []
    for sentence in _sentences(plain(text)):
        if is_refusal(sentence):
            continue
        lowered = sentence.casefold()
        for code, phrase in _INJECTION:
            if phrase in lowered and code not in found:
                found.append(code)
    return found


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def sentences(text: str) -> list[str]:
    return _sentences(plain(text))


def leading_negation_blocks(sentence: str, cue_at: int) -> bool:
    """True when a negation or a retraction sits before the cue."""
    window = sentence[:cue_at]
    return _LEADING_NEGATION.search(window) is not None


def decision_cue(sentence: str) -> bool:
    match = _DECISION_CUE.search(sentence)
    if not match:
        return False
    if leading_negation_blocks(sentence, match.start()):
        return False
    if _RETRACTION.search(sentence):
        return False
    return True


def is_retraction(sentence: str) -> bool:
    return _RETRACTION.search(sentence) is not None


def hold_reason(text: str, message: dict[str, Any] | None = None) -> str | None:
    """Why a message goes to a person. None means it may be classified.

    A marked message is held even when no cue matches. That is the open route
    for anything else that should not be digested. Unmarked wording that hits
    neither a cue nor the evaluative pattern is not detected.
    """
    marker = ""
    if isinstance(message, dict):
        marker = str(message.get("sensitivity") or "").casefold()
    if marker in {"review", "hold", "sensitive"}:
        return "marked_for_a_person"
    body = plain(text)
    if _PRIVATE.search(body):
        return "sensitive_content"
    if _RATE_PERSON.search(body):
        return "asks_for_a_judgement"
    named = _NAME.search(body) is not None
    if named and _JUDGEMENT_WORD.search(body):
        return "judgement_about_a_named_person"
    if named and _EVALUATIVE.search(body):
        return "judgement_about_a_named_person"
    return None
