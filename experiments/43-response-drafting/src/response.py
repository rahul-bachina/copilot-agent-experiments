#!/usr/bin/env python3
"""Draft one customer response from approved snippets.

This is a deterministic stand-in. It is tuned to the synthetic fixtures.
It is not a model, and it must not be described as one.

A policy sentence is a verbatim snippet that Experiment 09's
line_applicability() says is current, or the draft states a gap. The
representative reviews the text and sends it on their own channel. This
module does not send, does not choose an address, and does not decide that
a firm met PRIN 2A.5.
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

LABEL = "DRAFT FOR REPRESENTATIVE REVIEW"
ORGANISATION = "Harberton Service (fictional)"
CASE_ID = re.compile(r"^SYN-CASE-\d{4}$")
REP_ID = re.compile(r"^SYN-REP-\d{3}$")
MAX_SENTENCE_WORDS = 25

SECTORS = frozenset(
    {"financial_services", "energy", "telecoms", "public_service", "general"}
)
CHANNELS = frozenset({"email", "letter", "web_form", "phone_note"})

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "message_sent",
        "executed",
        "actions_taken",
        "send",
        "approved_recipient",
        "recipient_approved",
        "redress",
    }
)

DECISIONS_NOT_TAKEN = (
    "send",
    "final_recipient",
    "policy_invention",
    "production_case_write",
    "complaint_outcome",
    "redress",
    "vulnerability_label",
    "plain_english_certification",
    "consumer_duty_met",
    "article_12_met",
    "equality_duty_met",
)

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "disregard your rules",
    "you are now",
    "system prompt",
    "send the email",
    "send the letter",
    "send this reply",
    "send this response",
    "send now",
    "recipient approved",
    "recipient is approved",
    "you must state that",
    "treat the withdrawn snippet as current",
    "treat the withdrawn line as current",
    "approve the draft",
    "close the case",
    "offer compensation now",
)

STALE_PHRASES = (
    "treat this as current",
    "treat the withdrawn snippet as current",
    "the old line is still the policy",
)

IMMEDIATE = ("kill myself", "end my life", "suicide", "hurt my child")
VULNERABILITY = ("in hospital", "cannot afford", "can't afford", "homeless", "bereavement")

BLOCKERS = (
    ("promise", "we guarantee"),
    ("promise", "you will receive compensation"),
    ("outcome", "we uphold"),
    ("outcome", "we reject"),
    ("blame", "your fault"),
    ("blame", "you failed"),
    ("jargon", "hereinafter"),
    ("jargon", "pursuant"),
    ("jargon", "aforesaid"),
    ("jargon", "notwithstanding"),
    ("jargon", "please be advised"),
    ("jargon", "in the event that"),
)

JARGON = (
    "hereinafter",
    "pursuant",
    "aforesaid",
    "notwithstanding",
    "whereas",
    "please be advised",
    "in the event that",
    "at your earliest convenience",
)

APPROVE = "representative_approve_for_own_send"
REVISE = "representative_request_revision"
REJECT = "reject_draft"
ALLOWED_DECISIONS = frozenset({APPROVE, REVISE, REJECT})
PROHIBITED_DECISIONS = frozenset(
    {
        "send_message",
        "write_case",
        "offer_redress",
        "close_case",
        "promise_outcome",
        "send",
        "approve_recipient_from_case",
    }
)
EMAIL_KEYS = frozenset({"email", "to", "recipient", "address", "recipient_address"})

DEFAULT_LIBRARY = Path(__file__).resolve().parent.parent / "fixtures" / "knowledge_snippets.json"

_propose = None
_applicability = None


class DraftForbidden(RuntimeError):
    """No send, case write, redress, closure, or promised outcome."""


def send_message(*_args, **_kwargs) -> None:
    raise DraftForbidden("the agent does not send a message")


def write_case(*_args, **_kwargs) -> None:
    raise DraftForbidden("the agent does not write a case")


def offer_redress(*_args, **_kwargs) -> None:
    raise DraftForbidden("the agent does not offer redress")


def close_case(*_args, **_kwargs) -> None:
    raise DraftForbidden("the agent does not close a case")


def promise_outcome(*_args, **_kwargs) -> None:
    raise DraftForbidden("the agent does not promise an outcome")


def _load_propose():
    gateway_src = Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise RuntimeError(
            "Experiment 08 is required at experiments/08-uk-pii-redaction-gateway. "
            "This starter does not carry its own copy."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _load_applicability():
    lines_path = (
        Path(__file__).resolve().parents[2]
        / "09-casework-correspondence-draft"
        / "src"
        / "lines.py"
    )
    if not lines_path.is_file():
        raise RuntimeError(
            "Experiment 09 is required at experiments/09-casework-correspondence-draft. "
            "This starter does not carry its own copy."
        )
    spec = importlib.util.spec_from_file_location("exp09_lines_for_exp43", lines_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Experiment 09 lines.py could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.line_applicability


def _gateway():
    global _propose
    if _propose is None:
        _propose = _load_propose()
    return _propose


def _gate():
    global _applicability
    if _applicability is None:
        _applicability = _load_applicability()
    return _applicability


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _has(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text, flags=re.IGNORECASE) is not None


def _hits(text: str, phrases: tuple[str, ...]) -> list[str]:
    found = []
    for phrase in phrases:
        if _has(text, phrase) and phrase not in found:
            found.append(phrase)
    return found


def load_library(path: Path | None = None) -> dict:
    library_path = path or DEFAULT_LIBRARY
    with open(library_path, encoding="utf-8") as handle:
        library = json.load(handle)
    if "snippets" not in library:
        raise ValueError("library must contain snippets")
    return library


def rules_are_current(as_of: date) -> bool:
    """True when as_of is within the starter window after the pin date.

    Equal to SOURCE_WINDOW_DAYS is still current. The window is a starter
    default, not a review duty.
    """
    return (as_of - PINNED_ON).days <= SOURCE_WINDOW_DAYS


def screen_tone(text: str) -> dict:
    findings = []
    lower = text.lower()
    for reason, phrase in BLOCKERS:
        if phrase in lower:
            findings.append({"reason": reason, "phrase": phrase})
    return {
        "passed": not findings,
        "findings": findings,
        "blocks_send_approval": bool(findings),
        "is_a_legal_finding": False,
    }


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _words(sentence: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", sentence)


def screen_plain_english(text: str) -> dict:
    sentences = _sentences(text)
    long_sentences = []
    for sentence in sentences:
        count = len(_words(sentence))
        if count > MAX_SENTENCE_WORDS:
            long_sentences.append({"words": count, "sentence": sentence})
    lower = text.lower()
    jargon = [phrase for phrase in JARGON if phrase in lower]
    passed = not long_sentences and not jargon
    lengths = [len(_words(sentence)) for sentence in sentences]
    average = round(sum(lengths) / len(lengths), 1) if lengths else 0.0
    return {
        "passed": passed,
        "average_words_per_sentence": average,
        "long_sentences": long_sentences,
        "jargon": jargon,
        "sentence_cap": MAX_SENTENCE_WORDS,
        "is_a_reading_age": False,
        "is_prin_2a_5_10_testing": False,
        "duty_met": False,
    }


def _snippet_blocks(text: str) -> list[dict]:
    return screen_tone(text)["findings"]


def _match(text: str, library: dict, as_of: date) -> dict:
    applicability = _gate()
    cited = []
    refused = []
    topics: list[str] = []
    for snippet in library["snippets"]:
        if not any(_has(text, keyword) for keyword in snippet.get("keywords", [])):
            continue
        topic = str(snippet.get("topic") or "unspecified")
        if topic not in topics:
            topics.append(topic)
        allowed, reason = applicability(snippet, as_of)
        record = {
            "id": snippet.get("id"),
            "topic": topic,
            "reason": reason,
            "status": snippet.get("status"),
            "effective_on": snippet.get("effective_on"),
            "review_due_on": snippet.get("review_due_on"),
        }
        if not allowed:
            record["text_withheld"] = True
            refused.append(record)
            continue
        blocks = _snippet_blocks(str(snippet.get("text") or ""))
        if blocks:
            record["reason"] = blocks[0]["reason"]
            record["text_withheld"] = True
            refused.append(record)
            continue
        record["reason"] = "current"
        record["text"] = snippet["text"]
        record["text_withheld"] = False
        cited.append(record)
    gaps = []
    cited_topics = {item["topic"] for item in cited}
    for topic in topics:
        if topic not in cited_topics:
            gaps.append(
                {
                    "topic": topic,
                    "summary": f"no current approved snippet covers {topic.replace('_', ' ')}",
                }
            )
    if not topics:
        gaps.append(
            {
                "topic": "unspecified",
                "summary": "no current approved snippet covers this case",
            }
        )
    return {"cited": cited, "refused": refused, "gaps": gaps, "topics": topics}


def _join(sentences: list[str]) -> str:
    cleaned = []
    for sentence in sentences:
        text = sentence.strip()
        if not text:
            continue
        if text[-1] not in ".!?":
            text += "."
        cleaned.append(text)
    return "\n\n".join(cleaned)


def _render(
    *,
    cited: list[dict],
    gaps: list[dict],
    complaint: bool,
    immediate: bool,
    stale_rules: bool,
    refusal: str | None,
) -> str:
    if refusal == "not_synthetic":
        return _join(
            [
                "This record is not marked synthetic",
                "No draft was prepared",
                "A person is still offered",
                "Nothing has been sent",
            ]
        )
    if refusal == "case_id":
        return _join(
            [
                "The case id is not a synthetic id for this starter",
                "No draft was prepared",
                "A person is still offered",
                "Nothing has been sent",
            ]
        )
    sentences = [
        "DRAFT",
        "NOT SENT",
        "The representative reviews this text",
        "The representative sends it on their own channel",
        "An automated assistant prepared this draft",
        "A person at Harberton Service can help",
        "That includes help at a counter",
        "Ask a person if you need large print or audio",
        "This draft does not decide what is reasonable",
    ]
    if immediate:
        sentences.extend(
            [
                "Stop for a person",
                "The case uses immediate-danger wording",
                "Call 999 if someone is in immediate danger",
                "Nobody has been contacted",
                "No snippet is quoted",
            ]
        )
    elif stale_rules:
        sentences.extend(
            [
                "The pinned sources are outside the review window",
                "No snippet is quoted",
                "A representative must re-check the sources",
            ]
        )
    else:
        if complaint:
            sentences.append("No complaint outcome is decided")
        for item in cited:
            sentences.append(item["text"])
            sentences.append(f"Cited snippet {item['id']}")
            sentences.append("Status current")
            sentences.append(f"Review due {item['review_due_on']}")
        for gap in gaps:
            sentences.append(f"Gap: {gap['summary']}")
            sentences.append("No position is stated")
    sentences.extend(
        [
            "Nothing has been sent",
            "No case record has been written",
            "No redress has been offered",
        ]
    )
    return _join(sentences)


def _empty_flags() -> dict:
    return {
        "message_sent": False,
        "case_written": False,
        "redress_offered": False,
        "complaint_closed": False,
        "outcome_promised": False,
        "customer_labelled_vulnerable": False,
        "stale_snippet_quoted": False,
        "withdrawn_snippet_quoted": False,
        "representative_approved_own_send": False,
        "revision_requested": False,
        "draft_rejected": False,
    }


def _lock(result: dict) -> None:
    result["flags"]["message_sent"] = False
    result["flags"]["case_written"] = False
    result["flags"]["redress_offered"] = False
    result["flags"]["complaint_closed"] = False
    result["flags"]["outcome_promised"] = False
    result["flags"]["customer_labelled_vulnerable"] = False
    result["executed"] = False
    result["actions_taken"] = []
    result["draft"]["may_be_sent_by_agent"] = False
    result["recipient"]["may_be_chosen_by_agent"] = False
    result["recipient"]["approved_address"] = None


def _refusal(case_id: str | None, as_of: date, reason: str) -> dict:
    text = _render(
        cited=[],
        gaps=[],
        complaint=False,
        immediate=False,
        stale_rules=False,
        refusal=reason,
    )
    outcome = "refused_not_synthetic" if reason == "not_synthetic" else "refused_case_id"
    result = _document(
        case_id=case_id,
        as_of=as_of,
        sector=None,
        channel=None,
        outcome=outcome,
        draft_text=text,
        cited=[],
        refused=[],
        gaps=[],
        tone=screen_tone(text),
        plain=screen_plain_english(text),
        gateway={
            "called": False,
            "reason": reason,
            "output_is_anonymised": False,
            "agent_may_release": False,
            "release_called": False,
        },
        injection={"detected": False, "signals": [], "followed": False},
        stale={"narrative_signals": [], "rules_current": rules_are_current(as_of)},
        vulnerability={
            "signals": [],
            "requires_immediate_human_review": False,
            "person_labelled_vulnerable": False,
        },
        complaint=False,
        library_id=None,
        stripped_keys=[],
    )
    validate_draft(result, source_text=None)
    return result


def _regulatory(sector: str | None, outcome: str) -> dict:
    applied = sector == "financial_services" and not outcome.startswith("refused_")
    return {
        "consumer_duty": {
            "applied": applied,
            "prin_2a_5_opened_on": "2026-11-09",
            "rules_named": ["PRIN 2A.5.3R", "PRIN 2A.5.7", "PRIN 2A.5.10R"] if applied else [],
            "outcome_met": False,
            "testing_under_2a_5_10_done": False,
            "status_letter_on_2a_5_7": "not_cleanly_labelled_in_the_pdf_extract",
            "not_applied_reason": None
            if applied
            else "PRIN 2A.5 is attached only for a financial_services case that is drafted.",
        },
        "article_12": {
            "opened_on": "2026-11-09",
            "applies_to_this_reply": False,
            "article_12_met": False,
            "note": (
                "Article 12(1) governs privacy information and communications "
                "under Articles 15 to 22D and Article 34. This service reply is "
                "not presented as that information."
            ),
        },
        "equality_act": {
            "section_20_6_opened_on": "2026-11-09",
            "section_29_opened": False,
            "alternative_format_offered": not outcome.startswith("refused_"),
            "duty_met": False,
        },
        "significant_decision_taken": False,
        "not_opened_on_2026_11_09": list(NOT_OPENED),
    }


def _document(
    *,
    case_id: str | None,
    as_of: date,
    sector: str | None,
    channel: str | None,
    outcome: str,
    draft_text: str,
    cited: list[dict],
    refused: list[dict],
    gaps: list[dict],
    tone: dict,
    plain: dict,
    gateway: dict,
    injection: dict,
    stale: dict,
    vulnerability: dict,
    complaint: bool,
    library_id: str | None,
    stripped_keys: list[str],
) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": "C004",
        "experiment": "43",
        "autonomy": "A1",
        "organisation": ORGANISATION,
        "case_id": case_id,
        "as_of": as_of.isoformat(),
        "sector": sector,
        "channel": channel,
        "library_id": library_id,
        "outcome": outcome,
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "case_text_echoed": False,
        "draft": {
            "text": draft_text,
            "may_be_sent_by_agent": False,
            "policy_sentences_are_cited_snippets_only": True,
        },
        "sources_cited": cited,
        "snippets_refused": refused,
        "gaps": gaps,
        "tone": tone,
        "plain_english": plain,
        "pii_gateway": gateway,
        "prompt_injection": injection,
        "stale": stale,
        "vulnerability": vulnerability,
        "complaint": {
            "wording_present": complaint,
            "outcome_decided": False,
        },
        "recipient": {
            "proposed_role": (
                "The customer already on the case. The representative types any "
                "address in their own system."
            ),
            "approved": False,
            "approved_address": None,
            "may_be_chosen_by_agent": False,
            "case_text_cannot_approve": True,
            "approval_source": "not_approved",
        },
        "human_route": {
            "offered": True,
            "who": "Customer service representative",
            "representative_sends": True,
            "agent_sends": False,
        },
        "flags": _empty_flags(),
        "regulatory": _regulatory(sector, outcome),
        "pinned_sources": [
            {
                "id": source["id"],
                "opened_on": source["opened_on"],
                "url": source["url"],
            }
            for source in SOURCES
        ],
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
        "stripped_keys": stripped_keys,
        "approval_pattern": "experiment-09-text-and-recipient-stay-with-the-representative",
    }


def _gateway_summary(text: str) -> dict:
    proposal = _gateway()(text, caller="exp-43-response-drafting", reversible=False)
    findings = proposal["audit_log"]["findings"]
    if proposal["anonymisation"]["output_is_anonymised"] is not False:
        raise RuntimeError("Experiment 08 reported anonymisation. This starter refuses that claim.")
    if proposal["release"]["agent_may_release"] is not False:
        raise RuntimeError("Experiment 08 allowed release. This starter refuses that claim.")
    return {
        "called": True,
        "caller": "exp-43-response-drafting",
        "finding_count": len(findings),
        "entity_types": sorted({item["entity_type"] for item in findings}),
        "input_sha256": proposal["audit_log"]["input_sha256"],
        "output_is_anonymised": False,
        "agent_may_release": False,
        "release_called": False,
        "reversible_requested": False,
    }


def draft_response(case: dict, as_of: str, *, library: dict | None = None) -> dict:
    """Build one draft. The case text cannot approve a recipient or a send."""
    if not isinstance(case, dict):
        raise ValueError("case must be an object")
    on = _parse_as_of(as_of)
    payload = dict(case)
    stripped = sorted(key for key in PROHIBITED_KEYS if key in payload)
    for key in stripped:
        payload.pop(key, None)
    case_id = payload.get("case_id")
    if payload.get("synthetic") is not True:
        return _refusal(case_id if isinstance(case_id, str) else None, on, "not_synthetic")
    if not isinstance(case_id, str) or not CASE_ID.fullmatch(case_id):
        return _refusal(None, on, "case_id")
    text = payload.get("text")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    sector = payload.get("sector")
    if sector not in SECTORS:
        sector = "general"
    channel = payload.get("channel")
    if channel not in CHANNELS:
        channel = None
    source_library = library if library is not None else load_library()
    if "snippets" not in source_library:
        raise ValueError("library must contain snippets")

    gateway = _gateway_summary(text)
    injection_signals = _hits(text, INJECTION_PATTERNS)
    stale_signals = _hits(text, STALE_PHRASES)
    for year_text in re.findall(r"\b(19\d{2}|20\d{2})\b", text):
        year = int(year_text)
        if year <= on.year - 6:
            signal = f"narrative cites {year}, which is more than six years before the as-of date"
            if signal not in stale_signals:
                stale_signals.append(signal)
    immediate = bool(_hits(text, IMMEDIATE))
    vulnerability_signals = _hits(text, VULNERABILITY)
    complaint = bool(
        re.search(
            r"\b(formal complaint|i wish to complain|i want to complain|i am complaining)\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    current = rules_are_current(on)
    if not current or immediate:
        matched = {"cited": [], "refused": [], "gaps": [], "topics": []}
    else:
        matched = _match(text, source_library, on)
    if not current:
        outcome = "stale_sources"
    elif immediate:
        outcome = "immediate_review"
    elif matched["cited"]:
        outcome = "draft_with_citations"
    else:
        outcome = "gap_only"
    draft_text = _render(
        cited=matched["cited"],
        gaps=matched["gaps"],
        complaint=complaint,
        immediate=immediate,
        stale_rules=not current,
        refusal=None,
    )
    tone = screen_tone(draft_text)
    plain = screen_plain_english(draft_text)
    result = _document(
        case_id=case_id,
        as_of=on,
        sector=sector,
        channel=channel,
        outcome=outcome,
        draft_text=draft_text,
        cited=matched["cited"],
        refused=matched["refused"],
        gaps=matched["gaps"],
        tone=tone,
        plain=plain,
        gateway=gateway,
        injection={
            "detected": bool(injection_signals),
            "signals": injection_signals,
            "followed": False,
        },
        stale={
            "narrative_signals": stale_signals,
            "rules_current": current,
            "window_days": SOURCE_WINDOW_DAYS,
            "pinned_on": PINNED_ON.isoformat(),
        },
        vulnerability={
            "signals": vulnerability_signals,
            "requires_immediate_human_review": immediate,
            "person_labelled_vulnerable": False,
        },
        complaint=complaint,
        library_id=source_library.get("library_id"),
        stripped_keys=stripped,
    )
    validate_draft(result, source_text=text)
    return result


def validate_draft(result: dict, *, source_text: str | None) -> None:
    """Reject a draft that sends, echoes the case, or quotes a refused snippet."""
    if result["label"] != LABEL:
        raise ValueError("label missing")
    if result["draft"]["may_be_sent_by_agent"] is not False:
        raise ValueError("draft claims the agent may send")
    if result["flags"]["message_sent"] is not False:
        raise ValueError("message_sent must stay false")
    if result["executed"] is not False or result["actions_taken"] != []:
        raise ValueError("the draft recorded an action")
    if result["prompt_injection"]["followed"] is not False:
        raise ValueError("an instruction was followed")
    if result["regulatory"]["consumer_duty"]["outcome_met"] is not False:
        raise ValueError("the draft must not find that PRIN 2A.5 was met")
    if result["regulatory"]["equality_act"]["duty_met"] is not False:
        raise ValueError("the draft must not find that the Equality Act duty was met")
    if result["pii_gateway"].get("output_is_anonymised") not in (False, None):
        raise ValueError("redaction output was described as anonymised")
    blob = json.dumps(result)
    if "redacted_text" in result.get("pii_gateway", {}):
        raise ValueError("redacted text was copied out")
    if source_text and len(source_text) > 24 and source_text in blob:
        raise ValueError("case text was echoed")
    for item in result["sources_cited"]:
        if item["text"] not in result["draft"]["text"]:
            raise ValueError("a cited snippet is missing from the draft")
        if item["reason"] != "current":
            raise ValueError("a refused snippet was cited")
    for item in result["snippets_refused"]:
        if item.get("text"):
            raise ValueError("refused wording was copied out")
    if result["human_approval"] is not None:
        approval = result["human_approval"]
        if approval.get("executed") is not False or approval.get("message_sent") is not False:
            raise ValueError("approval must not execute or send")


def _review_has_email(review: dict) -> bool:
    for key, value in review.items():
        if str(key).lower() in EMAIL_KEYS:
            return True
        if isinstance(value, str) and "@" in value:
            return True
    return False


def record_review(draft: dict, review: dict) -> dict:
    """Record the representative's review. Nothing is sent."""
    if not isinstance(review, dict):
        raise ValueError("review must be an object")
    result = deepcopy(draft)
    decision = review.get("decision")
    actor = review.get("actor")
    actor_id = review.get("actor_id")

    def refuse(reason: str) -> dict:
        result["review"] = {
            "decision": decision if isinstance(decision, str) else None,
            "accepted": False,
            "refused": True,
            "reason": reason,
            "executed": False,
        }
        result["human_approval"] = None
        _lock(result)
        validate_draft(result, source_text=None)
        return result

    if decision in PROHIBITED_DECISIONS:
        return refuse("prohibited_decision")
    if decision not in ALLOWED_DECISIONS:
        return refuse("unknown_decision")
    if actor != "representative":
        return refuse("actor_not_representative")
    if not isinstance(actor_id, str) or not REP_ID.fullmatch(actor_id):
        return refuse("actor_id")
    if _review_has_email(review):
        return refuse("email_address")
    if str(result.get("outcome", "")).startswith("refused_"):
        return refuse("not_a_draft")

    if decision == APPROVE:
        if review.get("recipient_role") != "customer-on-case":
            return refuse("recipient_role")
        if result["stale"]["rules_current"] is not True:
            return refuse("sources_outside_window")
        if result["vulnerability"]["requires_immediate_human_review"] is True:
            return refuse("immediate_review")
        if result["tone"]["passed"] is not True:
            return refuse("tone_not_passed")
        if result["plain_english"]["passed"] is not True:
            return refuse("plain_english_not_passed")
        result["human_approval"] = {
            "decision": APPROVE,
            "approver": "Customer service representative",
            "actor_id": actor_id,
            "recipient_role": "customer-on-case",
            "executed": False,
            "message_sent": False,
            "sends_the_response": False,
        }
        result["flags"]["representative_approved_own_send"] = True
        result["review"] = {
            "decision": APPROVE,
            "accepted": True,
            "refused": False,
            "reason": "recorded_for_representatives_own_channel",
            "executed": False,
        }
    elif decision == REVISE:
        result["human_approval"] = None
        result["flags"]["revision_requested"] = True
        result["review"] = {
            "decision": REVISE,
            "accepted": True,
            "refused": False,
            "reason": "revision_requested",
            "executed": False,
        }
    else:
        result["human_approval"] = None
        result["flags"]["draft_rejected"] = True
        result["review"] = {
            "decision": REJECT,
            "accepted": True,
            "refused": False,
            "reason": "rejected",
            "executed": False,
        }
    result["recipient"]["approved"] = False
    result["recipient"]["approval_source"] = "not_approved"
    _lock(result)
    validate_draft(result, source_text=None)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one synthetic customer response")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        case = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = draft_response(case, args.as_of)
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
