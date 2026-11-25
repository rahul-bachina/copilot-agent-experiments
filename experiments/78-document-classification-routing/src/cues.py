"""Class phrases, concerns, and instructions.

Class phrases use the negation window. Distress, safeguarding, and
whistleblowing stems still match when the sentence denies them. A
safeguarding policy title is not a safeguarding cue.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

if __package__ in {None, ""}:
    from negate import affirmed, bounded_at, sentences
else:
    from .negate import affirmed, bounded_at, sentences

ROOT = Path(__file__).resolve().parents[1]

_INSTRUCTIONS = (
    (re.compile(r"ignore (?:all|any|previous|the above) instructions", re.I), "ignore_instructions"),
    (re.compile(r"\byou are now\b", re.I), "you_are_now"),
    (re.compile(r"\bsystem prompt\b", re.I), "system_prompt"),
    (re.compile(r"\bclassify this as\b", re.I), "classify_as"),
    (re.compile(r"\bfile this\b", re.I), "file_this"),
    (re.compile(r"\bmove this\b", re.I), "move_this"),
    (re.compile(r"\bdelete this\b", re.I), "delete_this"),
    (re.compile(r"\bsend this\b", re.I), "send_this"),
    (re.compile(r"\bdrop the legal hold\b", re.I), "drop_legal_hold"),
    (re.compile(r"\bstrip the (?:retention|marking|legal hold)\b", re.I), "strip_label"),
    (re.compile(r"\bthere is no legal hold\b", re.I), "deny_legal_hold"),
    (re.compile(r"\bdo not queue\b", re.I), "do_not_queue"),
    (re.compile(r"\bdon't queue\b", re.I), "do_not_queue"),
    (re.compile(r"\bmark this\b", re.I), "mark_this"),
    (re.compile(r"\bdowngrade to\b", re.I), "downgrade"),
    (re.compile(r"\bdisregard the (?:marking|hold|retention)\b", re.I), "disregard_label"),
)

_APPROVAL = (
    "has approved",
    "already approved",
    "approval: granted",
    "consider this approved",
    "human approval is recorded",
    "this document is approved",
)

_DISTRESS = (
    "can't cope",
    "cannot cope",
    "not coping",
    "suicidal",
    "kill myself",
    "end my life",
    "end their life",
    "end her life",
    "end his life",
    "do not feel safe",
    "don't feel safe",
    "not safe",
    "frightened",
    "scared for my safety",
    "scared for their safety",
    "in distress",
    "feel desperate",
    "i am vulnerable",
    "feels vulnerable",
    "adult at risk",
)

_SAFEGUARDING = (
    "safeguarding concern",
    "safeguarding referral",
    "safeguarding disclosure",
    "child protection",
    "adult at risk",
    "being harmed",
    "hurting them",
    "domestic abuse",
)

_WHISTLE = (
    "whistleblow",
    "whistle-blow",
    "whistleblowing",
    "whistleblower",
    "protected disclosure",
    "public interest disclosure",
    "a grievance",
)

_URGENT = (
    "treat as urgent",
    "is urgent",
    "as urgent",
    "needed today",
    "act today",
    "before the end of the day",
    "immediate risk",
    "cannot wait",
    "this is an emergency",
)

_CARVE = re.compile(
    r"\b(?:except|unless|provided that|subject to|save that|apart from|other than)\b",
    re.I,
)
_CLEARANCE = re.compile(r"\bmy clearance is\b", re.I)
_ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def load_taxonomy() -> dict:
    return json.loads((ROOT / "fixtures" / "taxonomy.json").read_text(encoding="utf-8"))


def normalise(text: str) -> tuple[str, list[str]]:
    """Drop zero-width characters. Record the signal. Do not follow it."""

    signals: list[str] = []
    if not isinstance(text, str):
        return "", signals
    if _ZERO_WIDTH.search(text):
        signals.append("zero_width")
    return _ZERO_WIDTH.sub("", text), signals


def visible_text(text: str) -> tuple[str, list[str]]:
    """HTML comments are not class evidence. Instructions inside them are kept as signals."""

    signals: list[str] = []
    comments = _HTML_COMMENT.findall(text)
    for comment in comments:
        signals.extend(instruction_signals(comment))
        signals.extend(approval_signals(comment))
    visible = _HTML_COMMENT.sub(" ", text)
    return visible, signals


def instruction_signals(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text):
        for pattern, signal in _INSTRUCTIONS:
            if pattern.search(sentence) and signal not in found:
                found.append(signal)
    return found


def is_instruction(sentence: str) -> bool:
    return any(pattern.search(sentence) for pattern, _signal in _INSTRUCTIONS)


def approval_signals(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text):
        if is_instruction(sentence):
            continue
        for phrase in _APPROVAL:
            if affirmed(sentence, phrase) and phrase not in found:
                found.append(phrase)
    return found


def without_instructions(text: str) -> str:
    kept = [sentence for sentence in sentences(text) if not is_instruction(sentence)]
    return "\n".join(kept)


def _stem(text: str, phrases: tuple[str, ...]) -> bool:
    for sentence in sentences(text):
        folded = sentence.casefold()
        for phrase in phrases:
            if bounded_at(folded, phrase.casefold()):
                return True
    return False


def concerns_in(text: str) -> dict:
    distress = _stem(text, _DISTRESS)
    safeguarding = _stem(text, _SAFEGUARDING)
    whistle = _stem(text, _WHISTLE)
    urgent = any(affirmed(text, phrase) for phrase in _URGENT)
    return {
        "distress": distress,
        "safeguarding": safeguarding,
        "whistleblowing": whistle,
        "urgent": urgent,
        "cue_copied": False,
    }


def _hits_in_sentence(sentence: str, phrases: list[str]) -> list[str]:
    found: list[str] = []
    for phrase in sorted(phrases, key=len, reverse=True):
        if not affirmed(sentence, phrase):
            continue
        if any(phrase.casefold() in earlier.casefold() for earlier in found):
            continue
        found.append(phrase)
    return found


def match_classes(text: str, classes: list[dict]) -> list[dict]:
    """Longest phrase wins. A carve-out in the same sentence blocks a clean class."""

    usable = without_instructions(text)
    rows = []
    for item in classes:
        strong: list[str] = []
        weak: list[str] = []
        carve = False
        for sentence in sentences(usable):
            strong_hits = _hits_in_sentence(sentence, list(item.get("strong") or []))
            weak_hits = _hits_in_sentence(sentence, list(item.get("weak") or []))
            weak_hits = [
                phrase
                for phrase in weak_hits
                if not any(phrase.casefold() in stem.casefold() for stem in strong_hits)
            ]
            if strong_hits or weak_hits:
                if _CARVE.search(sentence):
                    carve = True
            for phrase in strong_hits:
                if phrase not in strong:
                    strong.append(phrase)
            for phrase in weak_hits:
                if phrase not in weak and not any(phrase.casefold() in stem.casefold() for stem in strong):
                    weak.append(phrase)
        if strong or weak:
            rows.append(
                {
                    "class_id": item["id"],
                    "title": item["title"],
                    "strong": strong,
                    "weak": weak,
                    "carve_out": carve,
                }
            )
    rows.sort(key=lambda row: (-(len(row["strong"]) * 10 + len(row["weak"])), row["class_id"]))
    return rows


def category_hit(name: str, text: str) -> bool:
    cleaned, _signals = normalise(text if isinstance(text, str) else "")
    visible, _more = visible_text(cleaned)
    if name == "distress":
        return _stem(visible, _DISTRESS)
    if name == "safeguarding":
        return _stem(visible, _SAFEGUARDING)
    if name == "whistleblowing":
        return _stem(visible, _WHISTLE)
    if name == "urgent":
        return any(affirmed(visible, phrase) for phrase in _URGENT)
    if name == "embedded_instruction":
        return bool(instruction_signals(visible))
    if name == "approval_marker":
        return bool(approval_signals(visible))
    if name in {"foi", "sar"}:
        class_id = "foi_request" if name == "foi" else "subject_access_request"
        classes = load_taxonomy()["classes"]
        return any(row["class_id"] == class_id for row in match_classes(visible, classes))
    return False
