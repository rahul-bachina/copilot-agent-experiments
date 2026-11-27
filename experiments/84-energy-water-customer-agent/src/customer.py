"""Answer a synthetic energy or water customer. Do not act on the account.

Autonomy is A1. The customer confirms a proposed action against the
agent-held copy and its hash. The confirmation does not submit the
reading, agree a plan, add anyone to a register, or change a tariff.

A message, an account note, and a caller-supplied policy are untrusted.
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
    from amounts import parse_amount, reading_token
    from cues import (
        affordability_hit,
        age_hit,
        bereavement_hit,
        carve_out_affirmed,
        complaint_hit,
        debt_hit,
        disability_hit,
        disconnection_hit,
        distress_hit,
        foi_hit,
        forged_confirmation_hit,
        grievance_hit,
        hardship_hit,
        human_request_hit,
        injection_hit,
        install_prepay_hit,
        language_hit,
        leading_hit,
        medical_hit,
        mental_health_hit,
        meter_request_hit,
        plan_agree_hit,
        plan_request_hit,
        prepayment_hit,
        psr_request_hit,
        role_claim,
        safeguarding_hit,
        sar_hit,
        sensitive_flags,
        tariff_change_hit,
        vulnerability_flags,
        whistleblowing_hit,
        write_off_hit,
    )
    from dates import as_date, parse_date, with_question_date
    from fairness import report as fairness_report
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import empty_mask, mask_text
    from negate import affirmed
    from siblings import complaint_signals, identifier_counts
    from sources import uk_context
else:
    from .amounts import parse_amount, reading_token
    from .cues import (
        affordability_hit,
        age_hit,
        bereavement_hit,
        carve_out_affirmed,
        complaint_hit,
        debt_hit,
        disability_hit,
        disconnection_hit,
        distress_hit,
        foi_hit,
        forged_confirmation_hit,
        grievance_hit,
        hardship_hit,
        human_request_hit,
        injection_hit,
        install_prepay_hit,
        language_hit,
        leading_hit,
        medical_hit,
        mental_health_hit,
        meter_request_hit,
        plan_agree_hit,
        plan_request_hit,
        prepayment_hit,
        psr_request_hit,
        role_claim,
        safeguarding_hit,
        sar_hit,
        sensitive_flags,
        tariff_change_hit,
        vulnerability_flags,
        whistleblowing_hit,
        write_off_hit,
    )
    from .dates import as_date, parse_date, with_question_date
    from .fairness import report as fairness_report
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import empty_mask, mask_text
    from .negate import affirmed
    from .siblings import complaint_signals, identifier_counts
    from .sources import uk_context

LABEL = (
    "DRAFT FOR THE CUSTOMER. YOU ARE TALKING TO AN AI. "
    "A PERSON IS AVAILABLE ON THIS TURN. "
    "THE AGENT DOES NOT CHANGE A TARIFF, AGREE A PAYMENT PLAN, "
    "WRITE OFF DEBT, INSTALL OR SWITCH A PREPAYMENT METER, OR MAKE A DECISION."
)
DISCLOSURE = (
    "You are talking to an AI assistant. Reedmarsh Energy and Reedmarsh Water are invented. "
    "This is not a person."
)
HUMAN_OFFER = (
    "You can ask for a human advisor at any time, including on this turn. "
    "Say that you want a person and this turn goes to a human advisor."
)
CATALOGUE_ID = "UK12"
EXPERIMENT_ID = "exp-84-energy-water-customer-agent"
ROOT = Path(__file__).resolve().parents[1]
CONVERSATION_ID = re.compile(r"^CV-\d{4}$")
ACCOUNT_ID = re.compile(r"^ACC-\d{4}$")
STALE_AFTER_DAYS = 90
_READING = re.compile(
    r"\b(?:meter )?reading\b(?:\s+is|\s+of|:)?\s*([0-9][0-9,]{0,14}(?:\.[0-9]+)?)",
    re.IGNORECASE,
)
_DATED = re.compile(
    r"\b(?:on|dated)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{4})",
    re.IGNORECASE,
)
_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_DATE_TOKEN = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}")
_NEGATION = re.compile(r"\b(?:not|no|never|without)\b", re.IGNORECASE)
_HELD: dict[str, dict] = {}
_EVENTS: list[dict] = []
_UNTRUSTED = (
    "confirmation_recorded",
    "explicit_confirm",
    "human_approval",
    "approved",
    "content_hash",
    "confirmed_action",
    "tariff_changed",
    "payment_plan_agreed",
    "debt_written_off",
    "prepayment_installed",
    "prepayment_switched",
    "decision_made",
    "action_submitted",
    "psr_added",
    "supply_disconnected",
    "route_seen",
    "role",
    "clearance",
    "instructions_followed",
)


class CustomerForbidden(RuntimeError):
    """The agent does not change the account or make a decision."""

    __test__ = False


class NotSynthetic(ValueError):
    """The request was not marked synthetic."""


def change_tariff(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not change a tariff.")


def agree_payment_plan(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not agree a payment plan.")


def write_off_debt(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not write off debt.")


def install_prepayment_meter(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not install a prepayment meter.")


def switch_prepayment_meter(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not switch a prepayment meter.")


def disconnect_supply(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not disconnect a supply.")


def add_to_priority_register(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not add anyone to the Priority Services Register.")


def decide(*_args, **_kwargs) -> None:
    raise CustomerForbidden("The agent does not make a decision.")


def reset_held() -> None:
    _HELD.clear()
    _EVENTS.clear()


def held_record(conversation_id: object) -> dict | None:
    if not isinstance(conversation_id, str):
        return None
    row = _HELD.get(conversation_id)
    if not isinstance(row, dict):
        return None
    return {
        "conversation_id": conversation_id,
        "content_hash": row.get("content_hash"),
        "action_digest": row.get("action_digest"),
    }


def pinned_accounts() -> dict:
    return json.loads((ROOT / "fixtures" / "accounts.json").read_text(encoding="utf-8"))["accounts"]


def pinned_directory() -> dict:
    return json.loads((ROOT / "fixtures" / "directory.json").read_text(encoding="utf-8"))


def pinned_knowledge() -> list[dict]:
    return json.loads((ROOT / "fixtures" / "knowledge.json").read_text(encoding="utf-8"))["articles"]


def pinned_policy() -> dict:
    return json.loads((ROOT / "fixtures" / "policy.json").read_text(encoding="utf-8"))


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


def _question_date(value: object) -> date:
    parsed = parse_date(value)
    day = as_date(parsed)
    if day is None:
        raise ValueError("The question date is unparseable. It was not replaced.")
    return day


def _force(result: dict) -> None:
    result["ai_disclosed"] = True
    result["human_route_offered"] = True
    result["opening"] = DISCLOSURE + " " + HUMAN_OFFER
    result["tariff_changed"] = False
    result["payment_plan_agreed"] = False
    result["debt_written_off"] = False
    result["prepayment_installed"] = False
    result["prepayment_switched"] = False
    result["decision_made"] = False
    result["action_submitted"] = False
    result["psr_added"] = False
    result["supply_disconnected"] = False
    result["instructions_followed"] = False
    result["approval_marker_trusted"] = False
    result["role_in_text_trusted"] = False
    result["clearance_in_text_trusted"] = False
    result["caller_knowledge_applied"] = False
    result["caller_policy_applied"] = False
    result["caller_directory_applied"] = False
    result["caller_account_applied"] = False
    result["coerced"] = False
    result["described_as_anonymised"] = False
    result["may_be_relied_on"] = False
    result["routine_queue"] = False
    result["production_written"] = False
    result["experiment_13_triage_called"] = False
    result["disp_clock_applied"] = False
    result["message_stored"] = False
    result["values_copied"] = False


def _projection(result: dict) -> dict:
    action = result.get("proposed_action")
    return {
        "conversation_id": result.get("conversation_id"),
        "account_ref": result.get("account_ref"),
        "customer_ref": result.get("customer_ref"),
        "sector": result.get("sector"),
        "as_of": result.get("as_of"),
        "group": result.get("group"),
        "outcome": result.get("outcome"),
        "article_id": result.get("article_id"),
        "answer_text": (result.get("answer") or {}).get("text"),
        "proposed_action": action,
        "vulnerability": result.get("vulnerability"),
        "sensitive": result.get("sensitive"),
        "complaint": result.get("complaint") is True,
        "affordability": result.get("affordability") is True,
        "debt": result.get("debt") is True,
        "disconnection": result.get("disconnection") is True,
        "prepayment": result.get("prepayment") is True,
        "human_requested": result.get("human_requested") is True,
        "leading": result.get("leading") is True,
        "carve_out": result.get("carve_out") is True,
        "prompt_injection": result.get("prompt_injection"),
        "marking": result.get("marking"),
        "legal_hold": result.get("legal_hold") is True,
        "legal_hold_unparseable": result.get("legal_hold_unparseable") is True,
        "retention": result.get("retention"),
        "retention_unparseable": result.get("retention_unparseable") is True,
        "conflicting_values": result.get("conflicting_values") is True,
        "stale": result.get("stale") is True,
        "future_date": result.get("future_date") is True,
        "unparseable_date": result.get("unparseable_date") is True,
        "malformed_amount": result.get("malformed_amount") is True,
        "balance_quoted": result.get("balance_quoted"),
        "required_acknowledgements": result.get("required_acknowledgements"),
        "route_seen": result.get("route_seen") is True,
        "dates": result.get("dates"),
        "masking": result.get("masking"),
        "uk_identifiers": result.get("uk_identifiers"),
        "opening": result.get("opening"),
        "human_route_offered": True,
        "ai_disclosed": True,
        "routine_queue": False,
        "tariff_changed": result.get("tariff_changed") is True,
        "payment_plan_agreed": result.get("payment_plan_agreed") is True,
        "debt_written_off": result.get("debt_written_off") is True,
        "prepayment_installed": result.get("prepayment_installed") is True,
        "prepayment_switched": result.get("prepayment_switched") is True,
        "decision_made": result.get("decision_made") is True,
        "action_submitted": result.get("action_submitted") is True,
        "psr_added": result.get("psr_added") is True,
        "supply_disconnected": result.get("supply_disconnected") is True,
        "instructions_followed": result.get("instructions_followed") is True,
        "suppression": result.get("suppression"),
        "caller_differences": result.get("caller_differences"),
    }


def _hash(result: dict) -> str:
    return _digest(_projection(result))


def _blank(conversation_id: str, question: date) -> dict:
    result = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "synthetic": True,
        "conversation_id": conversation_id,
        "as_of": question.isoformat(),
        "model_called": False,
        "network_called": False,
        "confirmation_recorded": False,
        "route_seen": False,
        "human_approval": None,
        "proposed_action": None,
        "article_id": None,
        "answer": {"text": None, "pinned": False, "sufficient": False},
        "handover": _handover(False, "offer", None, "human route offered on this turn", "A person is available."),
        "sources_opened_on": uk_context()["opened_on"],
        "stale_after_days": STALE_AFTER_DAYS,
        "stale_after_days_is_starter_rule": True,
    }
    _force(result)
    return result


def _handover(required: bool, urgency: str, queue: str | None, reason: str, summary: str) -> dict:
    return {
        "required": required,
        "urgency": urgency,
        "queue": queue,
        "reason": reason,
        "summary": summary,
        "pattern": "experiment-13-warm-handover",
        "experiment_13_triage_called": False,
    }


def _finish(result: dict) -> dict:
    _force(result)
    result["content_hash"] = _hash(result)
    if result.get("outcome") == "propose_action" and isinstance(result.get("proposed_action"), dict):
        _HELD[result["conversation_id"]] = {
            "content_hash": result["content_hash"],
            "projection": _projection(result),
            "action_digest": _digest(result["proposed_action"]),
            "customer_ref": result.get("customer_ref"),
            "required_acknowledgements": list(result.get("required_acknowledgements") or []),
        }
    event = {
        "group": result.get("group"),
        "sector": result.get("sector"),
        "outcome": result.get("outcome"),
        "handed_to_human": bool((result.get("handover") or {}).get("required")),
    }
    result["fairness_event"] = event
    _EVENTS.append(event)
    return result


def fairness_log() -> list[dict]:
    return [dict(row) for row in _EVENTS]


def _match_articles(text: str, sector: str) -> list[dict]:
    found = []
    for article in pinned_knowledge():
        if article.get("sector") not in {sector, "both"}:
            continue
        phrases = article.get("phrases") or []
        if any(affirmed(text, phrase) for phrase in phrases):
            found.append(article)
    return found


def _article_stale(article: dict, question: date) -> dict:
    parsed = with_question_date(parse_date(article.get("reviewed_on")), question)
    day = as_date(parsed)
    stale = bool(day and (question - day).days > STALE_AFTER_DAYS)
    return {
        "unparseable": bool(parsed.get("unparseable") or parsed.get("ambiguous")),
        "future": bool(parsed.get("future")),
        "stale": stale,
        "iso": parsed.get("iso"),
    }


def _material(pinned_body: str, caller_body: str) -> list[str]:
    if caller_body == pinned_body:
        return []
    changes = []
    if set(_NUMBER.findall(pinned_body)) != set(_NUMBER.findall(caller_body)):
        changes.append("number")
    if set(_DATE_TOKEN.findall(pinned_body)) != set(_DATE_TOKEN.findall(caller_body)):
        changes.append("date")
    if bool(_NEGATION.search(pinned_body)) != bool(_NEGATION.search(caller_body)):
        changes.append("negation")
    if not changes:
        changes.append("wording")
    return changes


def _caller_knowledge(request: dict) -> dict:
    supplied = request.get("caller_knowledge")
    if not isinstance(supplied, list):
        return {"present": supplied is not None, "applied": False, "changes": []}
    pinned = {article["id"]: article for article in pinned_knowledge()}
    changes = []
    for item in supplied:
        if not isinstance(item, dict):
            changes.append({"id": None, "changes": ["unparseable"]})
            continue
        article_id = item.get("id")
        body = item.get("body") if isinstance(item.get("body"), str) else ""
        current = pinned.get(article_id)
        if current is None:
            changes.append({"id": article_id, "changes": ["not_pinned"]})
            continue
        diff = _material(current.get("body") or "", body)
        if diff:
            changes.append({"id": article_id, "changes": diff})
    return {"present": True, "applied": False, "changes": changes}


def _reading_from(text: str, question: date) -> dict:
    match = _READING.search(text or "")
    if not match:
        return {"present": False, "unparseable": False, "reading": None, "date": None, "date_problem": None}
    token = reading_token(match.group(1))
    dated = _DATED.search(text or "")
    date_problem = None
    iso = None
    if dated:
        parsed = with_question_date(parse_date(dated.group(1)), question)
        if parsed.get("unparseable") or parsed.get("ambiguous") or parsed.get("future"):
            date_problem = parsed.get("reason") or "unparseable"
        else:
            iso = parsed.get("iso")
    return {
        "present": True,
        "unparseable": bool(token.get("unparseable")),
        "reading": token.get("reading"),
        "date": iso,
        "date_problem": date_problem,
        "coerced": False,
    }


def _account_holder(account_ref: str, customer_ref: object) -> bool:
    if not isinstance(customer_ref, str):
        return False
    for row in pinned_directory().get("customers") or []:
        if row.get("ref") != customer_ref:
            continue
        return (
            row.get("account_ref") == account_ref
            and row.get("active") is True
            and row.get("role") == "account_holder"
        )
    return False


def answer(request: dict, as_of: object) -> dict:
    """Return a draft. Nothing is submitted and no tariff is changed."""

    question = _question_date(as_of)
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    if request.get("synthetic") is not True:
        raise NotSynthetic("synthetic must be true")
    conversation_id = request.get("conversation_id")
    if not isinstance(conversation_id, str) or not CONVERSATION_ID.fullmatch(conversation_id):
        raise ValueError("conversation_id must look like CV-1001")
    result = _blank(conversation_id, question)
    result["untrusted_keys_ignored"] = sorted(key for key in _UNTRUSTED if key in request)
    result["stated_category"] = request.get("stated_category") if isinstance(request.get("stated_category"), str) else None
    result["stated_category_used"] = False
    message = request.get("message") if isinstance(request.get("message"), str) else ""
    notes = request.get("account_notes") if isinstance(request.get("account_notes"), str) else ""
    if not isinstance(request.get("message"), str):
        result["message_unparseable"] = True
    else:
        result["message_unparseable"] = False
    account_ref = request.get("account_ref")
    accounts = pinned_accounts()
    account = accounts.get(account_ref) if isinstance(account_ref, str) else None
    result["account_ref"] = account_ref if isinstance(account_ref, str) else None
    if not isinstance(account, dict) or not ACCOUNT_ID.fullmatch(str(account_ref)):
        result["outcome"] = "human_handover"
        result["account_found"] = False
        result["answer"] = {"text": pinned_policy()["account_not_found"], "pinned": True, "sufficient": False}
        result["handover"] = _handover(True, "immediate", "human_advisor", "account_not_on_the_pinned_file", "The account was not found. The message is not copied.")
        result["vulnerability"] = []
        result["sensitive"] = []
        return _finish(result)
    result["account_found"] = True
    result["customer_ref"] = account.get("customer_ref")
    result["sector"] = account.get("sector")
    result["group"] = account.get("group")
    caller_account = request.get("caller_account") if isinstance(request.get("caller_account"), dict) else None
    result["caller_account_differs"] = bool(caller_account and caller_account != {key: account.get(key) for key in caller_account})
    text = "\n".join(part for part in (message, notes, str(account.get("notes") or ""), str(account.get("cover") or "")) if part)
    caller_marking = request.get("caller_marking")
    if isinstance(caller_marking, str):
        text = text + "\n" + caller_marking
    meta_marks, _meta_bad = metadata_markings(account.get("protective_marking"))
    content_marks = content_markings(text)
    result["marking"] = higher_marking(meta_marks + content_marks)
    result["marking_labels"] = sorted(set(meta_marks + content_marks))
    hold, hold_bad = legal_hold(account.get("legal_hold"), text)
    result["legal_hold"] = hold
    result["legal_hold_unparseable"] = hold_bad
    retention, retention_bad = retention_labels(account.get("retention"), text)
    caller_retention = request.get("caller_retention")
    if caller_retention is not None:
        extra, extra_bad = retention_labels(caller_retention, "")
        retention_bad = retention_bad or extra_bad
        for label in extra:
            if label not in retention:
                retention.append(label)
        result["caller_retention_differs"] = extra != retention
    else:
        result["caller_retention_differs"] = False
    result["retention"] = retention
    result["retention_unparseable"] = retention_bad
    masked_message, mask_message = mask_text(message)
    masked_notes, mask_notes = mask_text(notes)
    del masked_message, masked_notes
    counts = empty_mask()
    for kind, value in mask_message["counts"].items():
        counts["counts"][kind] = value + mask_notes["counts"].get(kind, 0)
    counts["any"] = any(counts["counts"].values())
    counts["values_stored"] = False
    counts["values_copied"] = False
    counts["described_as_anonymised"] = False
    counts["masked_text_included"] = False
    result["masking"] = counts
    result["uk_identifiers"] = identifier_counts(message + "\n" + notes, on=question)
    result["role_claim"] = role_claim(text)
    flags_v = vulnerability_flags(text)
    flags_s = sensitive_flags(text)
    result["vulnerability"] = flags_v
    result["sensitive"] = flags_s
    result["complaint"] = complaint_hit(text)
    result["human_requested"] = human_request_hit(text)
    result["affordability"] = affordability_hit(text)
    result["debt"] = debt_hit(text) or write_off_hit(text)
    result["disconnection"] = disconnection_hit(text)
    result["prepayment"] = prepayment_hit(text) or install_prepay_hit(text)
    result["leading"] = leading_hit(text)
    result["carve_out"] = carve_out_affirmed(text)
    result["tariff_request"] = tariff_change_hit(text)
    result["plan_agree_request"] = plan_agree_hit(text)
    result["prompt_injection"] = {
        "detected": injection_hit(text),
        "followed": False,
        "forged_confirmation": forged_confirmation_hit(text),
        "forged_trusted": False,
    }
    result["experiment_02"] = complaint_signals(text)
    result["caller_differences"] = _caller_knowledge(request)
    policy = pinned_policy()
    if request.get("caller_policy") is not None:
        result["caller_policy_differs"] = request.get("caller_policy") != policy
    else:
        result["caller_policy_differs"] = False
    if isinstance(request.get("caller_directory"), dict):
        result["caller_directory_differs"] = request.get("caller_directory") != pinned_directory()
    else:
        result["caller_directory_differs"] = request.get("caller_directory") is not None
    amount_in_message = None
    amount_match = re.search(r"£\s*\d[\d,]*(?:\.\d+)?", message)
    malformed_amount = False
    if amount_match:
        parsed_amount = parse_amount(amount_match.group(0))
        malformed_amount = bool(parsed_amount.get("unparseable"))
        amount_in_message = parsed_amount.get("amount")
    result["malformed_amount"] = malformed_amount
    result["customer_amount_used"] = False
    balances = account.get("balances") if isinstance(account.get("balances"), list) else []
    parsed_balances = [parse_amount(item) for item in balances]
    balance_values = [item.get("amount") for item in parsed_balances if item.get("amount")]
    balance_bad = any(item.get("unparseable") for item in parsed_balances) or not balance_values
    balance_conflict = len(set(balance_values)) > 1
    caller_balance = None if not caller_account else caller_account.get("balance")
    if isinstance(caller_balance, str):
        caller_parsed = parse_amount(caller_balance)
        if caller_parsed.get("amount") and balance_values and caller_parsed["amount"] not in set(balance_values):
            balance_conflict = True
        if caller_parsed.get("unparseable"):
            balance_bad = True
    snap = with_question_date(parse_date(account.get("snapshot_date")), question)
    snap_day = as_date(snap)
    stale_account = bool(snap_day and (question - snap_day).days > STALE_AFTER_DAYS)
    result["dates"] = {"snapshot": snap, "coerced": False}
    result["stale"] = stale_account
    result["future_date"] = bool(snap.get("future"))
    result["unparseable_date"] = bool(snap.get("unparseable") or snap.get("ambiguous"))
    result["conflicting_values"] = balance_conflict
    withheld = above_ceiling(result["marking"], "OFFICIAL") or balance_conflict or balance_bad or stale_account or result["future_date"] or result["unparseable_date"]
    result["balance_withheld"] = withheld
    result["balance_quoted"] = None if withheld else balance_values[0]
    reading = _reading_from(message, question)
    result["reading"] = {"present": reading["present"], "unparseable": reading["unparseable"], "coerced": False, "date_problem": reading["date_problem"]}
    human_reasons = []
    if result["human_requested"]:
        human_reasons.append("human_requested")
    if flags_v:
        human_reasons.append("vulnerability")
    if flags_s:
        human_reasons.append("sensitive")
    if result["leading"]:
        human_reasons.append("leading_criterion")
    if result["affordability"] or result["debt"] or result["disconnection"] or result["prepayment"]:
        human_reasons.append("affordability_debt_disconnection_or_prepayment")
    if result["tariff_request"] or result["plan_agree_request"]:
        human_reasons.append("prohibited_action")
    if result["prompt_injection"]["detected"]:
        human_reasons.append("prompt_injection")
    if result["carve_out"]:
        human_reasons.append("carve_out")
    if above_ceiling(result["marking"], "OFFICIAL"):
        human_reasons.append("marking")
    if result["complaint"]:
        human_reasons.append("complaint")
    if balance_conflict:
        human_reasons.append("conflicting_values")
    if stale_account or result["future_date"] or result["unparseable_date"]:
        human_reasons.append("stale_or_unreadable_date")
    if result["message_unparseable"]:
        human_reasons.append("unparseable_message")
    if human_reasons:
        escalation = None
        if result["complaint"]:
            escalation = policy["energy_escalation"] if account.get("sector") == "energy" else policy["water_escalation"]
            if account.get("sector") not in {"energy", "water"}:
                escalation = policy["sector_unknown"]
        summary = "Flags: " + ", ".join(human_reasons) + ". The message is not copied."
        urgency = "immediate" if any(item in human_reasons for item in ("human_requested", "sensitive", "vulnerability", "affordability_debt_disconnection_or_prepayment")) else "priority"
        result["outcome"] = "human_handover"
        result["human_reasons"] = human_reasons
        result["answer"] = {
            "text": escalation or policy["human_handover"],
            "pinned": True,
            "sufficient": False,
        }
        result["handover"] = _handover(True, urgency, "human_advisor", ",".join(human_reasons), summary)
        result["required_acknowledgements"] = ["disclosure_seen", "human_route_seen"]
        return _finish(result)
    want_meter = meter_request_hit(message)
    want_plan = plan_request_hit(message)
    want_psr = psr_request_hit(message)
    if want_meter or want_plan or want_psr:
        if want_meter and (reading["unparseable"] or reading["date_problem"] or not reading["present"] or not reading["reading"]):
            result["outcome"] = "human_handover"
            result["human_reasons"] = ["meter_reading_not_readable"]
            result["answer"] = {"text": policy["reading_not_readable"], "pinned": True, "sufficient": False}
            result["handover"] = _handover(True, "priority", "human_advisor", "meter_reading_not_readable", "The reading was not readable. It was not set to zero. The message is not copied.")
            result["required_acknowledgements"] = ["disclosure_seen", "human_route_seen"]
            return _finish(result)
        if sum((want_meter, want_plan, want_psr)) > 1:
            result["outcome"] = "human_handover"
            result["conflicting_values"] = True
            result["human_reasons"] = ["conflicting_actions"]
            result["answer"] = {"text": policy["conflicting_actions"], "pinned": True, "sufficient": False}
            result["handover"] = _handover(True, "priority", "human_advisor", "conflicting_actions", "Two actions were asked for. Neither was chosen.")
            return _finish(result)
        if want_meter:
            kind = "meter_reading_submission"
            exact = (
                f"Propose a meter reading submission of {reading['reading']} for {account_ref}. "
                f"The reading date is {reading['date'] or 'not stated'}. This is a proposal. It is not submitted."
            )
            action = {
                "action_id": "ACT-" + conversation_id.split("-")[1],
                "kind": kind,
                "account_ref": account_ref,
                "exact_text": exact,
                "meter_reading": reading["reading"],
                "reading_date": reading["date"],
                "amount": None,
                "sector": account.get("sector"),
            }
        elif want_plan:
            kind = "payment_plan_request"
            exact = (
                f"Propose a payment-plan request for {account_ref}. "
                "This asks a person to consider a plan. It does not agree a plan."
            )
            action = {
                "action_id": "ACT-" + conversation_id.split("-")[1],
                "kind": kind,
                "account_ref": account_ref,
                "exact_text": exact,
                "meter_reading": None,
                "reading_date": None,
                "amount": None,
                "sector": account.get("sector"),
            }
        else:
            kind = "psr_referral"
            exact = (
                f"Propose a Priority Services Register referral for {account_ref}. "
                "A person decides whether to add anyone. Nobody is added here."
            )
            action = {
                "action_id": "ACT-" + conversation_id.split("-")[1],
                "kind": kind,
                "account_ref": account_ref,
                "exact_text": exact,
                "meter_reading": None,
                "reading_date": None,
                "amount": None,
                "sector": account.get("sector"),
            }
        acknowledgements = ["disclosure_seen", "human_route_seen"]
        if result["legal_hold"]:
            acknowledgements.append("hold_seen")
        if result["retention"]:
            acknowledgements.append("retention_seen")
        if malformed_amount:
            acknowledgements.append("amount_seen")
        result["outcome"] = "propose_action"
        result["proposed_action"] = action
        result["required_acknowledgements"] = acknowledgements
        result["answer"] = {"text": exact, "pinned": True, "sufficient": False}
        result["handover"] = _handover(False, "offer", None, "confirmation required before any account action", "The proposal is not submitted. A person is available.")
        return _finish(result)
    hits = _match_articles(message, str(account.get("sector")))
    if len(hits) > 1:
        result["outcome"] = "human_handover"
        result["conflicting_values"] = True
        result["human_reasons"] = ["conflicting_articles"]
        result["answer"] = {"text": policy["conflicting_articles"], "pinned": True, "sufficient": False}
        result["handover"] = _handover(True, "priority", "human_advisor", "conflicting_articles", "Two pinned articles matched. Neither was chosen.")
        return _finish(result)
    if len(hits) == 1:
        article = hits[0]
        state = _article_stale(article, question)
        result["dates"]["article"] = state
        if state["stale"] or state["future"] or state["unparseable"]:
            result["stale"] = result["stale"] or state["stale"]
            result["future_date"] = result["future_date"] or state["future"]
            result["unparseable_date"] = result["unparseable_date"] or state["unparseable"]
            result["outcome"] = "human_handover"
            result["article_id"] = article["id"]
            result["human_reasons"] = ["stale_article"]
            result["answer"] = {"text": policy["stale_article"], "pinned": True, "sufficient": False}
            result["handover"] = _handover(True, "priority", "human_advisor", "stale_article", "The pinned article was not quoted as current.")
            return _finish(result)
        body = article["body"]
        if article["id"] == "KB-BILL" and result["balance_quoted"] and snap_day:
            body = body + f" The pinned snapshot dated {snap_day.isoformat()} shows £{result['balance_quoted']}. That figure is not a decision."
        result["outcome"] = "answer"
        result["article_id"] = article["id"]
        result["answer"] = {"text": body, "pinned": True, "sufficient": True}
        result["handover"] = _handover(False, "offer", None, "human route offered on this turn", "A person is available. The message is not copied.")
        result["required_acknowledgements"] = ["disclosure_seen", "human_route_seen"]
        return _finish(result)
    result["outcome"] = "not_in_knowledge"
    result["answer"] = {"text": policy["not_in_knowledge"], "pinned": True, "sufficient": False}
    result["handover"] = _handover(False, "offer", None, "not in the pinned knowledge", "A person is available. Nothing was guessed.")
    result["required_acknowledgements"] = ["disclosure_seen", "human_route_seen"]
    return _finish(result)


def confirm_action(result: dict, confirmation: dict) -> dict:
    """Record the customer's confirmation of the held proposal. Do not submit it."""

    if not isinstance(result, dict) or not isinstance(confirmation, dict):
        raise TypeError("result and confirmation must be objects")
    output = deepcopy(result)
    conversation_id = output.get("conversation_id")
    held = _HELD.get(conversation_id) if isinstance(conversation_id, str) else None
    output["confirmation_recorded"] = False
    output["action_submitted"] = False
    output["held_copy_replaced"] = False
    if not isinstance(held, dict):
        output["rejection_reason"] = "no_held_copy"
        _force(output)
        return output
    current = _projection(output)
    if current != held["projection"] or _digest(current) != held["content_hash"]:
        output["rejection_reason"] = "post_confirmation_edit"
        _force(output)
        output["confirmation_recorded"] = False
        return output
    if confirmation.get("content_hash") != held["content_hash"]:
        output["rejection_reason"] = "hash_not_held"
        _force(output)
        output["confirmation_recorded"] = False
        return output
    if _digest(confirmation.get("confirmed_action")) != held["action_digest"]:
        output["rejection_reason"] = "action_not_held"
        _force(output)
        output["confirmation_recorded"] = False
        return output
    if confirmation.get("explicit_confirm") is not True:
        output["rejection_reason"] = "explicit_confirm_not_true"
        _force(output)
        output["confirmation_recorded"] = False
        return output
    if not _account_holder(output.get("account_ref"), confirmation.get("customer_ref")):
        output["rejection_reason"] = "customer_not_on_the_directory"
        _force(output)
        output["confirmation_recorded"] = False
        return output
    if confirmation.get("customer_ref") != held.get("customer_ref"):
        output["rejection_reason"] = "customer_not_the_account_holder"
        _force(output)
        output["confirmation_recorded"] = False
        return output
    missing = [
        name for name in held.get("required_acknowledgements") or []
        if confirmation.get(name) is not True
    ]
    if missing:
        output["rejection_reason"] = "acknowledgement_missing"
        output["acknowledgements_missing"] = missing
        _force(output)
        output["confirmation_recorded"] = False
        return output
    output["confirmation_recorded"] = True
    output["rejection_reason"] = None
    output["confirmed_action_id"] = (output.get("proposed_action") or {}).get("action_id")
    _force(output)
    output["confirmation_recorded"] = True
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Answer one synthetic energy or water customer.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.request).read_text(encoding="utf-8"))
    print(json.dumps(answer(payload, args.as_of), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
