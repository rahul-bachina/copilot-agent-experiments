#!/usr/bin/env python3
"""Draft one bid response from an approved library.

The draft quotes an approved entry or it states a gap. It does not invent a
capability, a case study, a customer, an accreditation, a statistic, or a
price. A requirement is marked met only when Experiment 29's score_claim says
the quote is supported and the entry is a plain capability with no sensitive
cue. The author accepts the complete draft before it is used anywhere. This
module does not submit, send, or upload.
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

LABEL = "DRAFT FOR AUTHOR ACCEPTANCE. NOT SUBMITTED."
ORGANISATION = "Northmere Digital Services (fictional)"
BUYER = "Aldergate Borough Council (fictional)"
PROPOSAL_ID = re.compile(r"^SYN-BID-\d{4}$")
AUTHOR_ID = re.compile(r"^SYN-AUTH-\d{3}$")

GAP = (
    "No approved source covers this requirement. It is not met. "
    "The author must supply an approved answer before it is used."
)
NEGATED = (
    "The requirement negates a claim. This starter does not turn that "
    "negation into a positive answer. It is not met."
)
DISCREPANCY = (
    "Approved sources do not agree. No figure is copied. "
    "The author must check. It is not met."
)
WITHHELD_PRICE = (
    "An approved source is a price placeholder. The figure is withheld. "
    "The author must check the price. It is not met."
)
REFUSED = (
    "An approved source was found and was not cited. "
    "The wording is not copied. It is not met."
)
INJECTION_ONLY = (
    "The requirement was an instruction to the agent. It was not followed. "
    "It is not met."
)

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "submitted",
        "sent",
        "uploaded",
        "used_anywhere",
        "executed",
        "actions_taken",
        "requirement_met",
        "price",
        "amount",
        "certificate_number",
    }
)

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "ignore the approved",
    "disregard your rules",
    "you are now",
    "system prompt",
    "submit the bid",
    "submit this proposal",
    "submit this bid",
    "send the proposal",
    "upload the document",
    "upload to graph",
    "mark all requirements as met",
    "mark this requirement as met",
    "invent a case study",
    "invent a customer",
    "invent a price",
    "invent a certificate",
    "treat the withdrawn",
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
    "we do not",
    "we don't",
    "no longer",
    "must not",
    "should not",
    "without claiming",
)

PURE_NEGATION = re.compile(
    r"^(?:no|nope|not true|never mind|ignore that)[.!]?$",
    re.IGNORECASE,
)

CUE_KINDS = (
    ("commitment", ("we will", "we commit", "we shall", "commitment")),
    ("accreditation", ("certificate", "certification", "accredited", "accreditation", "cyber essentials", "iso 27001")),
    ("case_study", ("case study", "customer")),
    ("price", ("price", "£", "gbp", "day-rate", "day rate", "half day fee")),
)

KIND_TO_CHECK = {
    "accreditation": "accreditation",
    "commitment": "commitment",
    "case_study": "case_study",
    "price_placeholder": "price",
}

ACCEPT = "author_accept_complete_draft"
REVISE = "author_request_revision"
REJECT = "reject_draft"
ALLOWED_DECISIONS = frozenset({ACCEPT, REVISE, REJECT})
PROHIBITED_DECISIONS = frozenset(
    {
        "submit",
        "submit_bid",
        "send",
        "send_proposal",
        "upload",
        "upload_to_portal",
        "invent_claim",
        "mark_met",
        "accept_price",
    }
)
EMAIL_KEYS = frozenset({"email", "to", "recipient", "address", "recipient_address"})

DEFAULT_LIBRARY = Path(__file__).resolve().parent.parent / "fixtures" / "approved_library.json"
EXPERIMENTS = Path(__file__).resolve().parents[2]

_CACHE: dict = {}


class ProposalForbidden(RuntimeError):
    """No submit, send, upload, or invented claim."""


def submit_bid(*_args, **_kwargs) -> None:
    raise ProposalForbidden("the agent does not submit a bid")


def send_proposal(*_args, **_kwargs) -> None:
    raise ProposalForbidden("the agent does not send a proposal")


def upload_to_portal(*_args, **_kwargs) -> None:
    raise ProposalForbidden("the agent does not upload a proposal")


def invent_claim(*_args, **_kwargs) -> None:
    raise ProposalForbidden("the agent does not invent a claim")


def _load(folder: str, filename: str, alias: str):
    path = EXPERIMENTS / folder / "src" / filename
    if not path.is_file():
        raise RuntimeError(
            f"{folder} is required at experiments/{folder}. "
            "This starter does not carry its own copy."
        )
    saved = {}
    for name in ("sources", "tokens", "siblings", "score", "normalise", "response", "lines"):
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
        for name in ("sources", "tokens", "siblings", "score", "normalise", "response", "lines"):
            sys.modules.pop(name, None)
        sys.modules.update(saved)
    return module


def _siblings():
    if _CACHE:
        return _CACHE
    response = _load("43-response-drafting", "response.py", "exp43_response_for_exp52")
    lines = _load("09-casework-correspondence-draft", "lines.py", "exp09_lines_for_exp52")
    score = _load("29-groundedness-evaluation", "score.py", "exp29_score_for_exp52")
    grounded_sources = _load("29-groundedness-evaluation", "sources.py", "exp29_sources_for_exp52")
    normalise = _load("36-cross-source-validation", "normalise.py", "exp36_normalise_for_exp52")
    _CACHE.update(
        {
            "screen_tone": response.screen_tone,
            "screen_plain_english": response.screen_plain_english,
            "line_applicability": lines.line_applicability,
            "score_claim": score.score_claim,
            "passage_currency": score.passage_currency,
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


def load_library(path: Path | None = None) -> dict:
    library_path = path or DEFAULT_LIBRARY
    with open(library_path, encoding="utf-8") as handle:
        library = json.load(handle)
    if "entries" not in library:
        raise ValueError("library must contain entries")
    return library


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


def _prepare_sentences(text: str) -> tuple[list[str], list[str]]:
    """Return sentences that may be matched, and injection patterns seen.

    A sentence that contains an instruction is not matched. A sentence that
    contains a negation is not matched. A following sentence that is only
    'no' negates the sentence before it. The requirement text is not returned.
    """
    raw = _sentences(text)
    negated_previous = False
    signals: list[str] = []
    usable: list[str] = []
    marked = []
    for sentence in raw:
        found = _injection_signals(sentence)
        if found:
            for pattern in found:
                if pattern not in signals:
                    signals.append(pattern)
            marked.append(("drop", sentence))
            continue
        if PURE_NEGATION.match(sentence):
            if marked:
                kind, _previous = marked[-1]
                if kind == "keep":
                    marked[-1] = ("drop", _previous)
            marked.append(("drop", sentence))
            negated_previous = True
            continue
        if _sentence_negated(sentence) or negated_previous:
            marked.append(("drop", sentence))
            negated_previous = False
            continue
        negated_previous = False
        marked.append(("keep", sentence))
    for kind, sentence in marked:
        if kind == "keep":
            usable.append(sentence)
    return usable, signals


def _phrase_in(sentence: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", sentence, flags=re.IGNORECASE) is not None


def _cues(body: str) -> list[str]:
    lower = body.lower()
    found = []
    for kind, phrases in CUE_KINDS:
        if any(phrase in lower for phrase in phrases):
            found.append(kind)
    if re.search(r"\d", body):
        found.append("statistic")
    return found


def _strip(pack: dict) -> tuple[dict, list[str]]:
    cleaned = {}
    stripped = []
    for key, value in pack.items():
        if key in PROHIBITED_KEYS:
            stripped.append(key)
            continue
        cleaned[key] = value
    return cleaned, stripped


def _safe_id(value) -> str | None:
    if isinstance(value, str) and PROPOSAL_ID.fullmatch(value):
        return value
    return None


def _empty_flags() -> dict:
    return {
        "submitted": False,
        "sent": False,
        "uploaded": False,
        "used_anywhere": False,
        "graph_called": False,
        "word_api_called": False,
        "assessment_summary_written": False,
        "invented_claim": False,
    }


def _sources_public() -> list[dict]:
    rows = []
    for source in SOURCES:
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "opened": source["opened"],
            }
        )
    return rows


def _base(proposal_id: str | None, as_of: date, outcome: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": "M004",
        "experiment": "52",
        "autonomy": "A1",
        "organisation": ORGANISATION,
        "buyer": BUYER,
        "proposal_id": proposal_id,
        "as_of": as_of.isoformat(),
        "outcome": outcome,
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "requirement_text_recorded": False,
        "compliance_matrix": [],
        "sections": [],
        "gaps": [],
        "author_checks": [],
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
        "stale": {
            "rules_current": rules_are_current(as_of),
            "pinned_on": PINNED_ON.isoformat(),
            "window_days": SOURCE_WINDOW_DAYS,
        },
        "reuse": {
            "response_drafting": {"experiment": "43", "called": False},
            "groundedness": {"experiment": "29", "called": False},
            "cross_source": {"experiment": "36", "called": False},
        },
        "regulatory": {
            "tender_notice": "Procurement Act 2023, section 21",
            "assessment_summary": "Procurement Act 2023, section 50",
            "assessment_summary_produced": False,
            "section_50_is_for_the_contracting_authority": True,
            "ppn_026_met": False,
            "ppn_002_met": False,
            "ppn_014_met": False,
            "cyber_essentials_held": None,
            "lawful_basis_decided": False,
            "not_opened": list(NOT_OPENED),
        },
        "sources": _sources_public(),
        "human_route": {
            "offered": True,
            "who": "The author, or another person the author asks",
            "agent_submits": False,
            "unrecognised_goes_to_author": True,
        },
        "flags": _empty_flags(),
        "word": {
            "built_in_this_call": False,
            "format": "Office Open XML .docx",
            "graph_called": False,
            "word_api_called": False,
        },
    }


def _refusal(proposal_id: str | None, as_of: date, reason: str) -> dict:
    result = _base(proposal_id, as_of, "refused")
    result["refusal"] = {"reason": reason, "text_recorded": False}
    result["human_route"]["reason"] = reason
    return result


def _lock(result: dict) -> None:
    flags = result["flags"]
    if flags["submitted"] or flags["sent"] or flags["uploaded"] or flags["used_anywhere"]:
        raise ProposalForbidden("a draft must not record a submit, a send, an upload, or a use")
    if result["actions_taken"]:
        raise ProposalForbidden("actions_taken must stay empty")
    if result["executed"] is not False:
        raise ProposalForbidden("executed must stay false")
    if result["regulatory"]["assessment_summary_produced"] is not False:
        raise ProposalForbidden("the agent does not write an assessment summary")
    for row in result["compliance_matrix"]:
        if row["requirement_met"] is True and not row.get("source_ids"):
            raise ProposalForbidden("a requirement cannot be met without a source")
        if row["requirement_met"] is True and row.get("groundedness", {}).get("verdict") != "supported":
            raise ProposalForbidden("a requirement cannot be met unless the quote is supported")


def ground_quote(
    text: str,
    passage_text: str,
    source_id: str,
    title: str,
    reviewed_on: str,
    as_of: str,
) -> dict:
    """Score one quote with Experiment 29. The passage is the approved body."""
    api = _siblings()
    passage = {
        "source_id": source_id,
        "title": title,
        "text": passage_text,
        "reviewed_on": reviewed_on,
    }
    currency = api["passage_currency"](passage, as_of, api["stale_after_days"])
    claim = {
        "answer_id": source_id,
        "claim_id": f"{source_id}-c1",
        "question": "",
        "text": text,
        "citations": [{"source_id": source_id, "quote": text}],
    }
    scored = api["score_claim"](
        claim,
        {source_id: passage},
        {source_id: currency},
    )
    return {
        "verdict": scored["verdict"],
        "other_failures": scored["other_failures"],
        "stale_source": scored["stale_source"],
        "stale_reason": scored["stale_reason"],
        "called": True,
    }


def _compare_amounts(amounts: list[str]) -> dict:
    api = _siblings()
    items = []
    for raw in amounts:
        canonical, accepted = api["normalise_value"]("currency", raw)
        items.append((canonical, api["display_fold"](raw), accepted))
    if len(items) < 2:
        return {"called": False, "classification": None, "reason": "single_value"}
    classification, reason = api["classify_values"](items)
    return {
        "called": True,
        "classification": classification,
        "reason": reason,
        "amount_count": len(amounts),
        "figures_withheld": True,
    }


def _author_check(requirement_id: str, kind: str) -> dict:
    return {
        "requirement_id": requirement_id,
        "kind": kind,
        "text_recorded": False,
    }


def _row(requirement_id: str, status: str, answer: str, sources: list[str], met: bool, extra: dict | None = None) -> dict:
    row = {
        "requirement_id": requirement_id,
        "status": status,
        "requirement_met": met,
        "source_ids": sources,
        "draft_answer": answer,
        "groundedness": {"called": False},
    }
    if extra:
        row.update(extra)
    return row


def _match_requirement(requirement: dict, entries: list[dict], as_of: date, pin_current: bool) -> dict:
    requirement_id = str(requirement.get("id") or "")
    text = str(requirement.get("text") or "")
    usable, signals = _prepare_sentences(text)
    checks: list[dict] = []
    if signals:
        checks.append(_author_check(requirement_id, "instruction_not_followed"))

    if not pin_current:
        checks.append(_author_check(requirement_id, "stale_sources"))
        return {
            "row": _row(requirement_id, "stale_sources", REFUSED, [], False),
            "checks": checks,
            "signals": signals,
            "quoted": [],
            "reuse_tone": False,
            "reuse_ground": False,
            "reuse_compare": None,
        }

    affirmed: list[dict] = []
    negated_topics: list[str] = []
    for entry in entries:
        hit_affirmed = False
        hit_only_in_dropped = False
        for sentence in _sentences(text):
            phrases = entry.get("phrases") or []
            if not any(_phrase_in(sentence, phrase) for phrase in phrases):
                continue
            if sentence in usable:
                hit_affirmed = True
            else:
                hit_only_in_dropped = True
        if hit_affirmed:
            affirmed.append(entry)
        elif hit_only_in_dropped:
            topic = str(entry.get("topic") or entry["id"])
            if topic not in negated_topics:
                negated_topics.append(topic)

    if not affirmed:
        if signals and not usable:
            status, answer, kind = "injection_not_followed", INJECTION_ONLY, "instruction_not_followed"
        elif negated_topics:
            status, answer, kind = "negated", NEGATED, "negated_claim"
        else:
            status, answer, kind = "gap", GAP, "unrecognised"
        if not any(item["kind"] == kind for item in checks):
            checks.append(_author_check(requirement_id, kind))
        return {
            "row": _row(
                requirement_id,
                status,
                answer,
                [],
                False,
                {"negated_topics": negated_topics} if negated_topics else None,
            ),
            "checks": checks,
            "signals": signals,
            "quoted": [],
            "reuse_tone": False,
            "reuse_ground": False,
            "reuse_compare": None,
        }

    api = _siblings()
    cited = []
    refused_reasons = []
    tone_called = False
    for entry in affirmed:
        allowed, reason = api["line_applicability"](entry, as_of)
        if not allowed:
            refused_reasons.append(reason)
            continue
        body = str(entry.get("body") or "")
        tone = api["screen_tone"](body)
        tone_called = True
        if not tone["passed"]:
            refused_reasons.append("tone")
            checks.append(_author_check(requirement_id, "commitment"))
            continue
        grounded = ground_quote(
            body,
            body,
            entry["id"],
            str(entry.get("title") or entry["id"]),
            str(entry.get("reviewed_on") or ""),
            as_of.isoformat(),
        )
        if grounded["stale_source"]:
            refused_reasons.append(grounded["stale_reason"] or "stale_source")
            checks.append(_author_check(requirement_id, "stale_source"))
            continue
        if grounded["verdict"] != "supported":
            refused_reasons.append(grounded["verdict"])
            checks.append(_author_check(requirement_id, "unsupported"))
            continue
        cited.append({"entry": entry, "grounded": grounded, "body": body})

    if not cited:
        checks.append(_author_check(requirement_id, "refused_source"))
        return {
            "row": _row(
                requirement_id,
                "refused_source",
                REFUSED,
                [],
                False,
                {"refused_reasons": refused_reasons},
            ),
            "checks": checks,
            "signals": signals,
            "quoted": [],
            "reuse_tone": tone_called,
            "reuse_ground": False,
            "reuse_compare": None,
        }

    price_entries = [item for item in cited if item["entry"].get("kind") == "price_placeholder"]
    cited = [item for item in cited if item["entry"].get("kind") != "price_placeholder"]
    compare = None
    price_note = ""
    price_ids: list[str] = []
    if price_entries:
        by_topic: dict[str, list] = {}
        for item in price_entries:
            by_topic.setdefault(str(item["entry"].get("topic")), []).append(item)
        compared = []
        material = False
        for items in by_topic.values():
            amounts = [str(item["entry"].get("amount") or "") for item in items]
            amounts = [amount for amount in amounts if amount]
            one = _compare_amounts(amounts) if len(amounts) >= 2 else {
                "called": False,
                "classification": None,
                "reason": "single_value",
                "figures_withheld": True,
                "amount_count": len(amounts),
            }
            compared.append(one)
            if one.get("classification") == "material_discrepancy":
                material = True
        called = [item for item in compared if item.get("called")]
        if material:
            classification = "material_discrepancy"
        elif any(item.get("classification") == "immaterial_difference" for item in compared):
            classification = "immaterial_difference"
        elif any(item.get("classification") == "match" for item in compared):
            classification = "match"
        else:
            classification = None
        compare = {
            "called": bool(called),
            "classification": classification,
            "figures_withheld": True,
            "topic_count": len(by_topic),
        }
        checks.append(_author_check(requirement_id, "price"))
        price_ids = [item["entry"]["id"] for item in price_entries]
        price_note = DISCREPANCY if material else WITHHELD_PRICE
        if not cited:
            status = "discrepancy" if price_note == DISCREPANCY else "cited_pending_author"
            return {
                "row": _row(
                    requirement_id,
                    status,
                    price_note,
                    price_ids,
                    False,
                    {"cross_source": compare, "quoted_body_withheld_because": "price"},
                ),
                "checks": checks,
                "signals": signals,
                "quoted": [],
                "reuse_tone": tone_called,
                "reuse_ground": True,
                "reuse_compare": compare if compare.get("called") else None,
            }

    quotes = []
    source_ids = []
    can_mark = True
    grounded_rows = []
    for item in cited:
        entry = item["entry"]
        body = item["body"]
        source_ids.append(entry["id"])
        quotes.append(body)
        grounded_rows.append(item["grounded"])
        cues = _cues(body)
        mapped = KIND_TO_CHECK.get(str(entry.get("kind")))
        if mapped and mapped not in cues:
            cues.append(mapped)
        for cue in cues:
            checks.append(_author_check(requirement_id, cue))
        if entry.get("kind") != "capability" or entry.get("may_be_marked_met") is not True or cues:
            can_mark = False
    if negated_topics:
        checks.append(_author_check(requirement_id, "negated_claim"))
    if price_note:
        can_mark = False
        quotes.append(price_note)
        source_ids.extend(price_ids)
    answer = "\n\n".join(quotes)
    status = "met" if can_mark else "cited_pending_author"
    extra = {
        "groundedness": grounded_rows[0],
        "negated_topics": negated_topics,
    }
    if compare is not None:
        extra["cross_source"] = compare
    return {
        "row": _row(
            requirement_id,
            status,
            answer,
            source_ids,
            can_mark,
            extra,
        ),
        "checks": checks,
        "signals": signals,
        "quoted": [item for item in quotes if item != price_note],
        "reuse_tone": tone_called,
        "reuse_ground": True,
        "reuse_compare": compare if compare and compare.get("called") else None,
    }


def _dedupe_checks(checks: list[dict]) -> list[dict]:
    seen = set()
    rows = []
    for item in checks:
        key = (item["requirement_id"], item["kind"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(item)
    return rows


def draft_proposal(pack: dict, as_of: str, *, library: dict | None = None) -> dict:
    """Draft one proposal. human_approval stays null. Nothing is submitted."""
    parsed = _parse_as_of(as_of)
    if not isinstance(pack, dict):
        return _refusal(None, parsed, "pack_not_an_object")
    cleaned, stripped = _strip(pack)
    proposal_id = _safe_id(cleaned.get("proposal_id"))
    if cleaned.get("synthetic") is not True:
        result = _refusal(proposal_id, parsed, "not_synthetic")
        if stripped:
            result["prompt_injection"] = {
                "detected": True,
                "followed": False,
                "signals": [f"stripped:{key}" for key in stripped],
            }
        _lock(result)
        return result
    if proposal_id is None:
        result = _refusal(None, parsed, "proposal_id")
        _lock(result)
        return result
    requirements = cleaned.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        result = _refusal(proposal_id, parsed, "no_requirements")
        _lock(result)
        return result
    for requirement in requirements:
        if not isinstance(requirement, dict) or not str(requirement.get("id") or "").strip():
            result = _refusal(proposal_id, parsed, "requirement_id")
            _lock(result)
            return result
        if not str(requirement.get("text") or "").strip():
            result = _refusal(proposal_id, parsed, "requirement_text")
            _lock(result)
            return result

    library_doc = library if library is not None else load_library()
    entries = list(library_doc.get("entries") or [])
    pin_current = rules_are_current(parsed)
    result = _base(proposal_id, parsed, "draft_for_author" if pin_current else "stale_sources")
    if stripped:
        result["prompt_injection"]["detected"] = True
        result["prompt_injection"]["signals"].extend(f"stripped:{key}" for key in stripped)

    quoted_all: list[str] = []
    tone_called = False
    ground_called = False
    compare_called = False
    compare_class = None
    signals: list[str] = []
    for requirement in requirements:
        matched = _match_requirement(requirement, entries, parsed, pin_current)
        result["compliance_matrix"].append(matched["row"])
        result["author_checks"].extend(matched["checks"])
        quoted_all.extend(matched["quoted"])
        tone_called = tone_called or matched["reuse_tone"]
        ground_called = ground_called or matched["reuse_ground"]
        if matched["reuse_compare"] and matched["reuse_compare"].get("called"):
            compare_called = True
            compare_class = matched["reuse_compare"].get("classification")
        for signal in matched["signals"]:
            if signal not in signals:
                signals.append(signal)
        if matched["row"]["status"] in {"gap", "stale_sources"}:
            result["gaps"].append(matched["row"]["requirement_id"])
        if matched["row"]["status"] == "met":
            result["sections"].append(
                {
                    "requirement_id": matched["row"]["requirement_id"],
                    "source_ids": matched["row"]["source_ids"],
                    "text": matched["row"]["draft_answer"],
                }
            )
        elif matched["row"]["source_ids"] and matched["row"]["status"] == "cited_pending_author":
            if matched["quoted"]:
                result["sections"].append(
                    {
                        "requirement_id": matched["row"]["requirement_id"],
                        "source_ids": matched["row"]["source_ids"],
                        "text": matched["row"]["draft_answer"],
                        "author_must_check": True,
                    }
                )

    result["author_checks"] = _dedupe_checks(result["author_checks"])
    if signals:
        result["prompt_injection"]["detected"] = True
        result["prompt_injection"]["signals"].extend(signals)
    result["prompt_injection"]["followed"] = False
    result["reuse"]["response_drafting"]["called"] = tone_called
    if tone_called and quoted_all:
        screen = _siblings()["screen_plain_english"]("\n\n".join(quoted_all))
        result["reuse"]["response_drafting"]["plain_english"] = {
            "passed": screen["passed"],
            "sentence_cap": screen["sentence_cap"],
            "is_a_reading_age": False,
            "duty_met": False,
        }
        result["reuse"]["response_drafting"]["tone_screen"] = "Experiment 43 screen_tone"
    result["reuse"]["groundedness"]["called"] = ground_called
    result["reuse"]["cross_source"]["called"] = compare_called
    if compare_class:
        result["reuse"]["cross_source"]["classification"] = compare_class
        result["reuse"]["cross_source"]["figures_withheld"] = True
    _lock(result)
    return result


def _review_has_email(review: dict) -> bool:
    for key in review:
        if key.lower() in EMAIL_KEYS:
            return True
    return False


def record_acceptance(draft: dict, review: dict) -> dict:
    """Record the author's decision. Acceptance does not submit or use the draft."""
    result = deepcopy(draft)
    result["flags"]["submitted"] = False
    result["flags"]["sent"] = False
    result["flags"]["uploaded"] = False
    result["flags"]["used_anywhere"] = False
    result["actions_taken"] = []
    result["executed"] = False

    def refuse(reason: str) -> dict:
        result["human_approval"] = None
        result["review"] = {"accepted": False, "refused": True, "reason": reason, "executed": False}
        _lock(result)
        return result

    if not isinstance(review, dict):
        return refuse("review_not_an_object")
    if _review_has_email(review):
        return refuse("recipient_not_accepted")
    decision = review.get("decision")
    if decision in PROHIBITED_DECISIONS:
        return refuse("prohibited_decision")
    if decision not in ALLOWED_DECISIONS:
        return refuse("decision")
    if review.get("actor_role") != "author":
        return refuse("actor_role")
    actor_id = review.get("actor_id")
    if not isinstance(actor_id, str) or not AUTHOR_ID.fullmatch(actor_id):
        return refuse("actor_id")
    if review.get("proposal_id") != result.get("proposal_id"):
        return refuse("proposal_id")

    if decision in {REVISE, REJECT}:
        result["human_approval"] = None
        result["review"] = {
            "accepted": False,
            "refused": False,
            "reason": "revision_requested" if decision == REVISE else "rejected_by_author",
            "decision": decision,
            "executed": False,
            "submitted": False,
        }
        _lock(result)
        return result

    if result.get("outcome") not in {"draft_for_author", "stale_sources"}:
        return refuse("not_a_complete_draft")
    if review.get("complete_draft_seen") is not True:
        return refuse("complete_draft_not_seen")
    ids = [row["requirement_id"] for row in result.get("compliance_matrix") or []]
    acknowledged = review.get("rows_acknowledged")
    if not isinstance(acknowledged, list) or set(acknowledged) != set(ids) or not ids:
        return refuse("rows_not_acknowledged")
    if result.get("author_checks") and review.get("author_checks_seen") is not True:
        return refuse("author_checks_not_acknowledged")
    if result.get("gaps") and review.get("gaps_seen") is not True:
        return refuse("gaps_not_acknowledged")
    for row in result["compliance_matrix"]:
        if row["requirement_met"] is True and row.get("groundedness", {}).get("verdict") != "supported":
            return refuse("unsupported_marked_met")
        if row["requirement_met"] is True and not row.get("source_ids"):
            return refuse("met_without_source")

    result["human_approval"] = {
        "recorded": True,
        "decision": ACCEPT,
        "actor_role": "author",
        "executed": False,
        "submitted": False,
        "used_anywhere": False,
    }
    result["review"] = {
        "accepted": True,
        "refused": False,
        "reason": "author_accepted_for_own_use",
        "decision": ACCEPT,
        "executed": False,
        "submitted": False,
        "used_anywhere": False,
    }
    result["flags"]["submitted"] = False
    result["flags"]["used_anywhere"] = False
    _lock(result)
    return result


def validate_draft(result: dict) -> None:
    _lock(result)
    if result.get("requirement_text_recorded") is not False:
        raise ProposalForbidden("requirement text must not be recorded")
    if result.get("model_called") is not False or result.get("network_called") is not False:
        raise ProposalForbidden("the core does not call a model or the network")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a proposal from an approved library")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--docx", type=Path)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    try:
        result = draft_proposal(pack, args.as_of)
    except ValueError:
        return 2
    if args.docx:
        from word_draft import write_docx

        write_docx(result, args.docx)
        result["word"]["built_in_this_call"] = True
        result["word"]["path_recorded"] = False
    validate_draft(result)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
