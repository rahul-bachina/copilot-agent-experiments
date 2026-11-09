#!/usr/bin/env python3
"""Propose a queue, a priority, and a reason for one synthetic case.

The same case and the same as-of date produce the same JSON. human_approval
is null until a separate review object is supplied. Confirmation does not
reroute, close, or escalate the case, and it does not change a routing rule.

Vulnerability and statutory-clock cases always propose a human queue. A
confidence band is not applied to those cases, and it cannot move them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from clocks import awaabs_view, cite
    from fairness import adjustment_mentioned, characteristic_feature, fairness_instruction
    from injection import signals_in, strip_instruction_sentences
    from rules import match_rules
    from sources import NOT_OPENED, RETRIEVED_ON, SOURCES, STALE_AFTER_DAYS
else:
    from .clocks import awaabs_view, cite
    from .fairness import adjustment_mentioned, characteristic_feature, fairness_instruction
    from .injection import signals_in, strip_instruction_sentences
    from .rules import match_rules
    from .sources import NOT_OPENED, RETRIEVED_ON, SOURCES, STALE_AFTER_DAYS

RULE_WINDOW = STALE_AFTER_DAYS

CALLER = "exp-42-case-routing-assistant"
CATALOGUE_ID = "C003"
LABEL = "DRAFT FOR QUEUE REVIEW"
SCANNER_ID = "exp-15-vulnerability-urgency-scanner"
CASE_ID = re.compile(r"^SYN-CASE-\d{4}$")
ADVISER_ID = re.compile(r"^SYN-ADVISER-\d{3}$")
OWNER_ID = re.compile(r"^SYN-OWNER-\d{3}$")

VULNERABILITY = frozenset(
    {
        "possible_safeguarding_risk",
        "possible_self_harm_risk",
        "possible_financial_hardship",
    }
)
URGENT_VULNERABILITY = frozenset(
    {
        "possible_safeguarding_risk",
        "possible_self_harm_risk",
    }
)
DEADLINE_CATEGORY = "possible_deadline_or_time_limit"

CHANNELS = frozenset({"web_form", "email", "phone", "portal", "letter"})
SECTORS = frozenset({"council", "housing", "utility", "financial_services", "other"})

PROHIBITED_INPUT_KEYS = frozenset(
    {
        "human_approval",
        "rerouted",
        "queue_changed",
        "closed",
        "escalated",
        "rules_changed",
        "priority_changed",
        "executed",
        "actions_taken",
        "proposed_queue",
        "confidence",
        "owner_approved",
    }
)

_STATUTE = (
    ("foi", re.compile(r"\b(?:freedom of information|foi request)\b", re.IGNORECASE)),
    ("eir", re.compile(r"\benvironmental information\b", re.IGNORECASE)),
    ("sar", re.compile(r"\b(?:subject access request|subject access|\bSAR\b)\b", re.IGNORECASE)),
    ("awaabs", re.compile(r"\b(?:damp|mould|mold|awaab(?:'s)? law)\b", re.IGNORECASE)),
)
_COMPLAINT = re.compile(
    r"\b(?:formal complaint|i want to complain|i wish to complain|i am unhappy|i'm unhappy)\b",
    re.IGNORECASE,
)
_ENTITLEMENT = re.compile(
    r"\b(?:am i entitled|am i eligible|eligibility|how much (?:benefit|support) will i)\b",
    re.IGNORECASE,
)
_DANGER = re.compile(r"\b(?:in immediate danger|call 999)\b", re.IGNORECASE)

_CLASS = {
    "foi": "foi_request",
    "eir": "eir_request",
    "sar": "subject_access_request",
    "awaabs": "other",
    "disp": "complaint",
}

CONFIRM_ROUTE = "adviser_confirm_proposed_route"
ACCEPT_HUMAN = "adviser_accept_human_queue"
APPROVE_RULE = "queue_owner_approve_rule_change"
REJECT = "reject_proposal"
HUMAN_OUTCOMES = frozenset(
    {
        "human_vulnerability",
        "human_statutory",
        "human_fairness",
        "human_adjustment",
        "human_complaint",
        "human_entitlement",
        "human_review",
        "stale_rule",
        "rule_not_owner_approved",
    }
)
REFUSED_DECISIONS = frozenset(
    {
        "reroute",
        "close",
        "escalate",
        "change_routing_rules",
        "set_priority",
        "send",
        "decide_entitlement",
        "label_vulnerable",
    }
)


class RoutingForbidden(RuntimeError):
    """The assistant has no reroute, close, escalate, or rule-change path."""


class NotSynthetic(ValueError):
    """Raised only by the direct refusal helpers. propose_route returns a refusal."""


def reroute_case(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not reroute a case")


def close_case(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not close a case")


def escalate_case(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not escalate a case")


def change_routing_rules(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not change a routing rule")


def set_priority(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not change a priority on a system")


def send_message(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not send a message")


def decide_entitlement(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not decide entitlement")


def label_person_vulnerable(*_args, **_kwargs) -> None:
    raise RoutingForbidden("the assistant does not label a person as vulnerable")


def _load_scan():
    scanner_src = (
        Path(__file__).resolve().parents[2] / "15-vulnerability-urgency-scanner" / "src"
    )
    if not scanner_src.is_dir():
        raise RoutingForbidden(
            "Experiment 15 is required at experiments/15-vulnerability-urgency-scanner. "
            "This assistant does not carry its own vulnerability list."
        )
    inserted = str(scanner_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import scan as scan_module

    if scan_module.CALLER != SCANNER_ID:
        raise RoutingForbidden("the scanner module is not Experiment 15")
    return scan_module


def _parse_as_of(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError("as_of must be a date or an ISO date")


def _allow(value, allowed: frozenset[str]) -> str | None:
    if isinstance(value, str) and value in allowed:
        return value
    return None


def _case_id(value) -> str | None:
    if isinstance(value, str) and CASE_ID.match(value):
        return value
    return None


def _empty_flags() -> dict:
    return {
        "rerouted": False,
        "queue_changed": False,
        "priority_changed": False,
        "closed": False,
        "escalated": False,
        "rules_changed": False,
        "message_sent": False,
        "entitlement_decided": False,
        "person_labelled_vulnerable": False,
        "protected_characteristic_used_as_a_feature": False,
        "confidence_overrode_human_route": False,
        "clock_applied_as_a_route": False,
    }


def _force(result: dict) -> None:
    result["label"] = LABEL
    result["catalogue_id"] = CATALOGUE_ID
    result["autonomy"] = "A1"
    result["actions_taken"] = []
    result["executed"] = False
    result["model_called"] = False
    result["network_called"] = False
    result["case_text_echoed"] = False
    result["confirmation_required_before_reroute"] = True
    result["reroute_available_in_this_starter"] = False
    flags = result.setdefault("flags", {})
    flags.update(_empty_flags())
    result["prompt_injection"]["followed"] = False
    result["human_route"]["offered"] = True
    result["human_route"]["phone_published"] = False
    if result.get("confidence"):
        result["confidence"]["overrides_human_route"] = False


def _confidence(band: str, matched: int, conflict: bool) -> dict:
    note = (
        "This band counts approved rules that matched. It is not a model probability. "
        "It cannot move a human-mandatory case."
    )
    if band == "not_used":
        note = (
            "A confidence band is not applied. The case proposes a human queue. "
            "The band cannot move it."
        )
    return {
        "band": band,
        "basis": "deterministic_rule_match",
        "matched_rule_count": matched,
        "conflict": conflict,
        "overrides_human_route": False,
        "note": note,
    }


def _reason(reason_id: str, text: str, source: str) -> dict:
    return {"id": reason_id, "text": text, "source": source}


def _classification(kinds: list[str], *, complaint: bool, service_topic: str | None) -> dict:
    if len(kinds) > 1 and all(kind in {"foi", "eir", "sar"} for kind in kinds):
        primary = "mixed"
    elif len(kinds) == 1 and kinds[0] in _CLASS:
        primary = _CLASS[kinds[0]]
    elif complaint:
        primary = "complaint"
    else:
        primary = "other"
    return {
        "primary_type": primary,
        "service_topic": service_topic,
        "statutory_kinds": list(kinds),
        "experiment_01_model_called": False,
        "pattern": (
            "Classification names follow Experiment 01 (foi_request, eir_request, "
            "subject_access_request, complaint, mixed, other). They are assigned "
            "here by keyword. Experiment 01's model is not called."
        ),
    }


def _scanner_view(scanned: dict | None, *, called: bool, error: str | None) -> dict:
    categories: list[str] = []
    finding_count = None
    input_sha = None
    if scanned is not None:
        for flag in scanned.get("flags") or []:
            category = flag.get("category")
            if category and category not in categories:
                categories.append(category)
        gateway = scanned.get("pii_gateway") or {}
        finding_count = gateway.get("finding_count")
        input_sha = gateway.get("input_sha256")
    return {
        "called": called,
        "experiment": SCANNER_ID,
        "categories": categories,
        "finding_count": finding_count,
        "input_sha256": input_sha,
        "phrases_copied": False,
        "person_labelled_vulnerable": False,
        "error": error,
    }


def _source_view(as_of: date) -> list[dict]:
    rows = []
    for source in SOURCES.values():
        verified = date.fromisoformat(source["retrieved"])
        stale = (as_of - verified).days > STALE_AFTER_DAYS
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "retrieved": source["retrieved"],
                "stale": stale,
                "quoted": not stale,
                "taken": None if stale else source["taken"],
            }
        )
    return rows


def _human_route() -> dict:
    return {
        "offered": True,
        "phone_published": False,
        "note": (
            "A person can take this case. This starter does not publish a telephone "
            "number and does not read a live contact page."
        ),
    }


def _refusal(stripped: list[str]) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": "A1",
        "outcome": "refused_not_synthetic",
        "case_id": None,
        "channel": None,
        "sector": None,
        "proposed_queue": None,
        "priority": None,
        "reasons": [
            _reason(
                "R-SYNTHETIC",
                "This starter only reads a record marked synthetic. The text has not been copied.",
                "src/routing.py",
            )
        ],
        "confidence": _confidence("not_used", 0, False),
        "classification": _classification([], complaint=False, service_topic=None),
        "human_approval": None,
        "human_route": _human_route(),
        "ai_disclosure": (
            "This draft was prepared by an automated assistant. A person decides the queue. "
            "Nothing has been rerouted."
        ),
        "flags": _empty_flags(),
        "rules": {"current": [], "stale": [], "unapproved": [], "applied": False},
        "vulnerability": _scanner_view(None, called=False, error="not_synthetic"),
        "statutory_clock": {"present": False, "kinds": [], "date_calculated": False},
        "fairness": {
            "characteristic_used_as_a_feature": False,
            "instruction_detected": False,
            "duty_met": False,
            "due_regard_carried_out": False,
        },
        "rule_change": None,
        "prompt_injection": {"detected": False, "signals": [], "followed": False, "stripped_keys": stripped},
        "sources": [],
        "sources_not_opened": list(NOT_OPENED),
        "pii_gateway": {"output_is_anonymised": False, "agent_may_release": False},
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "case_text_echoed": False,
        "confirmation_required_before_reroute": True,
        "reroute_available_in_this_starter": False,
    }
    _force(result)
    return result


def _rule_change(payload) -> dict | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return {"status": "ignored", "applied": False, "rules_file_changed": False}
    feature = payload.get("feature")
    feature_text = feature if isinstance(feature, str) else None
    refused = characteristic_feature(feature_text)
    return {
        "status": "refused_protected_characteristic" if refused else "pending_owner_approval",
        "rule_id": payload.get("rule_id") if isinstance(payload.get("rule_id"), str) else None,
        "feature_refused": refused,
        "applied": False,
        "rules_file_changed": False,
        "note": (
            "The proposal is not used for this case. Queue-owner approval, if later recorded, "
            "still does not edit the rule file."
        ),
    }


def propose_route(case: dict, as_of: date | datetime | str) -> dict:
    """Return one routing proposal. Does not write a queue."""

    if not isinstance(case, dict):
        raise TypeError("case must be an object")
    on = _parse_as_of(as_of)
    stripped = sorted(key for key in PROHIBITED_INPUT_KEYS if key in case)
    if case.get("synthetic") is not True:
        return _refusal(stripped)

    text = case.get("text") if isinstance(case.get("text"), str) else ""
    kept = strip_instruction_sentences(text)
    injection = signals_in(text)
    scanned, scan_error = _scan(text)
    categories = []
    if scanned is not None:
        for flag in scanned.get("flags") or []:
            category = flag.get("category")
            if category and category not in categories:
                categories.append(category)

    kinds = [kind for kind, pattern in _STATUTE if pattern.search(kept)]
    structured = case.get("statutory_clock") if isinstance(case.get("statutory_clock"), dict) else {}
    structured_kind = structured.get("kind") if isinstance(structured.get("kind"), str) else None
    if structured_kind in {"foi", "eir", "sar", "awaabs", "disp"} and structured_kind not in kinds:
        kinds.append(structured_kind)

    rules = match_rules(kept, on, window_days=RULE_WINDOW)
    change = _rule_change(case.get("proposed_rule_change"))
    fairness_hit = fairness_instruction(text) or bool(change and change["feature_refused"])
    adjustment = adjustment_mentioned(text) and not fairness_hit
    complaint = _COMPLAINT.search(kept) is not None
    entitlement = _ENTITLEMENT.search(kept) is not None
    danger = _DANGER.search(text) is not None or "possible_self_harm_risk" in categories

    vuln_categories = [item for item in categories if item in VULNERABILITY]
    deadline_flag = DEADLINE_CATEGORY in categories
    if deadline_flag and "deadline_phrase" not in kinds:
        kinds.append("deadline_phrase")

    statutory = any(kind in {"foi", "eir", "sar", "awaabs", "disp", "deadline_phrase"} for kind in kinds)
    vulnerability = bool(vuln_categories)

    outcome = "human_review"
    queue = None
    priority = "priority"
    band = "not_used"
    reasons: list[dict] = []
    service_topic = None

    if vulnerability:
        outcome = "human_vulnerability"
        queue = "q-human-vulnerability"
        priority = "urgent-human" if any(item in URGENT_VULNERABILITY for item in vuln_categories) or statutory else "priority"
        reasons.append(
            _reason(
                "R-VULN-15",
                "Experiment 15 returned a safeguarding, self-harm, or hardship category. "
                "The person is not labelled. The category is not a score, and the case is not placed on a routine queue.",
                SCANNER_ID,
            )
        )
    elif fairness_hit:
        outcome = "human_fairness"
        queue = "q-human-fairness"
        reasons.append(
            _reason(
                "R-FAIRNESS",
                "A protected characteristic was used as a routing feature, in the text or in a proposed rule. "
                "Equality Act 2010 section 19 describes a provision, criterion or practice. Section 29(2) covers detriment in a service. "
                "This starter does not decide that the instruction is unlawful. It does not apply it.",
                "fairness.py",
            )
        )
    elif statutory:
        outcome = "human_statutory"
        queue = "q-human-statutory"
        priority = "urgent-human"
        reasons.append(
            _reason(
                "R-CLOCK",
                "A statutory-clock case always proposes a human queue. The date is not calculated in this assistant, "
                "except that Experiment 05 may illustrate an Awaab's Law clock with officer approval forced off.",
                "clocks.py",
            )
        )
    elif adjustment:
        outcome = "human_adjustment"
        queue = "q-human-review"
        reasons.append(
            _reason(
                "R-ADJUSTMENT",
                "The text mentions disability or an adjustment. That is not used as a routing feature. "
                "Equality Act 2010 section 29(7) says a reasonable-adjustment duty applies to a service-provider. "
                "Section 20 was not opened. A person reviews the case. No duty is treated as met.",
                "fairness.py",
            )
        )
    elif entitlement:
        outcome = "human_entitlement"
        queue = "q-human-review"
        reasons.append(
            _reason(
                "R-ENTITLEMENT",
                "An entitlement or eligibility question is not answered and is not placed on a routine queue.",
                "routing.py",
            )
        )
    elif complaint:
        outcome = "human_complaint"
        queue = "q-human-review"
        reasons.append(
            _reason(
                "R-COMPLAINT",
                "A complaint is not placed on a routine queue. No complaint timescale is calculated. DISP was not opened.",
                "routing.py",
            )
        )
    elif rules["stale"] and not rules["current"]:
        outcome = "stale_rule"
        reasons.append(
            _reason(
                "R-STALE",
                "The matching rule is older than 180 days. Equal to 180 days would still be current. The queue is not proposed.",
                "rules.py",
            )
        )
    elif rules["unapproved"] and not rules["current"]:
        outcome = "rule_not_owner_approved"
        reasons.append(
            _reason(
                "R-UNAPPROVED",
                "A draft rule matched. The queue owner has not approved it. It is not applied.",
                "rules.py",
            )
        )
    elif rules["conflict"] or (not rules["current"] and not rules["stale"] and not rules["unapproved"]):
        outcome = "human_review"
        if rules["conflict"]:
            reasons.append(
                _reason(
                    "R-CONFLICT",
                    "More than one approved queue matched. Neither queue is chosen.",
                    "rules.py",
                )
            )
        else:
            reasons.append(
                _reason(
                    "R-NO-RULE",
                    "No approved rule matched. The case is left for a person. A missing rule is not a decision.",
                    "rules.py",
                )
            )
    else:
        outcome = "proposed_route"
        queue = rules["queue"]
        priority = "routine"
        service_topic = rules["current"][0]["topic"]
        band = "high" if len(rules["current"]) == 1 else "medium"
        reasons.append(
            _reason(
                "R-RULE",
                "One approved service rule matched, and it names a service topic. "
                "A person must confirm before any reroute. This result does not reroute the case.",
                rules["current"][0]["id"],
            )
        )

    if danger and outcome == "human_vulnerability":
        reasons.append(
            _reason(
                "R-DANGER",
                "If someone is in immediate danger, contact the emergency services. This agent does not place that call.",
                "routing.py",
            )
        )

    if injection:
        reasons.append(
            _reason(
                "R-INJECTION",
                "An instruction in the case was recorded and was not followed. It did not close, reroute, or clear a human queue.",
                "injection.py",
            )
        )

    clock_kinds = [kind for kind in kinds if kind != "deadline_phrase"]
    citations = [cite(kind) for kind in clock_kinds]
    if outcome == "proposed_route":
        confidence_band = band
    elif outcome == "human_review":
        confidence_band = "low"
    else:
        confidence_band = "not_used"
    confidence = _confidence(confidence_band, len(rules["current"]), rules["conflict"])

    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "autonomy": "A1",
        "experiment": CALLER,
        "outcome": outcome,
        "case_id": _case_id(case.get("case_id")),
        "channel": _allow(case.get("channel"), CHANNELS),
        "sector": _allow(case.get("sector"), SECTORS),
        "as_of": on.isoformat(),
        "proposed_queue": queue,
        "priority": priority,
        "reasons": reasons,
        "confidence": confidence,
        "classification": _classification(clock_kinds, complaint=complaint, service_topic=service_topic),
        "human_approval": None,
        "human_route": _human_route(),
        "ai_disclosure": (
            "This draft was prepared by an automated assistant. A person decides the queue. "
            "Nothing has been rerouted, closed, or escalated."
        ),
        "flags": _empty_flags(),
        "rules": {
            "current_ids": [item["id"] for item in rules["current"]],
            "stale_ids": [item["id"] for item in rules["stale"]],
            "unapproved_ids": [item["id"] for item in rules["unapproved"]],
            "applied": outcome == "proposed_route",
            "applied_means_rerouted": False,
        },
        "vulnerability": _scanner_view(scanned, called=scan_error is None, error=scan_error),
        "statutory_clock": {
            "present": statutory,
            "kinds": clock_kinds,
            "deadline_phrase": deadline_flag,
            "date_calculated": False,
            "citations": citations,
        },
        "fairness": {
            "characteristic_used_as_a_feature": False,
            "instruction_detected": fairness_hit,
            "adjustment_mentioned": adjustment or (adjustment_mentioned(text) and fairness_hit),
            "duty_met": False,
            "due_regard_carried_out": False,
            "section_149_list_includes_marriage": False,
            "section_19_list_includes_marriage": True,
        },
        "rule_change": change,
        "prompt_injection": {
            "detected": bool(injection),
            "signals": injection,
            "followed": False,
            "stripped_keys": stripped,
        },
        "sources": _source_view(on),
        "sources_not_opened": list(NOT_OPENED),
        "input_sha256": text_hash,
        "pii_gateway": {
            "via": SCANNER_ID,
            "output_is_anonymised": False,
            "agent_may_release": False,
            "redacted_text_copied": False,
        },
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "case_text_echoed": False,
        "confirmation_required_before_reroute": True,
        "reroute_available_in_this_starter": False,
        "sources_current": all(not row["stale"] for row in _source_view(on)),
        "legal_retrieval_date": RETRIEVED_ON.isoformat(),
    }
    # Fix awaabs clock call: if fields missing, do not pretend they were read from the text.
    _attach_awaabs(result, kinds, structured, on)
    _force(result)
    return result


def _attach_awaabs(result: dict, kinds: list[str], structured: dict, on: date) -> None:
    if "awaabs" not in kinds:
        return
    fields = structured.get("fields") if isinstance(structured.get("fields"), dict) else None
    view = awaabs_view(fields, on)
    for row in result["statutory_clock"]["citations"]:
        if row["kind"] == "awaabs":
            row["experiment_05_called"] = view["called"]
            row["clock"] = view
            row["date_calculated"] = False
    result["flags"]["clock_applied_as_a_route"] = False


def _scan(text: str) -> tuple[dict | None, str | None]:
    try:
        scanner = _load_scan()
        return scanner.scan(text, synthetic=True, model=None), None
    except RoutingForbidden:
        raise
    except Exception as exc:  # noqa: BLE001 — a scanner failure must not invent a clear bill
        return None, type(exc).__name__


def record_review(proposal: dict, review: dict) -> dict:
    """Record a separate review. Does not reroute, and does not edit a rule."""

    if not isinstance(proposal, dict) or not isinstance(review, dict):
        raise TypeError("proposal and review must be objects")
    result = json.loads(json.dumps(proposal))
    decision = review.get("decision")
    actor = review.get("actor")
    actor_id = review.get("actor_id") if isinstance(review.get("actor_id"), str) else ""
    accepted = False
    reason = "refused"

    if decision in REFUSED_DECISIONS:
        reason = "prohibited_decision"
    elif decision == CONFIRM_ROUTE:
        if actor != "adviser" or not ADVISER_ID.match(actor_id):
            reason = "adviser_id_required"
        elif result.get("outcome") != "proposed_route":
            reason = "human_queue_is_not_a_bot_route"
        else:
            accepted = True
            reason = "confirmation_recorded_not_executed"
    elif decision == ACCEPT_HUMAN:
        if actor != "adviser" or not ADVISER_ID.match(actor_id):
            reason = "adviser_id_required"
        elif result.get("outcome") not in HUMAN_OUTCOMES:
            reason = "not_a_human_queue"
        else:
            accepted = True
            reason = "human_queue_accepted_not_executed"
    elif decision == APPROVE_RULE:
        change = result.get("rule_change") or {}
        if actor != "queue_owner" or not OWNER_ID.match(actor_id):
            reason = "queue_owner_id_required"
        elif change.get("status") != "pending_owner_approval":
            reason = "no_approvable_rule_change"
        elif review.get("rule_id") != change.get("rule_id"):
            reason = "rule_id_mismatch"
        else:
            accepted = True
            reason = "approval_recorded_rule_file_not_changed"
    elif decision == REJECT:
        if actor == "adviser" and ADVISER_ID.match(actor_id):
            accepted = True
            reason = "rejected"
        elif actor == "queue_owner" and OWNER_ID.match(actor_id):
            accepted = True
            reason = "rejected"
        else:
            reason = "actor_id_required"
    else:
        reason = "unknown_decision"

    result["review"] = {
        "decision": decision if isinstance(decision, str) else None,
        "actor": actor if actor in {"adviser", "queue_owner"} else None,
        "accepted": accepted,
        "refused": not accepted,
        "reason": reason,
        "executed": False,
    }
    if accepted and decision in {CONFIRM_ROUTE, ACCEPT_HUMAN}:
        result["human_approval"] = {
            "decision": decision,
            "actor": "adviser",
            "executed": False,
            "rerouted": False,
        }
    elif accepted and decision == APPROVE_RULE:
        result["human_approval"] = {
            "decision": decision,
            "actor": "queue_owner",
            "executed": False,
            "rules_changed": False,
        }
        if isinstance(result.get("rule_change"), dict):
            result["rule_change"]["status"] = "approval_recorded_not_applied"
            result["rule_change"]["applied"] = False
            result["rule_change"]["rules_file_changed"] = False
    else:
        result["human_approval"] = None
    _force(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose a queue for one synthetic case")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    path = Path(args.input)
    try:
        case = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    if not isinstance(case, dict):
        return 2
    try:
        proposal = propose_route(case, args.as_of)
    except (TypeError, ValueError):
        return 2
    json.dump(proposal, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
