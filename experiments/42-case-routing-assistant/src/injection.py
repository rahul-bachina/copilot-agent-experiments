"""Case text is data. Instructions inside it are recorded and not followed."""

from __future__ import annotations

import re

PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore (all |any )?(previous |prior |above |your )?instructions"),
    ("disregard_rules", r"disregard (the )?(rules|catalogue|catalog|routing)"),
    ("you_are_now", r"you are now"),
    ("system_prompt", r"system prompt"),
    ("reveal_prompt", r"reveal (the |your )?prompt"),
    ("role_jailbreak", r"\bDAN\b"),
    ("override_human", r"override (the )?(human|approval|queue owner)"),
    ("override_stale", r"override (the )?stale"),
    ("close_case", r"\bclose (this |the )?case\b"),
    ("reroute_now", r"\breroute (this |the )?case\b"),
    ("mark_rerouted", r"\bmark (this |the case )?as rerouted\b"),
    ("change_the_rule", r"\bchange the routing rule\b"),
    ("not_vulnerable", r"\b(this is|i am|i'm) not vulnerable\b"),
    ("route_to_bot", r"\broute (this |it |me )?to the bot\b"),
    ("skip_confirmation", r"\bskip (the )?confirmation\b"),
    ("pretend_approved", r"\b(rule|queue) (is |has been )?already approved\b"),
)

_COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)


def signals_in(text: str) -> list[str]:
    if not text:
        return []
    return [name for name, pattern in _COMPILED if pattern.search(text)]


def sentence_is_instruction(sentence: str) -> bool:
    return bool(signals_in(sentence))


def strip_instruction_sentences(text: str) -> str:
    """Drop sentences that are themselves instructions. Leave the rest."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    kept = [part for part in parts if part and not sentence_is_instruction(part)]
    return " ".join(kept).strip()
