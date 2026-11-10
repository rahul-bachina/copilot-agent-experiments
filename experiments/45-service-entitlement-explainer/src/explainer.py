"""Service entitlement explainer. Deterministic. Autonomy A0.

The draft explains an approved table. It does not grant, refuse, or change
an entitlement.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import dispute_codes, hidden_and_visible, signals_in, strip_instruction_spans
    from siblings import EntitlementForbidden, normalise
    from sources import assess
else:
    from .injection import dispute_codes, hidden_and_visible, signals_in, strip_instruction_spans
    from .siblings import EntitlementForbidden, normalise
    from .sources import assess

LABEL = "DRAFT EXPLANATION OF THE APPROVED TABLE. NOT A GRANT, A REFUSAL, OR A CHANGE."
CATALOGUE_ID = "C007"
EXPERIMENT_ID = "exp-45-service-entitlement-explainer"
STALE_AFTER_DAYS = 180
PHONE = "01632 960045"
ALLOWED_ORGS = frozenset({"Aldermere Home Plan", "Aldermere Packaged Account"})
SECTORS = frozenset({"home_services", "telecoms", "financial_services", "public_service"})
CUSTOMER_REF = re.compile(r"^SYN-[A-Z0-9-]{1,40}$")
ACTOR_ID = re.compile(r"^SYN-[A-Z0-9-]{1,40}$")
QUESTION_LIMIT = 4000

PROHIBITED_KEYS = frozenset(
    {
        "grant_entitlement",
        "refuse_entitlement",
        "change_entitlement",
        "entitlement_granted",
        "entitlement_refused",
        "entitlement_changed",
        "coverage_decision",
        "human_approval",
        "send_message",
        "write_record",
        "waive_exclusion",
        "section_69_applied",
        "unfair_term_found",
        "consumer_understanding_met",
        "consumer_duty_met",
        "model_called",
        "network_called",
        "actions_taken",
        "approved",
        "decision",
    }
)

ALLOWED_DECISIONS = frozenset(
    {
        "human_decides_included",
        "human_decides_not_included",
        "human_requests_more_information",
        "reject_explanation",
    }
)

_BANNED_PLAIN = (
    "we grant",
    "we refuse",
    "entitlement has been changed",
    "claim approved",
    "claim declined",
)

_ROUTE_SENTENCE = {
    "as_of_invalid": "The as-of date could not be read.",
    "question_missing": "No question was supplied.",
    "question_too_long": "The question is longer than this starter accepts.",
    "sector_missing": "No sector was supplied.",
    "sector_not_recognised": "The sector is not one this starter knows.",
    "table_missing": "No rules table was supplied.",
    "table_not_approved": "The rules table is not marked approved.",
    "table_stale": "The rules table is outside the review window.",
    "table_date_invalid": "The rules table approval date could not be read.",
    "no_matching_rule": "No approved rule matched the question.",
    "multiple_rules": "More than one rule matched. A person has to choose.",
    "outcomes_differ": "The matching rules do not say the same thing.",
    "customer_disputes": "The question disputes the entitlement. A person decides.",
    "rule_marked_ambiguous": "The approved rule is marked ambiguous.",
    "rule_marked_disputed": "The approved rule is marked disputed.",
    "rule_not_in_force": "The rule is not yet in force.",
    "rule_overdue": "The rule is past its review date.",
    "rule_stale": "The rule is outside the review window.",
    "rule_date_invalid": "A date on the rule could not be read.",
    "contract_stale": "The plan is outside the review window.",
    "contract_not_current": "The plan is not marked current.",
    "contract_date_invalid": "The plan review date could not be read.",
    "clause_missing": "The rule names a clause that is not on the plan.",
    "clause_not_current": "The clause is not marked current.",
    "clause_contains_instruction": "The clause contains an instruction and is not used as an explanation.",
    "span_does_not_support": "The clause does not contain the words the rule relies on.",
    "clause_conflicts_with_rule": "The clause and the rule do not say the same thing.",
    "conditional_rule": "The rule is conditional. A person has to apply it.",
    "rule_wording_rejected": "The approved plain-English sentence did not pass the screen.",
}


def _flags() -> dict[str, bool]:
    return {
        "entitlement_granted": False,
        "entitlement_refused": False,
        "entitlement_changed": False,
        "message_sent": False,
        "record_written": False,
        "unfair_term_found": False,
        "section_69_applied": False,
        "consumer_understanding_met": False,
        "section_49_met": False,
        "significant_decision_taken": False,
        "payment_taken": False,
        "exclusion_waived": False,
    }


def _strip_prohibited(node: Any, path: str = "") -> tuple[Any, list[str]]:
    ignored: list[str] = []
    if isinstance(node, dict):
        copied: dict[str, Any] = {}
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if key in PROHIBITED_KEYS:
                ignored.append(here)
                continue
            child, nested = _strip_prohibited(value, here)
            copied[key] = child
            ignored.extend(nested)
        return copied, ignored
    if isinstance(node, list):
        copied_list = []
        for index, value in enumerate(node):
            child, nested = _strip_prohibited(value, f"{path}[{index}]")
            copied_list.append(child)
            ignored.extend(nested)
        return copied_list, ignored
    return node, ignored


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _freshness(as_of: date, raw: Any, stale_after_days: int) -> str:
    parsed = _parse_date(raw)
    if parsed is None:
        return "invalid"
    age = (as_of - parsed).days
    if age < 0:
        return "future"
    if age > stale_after_days:
        return "stale"
    return "current"


def _shell(sector: str | None) -> dict[str, Any]:
    organisation = "a synthetic service organisation"
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A0",
        "organisation": organisation,
        "sector": sector if sector in SECTORS else None,
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "question_echoed": False,
        "decision": None,
        "outcome": "route_to_human",
        "coverage_stated": False,
        "position": None,
        "uncertainty": {"level": "high", "reasons": []},
        "explanation": {"text": ""},
        "citation": None,
        "rules_relied_on": [],
        "rules_seen": [],
        "human_route": {
            "offered": True,
            "queue": "entitlement-owner",
            "phone": PHONE,
            "phone_is_live": False,
            "non_digital_counter": True,
            "reason": "offered_on_every_explanation",
        },
        "prompt_injection": {
            "detected": False,
            "signals": [],
            "hidden_signals": [],
            "followed": False,
            "matching_text_kept_surrounding_words": True,
        },
        "flags": _flags(),
        "ai_disclosure": (
            "This explanation was prepared by an automated assistant. "
            "It is not a decision about an entitlement. A person is available, including at a counter."
        ),
        "citation_check": {
            "experiment_38_normalise": False,
            "experiment_38_id": "exp-38-policy-wording-comparison",
            "experiment_40_imported": False,
        },
        "ignored_fields": [],
        "regulatory": {},
    }


def _regulatory(source_view: dict, sector: str | None) -> dict[str, Any]:
    prin = next(row for row in source_view["pins"] if row["id"] == "prin-2a-5")
    return {
        "cra_sections_opened": ["49", "50", "52", "54", "57", "62", "64", "68", "69"],
        "sections_not_opened": ["51", "55", "56"],
        "schedule_2_opened": False,
        "article_6_opened": False,
        "articles_13_and_14_opened": False,
        "article_22_reopened": False,
        "section_80_opened": False,
        "unfair_term_found": False,
        "section_69_applied": False,
        "section_49_met": False,
        "significant_decision_taken": False,
        "consumer_understanding": {
            "relevant": sector == "financial_services",
            "rule": "PRIN 2A.5",
            "verified_on_this_open": prin["verified"],
            "met": False,
            "note": "Unverified on 10 November 2026. The handbook page did not return rule text.",
        },
        "sources": source_view,
    }


def _finish_route(document: dict, reason: str, extra: list[str] | None = None) -> dict:
    reasons = [reason]
    for item in extra or []:
        if item not in reasons:
            reasons.append(item)
    document["outcome"] = "route_to_human"
    document["coverage_stated"] = False
    document["position"] = None
    document["decision"] = None
    document["rules_relied_on"] = []
    document["uncertainty"] = {"level": "high", "reasons": reasons}
    document["human_route"]["offered"] = True
    document["human_route"]["reason"] = reason
    sentence = _ROUTE_SENTENCE.get(reason, "A person has to decide.")
    document["explanation"] = {
        "text": (
            "A person has to decide this entitlement. This explanation does not say "
            "whether the plan includes it. "
            f"Uncertainty is high: {sentence} "
            "This explanation does not grant, refuse, or change the entitlement."
        )
    }
    return document


def _clause_map(contract: dict) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for clause in contract.get("clauses") or []:
        if isinstance(clause, dict) and isinstance(clause.get("clause_ref"), str):
            found[clause["clause_ref"]] = clause
    return found


def _matched_rules(rules: list, folded_question: str) -> list[dict]:
    matched = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        for phrase in rule.get("phrases") or []:
            if not isinstance(phrase, str) or not phrase.strip():
                continue
            if normalise(phrase) in folded_question:
                matched.append(rule)
                break
    return matched


def _plain_ok(text: Any) -> bool:
    if not isinstance(text, str) or not text.startswith("The approved table says "):
        return False
    folded = text.casefold()
    return not any(banned in folded for banned in _BANNED_PLAIN)


def explain(request: dict, as_of: str, stale_after_days: int = STALE_AFTER_DAYS) -> dict:
    """Return one explanation. The same inputs return the same JSON."""
    if not isinstance(request, dict):
        raise TypeError("request must be an object")
    cleaned, ignored = _strip_prohibited(copy.deepcopy(request))
    sector = cleaned.get("sector") if isinstance(cleaned.get("sector"), str) else None
    document = _shell(sector)
    document["ignored_fields"] = ignored
    as_of_date = _parse_date(as_of)
    source_view = assess(as_of_date, stale_after_days, sector if sector in SECTORS else None)
    document["regulatory"] = _regulatory(source_view, sector if sector in SECTORS else None)

    organisation = cleaned.get("organisation")
    if isinstance(organisation, str) and organisation in ALLOWED_ORGS:
        document["organisation"] = organisation

    customer_ref = cleaned.get("customer_reference")
    if isinstance(customer_ref, str) and CUSTOMER_REF.fullmatch(customer_ref):
        document["customer_reference"] = customer_ref

    if cleaned.get("synthetic") is not True:
        document["outcome"] = "refused_not_synthetic"
        document["uncertainty"] = {"level": "high", "reasons": ["not_synthetic"]}
        document["human_route"]["reason"] = "not_synthetic"
        document["explanation"] = {
            "text": (
                "This starter only reads a synthetic plan. The question was not copied. "
                "A person has to look at the organisation's own record. "
                "This explanation does not grant, refuse, or change the entitlement."
            )
        }
        return document

    if as_of_date is None:
        return _finish_route(document, "as_of_invalid")

    question = cleaned.get("question")
    if not isinstance(question, str) or not question.strip():
        return _finish_route(document, "question_missing")
    if len(question) > QUESTION_LIMIT:
        return _finish_route(document, "question_too_long")

    visible, hidden = hidden_and_visible(question)
    hidden_signals: list[str] = []
    for body in hidden:
        for name in signals_in(body):
            if name not in hidden_signals:
                hidden_signals.append(name)
    visible_signals = signals_in(visible)
    signals = list(visible_signals)
    for name in hidden_signals:
        if name not in signals:
            signals.append(name)
    matching_text = strip_instruction_spans(visible)
    document["prompt_injection"] = {
        "detected": bool(signals),
        "signals": signals,
        "hidden_signals": hidden_signals,
        "followed": False,
        "matching_text_kept_surrounding_words": True,
    }

    if sector not in SECTORS:
        return _finish_route(document, "sector_missing" if sector is None else "sector_not_recognised")

    table = cleaned.get("rules_table")
    if not isinstance(table, dict):
        return _finish_route(document, "table_missing")
    if table.get("status") != "approved":
        return _finish_route(document, "table_not_approved")
    table_fresh = _freshness(as_of_date, table.get("approved_on"), stale_after_days)
    if table_fresh == "invalid":
        return _finish_route(document, "table_date_invalid")
    if table_fresh != "current":
        return _finish_route(document, "table_stale")

    contract = cleaned.get("contract") if isinstance(cleaned.get("contract"), dict) else {}
    document["citation_check"]["experiment_38_normalise"] = True
    folded_question = normalise(matching_text) if matching_text else ""
    rules = [rule for rule in (table.get("rules") or []) if isinstance(rule, dict)]
    matched = _matched_rules(rules, folded_question) if folded_question else []
    document["rules_seen"] = [rule.get("rule_id") for rule in matched if isinstance(rule.get("rule_id"), str)]

    if not matched:
        extra = ["instruction_not_followed"] if signals else []
        return _finish_route(document, "no_matching_rule", extra)

    if len(matched) > 1:
        outcomes = {rule.get("outcome_on_table") for rule in matched}
        extra = ["outcomes_differ"] if len(outcomes) > 1 else []
        if signals:
            extra.append("instruction_not_followed")
        return _finish_route(document, "multiple_rules", extra)

    rule = matched[0]
    extra: list[str] = []
    if signals:
        extra.append("instruction_not_followed")
    if dispute_codes(matching_text):
        return _finish_route(document, "customer_disputes", extra)
    if rule.get("disputed") is True or rule.get("status") == "disputed":
        return _finish_route(document, "rule_marked_disputed", extra)
    if rule.get("ambiguous") is True:
        return _finish_route(document, "rule_marked_ambiguous", extra)
    if rule.get("status") != "approved":
        return _finish_route(document, "table_not_approved", extra)

    effective = _parse_date(rule.get("effective_on"))
    review_due = _parse_date(rule.get("review_due_on"))
    if effective is None or review_due is None:
        return _finish_route(document, "rule_date_invalid", extra)
    if effective > as_of_date:
        return _finish_route(document, "rule_not_in_force", extra)
    if review_due < as_of_date:
        return _finish_route(document, "rule_overdue", extra)
    approved_fresh = _freshness(as_of_date, rule.get("approved_on"), stale_after_days)
    if approved_fresh == "invalid":
        return _finish_route(document, "rule_date_invalid", extra)
    if approved_fresh != "current":
        return _finish_route(document, "rule_stale", extra)

    if contract.get("status") != "current":
        return _finish_route(document, "contract_not_current", extra)
    contract_fresh = _freshness(as_of_date, contract.get("reviewed_on"), stale_after_days)
    if contract_fresh == "invalid":
        return _finish_route(document, "contract_date_invalid", extra)
    if contract_fresh != "current":
        return _finish_route(document, "contract_stale", extra)

    clause_ref = rule.get("clause_ref")
    clause = _clause_map(contract).get(clause_ref) if isinstance(clause_ref, str) else None
    if clause is None:
        return _finish_route(document, "clause_missing", extra)
    clause_text = clause.get("text") if isinstance(clause.get("text"), str) else ""
    if signals_in(clause_text):
        document["citation"] = {
            "clause_ref": clause_ref,
            "text": clause_text,
            "supported": False,
            "untrusted_instruction": True,
            "experiment_38_normalise": True,
        }
        return _finish_route(document, "clause_contains_instruction", extra)
    if clause.get("status") != "current":
        return _finish_route(document, "clause_not_current", extra)

    supported = False
    support_phrase = rule.get("support_phrase")
    if isinstance(support_phrase, str) and support_phrase.strip():
        supported = normalise(support_phrase) in normalise(clause_text)
    if not supported:
        document["citation"] = {
            "clause_ref": clause_ref,
            "text": clause_text,
            "supported": False,
            "untrusted_instruction": False,
            "experiment_38_normalise": True,
        }
        return _finish_route(document, "span_does_not_support", extra)

    conflict = False
    for marker in rule.get("conflict_if_clause_contains") or []:
        if isinstance(marker, str) and marker.strip() and normalise(marker) in normalise(clause_text):
            conflict = True
            break
    if conflict:
        document["citation"] = {
            "clause_ref": clause_ref,
            "text": clause_text,
            "supported": True,
            "untrusted_instruction": False,
            "experiment_38_normalise": True,
        }
        return _finish_route(document, "clause_conflicts_with_rule", extra)

    outcome_on_table = rule.get("outcome_on_table")
    if outcome_on_table == "conditional":
        return _finish_route(document, "conditional_rule", extra)
    if outcome_on_table not in {"included", "not_included"}:
        return _finish_route(document, "rule_marked_ambiguous", extra)
    if not _plain_ok(rule.get("plain_english")):
        return _finish_route(document, "rule_wording_rejected", extra)

    reasons = ["one_approved_rule", "clause_supports_rule", "no_conflict"]
    level = "low"
    if source_view["any_relevant_source_stale"]:
        level = "medium"
        reasons.append("sources_stale")
    if source_view["relevant_sources_unreliable"]:
        level = "medium"
        reasons.append("sources_unverified")
    if signals:
        level = "medium"
        reasons.append("instruction_not_followed")

    uncertainty_word = "low" if level == "low" else "medium"
    note = ""
    if "sources_stale" in reasons or "sources_unverified" in reasons:
        note = " Do not rely on a legal note that is stale or unverified."
    if signals:
        note += " An instruction in the question was not followed."
    rule_id = rule.get("rule_id") if isinstance(rule.get("rule_id"), str) else ""
    document["outcome"] = "explained"
    document["coverage_stated"] = True
    document["position"] = outcome_on_table
    document["decision"] = None
    document["rules_relied_on"] = [rule_id] if rule_id else []
    document["uncertainty"] = {"level": level, "reasons": reasons}
    document["human_route"]["reason"] = "offered_on_every_explanation"
    document["citation"] = {
        "clause_ref": clause_ref,
        "text": clause_text,
        "supported": True,
        "untrusted_instruction": False,
        "experiment_38_normalise": True,
    }
    document["explanation"] = {
        "text": (
            f"{rule['plain_english']} "
            f"The clause relied on is {clause_ref}: \"{clause_text}\" "
            f"Uncertainty is {uncertainty_word}: one approved rule, and the clause contains "
            "the words the rule relies on. "
            "This explanation does not grant, refuse, or change the entitlement. "
            "A person can decide if the customer disagrees."
            f"{note}"
        )
    }
    return document


def record_decision(draft: dict, review: dict) -> dict:
    """Record an entitlement owner's code. Do not apply it to a record."""
    if not isinstance(draft, dict):
        raise TypeError("draft must be an object")
    updated = copy.deepcopy(draft)
    updated["flags"] = _flags()
    updated["decision"] = None
    updated["actions_taken"] = []
    updated["executed"] = False
    if not isinstance(review, dict):
        updated["review"] = {"refused": True, "reason": "review_missing"}
        updated["human_approval"] = None
        return updated
    decision = review.get("decision")
    if decision not in ALLOWED_DECISIONS:
        updated["review"] = {"refused": True, "reason": "prohibited_decision"}
        updated["human_approval"] = None
        return updated
    actor_id = review.get("actor_id")
    if review.get("actor") != "entitlement_owner" or not isinstance(actor_id, str) or not ACTOR_ID.fullmatch(actor_id):
        updated["review"] = {"refused": True, "reason": "actor_not_accepted"}
        updated["human_approval"] = None
        return updated
    if any(key in review for key in ("email", "recipient", "message", "entitlement_record")):
        updated["review"] = {"refused": True, "reason": "prohibited_decision"}
        updated["human_approval"] = None
        return updated
    updated["human_approval"] = {
        "approver": "entitlement_owner",
        "actor_id": actor_id,
        "decision": decision,
        "applied_to_entitlement_record": False,
        "agent_decided": False,
    }
    updated["review"] = {"refused": False, "reason": "recorded"}
    return updated


def grant_entitlement(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("grant_entitlement is not a tool of this agent")


def refuse_entitlement(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("refuse_entitlement is not a tool of this agent")


def change_entitlement(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("change_entitlement is not a tool of this agent")


def waive_exclusion(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("waive_exclusion is not a tool of this agent")


def send_message(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("send_message is not a tool of this agent")


def write_record(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("write_record is not a tool of this agent")


def apply_section_69(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("apply_section_69 is not a tool of this agent")


def find_unfair_term(*_args: Any, **_kwargs: Any) -> None:
    raise EntitlementForbidden("find_unfair_term is not a tool of this agent")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Explain one synthetic entitlement. Do not decide it.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    path = Path(args.input)
    try:
        request = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    if not isinstance(request, dict):
        return 2
    document = explain(request, args.as_of)
    json.dump(document, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
