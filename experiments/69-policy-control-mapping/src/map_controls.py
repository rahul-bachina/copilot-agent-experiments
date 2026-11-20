#!/usr/bin/env python3
"""Propose policy-statement-to-control mappings.

The control owner approves each mapping. The agent does not mark a control
as met, close a gap, edit a policy, or write to a GRC system. The same inputs
and the same question date produce the same JSON. Approval words inside a
policy are not approval.
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
    from cues import biased, claims_clearance, claims_role, cue_categories, injection_codes
    from library import differences, load_pinned
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import SUPPRESS_BELOW, mask_text, publish_counts
    from reuse import (
        NeighbourMissing,
        assurance,
        compare_obligations,
        intake_policies,
        redact_uk_identifiers,
    )
    from sources import CAF_OBJECTIVES, caf_note, iso_note
    from statements import assess_sentence, split_sentences
else:
    from .cues import biased, claims_clearance, claims_role, cue_categories, injection_codes
    from .library import differences, load_pinned
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import SUPPRESS_BELOW, mask_text, publish_counts
    from .reuse import (
        NeighbourMissing,
        assurance,
        compare_obligations,
        intake_policies,
        redact_uk_identifiers,
    )
    from .sources import CAF_OBJECTIVES, caf_note, iso_note
    from .statements import assess_sentence, split_sentences

LABEL = (
    "MAPPING PROPOSAL FOR A CONTROL OWNER. "
    "A CONTROL IS NOT MARKED MET. A GAP IS NOT CLOSED. "
    "A POLICY IS NOT EDITED. NOTHING IS WRITTEN TO A GRC SYSTEM."
)
CATALOGUE_ID = "L003"
EXPERIMENT_ID = "exp-69-policy-control-mapping"
AUTONOMY = "A0"
NO_EVIDENCE = "no evidence found"
OWNER_ROLE = "Control owner"
POLICY_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
_PROHIBITED = frozenset(
    {
        "approved",
        "human_approval",
        "control_met",
        "gap_closed",
        "policy_edited",
        "grc_written",
        "clearance",
        "role",
        "mark_met",
        "close_gap",
        "mapped_as_met",
    }
)
_RATIONALE = {
    "expected_strength": (
        "The sentence uses {strength}. The control expects {expected}. "
        "Every signal is present and there is no carve-out. "
        "This is not a finding that the control is met."
    ),
    "should_is_not_must": (
        "The sentence uses {strength}. should is not must. "
        "The control expects {expected}. "
        "This is not a finding that the control is met."
    ),
    "qualification_weakens": (
        "The sentence has a carve-out after the obligation. "
        "A qualification that follows acceptable wording is not an unqualified mapping. "
        "This is not a finding that the control is met."
    ),
    "may_is_not_must": (
        "The sentence uses may. may is not must. "
        "This is not a finding that the control is met."
    ),
    "ambiguous_strength": (
        "The sentence uses more than one obligation word. Neither word was chosen. "
        "This is not a finding that the control is met."
    ),
    "partial": (
        "The sentence does not match the expected strength without a weakening. "
        "This is not a finding that the control is met."
    ),
}


class MappingForbidden(RuntimeError):
    """A prohibited action was called. Nothing was written."""


def mark_control_met(*_args, **_kwargs) -> None:
    raise MappingForbidden("The agent does not mark a control as met.")


def close_gap(*_args, **_kwargs) -> None:
    raise MappingForbidden("The agent does not close a gap.")


def edit_policy(*_args, **_kwargs) -> None:
    raise MappingForbidden("The agent does not edit a policy.")


def write_grc(*_args, **_kwargs) -> None:
    raise MappingForbidden("The agent does not write to a GRC system.")


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _parse_as_of(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("as_of must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _parse_date(value: object) -> tuple[date | None, bool]:
    if value is None or value == "":
        return None, False
    if not isinstance(value, str):
        return None, True
    try:
        return date.fromisoformat(value), False
    except ValueError:
        return None, True


def _strip(payload: dict) -> tuple[dict, list[str]]:
    cleaned = dict(payload)
    ignored = [key for key in list(cleaned) if key in _PROHIBITED]
    for key in ignored:
        cleaned.pop(key, None)
    return cleaned, ignored


def _person(directory: dict, ref: object) -> dict | None:
    people = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(people, list) or not isinstance(ref, str):
        return None
    for person in people:
        if isinstance(person, dict) and person.get("ref") == ref:
            return person
    return None


def _flags() -> dict:
    return {
        "control_met": False,
        "gap_closed": False,
        "policy_edited": False,
        "grc_written": False,
        "guessed": False,
        "coerced": False,
        "instructions_followed": False,
        "output_is_anonymised": False,
        "model_called": False,
        "network_called": False,
        "acceptable": False,
    }


def _name_count(text: str) -> int:
    _masked, report = mask_text(text)
    # publish_counts hides 1..4. Count tokens in the masked string instead.
    return _masked.count("[name]") if isinstance(_masked, str) else 0


def _mapping_core(row: dict) -> dict:
    return {
        "mapping_id": row["mapping_id"],
        "policy_id": row["policy_id"],
        "clause_ref": row["clause_ref"],
        "quote": row["quote"],
        "control_id": row["control_id"],
        "rationale": row["rationale"],
        "confidence": row["confidence"],
        "qualified": row["qualified"],
        "strength": row["strength"],
    }


def _proposal_hash(result: dict) -> str:
    payload = {
        "mappings": [_mapping_core(row) for row in result.get("mappings") or []],
        "gaps": [
            {"gap_id": row["gap_id"], "control_id": row["control_id"], "quote": row["quote"]}
            for row in result.get("gaps") or []
        ],
        "contradictions": [
            {
                "contradiction_id": row["contradiction_id"],
                "control_id": row["control_id"],
                "quotes": [item["quote"] for item in row.get("statements") or []],
            }
            for row in result.get("contradictions") or []
        ],
        "unmapped": [
            {"statement_id": row["statement_id"], "quote": row["quote"]}
            for row in result.get("unmapped_statements") or []
        ],
        "not_inclusions": [
            {"statement_id": row["statement_id"], "quote": row["quote"]}
            for row in result.get("not_inclusions") or []
        ],
        "injection_codes": list(result.get("prompt_injection", {}).get("codes") or []),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold"),
        "retention_labels": list(result.get("retention_labels") or []),
        "outcome": result.get("outcome"),
        "cue_categories": list(result.get("cue_categories") or []),
    }
    return _digest(payload)


def _show(text: str) -> str:
    shown, _report = mask_text(text)
    return shown


def _clauses(policy: dict, unparseable: list[dict]) -> list[dict]:
    policy_id = policy.get("policy_id")
    clauses = policy.get("clauses")
    if clauses is None and isinstance(policy.get("body"), str):
        built = []
        for line in policy["body"].splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r"^(\d+(?:\.\d+)*)\s+(\S.*)$", stripped)
            if not match:
                unparseable.append(
                    {"kind": "clause_line_unreadable", "policy_id": policy_id, "coerced": False}
                )
                continue
            built.append({"clause_ref": match.group(1), "text": match.group(2)})
        clauses = built
    rows = []
    if not isinstance(clauses, list):
        unparseable.append({"kind": "clauses_unreadable", "policy_id": policy_id, "coerced": False})
        return rows
    for clause in clauses:
        if not isinstance(clause, dict):
            unparseable.append({"kind": "clause_not_object", "policy_id": policy_id, "coerced": False})
            continue
        ref = clause.get("clause_ref")
        text = clause.get("text")
        if type(ref) is not str or not ref.strip():
            unparseable.append(
                {"kind": "clause_ref_unreadable", "policy_id": policy_id, "coerced": False}
            )
            continue
        if not isinstance(text, str) or not text.strip():
            unparseable.append(
                {
                    "kind": "clause_text_unreadable",
                    "policy_id": policy_id,
                    "clause_ref": ref,
                    "coerced": False,
                }
            )
            continue
        for sentence in split_sentences(text.strip()):
            rows.append(
                {
                    "policy_id": policy_id,
                    "policy_title": policy.get("title") if isinstance(policy.get("title"), str) else "",
                    "clause_ref": ref.strip(),
                    "text": sentence,
                    "document_date": policy.get("document_date"),
                }
            )
    return rows


def _token(sentence: str, strength: str) -> str | None:
    folded = sentence.casefold()
    if strength == "must_not":
        for token in ("must not", "shall not", "must never", "shall never"):
            if token in folded:
                return token
    if strength == "must" and "must not" not in folded and "shall not" not in folded:
        for token in ("is required to", "are required to", "must", "shall"):
            if token in folded:
                return token
    if strength == "should" and "should" in folded:
        return "should"
    return None


def _compare_pack(control_id: str, statements: list[dict], as_of: str) -> dict:
    fact_key = control_id.casefold().replace("-", "_")
    documents = []
    seen: set[str] = set()
    for index, row in enumerate(statements, start=1):
        token = _token(row["text"], row["strength"])
        reviewed, bad = _parse_date(row.get("document_date"))
        if token is None or bad or reviewed is None or len(row["text"]) > 500 or len(token) > 200:
            return {
                "called": False,
                "reason": "comparison_inputs_unreadable",
                "coerced": False,
                "agent_chose_source": False,
            }
        document_id = f"{row['policy_id']}-{index}"
        if not POLICY_ID.fullmatch(document_id) or document_id in seen:
            document_id = f"src-{index}"
        seen.add(document_id)
        title = row.get("policy_title") or document_id
        if not isinstance(title, str) or len(title) > 120:
            title = document_id
        documents.append(
            {
                "document_id": document_id,
                "title": title,
                "kind": "register_extract",
                "status": "current",
                "reviewed_on": reviewed.isoformat(),
                "pages": [
                    {
                        "page": 1,
                        "paragraphs": [
                            {"paragraph": 1, "lines": [{"line": 1, "text": row["text"]}]}
                        ],
                    }
                ],
                "fields": [
                    {
                        "fact_key": fact_key,
                        "page": 1,
                        "paragraph": 1,
                        "line": 1,
                        "value": token,
                    }
                ],
            }
        )
    if len(documents) < 2:
        return {
            "called": False,
            "reason": "fewer_than_two_policy_sources",
            "coerced": False,
            "agent_chose_source": False,
        }
    if len(documents) > 8:
        return {"called": False, "reason": "too_many_sources", "coerced": False, "agent_chose_source": False}
    pack = {
        "synthetic": True,
        "pack_id": fact_key[:40],
        "facts": [{"fact_key": fact_key, "field_type": "reference"}],
        "documents": documents,
    }
    try:
        return compare_obligations(pack, as_of)
    except (NeighbourMissing, ValueError, TypeError) as exc:
        return {
            "called": False,
            "reason": "compare_failed",
            "detail": exc.__class__.__name__,
            "coerced": False,
            "agent_chose_source": False,
        }


def _empty_shell(as_of: str, outcome: str, **extra) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "as_of": as_of,
        "outcome": outcome,
        "human_approval": None,
        "mappings": [],
        "gaps": [],
        "contradictions": [],
        "unmapped_statements": [],
        "not_inclusions": [],
        "biased_criteria": [],
        "may_be_relied_on": False,
        "caf": caf_note(),
        "iso": iso_note(),
        **_flags(),
    }
    result.update(extra)
    result["proposal_hash"] = _proposal_hash(result)
    return result


def map_controls(request: dict, library: dict, directory: dict, as_of: str) -> dict:
    """Return a mapping proposal. human_approval stays null."""

    question = _parse_as_of(as_of)
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise ValueError("record is not marked synthetic")
    if not isinstance(directory, dict):
        raise TypeError("directory must be an object")
    working, ignored_keys = _strip(request)
    pinned = load_pinned()
    supplied = working.get("supplied_library")
    if supplied is None and library != pinned:
        supplied = library
    elif isinstance(library, dict) and library != pinned and supplied is None:
        supplied = library
    library_diff = differences(supplied if isinstance(supplied, dict) or supplied is not None else None, pinned)
    if isinstance(library, dict) and library != pinned and working.get("supplied_library") is not None:
        extra = differences(library, pinned)
        for row in extra:
            if row not in library_diff:
                library_diff.append(row)

    caller_ref = working.get("caller_ref")
    person = _person(directory, caller_ref)
    policies = working.get("policies")
    cover = working.get("cover_note") if isinstance(working.get("cover_note"), str) else ""
    if not isinstance(policies, list):
        raise ValueError("policies must be a list")

    texts: list[str] = [cover] if cover else []
    meta_labels: list[str] = []
    retention: list[str] = []
    held = False
    hold_unparseable = False
    retention_unparseable = False
    marking_unparseable = False
    unparseable: list[dict] = []
    date_problems: list[dict] = []
    usable_policies: list[dict] = []
    files = []

    for policy in policies:
        if not isinstance(policy, dict):
            unparseable.append({"kind": "policy_not_object", "coerced": False})
            continue
        policy_id = policy.get("policy_id")
        if not isinstance(policy_id, str) or not POLICY_ID.fullmatch(policy_id):
            unparseable.append({"kind": "policy_id_unreadable", "coerced": False})
            continue
        labels, bad_mark = metadata_markings(policy.get("marking"))
        marking_unparseable = marking_unparseable or bad_mark
        meta_labels.extend(labels)
        kept, bad_ret = retention_labels(policy.get("retention"), "")
        retention_unparseable = retention_unparseable or bad_ret
        for label in kept:
            if label not in retention:
                retention.append(label)
        policy_held, bad_hold = legal_hold(policy.get("legal_hold"), "")
        hold_unparseable = hold_unparseable or bad_hold
        held = held or policy_held
        body_parts = []
        if isinstance(policy.get("body"), str):
            body_parts.append(policy["body"])
        if isinstance(policy.get("clauses"), list):
            for clause in policy["clauses"]:
                if isinstance(clause, dict) and isinstance(clause.get("text"), str):
                    body_parts.append(clause["text"])
        blob = "\n".join(body_parts)
        texts.append(blob)
        content_kept, bad_ret = retention_labels(None, blob)
        retention_unparseable = retention_unparseable or bad_ret
        for label in content_kept:
            if label not in retention:
                retention.append(label)
        content_held, _bad = legal_hold(None, blob)
        held = held or content_held
        for label in content_markings(blob):
            if label not in meta_labels:
                meta_labels.append(label)
        policy["_sentences"] = _clauses(policy, unparseable)
        document_date, bad_doc = _parse_date(policy.get("document_date"))
        effective, bad_eff = _parse_date(policy.get("effective_from")) if "effective_from" in policy else (None, False)
        review_due, bad_rev = _parse_date(policy.get("review_due")) if "review_due" in policy else (None, False)
        if bad_doc or bad_eff or bad_rev:
            unparseable.append(
                {"kind": "date_unreadable", "policy_id": policy_id, "coerced": False}
            )
            date_problems.append({"policy_id": policy_id, "reason": "unparseable"})
            continue
        if effective is not None and effective > question:
            date_problems.append({"policy_id": policy_id, "reason": "not_yet_in_force"})
            continue
        if review_due is not None and review_due <= question:
            date_problems.append({"policy_id": policy_id, "reason": "review_due"})
        usable_policies.append(policy)
        files.append(
            {
                "file_id": policy_id,
                "filename": f"{policy_id}.txt",
                "media_type": "text/plain",
                "document_date": document_date.isoformat() if document_date else None,
                "content": blob,
            }
        )

    joined = "\n".join(texts)
    marking = higher_marking(meta_labels)
    cues = cue_categories(joined)
    codes = injection_codes(joined)
    ceiling = person.get("clearance") if person else None
    if not isinstance(ceiling, str):
        ceiling = None

    base_extra = {
        "caller_ref": caller_ref if isinstance(caller_ref, str) else None,
        "caller_role_from_directory": person.get("role") if person else None,
        "self_declared_role_ignored": claims_role(joined),
        "self_declared_clearance_ignored": claims_clearance(joined),
        "clearance": ceiling if person and not person.get("guest") else None,
        "marking": marking,
        "marking_unparseable": marking_unparseable,
        "legal_hold": held,
        "legal_hold_unparseable": hold_unparseable,
        "retention_labels": retention,
        "retention_unparseable": retention_unparseable,
        "library_differences": library_diff,
        "library_authoritative": "pinned_fixture",
        "supplied_library_applied": False,
        "unparseable": unparseable,
        "date_problems": date_problems,
        "prompt_injection": {"detected": bool(codes), "codes": codes, "followed": False, "text_recorded": False},
        "cue_categories": cues,
        "cue_text_copied": False,
        "prohibited_request_keys": ignored_keys,
    }

    if cues:
        return _empty_shell(question.isoformat(), "human_route", **base_extra)
    if person is None:
        return _empty_shell(question.isoformat(), "caller_not_in_directory", **base_extra)
    if person.get("guest") is True:
        return _empty_shell(question.isoformat(), "guest", **base_extra)
    if above_ceiling(marking, ceiling):
        return _empty_shell(question.isoformat(), "above_clearance", **base_extra)

    controls = pinned["controls"]
    sentences: list[dict] = []
    for policy in usable_policies:
        sentences.extend(policy.get("_sentences") or [])

    buckets: dict[str, dict] = {
        control["control_id"]: {"support": [], "oppose": []} for control in controls
    }
    unmapped: list[dict] = []
    not_inclusions: list[dict] = []
    biased_rows: list[dict] = []
    for sentence in sentences:
        if injection_codes(sentence["text"]):
            continue
        if claims_clearance(sentence["text"]) or claims_role(sentence["text"]):
            continue
        if biased(sentence["text"]):
            biased_rows.append(sentence)
            continue
        matched = False
        for control in controls:
            assessment = assess_sentence(sentence["text"], control)
            if assessment["support"]:
                buckets[control["control_id"]]["support"].append({**sentence, **assessment, "expected": control["expected_strength"]})
                matched = True
            elif assessment["opposes"]:
                buckets[control["control_id"]]["oppose"].append({**sentence, **assessment, "expected": control["expected_strength"]})
                matched = True
            elif assessment["signals_all_present"] and assessment["strength"] == "denied":
                not_inclusions.append({**sentence, "control_id": control["control_id"], "included": False})
                matched = True
        if not matched:
            unmapped.append(sentence)

    mappings: list[dict] = []
    gaps: list[dict] = []
    contradictions: list[dict] = []
    for control in controls:
        control_id = control["control_id"]
        bucket = buckets[control_id]
        caf_objective = control.get("caf_objective")
        if caf_objective not in CAF_OBJECTIVES:
            caf_objective = None
        external = control.get("external_identifier") if isinstance(control.get("external_identifier"), str) else None
        if bucket["support"] and bucket["oppose"] or (bucket["oppose"] and not bucket["support"]):
            statements = bucket["support"] + bucket["oppose"]
            cross = _compare_pack(control_id, statements, question.isoformat()) if len(statements) >= 2 else {
                "called": False,
                "reason": "fewer_than_two_policy_sources",
                "coerced": False,
                "agent_chose_source": False,
            }
            contradictions.append(
                {
                    "contradiction_id": f"CON-{control_id}",
                    "control_id": control_id,
                    "external_identifier": external,
                    "external_text_copied": False,
                    "caf_objective": caf_objective,
                    "caf_achievement_decided": False,
                    "statements": [
                        {
                            "policy_id": row["policy_id"],
                            "clause_ref": row["clause_ref"],
                            "quote": _show(row["text"]),
                            "strength": row["strength"],
                            "included": False,
                        }
                        for row in statements
                    ],
                    "rationale": (
                        "The quoted sentences do not say the same thing, or a sentence opposes "
                        "the control's expected strength. This starter does not choose which "
                        "sentence to follow. The control is not marked met."
                    ),
                    "cross_source": cross,
                    "agent_chose_source": False,
                    "control_met": False,
                    "guessed": False,
                }
            )
            continue
        if not bucket["support"]:
            gaps.append(
                {
                    "gap_id": f"GAP-{control_id}",
                    "control_id": control_id,
                    "external_identifier": external,
                    "external_text_copied": False,
                    "caf_objective": caf_objective,
                    "quote": NO_EVIDENCE,
                    "clause_ref": None,
                    "rationale": "No policy sentence affirmed this control. Nothing was guessed.",
                    "confidence": None,
                    "gap_closed": False,
                    "control_met": False,
                    "guessed": False,
                }
            )
            continue
        for row in bucket["support"]:
            code = row.get("rationale_code") or "partial"
            mappings.append(
                {
                    "policy_id": row["policy_id"],
                    "clause_ref": row["clause_ref"],
                    "quote": _show(row["text"]),
                    "source_sentence": row["text"],
                    "control_id": control_id,
                    "external_identifier": external,
                    "external_text_copied": False,
                    "caf_objective": caf_objective,
                    "caf_achievement_decided": False,
                    "rationale": _RATIONALE[code].format(strength=row["strength"], expected=row["expected"]),
                    "confidence": row["confidence"],
                    "qualified": row["qualified"],
                    "strength": row["strength"],
                    "obligation_affirmed": row["obligation_affirmed"],
                    "included": row["included"],
                    "control_met": False,
                    "acceptable": False,
                    "guessed": False,
                }
            )

    mappings.sort(key=lambda row: (row["control_id"], row["policy_id"], row["clause_ref"], row["quote"]))
    for index, row in enumerate(mappings, start=1):
        row["mapping_id"] = f"MAP-{index:03d}"
        row.pop("source_sentence", None)
        row["content_hash"] = _digest(_mapping_core(row))

    for index, row in enumerate(unmapped, start=1):
        row["statement_id"] = f"UNM-{index:03d}"
        row["quote"] = _show(row.pop("text"))
        row["rationale"] = "No pinned control has its signals in this sentence. Nothing was guessed."
        row["control_id"] = None
        row["included"] = False
        row["guessed"] = False
        row.pop("policy_title", None)
        row.pop("document_date", None)
    for index, row in enumerate(not_inclusions, start=1):
        row["statement_id"] = f"NIN-{index:03d}"
        row["quote"] = _show(row.pop("text"))
        row["included"] = False
        row["obligation_affirmed"] = False
        row["rationale"] = "Negation or a denial was read. The sentence was not treated as included."
        row["guessed"] = False
        row.pop("policy_title", None)
        row.pop("document_date", None)
    biased_out = []
    for index, row in enumerate(biased_rows, start=1):
        biased_out.append(
            {
                "statement_id": f"BIAS-{index:03d}",
                "policy_id": row["policy_id"],
                "clause_ref": row["clause_ref"],
                "quote": _show(row["text"]),
                "applied": False,
                "route_to_human": True,
                "rationale": "A biased or leading criterion is flagged for a person. It is not applied.",
            }
        )

    name_total = _name_count(joined)
    people = publish_counts({"personal_name": name_total, "phone": 0, "email": 0, "date_of_birth": 0, "postal_address": 0})
    masked_joined, mask_report = mask_text(joined)

    intake = _safe_intake(files, question)
    try:
        uk = redact_uk_identifiers(joined, rules_as_of=question)
        uk_count = uk["count"]
        uk_view = {
            "called": True,
            "experiment_id": uk["experiment_id"],
            "types": uk["types"],
            "count": None if 0 < uk_count < SUPPRESS_BELOW else uk_count,
            "count_suppressed": 0 < uk_count < SUPPRESS_BELOW,
            "output_is_anonymised": False,
            "values_stored": False,
            "rules_stale": uk["rules_stale"],
            "described_as_anonymised": False,
        }
    except (NeighbourMissing, RuntimeError, ValueError, TypeError):
        uk_view = {"called": False, "output_is_anonymised": False, "values_stored": False, "coerced": False}

    try:
        assure = assurance(joined)
    except (NeighbourMissing, ValueError, TypeError, KeyError):
        assure = {"called": False, "screen_clears_agent": False, "atrs_record_produced": False, "coerced": False}

    stale = any(row["reason"] in {"review_due", "unparseable"} for row in date_problems) or bool(
        intake.get("any_document_stale") or intake.get("catalogue_stale") or intake.get("any_document_not_current")
    )
    sources_current = not stale and not date_problems
    mapped_controls = {row["control_id"] for row in mappings}
    gap_controls = {row["control_id"] for row in gaps}
    contradiction_controls = {row["control_id"] for row in contradictions}
    counts = {
        "control_count": len(controls),
        "controls_with_a_mapping": len(mapped_controls),
        "gap_count": len(gap_controls),
        "contradiction_count": len(contradiction_controls),
        "mapping_row_count": len(mappings),
        "unmapped_count": len(unmapped),
        "not_inclusion_count": len(not_inclusions),
        "counts_note": (
            "mapping_row_count is not added to control_count. "
            "A control is in one of controls_with_a_mapping, gap_count, or contradiction_count. "
            "unmapped_count counts statements, not controls."
        ),
    }
    if counts["controls_with_a_mapping"] + counts["gap_count"] + counts["contradiction_count"] != counts["control_count"]:
        raise RuntimeError("control counts do not add up")
    if mapped_controls & gap_controls or mapped_controls & contradiction_controls or gap_controls & contradiction_controls:
        raise RuntimeError("a control was counted twice")

    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": AUTONOMY,
        "as_of": question.isoformat(),
        "outcome": "proposal",
        "human_approval": None,
        "caller_ref": caller_ref if isinstance(caller_ref, str) else None,
        "caller_role_from_directory": person.get("role"),
        "self_declared_role_ignored": claims_role(joined),
        "self_declared_clearance_ignored": claims_clearance(joined),
        "clearance": ceiling,
        "marking": marking,
        "marking_unparseable": marking_unparseable,
        "legal_hold": held,
        "legal_hold_unparseable": hold_unparseable,
        "retention_labels": retention,
        "retention_unparseable": retention_unparseable,
        "library_differences": library_diff,
        "library_authoritative": "pinned_fixture",
        "supplied_library_applied": False,
        "unparseable": unparseable,
        "date_problems": date_problems,
        "sources_current": sources_current,
        "may_be_relied_on": False,
        "mappings": mappings,
        "gaps": gaps,
        "contradictions": contradictions,
        "unmapped_statements": unmapped,
        "not_inclusions": not_inclusions,
        "biased_criteria": biased_out,
        "counts": counts,
        "people_named": {
            "count": people["counts"]["personal_name"],
            "suppressed": "personal_name" in people["suppressed_categories"],
            "threshold": SUPPRESS_BELOW,
            "threshold_source": "this starter, not a statistics authority page",
        },
        "masking": {
            "categories_masked": mask_report["categories_masked"],
            "counts": mask_report["counts"],
            "suppressed_categories": mask_report["suppressed_categories"],
            "threshold": SUPPRESS_BELOW,
            "values_stored": False,
            "values_copied": False,
            "described_as_anonymised": False,
            "output_is_anonymised": False,
            "joined_text_stored": False,
        },
        "uk_identifiers": uk_view,
        "intake": intake,
        "assurance": assure,
        "prompt_injection": {"detected": bool(codes), "codes": codes, "followed": False, "text_recorded": False},
        "cue_categories": [],
        "cue_text_copied": False,
        "prohibited_request_keys": ignored_keys,
        "caf": caf_note(),
        "iso": iso_note(),
        "body_copied": False,
        "masked_character_count": len(masked_joined),
        **_flags(),
    }
    result["proposal_hash"] = _proposal_hash(result)
    result["may_be_relied_on"] = False
    return result


def _safe_intake(files: list[dict], question: date) -> dict:
    if not files:
        return {"called": False, "reason": "no_files", "files_confirmed": False, "purpose_confirmed": False, "coerced": False}
    if len(files) > 12:
        return {
            "called": False,
            "reason": "too_many_files",
            "files_confirmed": False,
            "purpose_confirmed": False,
            "coerced": False,
        }
    prepared = []
    for row in files:
        item = {
            "file_id": row["file_id"],
            "filename": row["filename"],
            "media_type": "text/plain",
            "content": row["content"],
        }
        if isinstance(row.get("document_date"), str):
            item["document_date"] = row["document_date"]
        prepared.append(item)
    try:
        return intake_policies(prepared, as_of=question)
    except (NeighbourMissing, ValueError, TypeError) as exc:
        return {
            "called": False,
            "reason": "intake_failed",
            "detail": exc.__class__.__name__,
            "files_confirmed": False,
            "purpose_confirmed": False,
            "coerced": False,
        }


def _item_hash(result: dict, approval: dict) -> str | None:
    item = approval.get("item")
    if item == "mapping":
        mapping_id = approval.get("mapping_id")
        for row in result.get("mappings") or []:
            if row.get("mapping_id") == mapping_id:
                return _digest(_mapping_core(row))
        return None
    if item == "gap-seen":
        gap_id = approval.get("gap_id")
        for row in result.get("gaps") or []:
            if row.get("gap_id") == gap_id:
                return _digest({"gap_id": row["gap_id"], "control_id": row["control_id"], "quote": row["quote"]})
        return None
    if item == "contradiction-seen":
        contradiction_id = approval.get("contradiction_id")
        for row in result.get("contradictions") or []:
            if row.get("contradiction_id") == contradiction_id:
                return _digest(
                    {
                        "contradiction_id": row["contradiction_id"],
                        "quotes": [item_row["quote"] for item_row in row["statements"]],
                    }
                )
        return None
    if item == "distress-seen":
        if result.get("outcome") != "human_route":
            return None
        return _digest({"outcome": "human_route", "cue_categories": list(result.get("cue_categories") or [])})
    if item == "unmapped-seen":
        statement_id = approval.get("statement_id")
        for row in result.get("unmapped_statements") or []:
            if row.get("statement_id") == statement_id:
                return _digest({"statement_id": row["statement_id"], "quote": row["quote"]})
        return None
    return None


def record_owner_approval(result: dict, directory: dict, approval: dict) -> dict:
    """Record one approval bound to the recomputed content hash.

    A string is not coerced to true. The directory role is the role.
    Marking a control met, closing a gap, editing a policy, and writing to a
    GRC system stay false.
    """

    out = deepcopy(result)
    out["human_approval"] = None
    out.update(_flags())
    out["blocked_reason"] = None
    if not isinstance(approval, dict):
        out["blocked_reason"] = "approval_not_object"
        return out
    person = _person(directory, approval.get("approver_ref"))
    if person is None:
        out["blocked_reason"] = "approver_not_in_directory"
        return out
    if person.get("guest") is True or person.get("role") != OWNER_ROLE:
        out["blocked_reason"] = "approver_not_control_owner"
        return out
    if approval.get("decision") != "approved":
        out["blocked_reason"] = "decision_not_approved"
        return out
    recomputed = _proposal_hash(out)
    if approval.get("proposal_hash") != recomputed:
        out["blocked_reason"] = "proposal_hash_mismatch"
        return out
    if out.get("caf", {}).get("indicators_unverified") is True and approval.get("pins_seen") is not True:
        out["blocked_reason"] = "pins_not_seen"
        return out
    if out.get("library_differences") and approval.get("library_differences_seen") is not True:
        out["blocked_reason"] = "library_differences_not_seen"
        return out
    if out.get("sources_current") is False and approval.get("stale_seen") is not True:
        out["blocked_reason"] = "stale_not_seen"
        return out
    if out.get("biased_criteria") and approval.get("bias_seen") is not True:
        out["blocked_reason"] = "bias_not_seen"
        return out
    if out.get("outcome") == "human_route" and approval.get("item") != "distress-seen":
        out["blocked_reason"] = "distress_route_open"
        return out
    expected = _item_hash(out, approval)
    if expected is None:
        out["blocked_reason"] = "item_not_in_proposal"
        return out
    if approval.get("content_hash") != expected:
        out["blocked_reason"] = "content_hash_mismatch"
        return out
    out["human_approval"] = {
        "approver_ref": person["ref"],
        "role": OWNER_ROLE,
        "item": approval.get("item"),
        "mapping_id": approval.get("mapping_id"),
        "gap_id": approval.get("gap_id"),
        "contradiction_id": approval.get("contradiction_id"),
        "statement_id": approval.get("statement_id"),
        "content_hash": expected,
        "proposal_hash": recomputed,
        "control_met": False,
        "gap_closed": False,
        "policy_edited": False,
        "grc_written": False,
    }
    out["proposal_hash"] = recomputed
    return out


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose policy-to-control mappings. Experiment 69.")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        result = map_controls(_load(args.request), _load(args.library), _load(args.directory), args.as_of)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(exc.__class__.__name__, file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
