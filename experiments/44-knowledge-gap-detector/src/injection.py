"""Pack text is data. Instructions inside it are recorded and not followed.

Phrase removal keeps the rest of the sentence. A negation such as
'Do not escalate.' is an instruction. 'Do not park on the yellow lines.'
is not, and it stays available for matching.
"""

from __future__ import annotations

import re

PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (all |any )?(previous |prior |above |your )?instructions"),
    ("disregard_rules", r"disregard (the )?(rules|catalogue|catalog|knowledge base|gaps)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("reveal_prompt", r"reveal (the |your )?prompt"),
    ("role_jailbreak", r"\bDAN\b"),
    ("override_stale", r"override (the )?stale"),
    ("do_not_escalate", r"do not escalate"),
    ("do_not_publish", r"do not publish"),
    ("do_not_ask_person", r"do not (ask for|offer) a (person|human)"),
    ("skip_manager", r"skip the knowledge manager"),
    ("publish_now", r"publish the article now"),
    ("edit_now", r"edit the article now"),
    ("delete_now", r"delete the article now"),
    ("mark_confirmed", r"mark (the |this )?gap confirmed"),
    ("treat_stale_current", r"treat (the )?stale article as current"),
    ("impersonate_manager", r"(i am|i'm|this is) the knowledge manager"),
    ("execute_now", r"reset the password now"),
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)


def signals_in(text: str) -> list[str]:
    if not text:
        return []
    return [name for name, pattern in _COMPILED if pattern.search(text)]


def content_for_matching(text: str) -> tuple[list[str], str]:
    """Return injection signals and the text left for matching.

    Only the matched instruction phrase is removed. The rest of the sentence
    stays, including a question that sat beside 'Do not escalate.'
    """

    raw = text or ""
    signals = signals_in(raw)
    cleaned = raw
    for _, pattern in _COMPILED:
        cleaned = pattern.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.strip(".,;:!?\"'()[]")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not re.search(r"[A-Za-z0-9]", cleaned):
        cleaned = ""
    return signals, cleaned
