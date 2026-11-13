#!/usr/bin/env python3
"""Propose a slide outline from approved passages.

The outline quotes a passage or it records a gap. It does not invent a
figure, a quote, a logo, a customer, or an outcome. A claim is marked
sourced only when Experiment 29's score_claim says the quote is supported.
The presenter approves the outline and every citation before any slide file
is produced. This module does not publish, send, or share.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

from sources import NOT_OPENED, PINNED_ON, SOURCE_WINDOW_DAYS, SOURCES

LABEL = "OUTLINE FOR PRESENTER APPROVAL. NOT A DECK. NOT SHARED."
PACK_ID = re.compile(r"^SYN-DECK-\d{4}$")
PRESENTER_ID = re.compile(r"^SYN-PRES-\d{3}$")

GAP_NOTE = "No approved source covers this point. It is not sourced."

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "presenter_approved",
        "slides_produced",
        "shared",
        "published",
        "sent",
        "uploaded",
        "sourced",
        "approval",
        "logo_added",
        "customer_invented",
        "outcome_invented",
        "figure_invented",
    }
)

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "ignore the sources",
    "ignore the approved",
    "disregard your rules",
    "you are now",
    "system prompt",
    "publish the deck",
    "share the deck",
    "send the deck",
    "upload the deck",
    "mark all claims as sourced",
    "mark this claim as sourced",
    "the presenter has approved",
    "presenter approved",
    "invent a logo",
    "invent a customer",
    "invent a figure",
    "invent an outcome",
    "invent a quote",
    "remove the marking",
    "strip the marking",
    "downgrade the marking",
    "ignore the marking",
    "never mind",
)

NEGATORS = (
    "not true that",
    "it is not the case that",
    "never mind",
    "do not",
    "don't",
    "does not",
    "doesn't",
    "cannot",
    "can't",
    "no longer",
    "must not",
    "should not",
    "without claiming",
)

PURE_NEGATION = re.compile(
    r"^(?:no|nope|not true|never mind|ignore that)[.!]?$",
    re.IGNORECASE,
)

SAFEGUARDING = (
    "self-harm",
    "self harm",
    "suicide",
    "suicidal",
    "kill myself",
    "safeguarding",
    "domestic abuse",
    "domestic violence",
    "child abuse",
    "sexual abuse",
    "i am frightened",
    "in danger",
)

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?:\+44\s?7\d{3}\s?\d{6}|07\d{3}\s?\d{6}|07\d{9})")
POSTCODE_RE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
DOB_RE = re.compile(r"(?i)\b(?:date of birth|d\.?o\.?b\.?|born on)\b")
TITLE_NAME_RE = re.compile(
    r"\b(?:Mr|Mrs|Ms|Mx|Dr|Cllr|Councillor)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b"
)
PAIR_NAME_RE = re.compile(r"\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b")
ALLOWED_NAME_WORDS = frozenset(
    {
        "Northmere",
        "Digital",
        "Services",
        "Aldergate",
        "Borough",
        "Council",
        "Leadership",
        "Team",
        "October",
        "November",
        "December",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "Official",
        "Sensitive",
        "Secret",
        "Routine",
        "Requests",
        "Approved",
        "Catalogue",
        "Staff",
        "British",
        "English",
        "Government",
        "Public",
        "Sector",
        "Plain",
        "Published",
        "Documents",
        "Service",
        "Desk",
        "Legal",
        "Hold",
        "Recipients",
        "Only",
    }
)

MARKING_RE = re.compile(
    r"\b(TOP SECRET|OFFICIAL-SENSITIVE(?:\s*-\s*RECIPIENTS ONLY)?|OFFICIAL|SECRET)\b",
    re.IGNORECASE,
)
MARKING_RANK = {
    "OFFICIAL": 1,
    "OFFICIAL-SENSITIVE": 2,
    "OFFICIAL-SENSITIVE - RECIPIENTS ONLY": 3,
    "SECRET": 4,
    "TOP SECRET": 5,
}
LEGAL_HOLD_RE = re.compile(r"(?i)\blegal hold\b|\bdo not destroy\b")
RETENTION_RE = re.compile(r"(?i)\bretain until\b|\bretention\b")

APPROVE = "presenter_approve_outline_and_citations"
REVISE = "presenter_request_revision"
REJECT = "reject_outline"
ALLOWED_DECISIONS = frozenset({APPROVE, REVISE, REJECT})
PROHIBITED_DECISIONS = frozenset(
    {
        "publish",
        "publish_deck",
        "share",
        "share_deck",
        "send",
        "send_deck",
        "upload",
        "invent_claim",
        "invent_figure",
        "add_logo",
        "mark_sourced",
        "produce_slides",
    }
)

EXPERIMENTS = Path(__file__).resolve().parents[2]
_CACHE: dict = {}


class NarrativeForbidden(RuntimeError):
    """No share, publish, send, or invented claim."""


def share_deck(*_args, **_kwargs) -> None:
    raise NarrativeForbidden("the agent does not share a deck")


def publish_deck(*_args, **_kwargs) -> None:
    raise NarrativeForbidden("the agent does not publish a deck")


def send_deck(*_args, **_kwargs) -> None:
    raise NarrativeForbidden("the agent does not send a deck")


def invent_claim(*_args, **_kwargs) -> None:
    raise NarrativeForbidden("the agent does not invent a claim")


def _load(folder: str, filename: str, alias: str):
    path = EXPERIMENTS / folder / "src" / filename
    if not path.is_file():
        raise RuntimeError(
            f"{folder} is required at experiments/{folder}. "
            "This starter does not carry its own copy."
        )
    saved = {}
    for name in ("sources", "tokens", "siblings", "score", "normalise"):
        if name in sys.modules:
            saved[name] = sys.modules.pop(name)
    src = str(path.parent)
    sys.path.insert(0, src)
    try:
        spec = importlib.util.spec_from_file_location(alias, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[alias] = module
        spec.loader.exec_module(module)
    finally:
        if src in sys.path:
            sys.path.remove(src)
        for name in ("sources", "tokens", "siblings", "score", "normalise"):
            sys.modules.pop(name, None)
        sys.modules.update(saved)
    return module


def _siblings():
    if _CACHE:
        return _CACHE
    score = _load("29-groundedness-evaluation", "score.py", "exp29_score_for_exp53")
    grounded_sources = _load(
        "29-groundedness-evaluation", "sources.py", "exp29_sources_for_exp53"
    )
    normalise = _load(
        "36-cross-source-validation", "normalise.py", "exp36_normalise_for_exp53"
    )
    _CACHE.update(
        {
            "score_claim": score.score_claim,
            "passage_currency": score.passage_currency,
            "normalise_text": score.normalise,
            "extract_numbers": score.extract_numbers,
            "stale_after_days": grounded_sources.DEFAULT_STALE_AFTER_DAYS,
            "normalise_value": normalise.normalise_value,
            "classify_values": normalise.classify_values,
            "display_fold": normalise.display_fold,
        }
    )
    return _CACHE


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def rules_are_current(as_of: date) -> bool:
    """True when as_of is within the starter window. Equal to the window is current."""
    return (as_of - PINNED_ON).days <= SOURCE_WINDOW_DAYS


def _norm(text: str) -> str:
    return _siblings()["normalise_text"](text).strip(" .")


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _sentence_negated(sentence: str) -> bool:
    lower = sentence.lower()
    if any(neg in lower for neg in NEGATORS):
        return True
    if re.search(r"\bnot\b", lower):
        return True
    if re.search(r"\bno\b", lower):
        return True
    return False


def _injection_signals(sentence: str) -> list[str]:
    lower = sentence.lower()
    return [pattern for pattern in INJECTION_PATTERNS if pattern in lower]


def _prepare(text: str) -> tuple[list[tuple[str, str, str | None]], list[str]]:
    """Sentences that may be matched, and injection patterns seen.

    A sentence that contains an instruction is not matched. A sentence that
    contains a negation is not matched. A following sentence that is only
    'no' negates the sentence before it.
    """
    signals: list[str] = []
    marked: list[tuple[str, str, str | None]] = []
    for sentence in _sentences(text):
        found = _injection_signals(sentence)
        if found:
            for pattern in found:
                if pattern not in signals:
                    signals.append(pattern)
            marked.append(("drop", sentence, "injection"))
            continue
        if PURE_NEGATION.match(sentence):
            if marked and marked[-1][0] == "keep":
                marked[-1] = ("drop", marked[-1][1], "negated")
            marked.append(("drop", sentence, "negated"))
            continue
        if _sentence_negated(sentence):
            marked.append(("drop", sentence, "negated"))
            continue
        marked.append(("keep", sentence, None))
    return marked, signals


def _personal_categories(text: str) -> list[str]:
    found: list[str] = []

    def add(name: str) -> None:
        if name not in found:
            found.append(name)

    if EMAIL_RE.search(text):
        add("email")
    if PHONE_RE.search(text):
        add("phone")
    if DOB_RE.search(text):
        add("date_of_birth")
    if POSTCODE_RE.search(text):
        add("postal_address")
    if TITLE_NAME_RE.search(text):
        add("name")
    else:
        for first, second in PAIR_NAME_RE.findall(text):
            if first not in ALLOWED_NAME_WORDS or second not in ALLOWED_NAME_WORDS:
                add("name")
                break
    return found


def _safeguarding(text: str) -> bool:
    lower = text.lower()
    return any(cue in lower for cue in SAFEGUARDING)


def _canonical_marking(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw).strip().upper()
    text = text.replace(" - ", " - ")
    if text.startswith("OFFICIAL-SENSITIVE"):
        if "RECIPIENTS ONLY" in text:
            return "OFFICIAL-SENSITIVE - RECIPIENTS ONLY"
        return "OFFICIAL-SENSITIVE"
    return text


def _walk_strings(node) -> list[str]:
    found: list[str] = []
    if isinstance(node, str):
        found.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            found.extend(_walk_strings(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_walk_strings(value))
    return found


def _strip(node, path: str = "") -> tuple[object, list[str]]:
    found: list[str] = []
    if isinstance(node, dict):
        clean = {}
        for key, value in node.items():
            nested = f"{path}.{key}" if path else key
            if key in PROHIBITED_KEYS:
                found.append(key)
                continue
            if key in {"protective_marking", "legal_hold"} and path:
                found.append(key)
                continue
            child, child_found = _strip(value, nested)
            found.extend(child_found)
            clean[key] = child
        return clean, found
    if isinstance(node, list):
        clean_list = []
        for index, value in enumerate(node):
            child, child_found = _strip(value, f"{path}[{index}]")
            found.extend(child_found)
            clean_list.append(child)
        return clean_list, found
    return node, found


def _markings(pack: dict) -> dict:
    texts = _walk_strings(pack)
    found: list[str] = []
    for text in texts:
        for match in MARKING_RE.findall(text):
            token = _canonical_marking(match)
            if token in MARKING_RANK and token not in found:
                found.append(token)
    found.sort(key=lambda item: MARKING_RANK[item], reverse=True)
    legal = pack.get("legal_hold") is True or any(LEGAL_HOLD_RE.search(text) for text in texts)
    retention: list[str] = []
    for text in texts:
        for match in RETENTION_RE.findall(text):
            phrase = match.lower()
            if phrase not in retention:
                retention.append(phrase)
        if LEGAL_HOLD_RE.search(text):
            for phrase in ("legal hold", "do not destroy"):
                if phrase in text.lower() and phrase not in retention and phrase != "legal hold":
                    retention.append(phrase)
            if "legal hold" in text.lower() and "legal hold" not in retention:
                retention.insert(0, "legal hold")
    applied = found[0] if found else None
    return {
        "found": found,
        "applied": applied,
        "missing": applied is None,
        "legal_hold": legal,
        "retention_labels": retention,
        "stripped": False,
        "downgraded": False,
    }


def _passages(pack: dict) -> list[dict]:
    rows: list[dict] = []
    briefing = pack.get("briefing_note") or {}
    for passage in briefing.get("passages") or []:
        if isinstance(passage, dict) and passage.get("text"):
            rows.append(
                {
                    "passage_id": str(passage.get("passage_id") or ""),
                    "document_id": str(briefing.get("document_id") or ""),
                    "document_kind": "briefing_note",
                    "role": str(passage.get("role") or "narrative"),
                    "kind": "narrative",
                    "text": str(passage.get("text")),
                    "reviewed_on": passage.get("reviewed_on"),
                    "figure_id": passage.get("figure_id"),
                    "figure_value": passage.get("figure_value"),
                    "label": passage.get("label"),
                }
            )
    policy = pack.get("policy_extract") or {}
    for passage in policy.get("passages") or []:
        if isinstance(passage, dict) and passage.get("text"):
            rows.append(
                {
                    "passage_id": str(passage.get("passage_id") or ""),
                    "document_id": str(policy.get("document_id") or ""),
                    "document_kind": "policy_extract",
                    "role": str(passage.get("role") or "narrative"),
                    "kind": "narrative",
                    "text": str(passage.get("text")),
                    "reviewed_on": passage.get("reviewed_on"),
                    "figure_id": passage.get("figure_id"),
                    "figure_value": passage.get("figure_value"),
                    "label": passage.get("label"),
                }
            )
    sheet = pack.get("figures_sheet") or {}
    for row in sheet.get("rows") or []:
        if isinstance(row, dict) and row.get("text"):
            rows.append(
                {
                    "passage_id": str(row.get("figure_id") or ""),
                    "document_id": str(sheet.get("document_id") or ""),
                    "document_kind": "figures_sheet",
                    "role": "figure",
                    "kind": "figure",
                    "text": str(row.get("text")),
                    "reviewed_on": row.get("reviewed_on"),
                    "figure_id": row.get("figure_id"),
                    "figure_value": row.get("value"),
                    "label": row.get("label") or "",
                    "sheet_approved": sheet.get("approved") is True,
                }
            )
    return rows


def _currency(passage: dict, as_of: str) -> dict:
    siblings = _siblings()
    return siblings["passage_currency"](
        {
            "source_id": passage["passage_id"],
            "title": passage["document_kind"],
            "reviewed_on": passage.get("reviewed_on"),
            "text": passage["text"],
        },
        as_of,
        siblings["stale_after_days"],
    )


def _score(passage: dict, claim_id: str, pack_id: str, currency: dict) -> dict:
    siblings = _siblings()
    claim = {
        "answer_id": pack_id,
        "claim_id": claim_id,
        "question": "slide",
        "text": passage["text"],
        "citations": [{"source_id": passage["passage_id"], "quote": passage["text"]}],
    }
    passages = {passage["passage_id"]: {"text": passage["text"]}}
    rows = {passage["passage_id"]: currency}
    return siblings["score_claim"](claim, passages, rows)


def _figure_class(values: list[str]) -> tuple[str, str]:
    siblings = _siblings()
    items = []
    for value in values:
        canonical, accepted = siblings["normalise_value"]("figure", value)
        items.append((canonical, siblings["display_fold"](value), accepted))
    return siblings["classify_values"](items)


def _figure_gate(passage: dict, passages: list[dict], sheet_approved: bool) -> dict:
    """Decide whether a number on this passage may be quoted."""
    siblings = _siblings()
    figure_id = passage.get("figure_id")
    if passage["kind"] == "figure" or figure_id:
        if not sheet_approved and passage["kind"] == "figure":
            return {"allowed": False, "reason": "figures_sheet_not_approved", "called": False}
        if not sheet_approved and figure_id:
            return {"allowed": False, "reason": "figures_sheet_not_approved", "called": False}
        grouped = [
            item
            for item in passages
            if item.get("figure_id") == figure_id and item.get("figure_value")
        ]
        values = [str(item["figure_value"]) for item in grouped]
        if passage.get("figure_value") and str(passage["figure_value"]) not in values:
            values.append(str(passage["figure_value"]))
        if len(values) >= 2:
            kind, reason = _figure_class(values)
            if kind == "material_discrepancy":
                return {
                    "allowed": False,
                    "reason": "figure_discrepancy",
                    "called": True,
                    "classification": kind,
                    "classification_reason": reason,
                }
            return {
                "allowed": True,
                "reason": None,
                "called": True,
                "classification": kind,
                "classification_reason": reason,
            }
        if passage.get("figure_value"):
            canonical, accepted = siblings["normalise_value"]("figure", str(passage["figure_value"]))
            if not accepted:
                return {"allowed": False, "reason": "figure_not_on_approved_sheet", "called": True}
            return {
                "allowed": True,
                "reason": None,
                "called": True,
                "classification": "single_approved_value",
                "classification_reason": canonical,
            }
        return {"allowed": True, "reason": None, "called": False}
    numbers = siblings["extract_numbers"](passage["text"])
    if not numbers:
        return {"allowed": True, "reason": None, "called": False}
    if not sheet_approved:
        return {"allowed": False, "reason": "figures_sheet_not_approved", "called": False}
    blob = "\n".join(
        f"{item.get('figure_value') or ''} {item['text']}"
        for item in passages
        if item["kind"] == "figure"
    )
    for number in numbers:
        if not re.search(rf"(?<!\d){re.escape(number)}(?!\d)", blob):
            return {"allowed": False, "reason": "figure_not_on_approved_sheet", "called": True}
    return {"allowed": True, "reason": None, "called": True, "classification": "number_on_approved_sheet"}


def _citation(passage: dict) -> dict:
    return {
        "document_id": passage["document_id"],
        "document_kind": passage["document_kind"],
        "passage_id": passage["passage_id"],
        "quote": passage["text"],
    }


def _gap(point_id: str, reason: str, *, categories: list[str] | None = None) -> dict:
    row = {
        "point_id": point_id,
        "reason": reason,
        "sourced": False,
        "citation": None,
        "claim_text_recorded": False,
        "note": GAP_NOTE,
    }
    if categories:
        row["personal_data_categories"] = categories
    return row


def _claim(claim_id: str, point_id: str, passage: dict, scored: dict, figure: dict) -> dict:
    sourced = (
        scored.get("verdict") == "supported"
        and scored.get("stale_source") is False
        and bool(scored.get("citations"))
        and all(item.get("quote_found") for item in scored["citations"])
    )
    return {
        "claim_id": claim_id,
        "point_id": point_id,
        "sourced": sourced,
        "text": passage["text"] if sourced else None,
        "citations": [_citation(passage)] if sourced else [],
        "groundedness": {
            "verdict": scored.get("verdict"),
            "stale_source": scored.get("stale_source"),
            "stale_reason": scored.get("stale_reason"),
        },
        "cross_source": {
            "called": bool(figure.get("called")),
            "classification": figure.get("classification"),
            "reason": figure.get("classification_reason"),
        },
        "passage_id": passage["passage_id"],
        "kind": passage["kind"],
        "label": passage.get("label") or None,
    }


def _suppressed(passage: dict, requests: list[str]) -> bool:
    target = _norm(passage["text"])
    if not target:
        return False
    for text in requests:
        marked, _signals = _prepare(text)
        for kind, sentence, reason in marked:
            if reason == "negated" or kind == "drop" and _sentence_negated(sentence):
                if target in _norm(sentence):
                    return True
            if reason == "negated" and target in _norm(sentence):
                return True
    return False


def _match(sentence: str, passages: list[dict]) -> dict | None:
    wanted = _norm(sentence)
    for passage in passages:
        if _norm(passage["text"]) == wanted:
            return passage
    return None


def _word_count(text: str) -> int:
    return len([word for word in text.split() if word])


def _accessibility(slides: list[dict]) -> dict:
    items = []
    over: list[str] = []
    for slide in slides:
        if slide.get("kind") == "figure" and slide.get("alt_text"):
            items.append(
                {
                    "slide_id": slide["slide_id"],
                    "alt_text": slide["alt_text"],
                    "reason": "figure_label",
                }
            )
        elif slide.get("kind") == "figure":
            items.append(
                {
                    "slide_id": slide["slide_id"],
                    "alt_text": None,
                    "reason": "figure_label_missing",
                }
            )
        else:
            items.append(
                {
                    "slide_id": slide["slide_id"],
                    "alt_text": None,
                    "reason": "no_image",
                }
            )
        if _word_count(slide.get("headline") or "") > 25:
            over.append(slide["slide_id"])
    return {
        "alt_text": {"logo_added": False, "items": items, "certified": False},
        "reading_order": {
            "slide_ids": [slide["slide_id"] for slide in slides],
            "speaker_notes_follow_slides": True,
            "certified": False,
        },
        "colour_contrast": {
            "assessed": False,
            "presenter_must_check": True,
            "wcag_22_aa_certified": False,
            "note": (
                "This starter does not render colours. "
                "GOV.UK guidance names WCAG 2.2 AA. The regulation text that was opened does not."
            ),
        },
        "plain_english": {
            "word_limit": 25,
            "limit_is_guidance": True,
            "guidance": (
                "Publishing accessible documents says aim for around 25 words or less "
                "per sentence. The GOV.UK style guide says use plain English. "
                "This count is not a certificate."
            ),
            "over_limit": over,
            "certified": False,
        },
        "accessibility_certified": False,
    }


def _flags(**overrides) -> dict:
    base = {
        "slides_produced": False,
        "shared": False,
        "published": False,
        "sent": False,
        "uploaded": False,
        "graph_called": False,
        "powerpoint_api_called": False,
        "logo_added": False,
        "customer_invented": False,
        "outcome_invented": False,
        "figure_invented": False,
        "classification_downgraded": False,
        "marking_stripped": False,
    }
    base.update(overrides)
    return base


def _shell(pack_id: str | None, as_of: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": "M005",
        "experiment": 53,
        "autonomy": "A1",
        "pack_id": pack_id,
        "as_of": as_of,
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "request_text_recorded": False,
        "flags": _flags(),
        "regulatory": {
            "accessibility_certified": False,
            "wcag_22_aa_met": False,
            "regulations_scope_decided": False,
            "classification_chosen": False,
            "lawful_basis_decided": False,
        },
        "human_route": {
            "offered": True,
            "agent_publishes": False,
            "agent_shares": False,
            "agent_sends": False,
        },
        "sources_pinned_on": PINNED_ON.isoformat(),
        "not_opened": [item["id"] for item in NOT_OPENED],
        "reuse": {
            "experiment_29": "score_claim and passage_currency",
            "experiment_36": "normalise_value and classify_values",
            "experiment_52_pattern": "approval is a separate step, negation is not a citation, pack text is not approval",
        },
    }


def _lock(result: dict) -> dict:
    flags = result.setdefault("flags", {})
    slides_produced = flags.get("slides_produced") is True
    flags.update(_flags(slides_produced=slides_produced))
    result["actions_taken"] = []
    result["executed"] = False
    result["model_called"] = False
    result["network_called"] = False
    result["request_text_recorded"] = False
    result["regulatory"]["accessibility_certified"] = False
    result["regulatory"]["wcag_22_aa_met"] = False
    result["regulatory"]["classification_chosen"] = False
    result["regulatory"]["lawful_basis_decided"] = False
    for claim in result.get("claims") or []:
        if claim.get("sourced") is True:
            citations = claim.get("citations") or []
            if not citations or any(not item.get("quote") for item in citations):
                raise NarrativeForbidden("sourced without a citation")
            if claim.get("groundedness", {}).get("verdict") != "supported":
                raise NarrativeForbidden("sourced without support")
    if flags.get("slides_produced") and not (result.get("human_approval") or {}).get("recorded"):
        raise NarrativeForbidden("slides without approval")
    return result


def _refused(as_of: str, reason: str) -> dict:
    result = _shell(None, as_of)
    result["outcome"] = "refused"
    result["reason"] = reason
    result["claims"] = []
    result["gaps"] = []
    result["slides"] = []
    result["key_message"] = {"text": None, "sourced": False, "citations": [], "reason": reason}
    result["prompt_injection"] = {"detected": False, "patterns": [], "followed": False}
    result["safeguarding"] = {"flagged": False, "point_ids": []}
    result["personal_data"] = {"withheld": False, "categories": []}
    result["markings"] = {
        "found": [],
        "applied": None,
        "missing": True,
        "legal_hold": False,
        "retention_labels": [],
        "stripped": False,
        "downgraded": False,
    }
    result["accessibility"] = _accessibility([])
    result["stale"] = {"rules_current": None, "passages": []}
    return _lock(result)


def _speaker_notes(marking: str | None, headline: str, citation: dict) -> str:
    mark = marking or "MARKING NOT SUPPLIED. The presenter must confirm it."
    return (
        f"{mark}\n"
        f"{headline}\n"
        f"Source {citation['document_id']} {citation['passage_id']}.\n"
        "Not shared."
    )


def propose_outline(pack: dict, as_of: str) -> dict:
    """Return an outline. human_approval is null. Slides are not produced."""
    if not isinstance(pack, dict):
        raise ValueError("pack must be an object")
    parsed = _parse_as_of(as_of)
    cleaned, stripped = _strip(pack)
    if not isinstance(cleaned, dict):
        raise ValueError("pack must be an object")
    if cleaned.get("synthetic") is not True:
        return _refused(as_of, "not_synthetic")
    pack_id = cleaned.get("pack_id")
    if not isinstance(pack_id, str) or not PACK_ID.fullmatch(pack_id):
        return _refused(as_of, "pack_id")
    for field in ("organisation", "audience"):
        value = cleaned.get(field)
        if value is not None and "fictional" not in str(value).lower():
            return _refused(as_of, "not_fictional")

    result = _shell(pack_id, as_of)
    result["organisation"] = cleaned.get("organisation") or "not supplied"
    result["audience"] = cleaned.get("audience") or "not supplied"
    markings = _markings(cleaned)
    result["markings"] = markings
    current = rules_are_current(parsed)
    passages = _passages(cleaned)
    sheet = cleaned.get("figures_sheet") or {}
    sheet_approved = sheet.get("approved") is True
    currencies = {passage["passage_id"]: _currency(passage, as_of) for passage in passages}
    result["stale"] = {
        "rules_current": current,
        "window_days": SOURCE_WINDOW_DAYS,
        "pinned_on": PINNED_ON.isoformat(),
        "review_window_days": _siblings()["stale_after_days"],
        "passages": [
            {
                "passage_id": passage_id,
                "stale": row["stale"],
                "stale_reason": row["stale_reason"],
            }
            for passage_id, row in currencies.items()
        ],
    }

    requests = []
    for point in cleaned.get("requested_points") or []:
        if isinstance(point, dict):
            requests.append(str(point.get("text") or ""))
    signals: list[str] = []
    for text in requests:
        _marked, found = _prepare(text)
        for pattern in found:
            if pattern not in signals:
                signals.append(pattern)
    if stripped:
        signals.append("prohibited_key")
    result["prompt_injection"] = {
        "detected": bool(signals),
        "patterns": signals,
        "followed": False,
        "prohibited_keys_stripped": sorted(set(stripped)),
    }

    safeguarding_ids: list[str] = []
    personal_categories: list[str] = []
    claims: list[dict] = []
    gaps: list[dict] = []
    used_passages: set[str] = set()

    key = next((passage for passage in passages if passage["role"] == "key_message"), None)
    if key is None:
        result["key_message"] = {
            "text": None,
            "sourced": False,
            "citations": [],
            "reason": "key_message_missing",
        }
        gaps.append(_gap("KEY", "key_message_missing"))
    elif not current:
        result["key_message"] = {
            "text": None,
            "sourced": False,
            "citations": [],
            "reason": "stale_rules",
        }
        gaps.append(_gap("KEY", "stale_rules"))
    elif _suppressed(key, requests):
        result["key_message"] = {
            "text": None,
            "sourced": False,
            "citations": [],
            "reason": "negated",
        }
        gaps.append(_gap("KEY", "negated"))
    elif _safeguarding(key["text"]):
        safeguarding_ids.append("KEY")
        result["key_message"] = {
            "text": None,
            "sourced": False,
            "citations": [],
            "reason": "safeguarding",
        }
        gaps.append(_gap("KEY", "safeguarding"))
    else:
        categories = _personal_categories(key["text"])
        if categories:
            personal_categories.extend(categories)
            result["key_message"] = {
                "text": None,
                "sourced": False,
                "citations": [],
                "reason": "personal_data_withheld",
            }
            gaps.append(_gap("KEY", "personal_data_withheld", categories=categories))
        else:
            figure = _figure_gate(key, passages, sheet_approved)
            if not figure["allowed"]:
                result["key_message"] = {
                    "text": None,
                    "sourced": False,
                    "citations": [],
                    "reason": figure["reason"],
                }
                gaps.append(_gap("KEY", figure["reason"]))
            elif currencies[key["passage_id"]]["stale"]:
                result["key_message"] = {
                    "text": None,
                    "sourced": False,
                    "citations": [],
                    "reason": "stale_source",
                }
                gaps.append(_gap("KEY", "stale_source"))
            else:
                scored = _score(key, "KEY", pack_id, currencies[key["passage_id"]])
                claim = _claim("KEY", "KEY", key, scored, figure)
                claims.append(claim)
                if claim["sourced"]:
                    result["key_message"] = {
                        "text": claim["text"],
                        "sourced": True,
                        "citations": claim["citations"],
                        "reason": None,
                    }
                    used_passages.add(key["passage_id"])
                else:
                    result["key_message"] = {
                        "text": None,
                        "sourced": False,
                        "citations": [],
                        "reason": scored.get("verdict"),
                    }
                    gaps.append(_gap("KEY", "not_supported"))

    if not current:
        for point in cleaned.get("requested_points") or []:
            if isinstance(point, dict) and point.get("point_id"):
                gaps.append(_gap(str(point["point_id"]), "stale_rules"))
    else:
        for point in cleaned.get("requested_points") or []:
            if not isinstance(point, dict):
                continue
            point_id = str(point.get("point_id") or "")
            text = str(point.get("text") or "")
            marked, _found = _prepare(text)
            keep = [(sentence, reason) for kind, sentence, reason in marked if kind == "keep"]
            drops = [(sentence, reason) for kind, sentence, reason in marked if kind == "drop"]
            if not keep:
                reason = drops[0][1] if drops else "no_approved_source"
                if reason == "injection":
                    gaps.append(_gap(point_id, "injection"))
                else:
                    gaps.append(_gap(point_id, "negated"))
                continue
            for index, (sentence, _reason) in enumerate(keep):
                claim_id = point_id if len(keep) == 1 else f"{point_id}-{index + 1}"
                if _safeguarding(sentence):
                    safeguarding_ids.append(point_id)
                    gaps.append(_gap(claim_id, "safeguarding"))
                    continue
                categories = _personal_categories(sentence)
                if categories:
                    for category in categories:
                        if category not in personal_categories:
                            personal_categories.append(category)
                    gaps.append(_gap(claim_id, "personal_data_withheld", categories=categories))
                    continue
                passage = _match(sentence, passages)
                if passage is None:
                    lower = sentence.lower()
                    if "logo" in lower:
                        reason = "logo_not_approved"
                    elif "customer" in lower or "client" in lower:
                        reason = "customer_not_in_source"
                    elif any(cue in lower for cue in ("outcome", "saved", "cut wait", "percent", "%")):
                        reason = "outcome_not_in_source"
                    elif _siblings()["extract_numbers"](sentence):
                        reason = "figure_not_on_approved_sheet"
                    else:
                        reason = "no_approved_source"
                    gaps.append(_gap(claim_id, reason))
                    continue
                if _suppressed(passage, [text]):
                    gaps.append(_gap(claim_id, "negated"))
                    continue
                if passage["passage_id"] in used_passages:
                    continue
                figure = _figure_gate(passage, passages, sheet_approved)
                if not figure["allowed"]:
                    gaps.append(_gap(claim_id, figure["reason"]))
                    continue
                if currencies[passage["passage_id"]]["stale"]:
                    gaps.append(_gap(claim_id, "stale_source"))
                    continue
                scored = _score(passage, claim_id, pack_id, currencies[passage["passage_id"]])
                claim = _claim(claim_id, point_id, passage, scored, figure)
                if not claim["sourced"]:
                    gaps.append(_gap(claim_id, "not_supported"))
                    continue
                claims.append(claim)
                used_passages.add(passage["passage_id"])

    slides = []
    order = 0
    for claim in claims:
        if claim["sourced"] is not True:
            continue
        citation = claim["citations"][0]
        headline = citation["quote"]
        alt = claim["label"] if claim["kind"] == "figure" and claim.get("label") else None
        slide = {
            "slide_id": f"S{order}",
            "claim_id": claim["claim_id"],
            "headline": headline,
            "supporting_points": [citation],
            "speaker_notes": _speaker_notes(markings["applied"], headline, citation),
            "sourced": True,
            "kind": claim["kind"],
            "alt_text": alt,
        }
        slides.append(slide)
        order += 1

    result["claims"] = claims
    result["gaps"] = gaps
    result["slides"] = slides
    result["accessibility"] = _accessibility(slides)
    result["safeguarding"] = {"flagged": bool(safeguarding_ids), "point_ids": safeguarding_ids}
    result["personal_data"] = {
        "withheld": bool(personal_categories),
        "categories": personal_categories,
    }
    result["outcome"] = "outline_for_presenter" if current else "stale_sources"
    if not current:
        result["slides"] = []
        result["accessibility"] = _accessibility([])
    return _lock(result)


def record_presenter_approval(outline: dict, review: dict) -> dict:
    """Record the presenter's decision. Approval does not produce or share slides."""
    result = deepcopy(outline)
    result["flags"]["slides_produced"] = False
    result["flags"]["shared"] = False
    result["flags"]["published"] = False
    result["flags"]["sent"] = False

    def refuse(reason: str) -> dict:
        result["human_approval"] = None
        result["review"] = {
            "accepted": False,
            "refused": True,
            "reason": reason,
            "executed": False,
            "slides_produced": False,
            "shared": False,
        }
        return _lock(result)

    if not isinstance(review, dict):
        return refuse("review_not_an_object")
    decision = review.get("decision")
    if decision in PROHIBITED_DECISIONS:
        return refuse("prohibited_decision")
    if decision not in ALLOWED_DECISIONS:
        return refuse("decision")
    if review.get("actor_role") != "presenter":
        return refuse("actor_role")
    actor_id = review.get("actor_id")
    if not isinstance(actor_id, str) or not PRESENTER_ID.fullmatch(actor_id):
        return refuse("actor_id")
    if review.get("pack_id") != result.get("pack_id"):
        return refuse("pack_id")

    if decision in {REVISE, REJECT}:
        result["human_approval"] = None
        result["review"] = {
            "accepted": False,
            "refused": False,
            "reason": "revision_requested" if decision == REVISE else "rejected_by_presenter",
            "decision": decision,
            "executed": False,
            "slides_produced": False,
            "shared": False,
        }
        return _lock(result)

    if result.get("outcome") != "outline_for_presenter":
        return refuse("not_an_outline")
    if review.get("outline_seen") is not True:
        return refuse("outline_not_seen")
    sourced = [claim["claim_id"] for claim in result.get("claims") or [] if claim.get("sourced")]
    approved = review.get("citations_approved")
    if not isinstance(approved, list) or set(approved) != set(sourced):
        return refuse("citations_not_approved")
    if result.get("gaps") and review.get("gaps_seen") is not True:
        return refuse("gaps_not_seen")
    if review.get("accessibility_seen") is not True:
        return refuse("accessibility_not_seen")
    if review.get("markings_seen") is not True:
        return refuse("markings_not_seen")
    if (result.get("safeguarding") or {}).get("flagged") and review.get("safeguarding_seen") is not True:
        return refuse("safeguarding_not_seen")
    for claim in result.get("claims") or []:
        if claim.get("sourced") is True:
            if not claim.get("citations"):
                return refuse("sourced_without_citation")
            if claim.get("groundedness", {}).get("verdict") != "supported":
                return refuse("sourced_without_support")

    result["human_approval"] = {
        "recorded": True,
        "decision": APPROVE,
        "actor_role": "presenter",
        "executed": False,
        "slides_produced": False,
        "shared": False,
    }
    result["review"] = {
        "accepted": True,
        "refused": False,
        "reason": "presenter_approved_outline_and_citations",
        "decision": APPROVE,
        "executed": False,
        "slides_produced": False,
        "shared": False,
    }
    result["flags"]["slides_produced"] = False
    return _lock(result)


def produce_slides(outline: dict, path: Path | str | None = None) -> dict:
    """Write a local slide file only after the presenter approval step.

    The file is not shared. A missing approval leaves slides_produced false.
    """
    result = deepcopy(outline)
    approval = result.get("human_approval") or {}
    if approval.get("recorded") is not True or approval.get("decision") != APPROVE:
        result["flags"]["slides_produced"] = False
        result["flags"]["shared"] = False
        result["outcome"] = "slides_refused"
        result["review"] = {
            "accepted": False,
            "refused": True,
            "reason": "approval_missing",
            "executed": False,
            "slides_produced": False,
            "shared": False,
        }
        return _lock(result)
    if outline.get("outcome") != "outline_for_presenter":
        result["flags"]["slides_produced"] = False
        result["outcome"] = "slides_refused"
        result["review"] = {
            "accepted": False,
            "refused": True,
            "reason": "not_an_outline",
            "executed": False,
            "slides_produced": False,
            "shared": False,
        }
        return _lock(result)

    notes: list[str] = []
    claims = {claim["claim_id"]: claim for claim in result.get("claims") or []}
    for slide in result.get("slides") or []:
        claim = claims.get(slide.get("claim_id"))
        if not claim or claim.get("sourced") is not True:
            result["flags"]["slides_produced"] = False
            result["outcome"] = "slides_refused"
            result["review"] = {
                "accepted": False,
                "refused": True,
                "reason": "slide_not_sourced",
                "executed": False,
                "slides_produced": False,
                "shared": False,
            }
            return _lock(result)
        quote = (claim.get("citations") or [{}])[0].get("quote")
        if slide.get("headline") != quote or not quote:
            result["flags"]["slides_produced"] = False
            result["outcome"] = "slides_refused"
            result["review"] = {
                "accepted": False,
                "refused": True,
                "reason": "headline_not_the_quote",
                "executed": False,
                "slides_produced": False,
                "shared": False,
            }
            return _lock(result)
        notes.append(slide["speaker_notes"])

    if path is not None:
        from slides import write_pptx

        write_pptx(notes, Path(path), result.get("markings") or {})
    result["flags"]["slides_produced"] = True
    result["flags"]["shared"] = False
    result["outcome"] = "slides_for_presenter_not_shared"
    result["slides_file"] = {
        "built": path is not None,
        "graph_called": False,
        "powerpoint_api_called": False,
        "shared": False,
        "published": False,
    }
    if result.get("human_approval"):
        result["human_approval"]["slides_produced"] = True
        result["human_approval"]["shared"] = False
    return _lock(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose a PowerPoint narrative outline")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--approve", type=Path)
    parser.add_argument("--pptx", type=Path)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    try:
        result = propose_outline(pack, args.as_of)
        if args.approve:
            review = json.loads(args.approve.read_text(encoding="utf-8"))
            result = record_presenter_approval(result, review)
            if args.pptx and (result.get("human_approval") or {}).get("recorded"):
                result = produce_slides(result, args.pptx)
    except ValueError:
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
