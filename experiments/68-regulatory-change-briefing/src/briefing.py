#!/usr/bin/env python3
"""Draft a regulatory change briefing. The compliance owner decides applicability.

The core reads pinned synthetic snapshots. It does not browse a live site.
It does not decide that a change applies, change a policy, control, or record,
or send anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    from dates import NOT_STATED, day_gap, parse_as_of, parse_date_token, stated_dates
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from match import (
        affirmed_sentence,
        content_sentences,
        cue_categories,
        injection_signals,
        leading_criteria,
        people_counts,
        phrase_relation,
        superseded_affirmed,
        superseded_by_ids,
        supersedes_ids,
        withdrawn_affirmed,
    )
    from reuse import (
        assess_fca_source,
        intake_notice,
        mi_context,
        redact_uk_identifiers,
        snapshot_currency,
    )
    from sources import practice_pins, statute_pin
else:
    from .dates import NOT_STATED, day_gap, parse_as_of, parse_date_token, stated_dates
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .match import (
        affirmed_sentence,
        content_sentences,
        cue_categories,
        injection_signals,
        leading_criteria,
        people_counts,
        phrase_relation,
        superseded_affirmed,
        superseded_by_ids,
        supersedes_ids,
        withdrawn_affirmed,
    )
    from .reuse import (
        assess_fca_source,
        intake_notice,
        mi_context,
        redact_uk_identifiers,
        snapshot_currency,
    )
    from .sources import practice_pins, statute_pin

ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS_PATH = ROOT / "fixtures" / "publications.json"
REGISTER_PATH = ROOT / "fixtures" / "policy_register.json"
DIRECTORY_PATH = ROOT / "fixtures" / "directory.json"

CATALOGUE_ID = "L002"
EXPERIMENT_ID = "68-regulatory-change-briefing"
AUTONOMY = "A0"
LABEL = "REGULATORY CHANGE BRIEFING FOR A COMPLIANCE OWNER"
STATUSES = {"current", "withdrawn", "superseded", "draft"}
_STRIP = {
    "human_approval",
    "approved",
    "approval",
    "applies",
    "applicable",
    "not_applicable",
    "sent",
    "send",
    "policy_changed",
    "control_changed",
    "record_changed",
    "role",
    "clearance",
    "marked_safe",
    "marked_acceptable",
    "publications",
    "register",
    "directory",
}
_SEEN_FIELDS = {
    "approver_ref",
    "item",
    "decision",
    "publication_hash",
    "briefing_hash",
    "questions_hash",
    "pins_seen",
    "flags_seen",
    "sources_seen",
}


class NotSynthetic(ValueError):
    """The payload is not marked synthetic."""


class BriefingForbidden(RuntimeError):
    """A consequential action this agent does not take."""


def decide_applicability(*_args, **_kwargs) -> None:
    raise BriefingForbidden("The agent does not decide that a change applies or does not apply.")


def change_policy(*_args, **_kwargs) -> None:
    raise BriefingForbidden("The agent does not change a policy.")


def change_control(*_args, **_kwargs) -> None:
    raise BriefingForbidden("The agent does not change a control.")


def change_record(*_args, **_kwargs) -> None:
    raise BriefingForbidden("The agent does not change a record.")


def send(*_args, **_kwargs) -> None:
    raise BriefingForbidden("The agent does not send anything.")


def _sha(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("synthetic") is not True:
        raise NotSynthetic(path.name)
    return payload


def _require_synthetic(payload: dict, label: str) -> None:
    if not isinstance(payload, dict) or payload.get("synthetic") is not True:
        raise NotSynthetic(label)


def _person_rows(directory: dict) -> dict[str, dict]:
    rows = {}
    for person in directory.get("people") or []:
        if isinstance(person, dict) and isinstance(person.get("ref"), str):
            rows[person["ref"]] = {
                "ref": person["ref"],
                "role": person.get("role") if isinstance(person.get("role"), str) else None,
                "clearance": person.get("clearance") if isinstance(person.get("clearance"), str) else None,
            }
    return rows


def _policy_rows(register: dict) -> dict[str, dict]:
    rows = {}
    for policy in register.get("policies") or []:
        if isinstance(policy, dict) and isinstance(policy.get("policy_id"), str):
            topics = policy.get("topics") if isinstance(policy.get("topics"), list) else []
            rows[policy["policy_id"]] = {
                "policy_id": policy["policy_id"],
                "title": policy.get("title") if isinstance(policy.get("title"), str) else None,
                "topics": [topic for topic in topics if isinstance(topic, str)],
                "owner_role": policy.get("owner_role") if isinstance(policy.get("owner_role"), str) else None,
                "review_due": policy.get("review_due") if isinstance(policy.get("review_due"), str) else None,
                "status": policy.get("status") if isinstance(policy.get("status"), str) else None,
                "selection_note": policy.get("selection_note") if isinstance(policy.get("selection_note"), str) else "",
            }
    return rows


def _diff_maps(pinned: dict, caller: dict, key: str) -> list[dict]:
    differences = []
    for item_id in sorted(set(pinned) | set(caller)):
        if item_id not in pinned:
            differences.append({"id": item_id, "difference": "not_in_pinned"})
            continue
        if item_id not in caller:
            differences.append({"id": item_id, "difference": "missing_from_caller"})
            continue
        if pinned[item_id] != caller[item_id]:
            differences.append({"id": item_id, "difference": "fields_differ"})
    if key == "register":
        for field in ("internal_consultation_minimum_days", "minimum_is_statutory"):
            if pinned.get(field) != caller.get(field):
                differences.append({"id": field, "difference": "fields_differ"})
    return differences


def _published(value: object) -> tuple[date | None, str | None, bool]:
    """Return (date, iso, unparseable). None is undated, not an error."""

    if value is None or value == "":
        return None, None, False
    if not isinstance(value, str):
        return None, None, True
    parsed, bad = parse_date_token(value)
    if bad or parsed is None:
        return None, None, True
    if parsed.isoformat() != value:
        return None, None, True
    return parsed, parsed.isoformat(), False


def _flags_for(publication: dict, text: str, others: list[dict]) -> dict:
    status = publication.get("status")
    status_unparseable = status not in STATUSES
    withdrawn = status == "withdrawn" or withdrawn_affirmed(text)
    superseded = status == "superseded" or superseded_affirmed(text)
    by_ids = superseded_by_ids(text)
    own = supersedes_ids(text)
    publication_id = str(publication.get("id") or "")
    for other in others:
        if not isinstance(other, dict):
            continue
        other_text = other.get("body") if isinstance(other.get("body"), str) else ""
        if publication_id and publication_id in supersedes_ids(other_text):
            superseded = True
            other_id = str(other.get("id") or "")
            if other_id and other_id not in by_ids:
                by_ids.append(other_id)
    missing = [item for item in own if item not in {row.get("id") for row in others}]
    return {
        "status": None if status_unparseable else status,
        "status_unparseable": status_unparseable,
        "withdrawn": withdrawn,
        "superseded": superseded,
        "superseded_by": by_ids,
        "supersedes": own,
        "supersedes_not_found": missing,
        "coerced": False,
    }


def _minimum_days(register: dict) -> tuple[int | None, bool]:
    raw = register.get("internal_consultation_minimum_days")
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
        return None, True
    return raw, False


def _questions(state: dict) -> list[str]:
    questions = [
        "Does this change apply to this organisation? The compliance owner decides. This briefing does not.",
    ]
    effective = state["dates"]["effective"]
    close = state["dates"]["consultation_close"]
    if effective["not_stated"]:
        questions.append("The effective date is not stated. A blank is not a date.")
    if effective["unparseable"]:
        questions.append("An effective date in the notice could not be read. It was not replaced with a default.")
    if effective["multiple"]:
        questions.append("More than one effective date is stated. None was chosen.")
    if close["not_stated"]:
        questions.append("The consultation close date is not stated.")
    if close["unparseable"]:
        questions.append("A consultation close date could not be read. It was not replaced with a default.")
    if close["multiple"]:
        questions.append("More than one consultation close date is stated. None was chosen.")
    flags = state["flags"]
    if flags["withdrawn"]:
        questions.append("The notice is marked withdrawn. Whether anything remains in force is for the owner.")
    if flags["superseded"]:
        questions.append("The notice is marked superseded. The owner decides what, if anything, replaces it.")
    if state["undated"]:
        questions.append("The publication date is not stated.")
    if state["stale"]:
        questions.append(
            "The publication date is outside this starter's freshness window. That window is not a statute."
        )
    if state["below_register_window"]:
        questions.append(
            "The stated consultation length is below the pinned register's internal minimum. "
            "Section 138I(2)(e) does not state a number of days. The notice is not marked acceptable."
        )
    for row in state["might"]:
        shown = ", ".join(repr(topic) for topic in row.get("topics") or [row["topic"]])
        questions.append(
            f"Might {row['policy_id']} be affected because the notice states {shown}? "
            "The owner decides. The agent does not."
        )
    for row in state["negated"]:
        questions.append(
            f"The notice denies {row['topic']!r} for {row['policy_id']}. "
            "That denial is not a decision that the policy is out of scope."
        )
    for row in state["qualified"]:
        questions.append(
            f"A qualification follows wording that mentions {row['topic']!r} for {row['policy_id']}. "
            "It is not listed as an unqualified match."
        )
    if state["leading"]:
        questions.append("A leading criterion is on the pinned register. It was not applied.")
    if state["cues"]["distress"] or state["cues"]["grievance"]:
        questions.append(
            "A distress, grievance, or disclosure cue was flagged. The cue text is not copied. "
            "This is not a routine briefing."
        )
    if state["caller_text_differs"]:
        questions.append("The pasted notice differs from the pinned snapshot. The pinned snapshot was quoted.")
    if state["register_differences"] or state["directory_differences"]:
        questions.append(
            "The caller-supplied register or directory differs from the pinned copy. The pinned copy was used."
        )
    questions.append(
        "Section 138I was opened as publication-practice context. Section 138L was not opened. "
        "No view is taken on whether the consultation duty was met."
    )
    return questions


def _hash_bundle(result: dict) -> dict:
    publication = {
        "id": result.get("publication_id"),
        "published": result.get("publication_date"),
        "body_sha256": result.get("body_sha256"),
    }
    briefing = {
        "what_changed": result.get("what_changed"),
        "dates": result.get("dates"),
        "might_be_affected": result.get("might_be_affected"),
        "flags": result.get("flags"),
        "people": result.get("people"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "retention": result.get("retention"),
        "pins_confirmed": result.get("pins_confirmed"),
        "statute_quotes": (result.get("statute") or {}).get("quotes"),
        "below_register_window": result.get("below_register_window"),
    }
    return {
        "publication_hash": _sha(publication),
        "briefing_hash": _sha(briefing),
        "questions_hash": _sha(result.get("open_questions")),
    }


def _base(question: date, **extra) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "as_of": question.isoformat(),
        "human_approval": None,
        "applies": None,
        "applicability": "not decided",
        "marked_applicable": False,
        "marked_not_applicable": False,
        "marked_acceptable": False,
        "marked_safe": False,
        "policy_changed": False,
        "control_changed": False,
        "record_changed": False,
        "sent": False,
        "coerced": False,
        "instructions_followed": False,
        "network_called": False,
        "live_site_fetched": False,
        "model_called": False,
        "may_be_relied_on": False,
        "output_is_anonymised": False,
        "body_copied": False,
    }
    result.update(extra)
    return result


def draft_briefing(request: dict, register: dict, directory: dict, as_of: object) -> dict:
    """Return one briefing. The same inputs and the same question date match."""

    question = parse_as_of(as_of)
    _require_synthetic(request, "request")
    _require_synthetic(register, "register")
    _require_synthetic(directory, "directory")
    working = dict(request)
    ignored = sorted(key for key in list(working) if key in _STRIP)
    for key in ignored:
        working.pop(key, None)

    pinned_register = _load(REGISTER_PATH)
    pinned_directory = _load(DIRECTORY_PATH)
    pinned_publications = _load(PUBLICATIONS_PATH)
    notices = [row for row in pinned_publications.get("notices") or [] if isinstance(row, dict)]
    by_id = {row.get("id"): row for row in notices}

    register_differences = _diff_maps(_policy_rows(pinned_register), _policy_rows(register), "register")
    if register.get("internal_consultation_minimum_days") != pinned_register.get("internal_consultation_minimum_days"):
        if not any(row["id"] == "internal_consultation_minimum_days" for row in register_differences):
            register_differences.append(
                {"id": "internal_consultation_minimum_days", "difference": "fields_differ"}
            )
    directory_differences = _diff_maps(
        _person_rows(pinned_directory),
        _person_rows(directory),
        "directory",
    )

    publication_id = working.get("publication_id")
    if not isinstance(publication_id, str) or not publication_id:
        raise ValueError("publication_id is missing")
    caller_ref = working.get("caller_ref")
    people = _person_rows(pinned_directory)
    person = people.get(caller_ref) if isinstance(caller_ref, str) else None
    if person is None or not person.get("role") or not person.get("clearance"):
        return _base(
            question,
            outcome="caller_not_in_directory",
            publication_id=publication_id,
            caller_ref=caller_ref if isinstance(caller_ref, str) else None,
            role_from_directory=None,
            self_declared_role_ignored=True,
            what_changed={"quote": "not found", "verbatim": False, "source_id": publication_id},
            might_be_affected=[],
            open_questions=[
                "The caller is not in the pinned directory. No notice text was copied.",
            ],
            ignored_request_fields=ignored,
            applies=None,
        )

    notice = by_id.get(publication_id)
    if notice is None:
        result = _base(
            question,
            outcome="not_found",
            publication_id=publication_id,
            caller_ref=person["ref"],
            role_from_directory=person["role"],
            what_changed={
                "quote": "not found",
                "verbatim": False,
                "source_id": publication_id,
                "source": "Pinned synthetic snapshots. No live page was fetched.",
                "publication_date": NOT_STATED,
            },
            dates={
                "effective": {"display": NOT_STATED, "not_stated": True, "dates": [], "coerced": False},
                "consultation_close": {"display": NOT_STATED, "not_stated": True, "dates": [], "coerced": False},
            },
            might_be_affected=[],
            open_questions=["The publication id is not in the pinned snapshots. Nothing was guessed."],
            ignored_request_fields=ignored,
            flags={"withdrawn": False, "superseded": False, "undated": False, "stale": False},
        )
        result.update(_hash_bundle(result))
        return result

    body = notice.get("body") if isinstance(notice.get("body"), str) else ""
    pasted = working.get("pasted_text")
    caller_text_differs = isinstance(pasted, str) and pasted != body
    published, published_iso, published_bad = _published(notice.get("published"))
    currency = snapshot_currency(published_iso, question)
    undated = published_iso is None
    stale = currency.get("currency") == "stale"
    text_dates = stated_dates(body, published)
    flags = _flags_for(notice, body, notices)
    flags["undated"] = undated or published_bad
    flags["stale"] = stale
    flags["published_unparseable"] = published_bad

    meta = notice.get("metadata") if isinstance(notice.get("metadata"), dict) else {}
    request_meta = working.get("metadata") if isinstance(working.get("metadata"), dict) else {}
    meta_marks, meta_bad = metadata_markings(meta.get("marking"))
    request_marks, request_bad = metadata_markings(request_meta.get("marking"))
    content_marks = content_markings(body)
    marking = higher_marking(meta_marks + request_marks + content_marks)
    held, hold_bad = legal_hold(meta.get("legal_hold"), body)
    request_held, request_hold_bad = legal_hold(request_meta.get("legal_hold"), "")
    held = held or request_held
    retention, retention_bad = retention_labels(meta.get("retention"), body)
    request_retention, request_retention_bad = retention_labels(request_meta.get("retention"), "")
    for label in request_retention:
        if label not in retention:
            retention.append(label)

    cues = cue_categories(body)
    signals = injection_signals(body)
    if isinstance(pasted, str):
        for name in injection_signals(pasted):
            if name not in signals:
                signals.append(name)
        pasted_cues = cue_categories(pasted)
        cues = {
            "distress": cues["distress"] or pasted_cues["distress"],
            "grievance": cues["grievance"] or pasted_cues["grievance"],
        }

    policies = _policy_rows(pinned_register)
    might = []
    negated = []
    qualified = []
    leading_rows = []
    for policy in policies.values():
        note = leading_criteria(policy.get("selection_note") or "")
        if note["flagged"]:
            leading_rows.append(
                {
                    "policy_id": policy["policy_id"],
                    "flagged": True,
                    "applied": False,
                    "note_copied": False,
                }
            )
        plain_topics = []
        denied_topics = []
        qualified_topics = []
        quotes = []
        for topic in policy["topics"]:
            relation = phrase_relation(body, topic)
            if relation == "absent":
                continue
            if relation == "plain":
                sentence = affirmed_sentence(body, topic)
                plain_topics.append(topic)
                if sentence and sentence not in quotes:
                    quotes.append(sentence)
            elif relation == "denied":
                denied_topics.append(topic)
            else:
                qualified_topics.append(topic)
        if qualified_topics or (plain_topics and denied_topics):
            for topic in plain_topics + qualified_topics + denied_topics:
                qualified.append({"policy_id": policy["policy_id"], "topic": topic, "applies": None})
            continue
        if plain_topics:
            masked_quotes = [mask_text(sentence)[0] for sentence in quotes]
            might.append(
                {
                    "policy_id": policy["policy_id"],
                    "title": policy["title"],
                    "topics": plain_topics,
                    "topic": plain_topics[0],
                    "why": "The pinned notice states " + ", ".join(repr(topic) for topic in plain_topics) + ".",
                    "quote": masked_quotes[0] if masked_quotes else "not found",
                    "applies": None,
                    "applicability": "not decided",
                    "qualified": False,
                    "leading_applied": False,
                }
            )
        for topic in denied_topics:
            negated.append({"policy_id": policy["policy_id"], "topic": topic, "applies": None})
    might.sort(key=lambda row: row["policy_id"])
    negated.sort(key=lambda row: (row["policy_id"], row["topic"]))
    qualified.sort(key=lambda row: (row["policy_id"], row["topic"]))

    minimum, minimum_bad = _minimum_days(pinned_register)
    below = False
    length = None
    close = text_dates["consultation_close"]
    if (
        minimum is not None
        and published is not None
        and not close["not_stated"]
        and not close["multiple"]
        and not close["unparseable"]
        and len(close["dates"]) == 1
    ):
        end, end_bad = parse_date_token(close["dates"][0])
        if end is not None and not end_bad:
            length = day_gap(published, end)
            below = length < minimum
    if minimum_bad:
        below = False

    related = []
    for source_id in notice.get("related_fca_source_ids") or []:
        if isinstance(source_id, str):
            related.append(assess_fca_source(source_id, question))
    fca_stale = any(row.get("currency") == "stale" for row in related)
    mi = mi_context(notice.get("mi_context") if isinstance(notice.get("mi_context"), str) else None, question)

    people = people_counts(body)
    withheld = above_ceiling(marking, person["clearance"])
    quote_sentence = content_sentences(body)
    matches_withheld = 0
    if withheld:
        matches_withheld = len(might) + len(negated) + len(qualified)
        might = []
        negated = []
        qualified = []
        people = {
            "threshold": people["threshold"],
            "groups": [],
            "unparseable": False,
            "values_stored_for_small_numbers": False,
            "coerced": False,
            "withheld": True,
        }
    if withheld:
        quote = {
            "quote": "not copied",
            "verbatim": False,
            "reason": "above_clearance",
            "source_id": publication_id,
            "source": "Pinned synthetic snapshot. The body was not copied.",
            "publication_date": published_iso or NOT_STATED,
            "regulator": notice.get("regulator"),
            "title": notice.get("title"),
        }
        for row in might:
            row["quote"] = "not copied"
    elif not quote_sentence:
        quote = {
            "quote": "not found",
            "verbatim": False,
            "source_id": publication_id,
            "source": "Pinned synthetic snapshot. Not a live regulator page.",
            "publication_date": published_iso or NOT_STATED,
            "regulator": notice.get("regulator"),
            "title": notice.get("title"),
        }
    else:
        masked_quote, quote_mask = mask_text(quote_sentence[0])
        uk = redact_uk_identifiers(masked_quote, rules_as_of=question)
        quote = {
            "quote": uk["text"],
            "verbatim": quote_mask["counts"] == {
                "phone": 0,
                "email": 0,
                "date_of_birth": 0,
                "postal_address": 0,
                "personal_name": 0,
            }
            and uk["count"] == 0,
            "source_id": publication_id,
            "source": "Pinned synthetic snapshot. Not a live regulator page.",
            "publication_date": published_iso or NOT_STATED,
            "regulator": notice.get("regulator"),
            "title": notice.get("title"),
            "mask": quote_mask,
            "uk_identifier_types": uk["types"],
            "described_as_anonymised": False,
        }

    if withheld:
        body_mask = {"counts": {}, "any": False, "values_stored": False, "values_copied": False, "described_as_anonymised": False}
        uk_body = {"types": [], "count": 0, "values_stored": False}
    else:
        _full_mask, body_mask = mask_text(body)
        uk_body = redact_uk_identifiers(body, rules_as_of=question)
    intake = None
    if body and not withheld:
        intake = intake_notice(
            body,
            notice_id=publication_id,
            document_date=published_iso,
            as_of=question,
        )
    elif body and withheld:
        intake = {
            "called": False,
            "reason": "above_clearance",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "content_recorded": False,
        }

    review_flags = []
    for policy in policies.values():
        due, due_bad = parse_date_token(policy["review_due"]) if policy.get("review_due") else (None, False)
        if due_bad:
            review_flags.append({"policy_id": policy["policy_id"], "review_due": "unparseable", "coerced": False})
        elif due is not None and due <= question:
            review_flags.append(
                {
                    "policy_id": policy["policy_id"],
                    "review_due": due.isoformat(),
                    "stale": True,
                    "rule": "A review-due date on the question date is stale. This is this starter's rule.",
                }
            )

    state = {
        "dates": text_dates,
        "flags": flags,
        "undated": flags["undated"],
        "stale": stale,
        "below_register_window": below,
        "might": might,
        "negated": negated,
        "qualified": qualified,
        "leading": bool(leading_rows),
        "cues": cues,
        "caller_text_differs": caller_text_differs,
        "register_differences": register_differences,
        "directory_differences": directory_differences,
    }
    questions = _questions(state)
    if withheld:
        questions.insert(0, "The notice marking is above the directory clearance. The body was not copied.")

    outcome = "briefing"
    if cues["distress"] or cues["grievance"]:
        outcome = "human_route"
    if withheld:
        outcome = "above_clearance"

    sources_current = (
        currency.get("currency") == "within_threshold"
        and not fca_stale
        and not flags["undated"]
        and not published_bad
    )
    result = _base(
        question,
        outcome=outcome,
        routine=outcome == "briefing",
        publication_id=publication_id,
        publication_date=published_iso or NOT_STATED,
        caller_ref=person["ref"],
        role_from_directory=person["role"],
        clearance_from_directory=person["clearance"],
        self_declared_role_ignored=True,
        self_declared_clearance_ignored=True,
        what_changed=quote,
        dates=text_dates,
        might_be_affected=might,
        matches_withheld=matches_withheld,
        negated_mentions=negated,
        qualified_mentions=qualified,
        might_be_affected_count=len(might),
        open_questions=questions,
        open_question_count=len(questions),
        flags=flags,
        people=people,
        marking=marking,
        marking_unparseable=meta_bad or request_bad,
        legal_hold=held,
        legal_hold_unparseable=hold_bad or request_hold_bad,
        retention=retention,
        retention_unparseable=retention_bad or request_retention_bad,
        cue={"distress": cues["distress"], "grievance": cues["grievance"], "text_copied": False},
        prompt_injection={"detected": bool(signals), "signals": signals, "followed": False},
        mask_counts=body_mask,
        uk_identifiers={"types": uk_body["types"], "count": uk_body["count"], "values_stored": False},
        caller_text_differs=caller_text_differs,
        caller_text_used=False,
        register_differences=register_differences,
        directory_differences=directory_differences,
        pinned_register_used=True,
        pinned_directory_used=True,
        leading_criteria=leading_rows,
        leading_criteria_applied=False,
        consultation_length_days=length,
        below_register_window=below,
        register_minimum_days=minimum,
        register_minimum_unparseable=minimum_bad,
        statutory_minimum_days=None,
        marked_acceptable=False,
        snapshot_currency=currency,
        sources_current=sources_current,
        pins_confirmed=False,
        statute=statute_pin(question),
        publication_practice=practice_pins(),
        related_fca_sources=related,
        experiment_20=mi,
        experiment_12=intake,
        policy_review=review_flags,
        ignored_request_fields=ignored,
        body_sha256=_sha(body),
        statement=(
            "This briefing does not decide applicability. The compliance owner validates "
            "every conclusion. Nothing was sent and no policy, control, or record was changed."
        ),
    )
    result.update(_hash_bundle(result))
    return result


def verify_seen(result: dict) -> dict:
    """True only when the approval hashes still match this content."""

    approval = result.get("human_approval") if isinstance(result, dict) else None
    if not isinstance(approval, dict):
        return {"accepted": False, "reason": "no_approval"}
    fresh = _hash_bundle(result)
    for name in ("publication_hash", "briefing_hash", "questions_hash"):
        if approval.get(name) != fresh[name] or result.get(name) != fresh[name]:
            return {"accepted": False, "reason": f"{name}_mismatch"}
    if approval.get("applies") is not None or approval.get("sent") is not False:
        return {"accepted": False, "reason": "consequential_flag"}
    if result.get("applies") is not None or result.get("sent") is not False:
        return {"accepted": False, "reason": "consequential_flag"}
    return {"accepted": True, "reason": None}


def record_owner_seen(result: dict, directory: dict, decision: dict) -> dict:
    """Record that the pinned-directory compliance owner has seen this briefing.

    The record does not decide applicability, change a policy, or send.
    A string is not coerced to true. A hash that does not match is rejected.
    """

    if not isinstance(result, dict) or result.get("label") != LABEL:
        raise ValueError("result is not a regulatory change briefing")
    _require_synthetic(directory, "directory")
    if not isinstance(decision, dict):
        raise TypeError("decision must be an object")
    updated = deepcopy(result)
    updated["applies"] = None
    updated["applicability"] = "not decided"
    updated["policy_changed"] = False
    updated["control_changed"] = False
    updated["record_changed"] = False
    updated["sent"] = False
    updated["marked_applicable"] = False
    updated["marked_not_applicable"] = False
    updated["marked_acceptable"] = False
    pinned = _load(DIRECTORY_PATH)
    blocked = _seen_block(updated, pinned, decision, _diff_maps(_person_rows(pinned), _person_rows(directory), "directory"))
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
        "publication_hash": updated["publication_hash"],
        "briefing_hash": updated["briefing_hash"],
        "questions_hash": updated["questions_hash"],
        "applies": None,
        "policy_changed": False,
        "control_changed": False,
        "record_changed": False,
        "sent": False,
    }
    updated["blocked_reason"] = None
    checked = verify_seen(updated)
    if checked["accepted"] is not True:
        updated["human_approval"] = None
        updated["blocked_reason"] = checked["reason"]
    return updated


def _bool_true(value: object) -> bool:
    return value is True


def _seen_block(result: dict, directory: dict, decision: dict, directory_differences: list[dict]) -> str | None:
    for name in ("policy_changed", "control_changed", "record_changed", "sent", "applies"):
        if name in decision and decision[name] not in (False, None):
            return "consequential_flag"
    extra = set(decision) - _SEEN_FIELDS - {
        "policy_changed",
        "control_changed",
        "record_changed",
        "sent",
        "applies",
    }
    if extra:
        return "unexpected_fields"
    item = decision.get("item")
    if item not in {"briefing", "distress-seen", "grievance-seen"}:
        return "item_not_recognised"
    if decision.get("decision") != "seen":
        return "decision_not_seen"
    people = _person_rows(directory)
    person = people.get(decision.get("approver_ref"))
    if person is None:
        return "approver_not_in_directory"
    if person.get("role") != "compliance_owner":
        return "not_compliance_owner"
    fresh = _hash_bundle(result)
    if decision.get("publication_hash") != fresh["publication_hash"]:
        return "publication_hash_mismatch"
    if decision.get("briefing_hash") != fresh["briefing_hash"]:
        return "briefing_hash_mismatch"
    if decision.get("questions_hash") != fresh["questions_hash"]:
        return "questions_hash_mismatch"
    for name in ("pins_seen", "flags_seen", "sources_seen"):
        if name in decision and not isinstance(decision.get(name), bool):
            return f"{name}_not_boolean"
    cue = result.get("cue") or {}
    if item == "briefing" and cue.get("distress") and result.get("distress_seen") is not True:
        return "distress_not_seen"
    if item == "briefing" and cue.get("grievance") and result.get("grievance_seen") is not True:
        return "grievance_not_seen"
    if item == "distress-seen" and not cue.get("distress"):
        return "distress_not_flagged"
    if item == "grievance-seen" and not cue.get("grievance"):
        return "grievance_not_flagged"
    flags = result.get("flags") or {}
    needs_flags = bool(
        flags.get("withdrawn")
        or flags.get("superseded")
        or flags.get("undated")
        or flags.get("stale")
        or flags.get("published_unparseable")
        or result.get("below_register_window")
        or (result.get("dates") or {}).get("effective", {}).get("unparseable")
    )
    if item == "briefing" and needs_flags and not _bool_true(decision.get("flags_seen")):
        return "flags_not_seen"
    if item == "briefing" and result.get("pins_confirmed") is not True and not _bool_true(decision.get("pins_seen")):
        return "pins_not_seen"
    needs_sources = bool(
        result.get("caller_text_differs")
        or result.get("register_differences")
        or result.get("directory_differences")
        or directory_differences
    )
    if item == "briefing" and needs_sources and not _bool_true(decision.get("sources_seen")):
        return "sources_not_seen"
    return None


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a regulatory change briefing from pinned snapshots.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--register", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = draft_briefing(
            _read_json(args.request),
            _read_json(args.register),
            _read_json(args.directory),
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
