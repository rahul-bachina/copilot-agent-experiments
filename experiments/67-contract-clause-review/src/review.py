#!/usr/bin/env python3
"""Compare one synthetic contract with one clause playbook.

The lawyer owns legal interpretation. The agent does not give legal advice,
redline, accept terms, sign, or send. The same inputs and the same question
date produce the same JSON. Approval words inside the contract are not
approval. A seen step is a separate object, from a directory lawyer, for
this contract hash and this deviations hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from clauses import TOPICS, compare
    from cues import claims_clearance, claims_role, cue_categories, injection_signals
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from reuse import (
        NeighbourMissing,
        intake_contract,
        redact_uk_identifiers,
        strip_request,
        tool_contract_signals,
    )
    from sources import statutory_note
else:
    from .clauses import TOPICS, compare
    from .cues import claims_clearance, claims_role, cue_categories, injection_signals
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .reuse import (
        NeighbourMissing,
        intake_contract,
        redact_uk_identifiers,
        strip_request,
        tool_contract_signals,
    )
    from .sources import statutory_note

LABEL = "CLAUSE COMPARISON FOR A LAWYER. NOT LEGAL ADVICE. NOT A REDLINE. TERMS ARE NOT ACCEPTED."
CATALOGUE_ID = "L001"
EXPERIMENT_ID = "exp-67-contract-clause-review"
AUTONOMY = "A0"
NOT_FOUND = "not found"
NOT_COPIED = "not copied"
AUDIENCES = frozenset({"business", "consumer"})
ROLES = frozenset({"processor", "controller_only", "not_stated"})
PROHIBITED_KEYS = frozenset(
    {
        "approved",
        "human_approval",
        "terms_accepted",
        "signed",
        "sent",
        "redline_applied",
        "legal_advice",
        "legal_score",
        "marked_safe",
        "role",
        "clearance",
        "article_28_complied",
        "advice_given",
        "voidness_decided",
        "fairness_decided",
        "reasonableness_decided",
        "contract_hash",
        "deviations_hash",
    }
)


class ContractReviewForbidden(RuntimeError):
    """Advice, redlines, acceptance, signature, and sending are not tools."""


class NotSynthetic(ValueError):
    """The record was not marked synthetic. The message does not include the body."""


def give_legal_advice(*_args, **_kwargs) -> None:
    raise ContractReviewForbidden("The agent does not give legal advice.")


def redline(*_args, **_kwargs) -> None:
    raise ContractReviewForbidden("The agent does not redline a contract.")


def accept_terms(*_args, **_kwargs) -> None:
    raise ContractReviewForbidden("The agent does not accept terms.")


def sign(*_args, **_kwargs) -> None:
    raise ContractReviewForbidden("The agent does not sign.")


def send(*_args, **_kwargs) -> None:
    raise ContractReviewForbidden("The agent does not send.")


def _parse_day(value: object) -> date | None:
    if type(value) is date:
        return value
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _contract_hash(request: dict) -> str:
    payload = {key: request[key] for key in sorted(request) if key not in PROHIBITED_KEYS}
    return _sha(_canonical(payload))


def _strip_local(request: dict) -> tuple[dict, list[str]]:
    cleaned = {}
    ignored = []
    for key, value in request.items():
        if key in PROHIBITED_KEYS:
            ignored.append(key)
            continue
        cleaned[key] = value
    return cleaned, ignored


def _person(directory: dict, ref: object) -> dict | None:
    people = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(people, list) or not isinstance(ref, str):
        return None
    matches = [row for row in people if isinstance(row, dict) and row.get("ref") == ref]
    if len(matches) != 1:
        return None
    return matches[0]


def _audience(value: object) -> str:
    if isinstance(value, str) and value in AUDIENCES:
        return value
    return "unparseable"


def _role(value: object) -> str:
    if isinstance(value, str) and value in ROLES:
        return value
    return "unparseable"


def _playbook_dates(playbook: dict, as_of: date) -> dict:
    effective = _parse_day(playbook.get("effective_from")) if isinstance(playbook, dict) else None
    review_due = _parse_day(playbook.get("review_due")) if isinstance(playbook, dict) else None
    effective_raw = playbook.get("effective_from") if isinstance(playbook, dict) else None
    review_raw = playbook.get("review_due") if isinstance(playbook, dict) else None
    unparseable = (effective_raw not in (None, "") and effective is None) or (
        review_raw not in (None, "") and review_due is None
    )
    missing = effective is None or review_due is None
    not_yet = bool(effective and effective > as_of)
    stale = bool(review_due and review_due <= as_of)
    current = not unparseable and not missing and not not_yet and not stale
    return {
        "effective_from": effective.isoformat() if effective else None,
        "review_due": review_due.isoformat() if review_due else None,
        "unparseable": unparseable or missing,
        "not_yet_in_force": not_yet,
        "stale": stale,
        "current": current,
        "coerced": False,
    }


def _mask_sentence(sentence: str, *, rules_as_of: date) -> tuple[str, dict, bool]:
    masked, local = mask_text(sentence)
    try:
        redacted = redact_uk_identifiers(masked, rules_as_of=rules_as_of)
    except (NeighbourMissing, Exception):
        return NOT_COPIED, local, False
    shown = redacted["text"]
    if shown.startswith("[REDACTION PROPOSAL"):
        return NOT_COPIED, local, False
    return shown, local, True


def _publish_rows(rows: list[dict], *, withhold: bool, rules_as_of: date) -> tuple[list[dict], dict, bool]:
    published = []
    totals = {"phone": 0, "email": 0, "date_of_birth": 0, "postal_address": 0, "personal_name": 0}
    verbatim = True
    for source in rows:
        row = {key: value for key, value in source.items() if not str(key).startswith("_")}
        quotes = list(row.get("quotes") or [])
        shown: list[str] = []
        if withhold:
            row["quoted_text"] = NOT_COPIED
            row["further_quotes"] = []
            row["verbatim"] = False
            verbatim = False
        elif not quotes and row.get("cue_withheld"):
            row["quoted_text"] = NOT_COPIED
            row["further_quotes"] = []
            row["verbatim"] = False
            verbatim = False
        elif not quotes:
            row["quoted_text"] = NOT_FOUND
            row["further_quotes"] = []
            row["verbatim"] = True
        else:
            for quote in quotes:
                text, counts, ok = _mask_sentence(quote, rules_as_of=rules_as_of)
                if not ok:
                    verbatim = False
                    shown.append(NOT_COPIED)
                    continue
                for kind, count in counts["counts"].items():
                    totals[kind] = totals.get(kind, 0) + count
                shown.append(text)
            row["quoted_text"] = shown[0]
            row["further_quotes"] = shown[1:]
            row["verbatim"] = NOT_COPIED not in shown
            if not row["verbatim"]:
                verbatim = False
        row.pop("quotes", None)
        row["marked_safe"] = False
        published.append(row)
    masking = {
        "counts": totals,
        "any": any(totals.values()),
        "values_stored": False,
        "values_copied": False,
        "described_as_anonymised": False,
        "quotes_are_verbatim_apart_from_masks": verbatim and not withhold,
    }
    return published, masking, verbatim


def _publish_article(article: dict, *, withhold: bool, rules_as_of: date) -> dict:
    copied = deepcopy(article)
    elements = []
    for element in copied.get("elements") or []:
        row = dict(element)
        quote = row.get("quoted_text")
        if withhold:
            row["quoted_text"] = NOT_COPIED
        elif quote and quote != NOT_FOUND:
            text, _counts, ok = _mask_sentence(quote, rules_as_of=rules_as_of)
            row["quoted_text"] = text if ok else NOT_COPIED
        row["complies"] = False
        elements.append(row)
    copied["elements"] = elements
    copied["complies"] = False
    copied["marked_complete"] = False
    copied["marked_safe"] = False
    return copied


def _deviation_payload(rows: list[dict], article: dict) -> dict:
    shown = []
    for row in rows:
        shown.append(
            {
                "topic": row.get("topic"),
                "status": row.get("status"),
                "clause_reference": row.get("clause_reference"),
                "quoted_text": row.get("quoted_text"),
                "further_quotes": row.get("further_quotes") or [],
                "playbook_position": row.get("playbook_position"),
                "playbook_text": row.get("playbook_text"),
            }
        )
    return {
        "rows": shown,
        "article_28_not_found": list(article.get("not_found") or []),
    }


def review_contract(request: dict, playbook: dict, directory: dict, as_of: str) -> dict:
    question = _parse_day(as_of)
    if question is None:
        raise ValueError("as_of must be YYYY-MM-DD")
    if not isinstance(request, dict) or not isinstance(playbook, dict) or not isinstance(directory, dict):
        raise TypeError("request, playbook, and directory must be objects")
    if request.get("synthetic") is not True or playbook.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")
    if directory.get("synthetic") is not True:
        raise NotSynthetic("directory is not marked synthetic")

    cleaned, tool_ignored = strip_request(request)
    local_cleaned, local_ignored = _strip_local(cleaned)
    text = local_cleaned.get("text")
    if not isinstance(text, str):
        return _unreadable(question, "text_unparseable")
    audience = _audience(local_cleaned.get("audience"))
    role = _role(local_cleaned.get("processing_role"))
    caller = _person(directory, local_cleaned.get("caller_ref"))
    ceiling = caller.get("clearance") if caller else None
    directory_role = caller.get("role") if caller else "not_found"
    if directory_role not in {"lawyer", "guest"}:
        directory_role = "not_found" if caller is None else "unparseable"
        ceiling = None
    metadata = local_cleaned.get("metadata") if isinstance(local_cleaned.get("metadata"), dict) else {}
    meta_marks, meta_bad = metadata_markings(metadata.get("marking"))
    content_marks = content_markings(text)
    marking = higher_marking(meta_marks + content_marks)
    withhold = above_ceiling(marking, ceiling if isinstance(ceiling, str) else None)
    held, hold_bad = legal_hold(metadata.get("legal_hold"), text)
    labels, retention_bad = retention_labels(metadata.get("retention"), text)
    cues = cue_categories(text)
    signals = injection_signals(text)
    try:
        tool_signals = tool_contract_signals(text)
    except NeighbourMissing:
        tool_signals = []
    dates = _playbook_dates(playbook, question)
    compared = compare(text, playbook, audience, role)
    contract_date = local_cleaned.get("contract_date")
    parsed_contract_date = _parse_day(contract_date) if contract_date not in (None, "") else None
    contract_date_unparseable = contract_date not in (None, "") and parsed_contract_date is None
    contract_id = local_cleaned.get("contract_id")
    if not isinstance(contract_id, str) or not contract_id.strip() or len(contract_id) > 80:
        contract_id = "unspecified"
    try:
        intake = intake_contract(
            text,
            contract_id=contract_id,
            document_date=parsed_contract_date.isoformat() if parsed_contract_date else None,
            as_of=question,
        )
    except (NeighbourMissing, Exception):
        intake = {
            "called": False,
            "error": "not_run",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "handed_off": False,
            "content_recorded": False,
            "output_is_anonymised": False,
        }
    intake["files_confirmed"] = False
    intake["purpose_confirmed"] = False
    intake["handed_off"] = False
    try:
        identifiers = redact_uk_identifiers(text, rules_as_of=question)
        identifier_summary = {
            "types": identifiers["types"],
            "count": identifiers["count"],
            "output_is_anonymised": False,
            "values_stored": False,
            "rules_stale": identifiers["rules_stale"],
            "rules_pinned_on": identifiers["rules_pinned_on"],
        }
    except (NeighbourMissing, Exception):
        identifier_summary = {
            "types": [],
            "count": None,
            "output_is_anonymised": False,
            "values_stored": False,
            "rules_stale": None,
            "error": "not_run",
        }
    input_mask, _input_counts = mask_text(text)
    del input_mask
    rows, masking, _verbatim = _publish_rows(
        compared["rows"] + compared["outside_rows"],
        withhold=withhold,
        rules_as_of=question,
    )
    article = _publish_article(compared["article_28"], withhold=withhold, rules_as_of=question)
    note = statutory_note(question, audience, compared["jurisdictions"])
    topic_rows = [row for row in rows if row["topic"] in TOPICS]
    missing = [row["topic"] for row in topic_rows if row["status"] == "not_found"]
    deviations = [row for row in rows if row["result"] in {"deviation", "lawyer_route"}]
    in_playbook = [row for row in topic_rows if row["result"] == "in_playbook"]
    payload = _deviation_payload(rows, article)
    deviations_hash = _sha(_canonical(payload))
    contract_hash = _contract_hash(local_cleaned)
    if cues["distress"] or cues["grievance"]:
        outcome = "human_route"
    elif caller is None or directory_role == "not_found":
        outcome = "caller_not_in_directory"
    elif withhold:
        outcome = "above_clearance"
    elif not isinstance(text, str):
        outcome = "unreadable"
    else:
        outcome = "comparison"
    pins_confirmed = not note["any_unconfirmed"]
    playbook_current = dates["current"] and not intake.get("catalogue_stale")
    may_rely = (
        outcome == "comparison"
        and playbook_current
        and pins_confirmed
        and not cues["distress"]
        and not cues["grievance"]
    )
    input_counts = mask_text(text)[1]
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "as_of": question.isoformat(),
        "contract_id": contract_id,
        "playbook_id": playbook.get("playbook_id") if isinstance(playbook.get("playbook_id"), str) else "not found",
        "contract_hash": contract_hash,
        "deviations_hash": deviations_hash,
        "outcome": outcome,
        "human_approval": None,
        "legal_advice": False,
        "advice_given": False,
        "redline_applied": False,
        "terms_accepted": False,
        "signed": False,
        "sent": False,
        "legal_score": None,
        "marked_safe": False,
        "article_28_complied": False,
        "reasonableness_decided": False,
        "fairness_decided": False,
        "voidness_decided": False,
        "coerced": False,
        "instructions_followed": False,
        "prompt_injection": {
            "detected": bool(signals or tool_signals or intake.get("injection_detected")),
            "signals": signals,
            "tool_contract_reviewer_signals": tool_signals,
            "followed": False,
        },
        "prohibited_keys_ignored": sorted(set(tool_ignored + local_ignored)),
        "directory_role": directory_role,
        "clearance": ceiling if isinstance(ceiling, str) else None,
        "self_declared_role_ignored": claims_role(text),
        "self_declared_clearance_ignored": claims_clearance(text),
        "marking": marking,
        "marking_metadata_unparseable": meta_bad,
        "legal_hold": held,
        "legal_hold_metadata_unparseable": hold_bad,
        "legal_hold_dropped": False,
        "retention_labels": labels,
        "retention_metadata_unparseable": retention_bad,
        "retention_dropped": False,
        "quotes_withheld": withhold or caller is None,
        "contract_body_copied": False,
        "audience": audience,
        "audience_unparseable": audience == "unparseable",
        "processing_role": role,
        "processing_role_unparseable": role == "unparseable",
        "contract_date": parsed_contract_date.isoformat() if parsed_contract_date else None,
        "contract_date_unparseable": contract_date_unparseable,
        "playbook": dates,
        "clauses": topic_rows,
        "outside_playbook": [row for row in rows if row["topic"] == "outside_playbook"],
        "missing_clauses": missing,
        "deviations": deviations,
        "article_28": article,
        "statutory_note": note,
        "cue": cues,
        "distress_seen": False,
        "grievance_seen": False,
        "intake": intake,
        "uk_identifiers": identifier_summary,
        "input_mask_counts": input_counts,
        "output_mask": masking,
        "topic_count": len(topic_rows),
        "in_playbook_count": len(in_playbook),
        "deviation_count": len([row for row in topic_rows if row["result"] == "deviation"]),
        "lawyer_route_count": len([row for row in topic_rows if row["result"] == "lawyer_route"]),
        "missing_count": len(missing),
        "outside_playbook_count": len([row for row in rows if row["topic"] == "outside_playbook"]),
        "sources_current": bool(playbook_current and pins_confirmed),
        "may_be_relied_on": may_rely,
        "pins_confirmed": pins_confirmed,
        "model_called": False,
        "network_called": False,
        "statement": "This comparison is not legal advice. The lawyer decides. Terms are not accepted.",
    }


def _unreadable(question: date, reason: str) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "as_of": question.isoformat(),
        "outcome": "unreadable",
        "reason": reason,
        "human_approval": None,
        "legal_advice": False,
        "terms_accepted": False,
        "signed": False,
        "sent": False,
        "redline_applied": False,
        "legal_score": None,
        "marked_safe": False,
        "article_28_complied": False,
        "coerced": False,
        "instructions_followed": False,
        "contract_body_copied": False,
        "may_be_relied_on": False,
        "clauses": [],
        "deviations": [],
        "missing_clauses": [],
    }


def record_lawyer_seen(result: dict, directory: dict, decision: dict) -> dict:
    """Record that a directory lawyer has seen this exact comparison.

    The record does not accept terms, sign, or send. Strings are not coerced
    to true. A hash that does not match this result is not reused.
    """

    if not isinstance(result, dict) or result.get("label") != LABEL:
        raise ValueError("result is not a clause comparison")
    if not isinstance(directory, dict) or directory.get("synthetic") is not True:
        raise NotSynthetic("directory is not marked synthetic")
    if not isinstance(decision, dict):
        raise TypeError("decision must be an object")
    updated = deepcopy(result)
    updated["terms_accepted"] = False
    updated["signed"] = False
    updated["sent"] = False
    updated["redline_applied"] = False
    updated["legal_advice"] = False
    updated["marked_safe"] = False
    updated["article_28_complied"] = False
    blocked = _seen_block(updated, directory, decision)
    if blocked:
        updated["human_approval"] = None
        updated["blocked_reason"] = blocked
        return updated
    item = decision["item"]
    if item == "distress-seen":
        updated["distress_seen"] = True
    elif item == "grievance-seen":
        updated["grievance_seen"] = True
    updated["human_approval"] = {
        "recorded": True,
        "item": item,
        "approver_ref": decision["approver_ref"],
        "decision": "seen",
        "contract_hash": updated["contract_hash"],
        "deviations_hash": updated["deviations_hash"],
        "terms_accepted": False,
        "signed": False,
        "sent": False,
        "redline_applied": False,
        "legal_advice": False,
    }
    updated["blocked_reason"] = None
    return updated


def _seen_block(result: dict, directory: dict, decision: dict) -> str | None:
    item = decision.get("item")
    if item not in {"clause-review", "distress-seen", "grievance-seen"}:
        return "item_not_recognised"
    if decision.get("decision") != "seen":
        return "decision_not_seen"
    person = _person(directory, decision.get("approver_ref"))
    if person is None:
        return "approver_not_in_directory"
    if person.get("role") != "lawyer":
        return "not_lawyer"
    if decision.get("contract_hash") != result.get("contract_hash"):
        return "contract_hash_mismatch"
    if decision.get("deviations_hash") != result.get("deviations_hash"):
        return "deviations_hash_mismatch"
    cue = result.get("cue") or {}
    if item == "clause-review" and cue.get("distress") and result.get("distress_seen") is not True:
        return "distress_not_seen"
    if item == "clause-review" and cue.get("grievance") and result.get("grievance_seen") is not True:
        return "grievance_not_seen"
    playbook = result.get("playbook") or {}
    needs_playbook = bool(playbook.get("stale") or playbook.get("not_yet_in_force") or playbook.get("unparseable"))
    if item == "clause-review" and needs_playbook and decision.get("playbook_seen") is not True:
        return "playbook_not_seen"
    if item == "clause-review" and result.get("pins_confirmed") is not True and decision.get("pins_seen") is not True:
        return "pins_not_seen"
    if item == "distress-seen" and not cue.get("distress"):
        return "distress_not_flagged"
    if item == "grievance-seen" and not cue.get("grievance"):
        return "grievance_not_flagged"
    return None


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare a synthetic contract with a clause playbook.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--playbook", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = review_contract(
            _load_json(args.request),
            _load_json(args.playbook),
            _load_json(args.directory),
            args.as_of,
        )
    except (OSError, json.JSONDecodeError, NotSynthetic, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
