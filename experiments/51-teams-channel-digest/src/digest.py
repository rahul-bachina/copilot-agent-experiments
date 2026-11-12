#!/usr/bin/env python3
"""Draft a read-only Teams channel digest for one synthetic export.

The requesting user confirms the channels and the period before any digest
is produced. The digest quotes sentences. It does not paraphrase them. It
does not post, reply, react, mention, or forward. It does not call Microsoft
Graph, and it does not read the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from extract import extract_message, sentences as split_sentences
    from injection import PROHIBITED_KEYS, hold_reason, injection_codes, split_comments
    from reuse import NeighbourMissing, check_sentence, groundedness, redact
    from sources import (
        EXPORT_STALE_AFTER_DAYS,
        QUOTE_FOIA_1_1,
        QUOTE_MINIMISATION,
        QUOTE_PURPOSE,
        STALE_AFTER_DAYS,
        source_rows,
    )
else:
    from .extract import extract_message, sentences as split_sentences
    from .injection import PROHIBITED_KEYS, hold_reason, injection_codes, split_comments
    from .reuse import NeighbourMissing, check_sentence, groundedness, redact
    from .sources import (
        EXPORT_STALE_AFTER_DAYS,
        QUOTE_FOIA_1_1,
        QUOTE_MINIMISATION,
        QUOTE_PURPOSE,
        STALE_AFTER_DAYS,
        source_rows,
    )

LABEL = "DRAFT TEAMS CHANNEL DIGEST. NOT POSTED. NOT A MONITORING DECISION."
CATALOGUE_ID = "M002"
EXPERIMENT_ID = "exp-51-teams-channel-digest"
AUTONOMY = "A0"
CONFIRM = "confirm_channels_and_period"
USER_ROLE = "Requesting user"

_KINDS = (
    ("decisions", "decision", "D"),
    ("open_questions", "open_question", "Q"),
    ("actions", "action", "A"),
    ("attention", "attention", "T"),
)


class DigestForbidden(RuntimeError):
    """A side effect this agent does not have."""


def post_message(*_args: Any, **_kwargs: Any) -> None:
    raise DigestForbidden("post is not a tool of this agent")


def reply_message(*_args: Any, **_kwargs: Any) -> None:
    raise DigestForbidden("reply is not a tool of this agent")


def react_message(*_args: Any, **_kwargs: Any) -> None:
    raise DigestForbidden("react is not a tool of this agent")


def mention_user(*_args: Any, **_kwargs: Any) -> None:
    raise DigestForbidden("mention is not a tool of this agent")


def forward_message(*_args: Any, **_kwargs: Any) -> None:
    raise DigestForbidden("forward is not a tool of this agent")


def _parse_day(value: Any, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(field) from exc


def _flags() -> dict[str, Any]:
    return {
        "posted": False,
        "replied": False,
        "reacted": False,
        "mentioned": False,
        "forwarded": False,
        "sent": False,
    }


def _human_route() -> dict[str, Any]:
    return {
        "offered": True,
        "agent_posts": False,
        "agent_replies": False,
        "agent_reacts": False,
        "agent_mentions": False,
        "agent_forwards": False,
        "agent_monitors": False,
        "how": (
            "A person can read the messages in channels they already have. "
            "This agent does not post, reply, react, mention, or forward."
        ),
    }


def _shell(outcome: str) -> dict[str, Any]:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "outcome": outcome,
        "human_approval": None,
        "scope_confirmed": False,
        "digest_produced": False,
        "digest": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "graph_called": False,
        "foundry_called": False,
        "full_body_recorded": False,
        "a3_recommended": False,
        "flags": _flags(),
        "human_route": _human_route(),
        "prompt_injection": {"detected": False, "followed": False, "signals": []},
    }


def _strip(node: Any) -> tuple[Any, list[str]]:
    """Drop keys that would assert a side effect. Values are not kept."""
    removed: list[str] = []
    if isinstance(node, dict):
        kept: dict[str, Any] = {}
        for key, value in node.items():
            if key in PROHIBITED_KEYS:
                removed.append(str(key))
                continue
            child, nested = _strip(value)
            removed.extend(nested)
            kept[key] = child
        return kept, removed
    if isinstance(node, list):
        items = []
        for value in node:
            child, nested = _strip(value)
            removed.extend(nested)
            items.append(child)
        return items, removed
    return node, removed


def _refusal(reason: str) -> dict[str, Any]:
    result = _shell("refused")
    result["refusal"] = {"reason": reason, "text_recorded": False}
    return result


def _regulatory(as_of: str, sector: str, current: bool) -> dict[str, Any]:
    quotes = None
    if current:
        quotes = {
            "article_5_1_b": QUOTE_PURPOSE,
            "article_5_1_c": QUOTE_MINIMISATION,
            "foia_section_1_1": QUOTE_FOIA_1_1,
        }
    return {
        "sector_label": sector,
        "sources_current": current,
        "article_5_1_b_read": current,
        "article_5_1_c_read": current,
        "purpose_limitation_met": False,
        "data_minimisation_met": False,
        "lawful_basis_asserted": False,
        "foia_section_1_read": current,
        "public_authority_decided": False,
        "held_information_decided": False,
        "exemption_applied": False,
        "disclosure_decided": False,
        "monitoring_decided": False,
        "dpia_decided": False,
        "quotes": quotes,
        "as_of": as_of,
    }


def _index_channels(channels: Any) -> dict[str, dict[str, Any]] | None:
    if not isinstance(channels, list):
        return None
    index: dict[str, dict[str, Any]] = {}
    for channel in channels:
        if not isinstance(channel, dict):
            return None
        channel_id = str(channel.get("channel_id") or "").strip()
        if not channel_id or channel_id in index:
            return None
        index[channel_id] = channel
    return index


def _in_period(message: dict[str, Any], start: date, end: date, as_of: date) -> bool:
    sent = _parse_day(message.get("sent_on"), "sent_on")
    if sent > as_of:
        return False
    return start <= sent <= end


def _scope_channels(
    requested: list[str],
    index: dict[str, dict[str, Any]],
    accessible: set[str],
    start: date,
    end: date,
    as_of: date,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for channel_id in requested:
        channel = index.get(channel_id)
        if channel is None:
            rows.append(
                {
                    "channel_id": channel_id,
                    "status": "not_in_export",
                    "statement": "This source is not in the export. Nothing was invented.",
                    "message_count_in_period": None,
                    "readable": False,
                }
            )
            continue
        display_name = channel.get("display_name")
        if channel_id not in accessible:
            rows.append(
                {
                    "channel_id": channel_id,
                    "display_name": display_name,
                    "status": "not_accessible",
                    "statement": (
                        "The requesting user is not recorded as having access to "
                        "this channel. It was not read."
                    ),
                    "message_count_in_period": None,
                    "readable": False,
                }
            )
            continue
        if channel.get("available") is not True:
            rows.append(
                {
                    "channel_id": channel_id,
                    "display_name": display_name,
                    "status": "source_unavailable",
                    "statement": (
                        "This source is unavailable. No messages were read and "
                        "none were invented."
                    ),
                    "message_count_in_period": None,
                    "readable": False,
                }
            )
            continue
        messages = channel.get("messages") if isinstance(channel.get("messages"), list) else []
        count = 0
        for message in messages:
            if isinstance(message, dict) and _in_period(message, start, end, as_of):
                count += 1
        status = "no_messages_in_period" if count == 0 else "ready"
        statement = (
            "No messages in this period."
            if count == 0
            else (
                f"{count} messages fall in the requested period. "
                "They are not digested until this channel and this period are confirmed."
            )
        )
        rows.append(
            {
                "channel_id": channel_id,
                "display_name": display_name,
                "status": status,
                "statement": statement,
                "message_count_in_period": count,
                "readable": True,
            }
        )
    return rows


def _export_stale(retrieved_on: date, as_of: date) -> tuple[bool, str]:
    age = (as_of - retrieved_on).days
    if age < 0:
        return True, "retrieved_after_as_of"
    if age > EXPORT_STALE_AFTER_DAYS:
        return True, "older_than_starter_window"
    return False, "within_starter_window"


def preview_scope(bundle: dict[str, Any], as_of: str) -> dict[str, Any]:
    """Return the channels and the period. Do not produce a digest."""
    if not isinstance(bundle, dict):
        return _refusal("invalid_request")
    cleaned, removed = _strip(deepcopy(bundle))
    if cleaned.get("synthetic") is not True:
        return _refusal("not_synthetic")
    try:
        as_of_date = _parse_day(as_of, "as_of")
        request = cleaned.get("request")
        user = cleaned.get("requesting_user")
        if not isinstance(request, dict) or not isinstance(user, dict):
            return _refusal("invalid_request")
        start = _parse_day(request.get("period_start"), "period_start")
        end = _parse_day(request.get("period_end"), "period_end")
        retrieved = _parse_day(cleaned.get("retrieved_on"), "retrieved_on")
        channel_ids = request.get("channel_ids")
        accessible_ids = user.get("accessible_channel_ids")
        if not isinstance(channel_ids, list) or not channel_ids:
            return _refusal("invalid_request")
        if not isinstance(accessible_ids, list):
            return _refusal("invalid_request")
        if start > end:
            return _refusal("invalid_period")
        index = _index_channels(cleaned.get("channels"))
        if index is None:
            return _refusal("invalid_request")
    except ValueError:
        return _refusal("invalid_request")

    requested = [str(item).strip() for item in channel_ids]
    if any(not item for item in requested) or len(requested) != len(set(requested)):
        return _refusal("invalid_request")
    accessible = {str(item).strip() for item in accessible_ids}
    rows = _scope_channels(requested, index, accessible, start, end, as_of_date)
    stale, stale_reason = _export_stale(retrieved, as_of_date)
    source_list, current = source_rows(as_of)
    sector = str(cleaned.get("sector") or "unspecified")
    result = _shell("scope_only")
    result["export_id"] = cleaned.get("export_id")
    result["organisation"] = cleaned.get("organisation")
    result["sector"] = sector
    result["as_of"] = as_of
    result["period"] = {"start": start.isoformat(), "end": end.isoformat()}
    result["requesting_user"] = {
        "user_id": user.get("user_id"),
        "display_name": user.get("display_name"),
    }
    result["channels"] = rows
    result["stale_export"] = {
        "stale": stale,
        "reason": stale_reason,
        "window_days": EXPORT_STALE_AFTER_DAYS,
        "window_is_a_starter_default": True,
    }
    result["sources"] = source_list
    result["regulatory"] = _regulatory(as_of, sector, current)
    result["stripped_keys"] = sorted(set(removed))
    result["scope_confirmation"] = {
        "recorded": False,
        "required_before_digest": True,
        "approves_a_post": False,
        "approves_monitoring": False,
    }
    result["reuse"] = {
        "experiment_08": {"called": False},
        "experiment_41": {"called": False},
        "experiment_29": {"called": False},
    }
    return result


def _needs(preview: dict[str, Any], confirmed: list[str]) -> dict[str, bool]:
    rows = preview["channels"]
    return {
        "empty": any(
            row["channel_id"] in confirmed and row["status"] == "no_messages_in_period"
            for row in rows
        ),
        "unavailable": any(row["status"] in {"source_unavailable", "not_in_export"} for row in rows),
        "access": any(row["status"] == "not_accessible" for row in rows),
        "stale": bool((preview.get("stale_export") or {}).get("stale")),
    }


def confirm_scope(preview: dict[str, Any], review: dict[str, Any] | None) -> dict[str, Any]:
    """Record the user's channel and period confirmation. This does not digest."""
    result = deepcopy(preview)
    if result.get("outcome") != "scope_only":
        block = {"recorded": False, "refused": True, "reason": "no_scope"}
        result["scope_confirmation"] = block
        return result
    if not isinstance(review, dict):
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "confirmation_missing",
            "approves_a_post": False,
        }
        return result
    decision = str(review.get("decision") or "")
    if decision != CONFIRM:
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "prohibited_decision" if decision else "confirmation_missing",
            "approves_a_post": False,
        }
        return result
    if review.get("actor_role") != USER_ROLE or review.get("actor_id") != result["requesting_user"]["user_id"]:
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "actor_mismatch",
            "approves_a_post": False,
        }
        return result
    if review.get("export_id") != result.get("export_id"):
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "export_mismatch",
            "approves_a_post": False,
        }
        return result
    if review.get("period_start") != result["period"]["start"] or review.get("period_end") != result["period"]["end"]:
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "period_mismatch",
            "approves_a_post": False,
        }
        return result
    channel_ids = review.get("channel_ids")
    if not isinstance(channel_ids, list) or not channel_ids:
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "channels_missing",
            "approves_a_post": False,
        }
        return result
    confirmed = [str(item).strip() for item in channel_ids]
    readable = {row["channel_id"] for row in result["channels"] if row.get("readable")}
    requested = {row["channel_id"] for row in result["channels"]}
    if any(item not in requested for item in confirmed):
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "channel_not_requested",
            "approves_a_post": False,
        }
        return result
    if any(item not in readable for item in confirmed):
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "channel_not_readable",
            "approves_a_post": False,
        }
        return result
    if len(confirmed) != len(set(confirmed)):
        result["scope_confirmation"] = {
            "recorded": False,
            "refused": True,
            "reason": "duplicate_channel",
            "approves_a_post": False,
        }
        return result
    needed = _needs(result, confirmed)
    checks = (
        ("empty", "empty_period_seen", "empty_period_not_acknowledged"),
        ("unavailable", "unavailable_seen", "unavailable_not_acknowledged"),
        ("access", "not_accessible_seen", "access_gap_not_acknowledged"),
        ("stale", "stale_export_seen", "stale_export_not_acknowledged"),
    )
    for flag, field, reason in checks:
        if needed[flag] and review.get(field) is not True:
            result["scope_confirmation"] = {
                "recorded": False,
                "refused": True,
                "reason": reason,
                "approves_a_post": False,
            }
            return result
    result["scope_confirmed"] = True
    result["scope_confirmation"] = {
        "recorded": True,
        "refused": False,
        "reason": None,
        "actor_role": USER_ROLE,
        "actor_id": review.get("actor_id"),
        "channel_ids": confirmed,
        "period_start": result["period"]["start"],
        "period_end": result["period"]["end"],
        "approves_a_post": False,
        "approves_monitoring": False,
        "approves_the_digest_as_a_decision": False,
    }
    result["human_approval"] = None
    return result


def _lines(text: str) -> list[dict[str, Any]]:
    return [{"line": index, "text": sentence} for index, sentence in enumerate(split_sentences(text), start=1)]


def _assess(
    kind: str,
    point_id: str,
    text: str,
    message_id: str,
    line: int,
    event: dict[str, Any],
    passage: dict[str, Any],
    passage_row: dict[str, Any],
    as_of: str,
) -> dict[str, Any]:
    checker = check_sentence()
    score_claim, _, _ = groundedness()
    citation = {
        "event_id": message_id,
        "paragraph": 1,
        "line_start": line,
        "line_end": line,
    }
    exp41 = checker(
        {
            "sentence_id": point_id,
            "text": text,
            "fact_key": kind,
            "citation": citation,
        },
        {message_id: event},
        as_of=as_of,
        stale_after_days=STALE_AFTER_DAYS,
        withheld=set(),
        sentence_has_identifier=False,
    )
    exp29 = score_claim(
        {
            "answer_id": "digest",
            "claim_id": point_id,
            "question": kind,
            "text": text,
            "citations": [{"source_id": message_id, "quote": text}],
        },
        {message_id: passage},
        {message_id: passage_row},
    )
    kept = exp41.get("verdict") == "supported" and exp29.get("verdict") == "supported"
    return {
        "point_id": point_id,
        "kind": kind,
        "text": text if kept else None,
        "kept": kept,
        "message_ids": [message_id],
        "citation": citation,
        "exp41_verdict": exp41.get("verdict"),
        "exp29_verdict": exp29.get("verdict"),
        "claim": exp29,
    }


def _digest_channels(
    bundle: dict[str, Any],
    confirmed: list[str],
    display_name: str,
    start: date,
    end: date,
    as_of: date,
    as_of_text: str,
) -> dict[str, Any]:
    index = _index_channels(bundle.get("channels")) or {}
    score_claim, passage_currency, summarise_claims = groundedness()
    del score_claim
    sections: dict[str, list[dict[str, Any]]] = {name: [] for name, _, _ in _KINDS}
    not_relied: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    negation: list[dict[str, Any]] = []
    injection_signals: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    entity_types: list[str] = []
    anonymised_flags: list[bool] = []
    release_flags: list[bool] = []
    messages_read = 0
    not_classified = 0
    counters = {prefix: 0 for _, _, prefix in _KINDS}
    channel_rows: list[dict[str, Any]] = []
    followed = False

    for channel_id in confirmed:
        channel = index[channel_id]
        messages = channel.get("messages") if isinstance(channel.get("messages"), list) else []
        in_period = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            try:
                if _in_period(message, start, end, as_of):
                    in_period.append(message)
            except ValueError:
                withheld.append(
                    {
                        "message_id": str(message.get("message_id") or ""),
                        "channel_id": channel_id,
                        "reason": "sent_on_unreadable",
                        "text_copied": False,
                    }
                )
        if not in_period:
            channel_rows.append(
                {
                    "channel_id": channel_id,
                    "display_name": channel.get("display_name"),
                    "status": "no_messages_in_period",
                    "statement": "No messages in this period.",
                    "message_count_in_period": 0,
                    "point_count": 0,
                }
            )
            continue
        point_count = 0
        for message in in_period:
            message_id = str(message.get("message_id") or "").strip()
            if not message_id:
                continue
            messages_read += 1
            visible, hidden = split_comments(str(message.get("body") or ""))
            for comment in hidden:
                for code in injection_codes(comment):
                    injection_signals.append(
                        {"message_id": message_id, "code": code, "hidden_in": "html_comment", "followed": False}
                    )
            masked = redact(visible)
            anonymised_flags.append(masked["output_is_anonymised"] is True)
            release_flags.append(masked["agent_may_release"] is True)
            for entity in masked["entity_types"]:
                if entity not in entity_types:
                    entity_types.append(entity)
            for code in masked["prompt_injection_signals"]:
                injection_signals.append(
                    {"message_id": message_id, "code": code, "hidden_in": "redaction_gateway", "followed": False}
                )
            if masked["value_leaked"]:
                withheld.append(
                    {
                        "message_id": message_id,
                        "channel_id": channel_id,
                        "reason": "identifier_not_masked",
                        "text_copied": False,
                    }
                )
                continue
            reason = hold_reason(masked["text"], message)
            if reason:
                withheld.append(
                    {
                        "message_id": message_id,
                        "channel_id": channel_id,
                        "reason": reason,
                        "text_copied": False,
                    }
                )
                continue
            extracted = extract_message(masked["text"], display_name=display_name)
            for row in extracted["injections"]:
                injection_signals.append(
                    {
                        "message_id": message_id,
                        "code": ",".join(row["codes"]),
                        "line": row["line"],
                        "followed": False,
                    }
                )
                if row["followed"]:
                    followed = True
            for row in extracted["negated"]:
                negation.append(
                    {
                        "message_id": message_id,
                        "line": row["line"],
                        "positive_match": False,
                        "reason": row["reason"],
                    }
                )
            line_rows = _lines(masked["text"])
            event = {
                "event_id": message_id,
                "status": "current",
                "recorded_on": as_of_text,
                "paragraphs": [{"paragraph": 1, "lines": line_rows}],
            }
            passage = {
                "source_id": message_id,
                "title": message_id,
                "text": masked["text"],
                "reviewed_on": as_of_text,
            }
            passage_row = passage_currency(passage, as_of_text, STALE_AFTER_DAYS)
            used_lines = set()
            for key, kind, prefix in _KINDS:
                for row in extracted[key]:
                    counters[prefix] += 1
                    point_id = f"{prefix}{counters[prefix]}"
                    assessed = _assess(
                        kind,
                        point_id,
                        row["text"],
                        message_id,
                        row["line"],
                        event,
                        passage,
                        passage_row,
                        as_of_text,
                    )
                    claims.append(assessed["claim"])
                    used_lines.add(row["line"])
                    if assessed["kept"]:
                        point = {
                            "point_id": point_id,
                            "text": assessed["text"],
                            "channel_id": channel_id,
                            "message_ids": assessed["message_ids"],
                            "citation": assessed["citation"],
                            "exp41_verdict": assessed["exp41_verdict"],
                            "exp29_verdict": assessed["exp29_verdict"],
                        }
                        if kind == "action":
                            point["owner"] = row.get("owner")
                        sections[key].append(point)
                        point_count += 1
                    else:
                        not_relied.append(
                            {
                                "point_id": point_id,
                                "message_ids": [message_id],
                                "exp41_verdict": assessed["exp41_verdict"],
                                "exp29_verdict": assessed["exp29_verdict"],
                                "text_copied": False,
                            }
                        )
            classified = used_lines | {row["line"] for row in extracted["injections"]}
            classified |= {row["line"] for row in extracted["negated"]}
            not_classified += sum(1 for row in line_rows if row["line"] not in classified)
        status = "digested"
        statement = "Sentences in this period are listed only where a cue matched and both checkers supported the sentence."
        channel_rows.append(
            {
                "channel_id": channel_id,
                "display_name": channel.get("display_name"),
                "status": status,
                "statement": statement,
                "message_count_in_period": len(in_period),
                "point_count": point_count,
            }
        )

    summary = summarise_claims(claims) if claims else {
        "claim_count": 0,
        "answer_count": 0,
        "verdicts": {},
        "verdict_total": 0,
        "supported_count": 0,
        "non_supported_count": 0,
        "supported_rate": None,
        "each_claim_has_one_verdict": True,
        "stale_claim_count_is_separate": True,
        "other_failures_are_not_in_the_totals": True,
    }
    return {
        "sections": sections,
        "not_relied_on": not_relied,
        "withheld": withheld,
        "negation": {
            "positive_match": False,
            "count": len(negation),
            "rows": negation,
        },
        "injection_signals": injection_signals,
        "injection_followed": followed,
        "entity_types": entity_types,
        "output_is_anonymised": False,
        "anonymised_claim_seen": any(anonymised_flags),
        "release_claim_seen": any(release_flags),
        "messages_read": messages_read,
        "not_classified_count": not_classified,
        "channels": channel_rows,
        "groundedness": summary,
        "do_not_rely": bool(not_relied) or bool(withheld),
    }


def produce_digest(
    bundle: dict[str, Any],
    review: dict[str, Any] | None,
    as_of: str,
) -> dict[str, Any]:
    """Produce a digest only after the user has confirmed the channels and the period."""
    preview = preview_scope(bundle, as_of)
    if preview.get("outcome") != "scope_only":
        return preview
    confirmed = confirm_scope(preview, review)
    if not confirmed.get("scope_confirmed"):
        confirmed["outcome"] = "confirmation_refused"
        confirmed["digest_produced"] = False
        confirmed["digest"] = None
        return confirmed
    cleaned, _removed = _strip(deepcopy(bundle))
    try:
        as_of_date = _parse_day(as_of, "as_of")
        start = _parse_day(confirmed["period"]["start"], "period_start")
        end = _parse_day(confirmed["period"]["end"], "period_end")
    except ValueError:
        return _refusal("invalid_request")
    try:
        built = _digest_channels(
            cleaned,
            confirmed["scope_confirmation"]["channel_ids"],
            str(confirmed["requesting_user"].get("display_name") or ""),
            start,
            end,
            as_of_date,
            as_of,
        )
    except NeighbourMissing as exc:
        refused = _refusal("neighbour_missing")
        refused["refusal"]["neighbour"] = str(exc)
        return refused
    confirmed["outcome"] = "digest"
    confirmed["digest_produced"] = True
    confirmed["human_approval"] = None
    confirmed["prompt_injection"] = {
        "detected": bool(built["injection_signals"]),
        "followed": built["injection_followed"],
        "signals": built["injection_signals"],
    }
    section_total = sum(len(built["sections"][name]) for name, _, _ in _KINDS)
    confirmed["digest"] = {
        "decisions": built["sections"]["decisions"],
        "open_questions": built["sections"]["open_questions"],
        "actions": built["sections"]["actions"],
        "attention": built["sections"]["attention"],
        "not_relied_on": built["not_relied_on"],
        "withheld": built["withheld"],
        "negation": built["negation"],
        "channels": built["channels"],
        "counts": {
            "messages_read": built["messages_read"],
            "decision_count": len(built["sections"]["decisions"]),
            "open_question_count": len(built["sections"]["open_questions"]),
            "action_count": len(built["sections"]["actions"]),
            "attention_count": len(built["sections"]["attention"]),
            "withheld_count": len(built["withheld"]),
            "not_classified_count": built["not_classified_count"],
            "not_relied_on_count": len(built["not_relied_on"]),
            "section_point_count": section_total,
            "section_counts_are_not_added_to_message_count": True,
            "groundedness_claim_count_is_separate": True,
        },
        "groundedness": built["groundedness"],
        "do_not_rely": built["do_not_rely"],
        "full_body_recorded": False,
    }
    confirmed["full_body_recorded"] = False
    confirmed["reuse"] = {
        "experiment_08": {
            "called": True,
            "output_is_anonymised": False,
            "anonymised_claim_seen": built["anonymised_claim_seen"],
            "agent_may_release": False,
            "release_claim_seen": built["release_claim_seen"],
            "entity_types": built["entity_types"],
            "values_copied": False,
        },
        "experiment_41": {
            "called": True,
            "rule": "The sentence must be contained in the cited lines. A paraphrase fails.",
        },
        "experiment_29": {
            "called": True,
            "foundry_called": False,
            "rule": "Every content token, number, and date in the sentence must be in the cited message.",
        },
    }
    by_id = {row["channel_id"]: row for row in built["channels"]}
    merged: list[dict[str, Any]] = []
    for row in confirmed["channels"]:
        if row["channel_id"] in by_id:
            merged.append(by_id[row["channel_id"]])
            continue
        merged.append(
            {
                "channel_id": row["channel_id"],
                "display_name": row.get("display_name"),
                "status": row["status"],
                "statement": row["statement"],
                "message_count_in_period": row.get("message_count_in_period"),
                "point_count": 0,
            }
        )
    confirmed["digest"]["channels"] = merged
    confirmed["channels"] = merged
    return confirmed


def run(bundle: dict[str, Any], as_of: str, review: dict[str, Any] | None = None) -> dict[str, Any]:
    if review is None:
        return preview_scope(bundle, as_of)
    return produce_digest(bundle, review, as_of)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a read-only Teams channel digest.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--confirm", default=None)
    parser.add_argument("--post", action="store_true")
    parser.add_argument("--reply", action="store_true")
    parser.add_argument("--react", action="store_true")
    parser.add_argument("--mention", action="store_true")
    parser.add_argument("--forward", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.post:
            post_message()
        if args.reply:
            reply_message()
        if args.react:
            react_message()
        if args.mention:
            mention_user()
        if args.forward:
            forward_message()
        bundle = _load(Path(args.input))
        review = _load(Path(args.confirm)) if args.confirm else None
        result = run(bundle, args.as_of, review)
    except DigestForbidden as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
