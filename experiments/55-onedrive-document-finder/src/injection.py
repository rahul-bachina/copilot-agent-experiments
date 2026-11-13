"""Untrusted file text. Instructions are recorded and not followed.

A phrase that follows a negation cue in the same sentence is not a match.
Hidden HTML comments are not used as search evidence. A sentence that says
the user has approved is not an approval.
"""

from __future__ import annotations

import re

ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SENTENCE = re.compile(r"[^.!?\n]+[.!?\n]?")

INSTRUCTIONS = (
    (re.compile(r"ignore (?:all|any|previous|the above) instructions[^.]*", re.IGNORECASE), "ignore_instructions"),
    (re.compile(r"never mind,?\s+ignore[^.]*", re.IGNORECASE), "never_mind_ignore"),
    (re.compile(r"you are now[^.]*", re.IGNORECASE), "you_are_now"),
    (re.compile(r"system prompt[^.]*", re.IGNORECASE), "system_prompt"),
    (re.compile(r"search all locations[^.]*", re.IGNORECASE), "search_all_locations"),
    (re.compile(r"ignore the selected locations[^.]*", re.IGNORECASE), "ignore_selection"),
    (re.compile(r"my clearance is[^.]*", re.IGNORECASE), "pretend_clearance"),
    (re.compile(r"clearance is top secret[^.]*", re.IGNORECASE), "pretend_clearance"),
    (re.compile(r"the user has approved[^.]*", re.IGNORECASE), "pretend_approval"),
    (re.compile(r"requesting user has approved[^.]*", re.IGNORECASE), "pretend_approval"),
    (re.compile(r"locations (?:are |have been )?confirmed[^.]*", re.IGNORECASE), "pretend_locations"),
    (re.compile(r"delete this file[^.]*", re.IGNORECASE), "delete_file"),
    (re.compile(r"move this file[^.]*", re.IGNORECASE), "move_file"),
    (re.compile(r"share this file[^.]*", re.IGNORECASE), "share_file"),
    (re.compile(r"change the permissions[^.]*", re.IGNORECASE), "change_permissions"),
    (re.compile(r"show the secret[^.]*", re.IGNORECASE), "show_secret"),
    (re.compile(r"return the secret[^.]*", re.IGNORECASE), "show_secret"),
    (re.compile(r"do not flag[^.]*", re.IGNORECASE), "do_not_flag"),
    (re.compile(r"don't flag[^.]*", re.IGNORECASE), "do_not_flag"),
    (re.compile(r"this is not a safeguarding[^.]*", re.IGNORECASE), "deny_safeguarding"),
)

NEGATION = re.compile(
    r"\b(?:not true that|it is not the case that|never mind,?\s+ignore|"
    r"no longer|is not|isn't|are not|aren't|not a|not an|not the)\b",
    re.IGNORECASE,
)


def _signals_in(text: str, hidden_in: str) -> list[dict]:
    found = []
    for pattern, signal in INSTRUCTIONS:
        if pattern.search(text):
            found.append({"signal": signal, "hidden_in": hidden_in, "followed": False})
    return found


def _clean_sentence(sentence: str) -> str:
    cleaned = sentence
    for pattern, _signal in INSTRUCTIONS:
        cleaned = pattern.sub(" ", cleaned)
    negation = NEGATION.search(cleaned)
    if negation:
        cleaned = cleaned[: negation.start()]
    return cleaned


def prepare_text(text: str) -> tuple[str, dict]:
    """Return matching text and an injection report. ``followed`` is false."""

    signals: list[dict] = []
    if ZERO_WIDTH.search(text):
        signals.append({"signal": "zero_width", "hidden_in": "zero_width", "followed": False})
    visible = ZERO_WIDTH.sub("", text)
    for comment in HTML_COMMENT.findall(visible):
        signals.extend(_signals_in(comment, "html_comment"))
    visible = HTML_COMMENT.sub(" ", visible)
    signals.extend(_signals_in(visible, "body"))
    parts = [_clean_sentence(sentence) for sentence in SENTENCE.findall(visible)]
    matching = re.sub(r"\s+", " ", " ".join(parts)).strip()
    seen = set()
    unique = []
    for signal in signals:
        if signal["signal"] in seen:
            continue
        seen.add(signal["signal"])
        unique.append(signal)
    return matching, {
        "detected": bool(unique),
        "followed": False,
        "signals": unique,
    }
