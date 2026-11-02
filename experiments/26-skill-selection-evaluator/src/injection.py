"""Detect prompt injection and prohibited-action requests in an utterance.

An injection that names a skill is recorded and is not a routing bonus.
A request to send, deploy, spend, delete, approve, or grant access routes
to a person. A sentence that forbids the action is not a hit.
"""

from __future__ import annotations

import re
from typing import Any

PROHIBITED_PAYLOAD_KEYS = frozenset(
    {
        "maintainer_validated",
        "skills_edited",
        "diff_applied",
        "applied",
        "deployed",
        "decision",
        "precision",
        "recall",
        "a3_recommended",
        "approved",
        "owner_approved",
        "selected_route",
        "selected_skill",
        "predicted",
        "route",
        "score_override",
    }
)

_INJECTION_SENTENCE = re.compile(
    r"("
    r"ignore (all |any )?(previous|prior|above|your) instructions"
    r"|disregard (the )?(rules|policy|instructions|catalogue)"
    r"|you must (now )?(select|use|route)"
    r"|select skill [a-z0-9-]+"
    r"|route (this |it )?to (skill )?[a-z0-9-]+"
    r"|force (the )?skill [a-z0-9-]+"
    r"|^\s*system\s*:"
    r"|^\s*developer\s*:"
    r")",
    re.I,
)

_SKILL_NAME = re.compile(r"\bskill\s+([a-z0-9]+(?:-[a-z0-9]+)*)", re.I)
_ROUTE_NAME = re.compile(r"\broute (?:this |it )?to\s+(?:skill\s+)?([a-z0-9]+(?:-[a-z0-9]+)*)", re.I)

_PROHIBITED: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "external_send",
        re.compile(
            r"\b(send|email|e-mail)\b(?:\s+\w+){0,8}\s+(email|e-mail|message|reply|letter|confirmation|response)\b",
            re.I,
        ),
    ),
    (
        "external_send",
        re.compile(r"\bemail (the |this )?(resident|requester|customer|user|claimant)\b", re.I),
    ),
    ("deploy", re.compile(r"\b(deploy|publish) (the |this )?(agent|bot|flow|skill)\b", re.I)),
    ("spend", re.compile(r"\b(take|make|authorise|authorize) (the |a )?payment\b", re.I)),
    ("spend", re.compile(r"\b(spend|transfer) (the )?(money|funds)\b", re.I)),
    (
        "production_write",
        re.compile(r"\bdelete (the |all )?(production |live )?(records|cases|files|data)\b", re.I),
    ),
    (
        "production_write",
        re.compile(r"\b(write|update) (the )?(production |live |housing )?(record|case|system)\b", re.I),
    ),
    (
        "approve_reject",
        re.compile(r"\b(approve|reject) (the )?(claim|application|request|payment|case)\b", re.I),
    ),
    ("exfiltrate", re.compile(r"\b(exfiltrate|leak) (the |all )?(data|records|personal data)\b", re.I)),
    ("grant_access", re.compile(r"\bgrant (admin|administrator|access)\b", re.I)),
)

_NEGATION = re.compile(r"\b(do not|don't|dont|never|must not|do not ever)\b", re.I)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[\n]+|(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def analyse_utterance(text: str) -> dict[str, Any]:
    """Return the text to score, the forced skill names, and any prohibited hits.

    Forced names are removed from the scoring text by dropping the injection
    sentence. They are not added to any skill's score.
    """
    sentences = split_sentences(text or "")
    kept: list[str] = []
    forced: list[str] = []
    injection_hits: list[str] = []
    for sentence in sentences:
        if _INJECTION_SENTENCE.search(sentence) and not _NEGATION.search(sentence):
            injection_hits.append(sentence)
            for pattern in (_SKILL_NAME, _ROUTE_NAME):
                for match in pattern.finditer(sentence):
                    name = match.group(1).lower()
                    if name not in forced and name not in {"the", "this", "a"}:
                        forced.append(name)
            continue
        kept.append(sentence)
    prohibited = _prohibited(kept)
    scoring_text = " ".join(kept).strip()
    return {
        "scoring_text": scoring_text,
        "injection_detected": bool(injection_hits),
        "injection_sentences": injection_hits,
        "forced_skills": forced,
        "prohibited": prohibited,
        "empty_after_injection": bool(injection_hits) and not scoring_text,
    }


def _prohibited(sentences: list[str]) -> list[str]:
    found: list[str] = []
    for sentence in sentences:
        if _NEGATION.search(sentence):
            continue
        for name, pattern in _PROHIBITED:
            if pattern.search(sentence) and name not in found:
                found.append(name)
    return found


def skill_text_injection(description: str, triggers: list[str]) -> dict[str, Any]:
    """A skill description that tries to force its own selection is a finding.

    The injection sentences are not used as trigger phrases. The rest of the
    description can still be scored.
    """
    sentences = split_sentences(description or "")
    bad_sentences = [
        sentence
        for sentence in sentences
        if _INJECTION_SENTENCE.search(sentence) and not _NEGATION.search(sentence)
    ]
    bad_triggers = [
        trigger
        for trigger in triggers
        if _INJECTION_SENTENCE.search(trigger) and not _NEGATION.search(trigger)
    ]
    return {
        "detected": bool(bad_sentences or bad_triggers),
        "sentences": bad_sentences,
        "triggers": bad_triggers,
    }


def strip_prohibited(node: Any, path: str = "") -> tuple[Any, list[str]]:
    """Copy the bundle without output-shaped keys. Values are not kept."""
    ignored: list[str] = []
    if isinstance(node, dict):
        copied: dict[str, Any] = {}
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if key in PROHIBITED_PAYLOAD_KEYS:
                ignored.append(here)
                continue
            child, child_ignored = strip_prohibited(value, here)
            copied[key] = child
            ignored.extend(child_ignored)
        return copied, ignored
    if isinstance(node, list):
        copied_list = []
        for index, value in enumerate(node):
            child, child_ignored = strip_prohibited(value, f"{path}[{index}]")
            copied_list.append(child)
            ignored.extend(child_ignored)
        return copied_list, ignored
    return node, ignored
