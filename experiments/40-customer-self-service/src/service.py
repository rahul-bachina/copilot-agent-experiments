"""Draft one customer reply from the synthetic knowledge base.

The same enquiry and the same as-of date produce the same JSON. Nothing is
written to an account, nothing is sent, and a complaint is not closed.

Confirmation follows the shape of Experiment 21: a separate review object,
and a recorded confirmation does not perform the action. The warm handover
follows Experiment 13: a human route is always offered, and vulnerability
goes to a person before any account draft. Financial-services complaint and
vulnerability gates follow Experiment 02: analyse() may be called, the
customer is not labelled vulnerable, and the complaint is not closed. This
folder does not calculate a DISP clock. Correspondence approval follows
Experiment 09: a handler may approve a draft for their own channel, and
the agent still does not send. Experiments 13, 21, and 09 are not imported.
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

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from catalogue import (  # noqa: E402
        ORGANISATION,
        PROHIBITED_PRIORITY,
        STALE_AFTER_DAYS,
        age_days,
        is_stale,
        match_articles,
    )
    from identity import ENQUIRY_ID, HANDLER_ID, assess_identity  # noqa: E402
    from injection import signals_in, stop_signals, strip_instruction_sentences  # noqa: E402
    from sources import source_rows  # noqa: E402
else:
    from .catalogue import (
        ORGANISATION,
        PROHIBITED_PRIORITY,
        STALE_AFTER_DAYS,
        age_days,
        is_stale,
        match_articles,
    )
    from .identity import ENQUIRY_ID, HANDLER_ID, assess_identity
    from .injection import signals_in, stop_signals, strip_instruction_sentences
    from .sources import source_rows

LABEL = "DRAFT FOR CUSTOMER SERVICE REVIEW"
CALLER = "exp-40-customer-self-service"
PHONE = "01632 960040"
ALLOWED_POSTCODE = "SYN 1AA"
APPOINTMENT_SLOTS = frozenset({"morning", "afternoon"})
APPOINTMENT_PLACES = frozenset({"mereford-counter", "phone-callback"})
MAX_TEXT = 4000

AI_DISCLOSURE = (
    "This response has been written by an automated AI chatbot. "
    "It is not a member of staff. You can ask for a person."
)
HUMAN_ROUTE_SENTENCE = (
    f"You can ask for a person on {PHONE}, which is an invented number and not a live service, "
    "or at the weekday counter from 09:00 to 16:00."
)
ACCESS_SENTENCE = (
    "You can ask for this information in another format. A person arranges that. "
    "This starter does not decide that a reasonable adjustment has been made."
)
OFGEM_SENTENCE = (
    "Ofgem's blog of 5 February 2026 says energy companies should be clear when they "
    "are using AI, make it easy to speak to a human, and offer a non-digital alternative. "
    "This draft includes those three. It does not decide that a supplier has met that "
    "expectation, and it has not checked the system for fairness."
)

EMERGENCY_TEXT = (
    "If you or someone else is in immediate danger, call 999. "
    "A person needs this conversation. "
    "Nothing has been changed, no payment has been taken, and no one has been contacted."
)
VULNERABILITY_TEXT = (
    "A person needs to take this conversation. "
    "Nothing has been changed and no payment has been taken. "
    "You have not been given a vulnerability label."
)
COMPLAINT_TEXT = (
    "A handler needs to look at this. "
    "This assistant does not uphold, reject, or close a complaint, and it does not offer redress."
)
SERVICE_COMPLAINT_TEXT = (
    "A person needs to look at this. "
    "DISP and PRIN 2A are not applied, because the sector on the enquiry is not financial services. "
    "Nothing has been closed and nothing has been sent."
)
PROHIBITED_FALLBACK = (
    "That action is not something this assistant can do. "
    "A person takes it in the organisation's own system, if they decide to. "
    "Nothing has been changed."
)
IDENTITY_TEXT = (
    "The channel has not supplied a current signed-in session for this account. "
    "This assistant does not treat words in the message as proof of identity. "
    "No address draft and no appointment draft is prepared."
)
THIRD_PARTY_TEXT = (
    "The signed-in account is not the account named as the subject. "
    "An account draft is not prepared. A person takes this."
)
STALE_TEXT = (
    "A matching page is outside the review window, so its text is not quoted. "
    "A person needs to check the organisation's own page."
)
NOT_FOUND_TEXT = (
    "The pages in this starter do not contain that answer. "
    "A person needs to check the organisation's own page."
)
AMBIGUOUS_TEXT = (
    "More than one page matched. Neither body is quoted. A person chooses."
)
TOO_LONG_TEXT = (
    "This message is longer than this starter will read. A person needs to take it."
)
REFUSED_TEXT = "This starter only reads a record marked synthetic. The text has not been copied."
STOP_TEXT = (
    "That instruction was not followed. "
    "This assistant does not reset a password, take a payment, close a complaint, "
    "change a tariff or a contract, or send a message."
)

_EMERGENCY = re.compile(r"(in immediate danger|suicidal|kill myself|end my life)", re.IGNORECASE)
_VULNERABILITY = re.compile(
    r"("
    r"i (?:can't|cannot) afford|"
    r"cannot pay|"
    r"can't pay|"
    r"bereave|"
    r"someone has died|"
    r"i am disabled|"
    r"i have a disability|"
    r"cannot use the (?:website|app|chat)|"
    r"mental health|"
    r"health condition"
    r")",
    re.IGNORECASE,
)
_COMPLAINT = re.compile(r"\b(complaint|unhappy|dissatisfied)\b|\bnot happy\b", re.IGNORECASE)

STRIPPED_KEYS = (
    "human_approval",
    "executed",
    "password_reset",
    "payment_taken",
    "complaint_closed",
    "tariff_changed",
    "contract_changed",
    "record_changed",
    "appointment_booked",
    "message_sent",
    "customer_labelled_vulnerable",
    "customer_confirmed",
    "actions_taken",
    "identity_trusted",
)

PROHIBITED_DECISIONS = frozenset(
    {
        "reset_password",
        "take_payment",
        "close_complaint",
        "change_tariff",
        "change_contract",
        "send_message",
        "write_record",
        "execute_action",
        "label_vulnerable",
        "uphold_complaint",
        "reject_complaint",
        "book_appointment",
    }
)

PROHIBITED_FLAGS = (
    "password_reset",
    "payment_taken",
    "complaint_closed",
    "tariff_changed",
    "contract_changed",
    "record_changed",
    "appointment_booked",
    "message_sent",
    "customer_labelled_vulnerable",
    "secrets_collected",
    "stale_article_quoted",
)

CUSTOMER_CONFIRM = frozenset(
    {"customer_confirm_address_draft", "customer_confirm_appointment_draft"}
)
REVIEW_KEYS = frozenset({"decision", "actor", "actor_id", "recipient_role"})
ACCOUNT_OUTCOMES = frozenset({"account_action_proposed"})

_propose = None
_analyse = None


class ServiceForbidden(RuntimeError):
    """No password reset, payment, closure, tariff or contract change, write, or send."""


def reset_password(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not reset a password")


def take_payment(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not take a payment")


def close_complaint(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not close a complaint")


def change_tariff(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not change a tariff")


def change_contract(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not change a contract")


def send_message(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not send a message")


def write_record(*_args, **_kwargs) -> None:
    raise ServiceForbidden("the agent does not change a record")


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


def _load_analyse():
    intake_path = (
        Path(__file__).resolve().parents[2]
        / "02-consumer-duty-complaint-intake"
        / "src"
        / "intake.py"
    )
    if not intake_path.is_file():
        raise RuntimeError(
            "Experiment 02 is required at experiments/02-consumer-duty-complaint-intake. "
            "This starter does not carry its own copy."
        )
    src = str(intake_path.parent)
    if src not in sys.path:
        sys.path.insert(0, src)
    spec = importlib.util.spec_from_file_location("exp02_intake_for_exp40", intake_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Experiment 02 intake.py could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.analyse


def _gateway():
    global _propose
    if _propose is None:
        _propose = _load_propose()
    return _propose


def _analyser():
    global _analyse
    if _analyse is None:
        _analyse = _load_analyse()
    return _analyse


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _flags() -> dict:
    return {key: False for key in PROHIBITED_FLAGS + (
        "customer_confirmed",
        "handler_accepted_handover",
        "handler_approved_own_send",
    )}


def _enquiry_label(enquiry: dict) -> str:
    enquiry_id = enquiry.get("enquiry_id")
    if isinstance(enquiry_id, str) and ENQUIRY_ID.match(enquiry_id):
        return enquiry_id
    return "not-a-synthetic-id"


def _redact(text: str) -> dict:
    proposal = _gateway()(
        text,
        caller=CALLER,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] or proposal["release"]["agent_may_release"]:
        raise ServiceForbidden("Experiment 08 must not be treated as anonymisation or a release")
    findings = proposal["audit_log"]["findings"]
    return {
        "called": True,
        "experiment": "08-uk-pii-redaction-gateway",
        "catalogue_id": "O005",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "reversible": False,
        "model_suggestions_applied": False,
        "finding_count": len(findings),
        "entity_types": sorted({row["entity_type"] for row in findings}),
        "input_sha256": proposal["audit_log"]["input_sha256"],
        "rules_pinned_on": proposal["audit_log"]["rules_pinned_on"],
        "raw_values_logged": False,
        "redacted_text_copied": False,
    }


def _human_route(queue: str) -> dict:
    return {
        "offered": True,
        "ask_for_a_person": True,
        "phone": PHONE,
        "phone_is_live": False,
        "non_digital": "Weekday counter at the invented Mereford office, 09:00 to 16:00.",
        "queue": queue,
        "pattern": "Experiment 13 warm handover. This starter does not import that code.",
    }


def _customer_text(core: str, sector: str) -> str:
    parts = [core, AI_DISCLOSURE, HUMAN_ROUTE_SENTENCE, ACCESS_SENTENCE]
    if sector == "energy_retail":
        parts.append(OFGEM_SENTENCE)
    return " ".join(parts)


def _regulatory(sector: str, *, financial: bool) -> dict:
    return {
        "lawful_basis_asserted": False,
        "article_6_opened_on_2026_11_06": False,
        "article_9_opened_on_2026_11_06": False,
        "significant_decision_taken": False,
        "article_22a": (
            "Article 22A(1), opened 6 November 2026, defines a solely automated "
            "decision and a significant decision. This starter does not take one."
        ),
        "article_22c_safeguards_decided": False,
        "article_22d_regulations_read": False,
        "ofgem": {
            "scenario_is_energy_retail": sector == "energy_retail",
            "blog_opened": "2026-11-06",
            "blog_date": "2026-02-05",
            "ai_disclosure_included": True,
            "human_route_included": True,
            "non_digital_route_included": True,
            "fairness_monitoring_done": False,
            "licence_condition_verified": False,
            "may_2026_ethical_ai_document_opened": False,
        },
        "consumer_duty": {
            "applied": financial,
            "prin_2a_1_opened": "2026-11-06" if financial else None,
            "prin_2a_2_quoted": False,
            "disp_clock_calculated": False,
            "disp_reopened_on_2026_11_06": False,
            "fg22_5_opened": False,
            "fg21_1_opened": False,
            "breach_found": False,
        },
        "equality_act": {
            "section_20_6_opened": "2026-11-06",
            "section_29_7_opened": "2026-11-06",
            "section_149_noted": sector == "public_service",
            "accessible_format_offered": True,
            "duty_met": False,
            "due_regard_assessed": False,
        },
    }


def _empty_intake() -> dict:
    return {
        "called": False,
        "experiment": "02-consumer-duty-complaint-intake",
        "catalogue_id": "C006",
        "function": None,
        "reason": "not_a_financial_services_complaint_or_vulnerability",
        "customer_labelled_vulnerable": False,
        "breach_found": False,
        "complaint_closed": False,
        "clock_calculated": False,
        "handler_must_confirm": False,
    }


def _call_analyse(text: str) -> dict:
    view = _analyser()(text)
    drivers = []
    for flag in view.get("flags") or []:
        driver = flag.get("driver")
        if isinstance(driver, str):
            drivers.append(driver)
    return {
        "called": True,
        "experiment": "02-consumer-duty-complaint-intake",
        "catalogue_id": "C006",
        "function": "analyse",
        "meets_disp_suggestion": bool(view.get("meets")),
        "severity_suggestion": view.get("severity"),
        "product_suggestion": view.get("product"),
        "cause_suggestion": view.get("cause"),
        "vulnerability_drivers": drivers,
        "evidence_quotes_copied": False,
        "customer_labelled_vulnerable": False,
        "breach_found": False,
        "complaint_closed": False,
        "clock_calculated": False,
        "handler_must_confirm": True,
        "note": (
            "Experiment 02 analyse() is a suggestion for a handler. "
            "It is not a finding that the Consumer Duty was breached. "
            "The DISP clock was not calculated. DISP was not re-opened on 6 November 2026."
        ),
    }


def _structured(enquiry: dict, kind: str | None, as_of: date) -> dict:
    raw = enquiry.get("structured") if isinstance(enquiry.get("structured"), dict) else {}
    closed: dict = {}
    if kind == "address_update_draft" and raw.get("postcode") == ALLOWED_POSTCODE:
        closed["postcode"] = ALLOWED_POSTCODE
    if kind == "appointment_request_draft":
        slot = raw.get("appointment_slot")
        place = raw.get("appointment_place")
        when = raw.get("appointment_date")
        parsed = None
        if isinstance(when, str):
            try:
                parsed = date.fromisoformat(when)
            except ValueError:
                parsed = None
        if slot in APPOINTMENT_SLOTS:
            closed["appointment_slot"] = slot
        if place in APPOINTMENT_PLACES:
            closed["appointment_place"] = place
        if parsed is not None and parsed > as_of:
            closed["appointment_date"] = when
    if kind == "address_update_draft":
        complete = closed.get("postcode") == ALLOWED_POSTCODE
    elif kind == "appointment_request_draft":
        complete = all(key in closed for key in ("appointment_date", "appointment_slot", "appointment_place"))
    else:
        complete = False
    return {"complete": complete, "closed": closed, "values_invented": False}


def _prepare(matched: list[dict], as_of: date, sources_stale: bool) -> list[dict]:
    prepared = []
    for article in matched:
        row = dict(article)
        row["stale"] = sources_stale or is_stale(article["last_reviewed"], as_of)
        prepared.append(row)
    return prepared


def _choose(prepared: list[dict], identity: dict, complaint: bool, vulnerability: bool, emergency: bool, sector: str):
    if emergency:
        return "emergency_handover", None, False
    if vulnerability:
        return "vulnerability_handover", None, False
    current = [article for article in prepared if not article["stale"]]
    stale = [article for article in prepared if article["stale"]]
    prohibited = [article for article in current if article["article_class"] == "prohibited"]
    if prohibited:
        prohibited.sort(key=lambda article: PROHIBITED_PRIORITY.index(article["prohibited_kind"]))
        return f"prohibited_{prohibited[0]['prohibited_kind']}", prohibited[0], True
    if complaint and sector == "financial_services":
        policy = next((article for article in current if article["article_class"] == "complaint"), None)
        return "financial_complaint_handover", policy, policy is not None
    if complaint:
        return "service_complaint_handover", None, False
    if not prepared:
        return "no_article", None, False
    if not current:
        return "stale_article", stale[0], False
    if len(current) != 1:
        return "ambiguous", None, False
    article = current[0]
    if article["article_class"] == "account_action":
        if identity["third_party"]:
            return "third_party_handover", article, False
        if not identity["trusted"]:
            return "identity_not_verified", article, False
        return "account_action_proposed", article, True
    if article["article_class"] == "complaint":
        return "financial_complaint_handover", article, True
    return "knowledge_answer", article, True


def _core_text(outcome: str, article: dict | None, body_quoted: bool) -> str:
    if body_quoted and article is not None:
        return article["body"]
    fixed = {
        "emergency_handover": EMERGENCY_TEXT,
        "vulnerability_handover": VULNERABILITY_TEXT,
        "financial_complaint_handover": COMPLAINT_TEXT,
        "service_complaint_handover": SERVICE_COMPLAINT_TEXT,
        "identity_not_verified": IDENTITY_TEXT,
        "third_party_handover": THIRD_PARTY_TEXT,
        "stale_article": STALE_TEXT,
        "no_article": NOT_FOUND_TEXT,
        "ambiguous": AMBIGUOUS_TEXT,
        "too_long": TOO_LONG_TEXT,
        "refused_not_synthetic": REFUSED_TEXT,
        "instruction_not_followed": STOP_TEXT,
    }
    if outcome in fixed:
        return fixed[outcome]
    if outcome.startswith("prohibited_"):
        return PROHIBITED_FALLBACK
    return NOT_FOUND_TEXT


def _queue(outcome: str) -> str:
    if outcome in {"emergency_handover", "vulnerability_handover"}:
        return "vulnerability"
    if outcome in {"financial_complaint_handover", "service_complaint_handover"}:
        return "complaint"
    if outcome == "account_action_proposed":
        return "account_action"
    if outcome.startswith("prohibited_") or outcome == "instruction_not_followed":
        return "prohibited"
    return "general"


def _next_steps(outcome: str) -> list[str]:
    steps = [
        "You can ask for a person. The phone number in this draft is invented.",
        "You can ask for the information in another format. A person arranges that.",
    ]
    if outcome == "knowledge_answer":
        steps.insert(0, "Use the quoted page. It is an explanation of a next step, not a change to the account.")
    elif outcome == "account_action_proposed":
        steps.insert(
            0,
            "A draft is prepared. Confirming it in a separate review does not change the record and does not send a message.",
        )
    elif outcome.startswith("prohibited_") or outcome == "instruction_not_followed":
        steps.insert(0, "A person does this in the organisation's own system, if they decide to. This draft has not done it.")
    elif outcome in {"financial_complaint_handover", "service_complaint_handover"}:
        steps.insert(0, "A handler reads the complaint. This draft has not closed it.")
    elif outcome == "emergency_handover":
        steps.insert(0, "If you are in immediate danger, call 999.")
    else:
        steps.insert(0, "A person checks the organisation's own page or system.")
    return steps


def _article_view(article: dict | None, body_quoted: bool) -> dict | None:
    if article is None:
        return None
    return {
        "id": article["id"],
        "title": article["title"],
        "class": article["article_class"],
        "sector": article["sector"],
        "last_reviewed": article["last_reviewed"],
        "stale": article["stale"],
        "body_quoted": body_quoted,
        "body": article["body"] if body_quoted else None,
        "citation": f"{article['id']}, last reviewed {article['last_reviewed']}",
    }


def _correspondence(outcome: str, article: dict | None, fields: dict, account_ref: str | None) -> dict | None:
    if outcome != "account_action_proposed" or article is None:
        return None
    kind = article.get("action_kind")
    detail = ""
    if kind == "address_update_draft" and fields["closed"].get("postcode"):
        detail = f" Structured postcode: {fields['closed']['postcode']}."
    if kind == "appointment_request_draft" and fields["complete"]:
        closed = fields["closed"]
        detail = (
            f" Structured slot: {closed['appointment_date']} {closed['appointment_slot']} "
            f"at {closed['appointment_place']}."
        )
    return {
        "status": "draft_for_a_handler",
        "may_be_sent_by_agent": False,
        "pattern": "Experiment 09 correspondence approval. This starter does not import that code.",
        "text": (
            "DRAFT. Do not send. "
            f"A {kind} is proposed for account {account_ref or 'not-a-synthetic-id'}."
            f"{detail} The customer's free text is not copied. "
            "Customer confirmation does not change the record. "
            "A handler sends any outward message from their own channel, after a separate approval. "
            "Mereford Customer Service is fictional."
        ),
    }


def _proposed(article: dict | None, body_quoted: bool, fields: dict, outcome: str, identity: dict) -> dict | None:
    if outcome != "account_action_proposed" or article is None or not body_quoted:
        return None
    return {
        "kind": article.get("action_kind"),
        "executed": False,
        "record_changed": False,
        "appointment_booked": False,
        "customer_may_confirm": bool(fields["complete"] and identity["trusted"] and not identity["third_party"]),
        "fields_complete": fields["complete"],
        "fields": fields["closed"],
        "values_invented": False,
    }


def _base(enquiry: dict, as_of: str, sources: list[dict], sector: str) -> dict:
    any_source_stale = any(row["stale"] for row in sources)
    return {
        "label": LABEL,
        "experiment": "40-customer-self-service",
        "catalogue_id": "C001",
        "autonomy": "A1",
        "organisation": ORGANISATION,
        "model_called": False,
        "network_called": False,
        "executed": False,
        "actions_taken": [],
        "human_approval": None,
        "enquiry_id": _enquiry_label(enquiry),
        "enquiry_text_echoed": False,
        "sector": sector,
        "as_of": as_of,
        "stale_after_days": STALE_AFTER_DAYS,
        "rules_current": not any_source_stale,
        "any_source_stale": any_source_stale,
        "any_article_stale": False,
        "sources": sources,
        "ai_disclosure": AI_DISCLOSURE,
        "flags": _flags(),
    }


def _shell(enquiry: dict, as_of: str, sector: str) -> dict:
    as_of_date = _parse_as_of(as_of)
    sources = source_rows(as_of_date, STALE_AFTER_DAYS, age_days)
    draft = _base(enquiry if isinstance(enquiry, dict) else {}, as_of, sources, sector)
    draft["identity"] = {
        "trusted": False,
        "reason": "not_assessed",
        "third_party": False,
        "check_stale": False,
        "channel": "unknown",
        "sector": sector,
        "customer_is_subject": False,
        "account_ref": None,
    }
    draft["prompt_injection"] = {
        "detected": False,
        "signals": [],
        "followed": False,
        "stripped_keys": [],
    }
    draft["pii_gateway"] = {
        "called": False,
        "experiment": "08-uk-pii-redaction-gateway",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "redacted_text_copied": False,
        "finding_count": 0,
        "entity_types": [],
    }
    draft["complaint_gate"] = _empty_intake()
    draft["article"] = None
    draft["citations"] = []
    draft["proposed_action"] = None
    draft["correspondence_draft"] = None
    draft["human_route"] = _human_route("general")
    draft["regulatory"] = _regulatory(sector, financial=False)
    draft["next_steps"] = _next_steps("no_article")
    return draft


def _finish_text(draft: dict, core: str) -> None:
    draft["answer"] = {
        "text": _customer_text(core, draft["sector"]),
        "body_quoted": bool(draft["article"] and draft["article"]["body_quoted"]),
        "sufficient": bool(draft["article"] and draft["article"]["body_quoted"]),
    }


def _assert_safe(draft: dict) -> None:
    if draft["executed"] or draft["actions_taken"] or draft["human_approval"] is not None:
        raise ServiceForbidden("draft_reply must not execute or approve")
    if draft["enquiry_text_echoed"] or draft["model_called"] or draft["network_called"]:
        raise ServiceForbidden("draft_reply must not echo the enquiry or call out")
    for key in PROHIBITED_FLAGS:
        if draft["flags"][key]:
            raise ServiceForbidden(f"flag {key} must stay false")
    gateway = draft["pii_gateway"]
    if gateway.get("output_is_anonymised") or gateway.get("agent_may_release") or gateway.get("redacted_text_copied"):
        raise ServiceForbidden("the gateway result is not a release")
    if draft["human_route"]["offered"] is not True:
        raise ServiceForbidden("a human route is required")
    if "automated AI chatbot" not in draft["ai_disclosure"]:
        raise ServiceForbidden("the AI disclosure is required")
    action = draft.get("proposed_action")
    if action is not None and (action["executed"] or action["record_changed"] or action["appointment_booked"]):
        raise ServiceForbidden("a proposal must not execute")
    letter = draft.get("correspondence_draft")
    if letter is not None and letter["may_be_sent_by_agent"] is not False:
        raise ServiceForbidden("a correspondence draft must not be sendable by the agent")


def draft_reply(enquiry: dict, as_of: str, stale_after_days: int = STALE_AFTER_DAYS) -> dict:
    """Return a draft. human_approval is null. Nothing is executed."""

    if not isinstance(enquiry, dict):
        raise TypeError("enquiry must be a JSON object")
    as_of_date = _parse_as_of(as_of)
    if enquiry.get("synthetic") is not True:
        draft = _shell(enquiry, as_of, "unspecified")
        draft["outcome"] = "refused_not_synthetic"
        draft["identity"]["reason"] = "not_synthetic"
        _finish_text(draft, REFUSED_TEXT)
        draft["answer"]["body_quoted"] = False
        draft["answer"]["sufficient"] = False
        draft["next_steps"] = _next_steps("refused_not_synthetic")
        _assert_safe(draft)
        return draft

    cleaned = deepcopy(enquiry)
    stripped = [key for key in STRIPPED_KEYS if key in cleaned]
    for key in stripped:
        cleaned.pop(key, None)

    text = cleaned.get("text") if isinstance(cleaned.get("text"), str) else ""
    identity = assess_identity(cleaned, as_of)
    sector = identity["sector"]
    sources = source_rows(as_of_date, stale_after_days, age_days)
    sources_stale = any(row["stale"] for row in sources)
    draft = _base(cleaned, as_of, sources, sector)
    draft["identity"] = identity
    draft["rules_current"] = not sources_stale
    draft["any_source_stale"] = sources_stale

    if len(text) > MAX_TEXT:
        draft["prompt_injection"] = {"detected": False, "signals": [], "followed": False, "stripped_keys": stripped}
        draft["pii_gateway"] = {
            "called": False,
            "experiment": "08-uk-pii-redaction-gateway",
            "reason": "too_long",
            "output_is_anonymised": False,
            "agent_may_release": False,
            "redacted_text_copied": False,
            "finding_count": 0,
            "entity_types": [],
        }
        draft["complaint_gate"] = _empty_intake()
        draft["outcome"] = "too_long"
        draft["article"] = None
        draft["citations"] = []
        draft["proposed_action"] = None
        draft["correspondence_draft"] = None
        draft["human_route"] = _human_route("general")
        draft["regulatory"] = _regulatory(sector, financial=False)
        draft["next_steps"] = _next_steps("too_long")
        _finish_text(draft, TOO_LONG_TEXT)
        draft["answer"]["sufficient"] = False
        _assert_safe(draft)
        return draft

    signals = signals_in(text)
    stops = stop_signals(signals)
    matching_text = strip_instruction_sentences(text)
    emergency = bool(_EMERGENCY.search(matching_text))
    vulnerability = bool(_VULNERABILITY.search(matching_text))
    complaint = bool(_COMPLAINT.search(matching_text))
    matched = match_articles(matching_text, sector)
    prepared = _prepare(matched, as_of_date, sources_stale)
    draft["any_article_stale"] = any(article["stale"] for article in prepared)
    draft["prompt_injection"] = {
        "detected": bool(signals) or bool(stripped),
        "signals": signals,
        "followed": False,
        "stripped_keys": stripped,
    }
    draft["pii_gateway"] = _redact(text) if text else {
        "called": False,
        "experiment": "08-uk-pii-redaction-gateway",
        "reason": "no_free_text",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "redacted_text_copied": False,
        "finding_count": 0,
        "entity_types": [],
    }

    financial = sector == "financial_services" and (complaint or vulnerability) and not emergency and not stops
    if financial:
        draft["complaint_gate"] = _call_analyse(text)
    else:
        draft["complaint_gate"] = _empty_intake()
        if sector == "financial_services" and (complaint or vulnerability):
            draft["complaint_gate"]["reason"] = "stopped_before_analyse"

    if stops:
        outcome, primary, body_quoted = "instruction_not_followed", None, False
        citations = []
    else:
        outcome, primary, body_quoted = _choose(prepared, identity, complaint, vulnerability, emergency, sector)
        if outcome == "ambiguous":
            citations = [
                {"article_id": article["id"], "title": article["title"], "stale": article["stale"], "body_quoted": False}
                for article in prepared
                if not article["stale"]
            ]
            primary = None
        elif primary is None:
            citations = []
        else:
            citations = [
                {
                    "article_id": article["id"],
                    "title": article["title"],
                    "stale": article["stale"],
                    "body_quoted": article["id"] == primary["id"] and body_quoted,
                }
                for article in prepared
                if article["id"] == primary["id"] or article["stale"]
            ]
            if outcome == "stale_article":
                citations = [
                    {
                        "article_id": article["id"],
                        "title": article["title"],
                        "stale": True,
                        "body_quoted": False,
                    }
                    for article in prepared
                ]

    if any(row["body_quoted"] and row["stale"] for row in citations):
        raise ServiceForbidden("a stale article must not be quoted")

    fields = _structured(cleaned, None if primary is None else primary.get("action_kind"), as_of_date)
    draft["outcome"] = outcome
    draft["article"] = _article_view(primary, body_quoted)
    draft["citations"] = citations
    draft["proposed_action"] = _proposed(primary, body_quoted, fields, outcome, identity)
    draft["correspondence_draft"] = _correspondence(outcome, primary, fields, identity.get("account_ref"))
    draft["human_route"] = _human_route(_queue(outcome))
    draft["regulatory"] = _regulatory(sector, financial=financial)
    draft["next_steps"] = _next_steps(outcome)
    _finish_text(draft, _core_text(outcome, primary, body_quoted))
    if not body_quoted:
        draft["answer"]["sufficient"] = False
    draft["flags"]["stale_article_quoted"] = False
    _assert_safe(draft)
    return draft


def _review_refused(draft: dict, decision: str, reason: str) -> dict:
    updated = deepcopy(draft)
    updated["review"] = {
        "accepted": False,
        "refused": True,
        "reason": reason,
        "decision": decision,
        "executed": False,
    }
    updated["executed"] = False
    updated["actions_taken"] = []
    for key in PROHIBITED_FLAGS:
        updated["flags"][key] = False
    if updated.get("human_approval") is None:
        updated["flags"]["customer_confirmed"] = False
        updated["flags"]["handler_accepted_handover"] = False
        updated["flags"]["handler_approved_own_send"] = False
    if updated.get("proposed_action") is not None:
        updated["proposed_action"]["executed"] = False
        updated["proposed_action"]["record_changed"] = False
        updated["proposed_action"]["appointment_booked"] = False
    return updated


def _record_approval(draft: dict, review: dict, decision: str) -> dict:
    updated = deepcopy(draft)
    updated["human_approval"] = {
        "decision": decision,
        "actor": review.get("actor"),
        "actor_id": review.get("actor_id"),
        "executed": False,
        "record_changed": False,
        "message_sent": False,
        "complaint_closed": False,
    }
    updated["executed"] = False
    updated["actions_taken"] = []
    for key in PROHIBITED_FLAGS:
        updated["flags"][key] = False
    if updated.get("proposed_action") is not None:
        updated["proposed_action"]["executed"] = False
        updated["proposed_action"]["record_changed"] = False
        updated["proposed_action"]["appointment_booked"] = False
    if updated.get("correspondence_draft") is not None:
        updated["correspondence_draft"]["may_be_sent_by_agent"] = False
    updated["review"] = {
        "accepted": True,
        "refused": False,
        "reason": "recorded",
        "decision": decision,
        "executed": False,
    }
    return updated


def record_review(draft: dict, review: dict) -> dict:
    """Record a separate review. Confirmation does not change a record or send."""

    if not isinstance(draft, dict) or not isinstance(review, dict):
        raise TypeError("draft and review must be JSON objects")
    extra = set(review) - REVIEW_KEYS
    decision = review.get("decision")
    if not isinstance(decision, str):
        return _review_refused(draft, "", "decision_missing")
    if extra or ("recipient_role" in review and decision != "handler_approve_correspondence_for_own_send"):
        return _review_refused(draft, decision, "unexpected_review_fields")
    if decision in PROHIBITED_DECISIONS:
        return _review_refused(draft, decision, "prohibited_decision")
    if draft.get("outcome") == "refused_not_synthetic":
        return _review_refused(draft, decision, "not_synthetic")
    if draft.get("executed") is True or any(draft.get("flags", {}).get(key) for key in PROHIBITED_FLAGS):
        return _review_refused(draft, decision, "prohibited_flag")

    actor = review.get("actor")
    actor_id = review.get("actor_id")
    identity = draft.get("identity") or {}
    account_ref = identity.get("account_ref")
    proposed = draft.get("proposed_action") or {}
    prior = draft.get("human_approval")
    social = (draft.get("prompt_injection") or {}).get("followed") is True
    handler_ok = actor == "handler" and isinstance(actor_id, str) and HANDLER_ID.match(actor_id) is not None
    customer_ok = actor == "customer" and actor_id == account_ref and account_ref is not None

    if prior is not None and decision != "handler_approve_correspondence_for_own_send":
        return _review_refused(draft, decision, "already_reviewed")
    if (
        prior is not None
        and decision == "handler_approve_correspondence_for_own_send"
        and prior.get("decision") not in CUSTOMER_CONFIRM
    ):
        return _review_refused(draft, decision, "already_reviewed")

    allowed = False
    if decision == "customer_confirm_address_draft":
        allowed = (
            customer_ok
            and prior is None
            and draft.get("outcome") == "account_action_proposed"
            and proposed.get("kind") == "address_update_draft"
            and identity.get("trusted") is True
            and identity.get("customer_is_subject") is True
            and not identity.get("third_party")
            and not social
            and proposed.get("fields_complete") is True
            and proposed.get("customer_may_confirm") is True
            and proposed.get("executed") is False
        )
    elif decision == "customer_confirm_appointment_draft":
        allowed = (
            customer_ok
            and prior is None
            and draft.get("outcome") == "account_action_proposed"
            and proposed.get("kind") == "appointment_request_draft"
            and identity.get("trusted") is True
            and identity.get("customer_is_subject") is True
            and not identity.get("third_party")
            and not social
            and proposed.get("fields_complete") is True
            and proposed.get("customer_may_confirm") is True
            and proposed.get("executed") is False
        )
    elif decision == "handler_take_handover":
        allowed = handler_ok and prior is None
    elif decision == "reject_draft":
        allowed = (customer_ok or handler_ok) and prior is None
    elif decision == "handler_approve_correspondence_for_own_send":
        allowed = (
            handler_ok
            and review.get("recipient_role") == "account-holder"
            and draft.get("outcome") in ACCOUNT_OUTCOMES
            and (draft.get("correspondence_draft") or {}).get("may_be_sent_by_agent") is False
            and isinstance(prior, dict)
            and prior.get("decision") in CUSTOMER_CONFIRM
            and prior.get("executed") is False
        )
    else:
        return _review_refused(draft, decision, "unknown_decision")

    if not allowed:
        return _review_refused(draft, decision, "preconditions_not_met")

    updated = _record_approval(draft, review, decision)
    updated["flags"]["customer_confirmed"] = decision in CUSTOMER_CONFIRM or (
        isinstance(prior, dict) and prior.get("decision") in CUSTOMER_CONFIRM
    )
    updated["flags"]["handler_accepted_handover"] = decision == "handler_take_handover"
    updated["flags"]["handler_approved_own_send"] = decision == "handler_approve_correspondence_for_own_send"
    if decision == "handler_approve_correspondence_for_own_send" and isinstance(prior, dict):
        updated["human_approval"]["prior_customer_confirmation"] = prior.get("decision")
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one synthetic customer enquiry")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", dest="as_of")
    parser.add_argument("--review", type=Path)
    args = parser.parse_args(argv)
    try:
        enquiry = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        sys.stderr.write("Could not read the enquiry JSON\n")
        return 2
    as_of = args.as_of
    if as_of is None and isinstance(enquiry, dict):
        as_of = enquiry.get("as_of")
    if not isinstance(as_of, str):
        sys.stderr.write("as_of must be YYYY-MM-DD\n")
        return 2
    try:
        draft = draft_reply(enquiry, as_of)
    except (TypeError, ValueError) as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    if args.review:
        try:
            review = json.loads(args.review.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            sys.stderr.write("Could not read the review JSON\n")
            return 2
        try:
            draft = record_review(draft, review)
        except TypeError as exc:
            sys.stderr.write(str(exc) + "\n")
            return 2
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
