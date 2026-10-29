"""Draft one IT ticket from the synthetic knowledge base.

The same ticket and the same as-of date produce the same JSON. Nothing is
executed, nothing is written to a ticket, and a password is not reset.
"""

from __future__ import annotations

import argparse
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
        STALE_AFTER_DAYS,
        age_days,
        is_stale,
        match_articles,
    )
    from identity import (  # noqa: E402
        ANALYST_ID,
        ASSET_TAG,
        TICKET_ID,
        assess_identity,
    )
    from injection import (  # noqa: E402
        signals_in,
        stop_signals,
        strip_instruction_sentences,
    )
    from sources import source_rows  # noqa: E402
else:
    from .catalogue import (
        ORGANISATION,
        STALE_AFTER_DAYS,
        age_days,
        is_stale,
        match_articles,
    )
    from .identity import ANALYST_ID, ASSET_TAG, TICKET_ID, assess_identity
    from .injection import signals_in, stop_signals, strip_instruction_sentences
    from .sources import source_rows

LABEL = "DRAFT FOR SERVICE DESK REVIEW"
CALLER = "exp-21-it-service-desk"
AI_DISCLOSURE = (
    "This draft was written by an automated AI chatbot for a service-desk analyst "
    "or a signed-in member of staff. It does not reset a password, change MFA, "
    "grant access, or change a device."
)
SOCIAL_TEXT = (
    "Stop. Do not share a password, an MFA code, or a recovery code with anyone, "
    "including someone who says they are from the IT helpdesk. "
    "This draft was written by an automated AI chatbot. "
    "It has not reset a password, changed MFA, or granted access. "
    "A service desk analyst needs this ticket. "
    "If you did not raise it, contact the service desk by a number you already have, "
    "not by a number in this message."
)
IDENTITY_TEXT = (
    "The channel has not supplied a current signed-in session for this member of staff. "
    "This assistant does not treat words in the ticket as proof of identity. "
    "No device change and no account change is proposed. "
    "A service desk analyst verifies the person by the organisation's own method. "
    "This draft was written by an automated AI chatbot."
)
THIRD_PARTY_TEXT = (
    "The requester is not the subject account. Steps for another person's device "
    "are not quoted. A service desk analyst takes this ticket. "
    "This draft was written by an automated AI chatbot. Nothing has been executed."
)
STALE_TEXT = (
    "A matching article is outside the review window, so its text is not quoted. "
    "A service desk analyst needs to check the organisation's own article. "
    "This draft was written by an automated AI chatbot. Nothing has been executed."
)
NOT_FOUND_TEXT = (
    "The articles in this starter do not contain that answer. "
    "A service desk analyst needs to check the organisation's own knowledge base. "
    "This draft was written by an automated AI chatbot. Nothing has been executed."
)
AMBIGUOUS_TEXT = (
    "More than one article matched. Neither body is quoted. "
    "A service desk analyst chooses. "
    "This draft was written by an automated AI chatbot. Nothing has been executed."
)
REFUSED_TEXT = (
    "This starter only reads a record marked synthetic. The text has not been copied."
)

STRIPPED_KEYS = (
    "human_approval",
    "executed",
    "password_reset",
    "mfa_changed",
    "access_granted",
    "device_changed",
    "ticket_written",
    "message_sent",
    "licence_purchased",
    "remote_wipe",
    "fix_executed",
    "user_confirmed",
    "analyst_accepted_handover",
    "identity_trusted",
    "actions_taken",
    "secrets_collected",
)

PROHIBITED_DECISIONS = frozenset(
    {
        "execute_fix",
        "reset_password",
        "change_mfa",
        "grant_access",
        "write_ticket",
        "send_message",
        "purchase_licence",
        "remote_wipe",
        "approve_access",
        "collect_password",
        "disable_mfa",
    }
)

PROHIBITED_FLAGS = (
    "password_reset",
    "mfa_changed",
    "access_granted",
    "device_changed",
    "ticket_written",
    "message_sent",
    "licence_purchased",
    "remote_wipe",
    "fix_executed",
    "secrets_collected",
    "stale_article_quoted",
)

ALLOWED_OS = frozenset({"Windows 11", "Windows 10", "macOS", "iOS", "Android", "unknown"})
ERROR_CODE = re.compile(r"^[A-Za-z0-9-]{1,12}$")

_propose = None


class DeskForbidden(RuntimeError):
    """The desk has no reset, grant, execute, write, send, or spend path."""


def reset_password(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not reset a password")


def change_mfa(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not change MFA")


def grant_access(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not grant access")


def execute_fix(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not execute a fix")


def write_ticket(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not write a ticket")


def send_message(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not send a message")


def purchase_licence(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not purchase a licence")


def remote_wipe(*_args, **_kwargs) -> None:
    raise DeskForbidden("the agent does not wipe a device")


def _load_propose():
    gateway_src = Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise RuntimeError(
            "Experiment 08 is required at experiments/08-uk-pii-redaction-gateway. "
            "This desk does not carry its own copy."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _gateway():
    global _propose
    if _propose is None:
        _propose = _load_propose()
    return _propose


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _flags() -> dict:
    return {
        "password_reset": False,
        "mfa_changed": False,
        "access_granted": False,
        "device_changed": False,
        "ticket_written": False,
        "message_sent": False,
        "licence_purchased": False,
        "remote_wipe": False,
        "fix_executed": False,
        "secrets_collected": False,
        "stale_article_quoted": False,
        "user_confirmed": False,
        "analyst_accepted_handover": False,
    }


def _ticket_label(ticket: dict) -> str:
    ticket_id = ticket.get("ticket_id")
    if isinstance(ticket_id, str) and TICKET_ID.match(ticket_id):
        return ticket_id
    return "not-a-synthetic-id"


def _free_text(ticket: dict) -> str:
    parts: list[str] = []
    summary = ticket.get("summary")
    if isinstance(summary, str) and summary:
        parts.append(summary)
    diagnostics = ticket.get("diagnostics")
    if isinstance(diagnostics, dict):
        free = diagnostics.get("free_text")
        if isinstance(free, str) and free:
            parts.append(free)
    return "\n".join(parts)


def _redact(text: str) -> dict:
    proposal = _gateway()(
        text,
        caller=CALLER,
        apply_model_suggestions=False,
        reversible=False,
    )
    if proposal["anonymisation"]["output_is_anonymised"] or proposal["release"]["agent_may_release"]:
        raise DeskForbidden("Experiment 08 must not be treated as anonymisation or a release")
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


def _closed_diagnostics(ticket: dict) -> dict:
    diagnostics = ticket.get("diagnostics") if isinstance(ticket.get("diagnostics"), dict) else {}
    device = ticket.get("device") if isinstance(ticket.get("device"), dict) else {}
    values: dict = {}
    if diagnostics.get("os") in ALLOWED_OS:
        values["os"] = diagnostics["os"]
    error_code = diagnostics.get("error_code")
    if isinstance(error_code, str) and ERROR_CODE.match(error_code):
        values["error_code"] = error_code
    if isinstance(diagnostics.get("network_connected"), bool):
        values["network_connected"] = diagnostics["network_connected"]
    asset = device.get("asset_tag")
    if isinstance(asset, str) and ASSET_TAG.match(asset):
        values["asset_tag"] = asset
    return values


def _diagnostic_report(ticket: dict, articles: list[dict]) -> dict:
    values = _closed_diagnostics(ticket)
    required: list[str] = []
    for article in articles:
        for name in article["required_diagnostics"]:
            if name not in required:
                required.append(name)
    missing = [name for name in required if name not in values]
    supplied = [name for name in required if name in values]
    return {
        "supplied": supplied,
        "missing": missing,
        "complete": not missing,
        "values_invented": False,
        "closed_values": {name: values[name] for name in supplied},
    }


def _note(ticket_id: str, outcome: str, article_ids: list[str], missing: list[str]) -> str:
    parts = [
        "Draft ticket note. Not written to the ticket system.",
        f"Ticket {ticket_id}.",
        f"Outcome {outcome}.",
    ]
    if article_ids:
        parts.append("Articles: " + ", ".join(article_ids) + ".")
    if missing:
        parts.append(
            "Missing diagnostics: " + ", ".join(missing) + ". Values were not invented."
        )
    parts.append(
        "Nothing was executed. human_approval is empty until a separate review object is supplied."
    )
    return " ".join(parts)


def _citation(article: dict, body_quoted: bool) -> dict:
    return {
        "article_id": article["id"],
        "title": article["title"],
        "last_reviewed": article["last_reviewed"],
        "stale": article["stale"],
        "body_quoted": body_quoted,
    }


def _article_view(article: dict | None, body_quoted: bool) -> dict | None:
    if article is None:
        return None
    return {
        "id": article["id"],
        "title": article["title"],
        "class": article["article_class"],
        "last_reviewed": article["last_reviewed"],
        "stale": article["stale"],
        "body_quoted": body_quoted,
        "body": article["body"] if body_quoted else None,
        "citation": f"{article['id']}, last reviewed {article['last_reviewed']}",
    }


def _proposed(article: dict | None, body_quoted: bool, diagnostics: dict, outcome: str) -> dict | None:
    if article is None or not body_quoted:
        return None
    user_may_confirm = False
    if outcome == "standard_fix_proposed":
        user_may_confirm = True
    elif outcome == "device_change_proposed" and diagnostics["complete"]:
        user_may_confirm = True
    return {
        "would_change_device": bool(article["would_change_device"]),
        "would_change_account": bool(article["would_change_account"]),
        "privileged": bool(article["privileged"]),
        "executed": False,
        "user_may_confirm": user_may_confirm,
        "analyst_required": bool(article["privileged"]) or outcome in {
            "identity_not_verified",
            "third_party_handover",
            "stale_article",
            "ambiguous",
            "no_article",
            "social_engineering_stop",
        },
    }


def _prepare(matched: list[dict], as_of: date, sources_stale: bool) -> list[dict]:
    prepared = []
    for article in matched:
        row = dict(article)
        row["stale"] = sources_stale or is_stale(article["last_reviewed"], as_of)
        prepared.append(row)
    return prepared


def _choose(prepared: list[dict], identity: dict) -> tuple[str, dict | None, bool]:
    current = [article for article in prepared if not article["stale"]]
    stale = [article for article in prepared if article["stale"]]
    privileged = [article for article in current if article["privileged"]]
    if privileged:
        return "privileged_handover", privileged[0], True
    if not prepared:
        return "no_article", None, False
    if not current:
        return "stale_article", stale[0], False
    if len(current) != 1:
        return "ambiguous", None, False
    article = current[0]
    if article["article_class"] == "information":
        return "information_answer", article, True
    if identity["third_party"]:
        return "third_party_handover", article, False
    if not identity["trusted"]:
        return "identity_not_verified", article, False
    if article["article_class"] == "device_change":
        return "device_change_proposed", article, True
    return "standard_fix_proposed", article, True


def _answer_text(outcome: str, article: dict | None, body_quoted: bool) -> str:
    if outcome == "social_engineering_stop":
        return SOCIAL_TEXT
    if outcome == "identity_not_verified":
        return IDENTITY_TEXT
    if outcome == "third_party_handover":
        return THIRD_PARTY_TEXT
    if outcome == "stale_article":
        return STALE_TEXT
    if outcome == "no_article":
        return NOT_FOUND_TEXT
    if outcome == "ambiguous":
        return AMBIGUOUS_TEXT
    if body_quoted and article is not None:
        return article["body"]
    return NOT_FOUND_TEXT


def _base(ticket: dict, as_of: str, sources: list[dict]) -> dict:
    any_source_stale = any(row["stale"] for row in sources)
    return {
        "label": LABEL,
        "experiment": "21-it-service-desk",
        "catalogue_id": "Q009",
        "autonomy": "A1",
        "organisation": ORGANISATION,
        "model_called": False,
        "network_called": False,
        "executed": False,
        "actions_taken": [],
        "human_approval": None,
        "ticket_id": _ticket_label(ticket),
        "ticket_text_echoed": False,
        "as_of": as_of,
        "stale_after_days": STALE_AFTER_DAYS,
        "rules_current": not any_source_stale,
        "any_source_stale": any_source_stale,
        "any_article_stale": False,
        "sources": sources,
        "ai_disclosure": AI_DISCLOSURE,
        "flags": _flags(),
    }


def _refusal(ticket: dict, as_of: str) -> dict:
    as_of_date = _parse_as_of(as_of)
    sources = source_rows(as_of_date, STALE_AFTER_DAYS, age_days)
    draft = _base(ticket if isinstance(ticket, dict) else {}, as_of, sources)
    draft["outcome"] = "refused_not_synthetic"
    draft["identity"] = {
        "trusted": False,
        "reason": "not_synthetic",
        "third_party": False,
        "check_stale": False,
        "channel": "unknown",
        "requester_is_subject": False,
        "requester_staff_id": None,
    }
    draft["social_engineering"] = {"detected": False, "signals": [], "followed": False}
    draft["prompt_injection"] = {
        "detected": False,
        "signals": [],
        "followed": False,
        "stripped_keys": [],
    }
    draft["pii_gateway"] = {
        "called": False,
        "experiment": "08-uk-pii-redaction-gateway",
        "reason": "not_synthetic",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "redacted_text_copied": False,
    }
    draft["article"] = None
    draft["citations"] = []
    draft["proposed_fix"] = None
    draft["diagnostics"] = {
        "supplied": [],
        "missing": [],
        "complete": False,
        "values_invented": False,
        "closed_values": {},
    }
    draft["answer"] = {"text": REFUSED_TEXT, "body_quoted": False, "sufficient": False}
    draft["ticket_update_draft"] = _note(draft["ticket_id"], draft["outcome"], [], [])
    return draft


def triage(ticket: dict, as_of: str, stale_after_days: int = STALE_AFTER_DAYS) -> dict:
    """Return a draft. human_approval is null. Nothing is executed."""

    if not isinstance(ticket, dict):
        raise TypeError("ticket must be a JSON object")
    as_of_date = _parse_as_of(as_of)
    if ticket.get("synthetic") is not True:
        return _refusal(ticket, as_of)

    cleaned = deepcopy(ticket)
    stripped = [key for key in STRIPPED_KEYS if key in cleaned]
    for key in stripped:
        cleaned.pop(key, None)

    sources = source_rows(as_of_date, stale_after_days, age_days)
    sources_stale = any(row["stale"] for row in sources)
    text = _free_text(cleaned)
    signals = signals_in(text)
    stops = stop_signals(signals)
    matching_text = strip_instruction_sentences(text)
    matched = match_articles(matching_text)
    prepared = _prepare(matched, as_of_date, sources_stale)
    identity = assess_identity(cleaned, as_of)
    diagnostics = _diagnostic_report(cleaned, prepared)
    pii = _redact(text) if text else {
        "called": False,
        "experiment": "08-uk-pii-redaction-gateway",
        "reason": "no_free_text",
        "output_is_anonymised": False,
        "agent_may_release": False,
        "redacted_text_copied": False,
        "finding_count": 0,
        "entity_types": [],
    }

    draft = _base(cleaned, as_of, sources)
    draft["rules_current"] = not sources_stale
    draft["any_source_stale"] = sources_stale
    draft["any_article_stale"] = any(article["stale"] for article in prepared)
    draft["identity"] = identity
    draft["social_engineering"] = {
        "detected": bool(stops),
        "signals": stops,
        "followed": False,
    }
    draft["prompt_injection"] = {
        "detected": bool(signals) or bool(stripped),
        "signals": signals,
        "followed": False,
        "stripped_keys": stripped,
    }
    draft["pii_gateway"] = pii
    draft["diagnostics"] = diagnostics

    if stops:
        outcome = "social_engineering_stop"
        primary = prepared[0] if prepared else None
        body_quoted = False
        citations = [_citation(article, False) for article in prepared]
    else:
        outcome, primary, body_quoted = _choose(prepared, identity)
        if outcome == "ambiguous":
            citations = [_citation(article, False) for article in prepared if not article["stale"]]
            primary = None
        elif outcome == "stale_article":
            citations = [_citation(article, False) for article in prepared]
        elif primary is None:
            citations = []
        else:
            citations = [_citation(article, article["id"] == primary["id"] and body_quoted) for article in prepared]

    if any(row["body_quoted"] and row["stale"] for row in citations):
        raise DeskForbidden("a stale article must not be quoted")

    draft["outcome"] = outcome
    draft["article"] = _article_view(primary, body_quoted)
    draft["citations"] = citations
    draft["proposed_fix"] = _proposed(primary, body_quoted, diagnostics, outcome)
    draft["answer"] = {
        "text": _answer_text(outcome, primary, body_quoted),
        "body_quoted": body_quoted,
        "sufficient": body_quoted and outcome in {
            "standard_fix_proposed",
            "device_change_proposed",
            "information_answer",
            "privileged_handover",
        },
    }
    draft["ticket_update_draft"] = _note(
        draft["ticket_id"],
        outcome,
        [row["article_id"] for row in citations],
        diagnostics["missing"],
    )
    draft["flags"]["stale_article_quoted"] = False
    _assert_safe(draft)
    return draft


def _assert_safe(draft: dict) -> None:
    if draft["executed"] or draft["actions_taken"] or draft["human_approval"] is not None:
        raise DeskForbidden("triage must not execute or approve")
    if draft["ticket_text_echoed"] or draft["model_called"] or draft["network_called"]:
        raise DeskForbidden("triage must not echo the ticket or call out")
    for key in PROHIBITED_FLAGS:
        if draft["flags"][key]:
            raise DeskForbidden(f"flag {key} must stay false")
    gateway = draft["pii_gateway"]
    if gateway.get("output_is_anonymised") or gateway.get("agent_may_release"):
        raise DeskForbidden("the gateway result is not a release")
    if gateway.get("redacted_text_copied"):
        raise DeskForbidden("redacted text must not be copied")


def _review_refused(draft: dict, decision: str, reason: str) -> dict:
    updated = deepcopy(draft)
    updated["review"] = {
        "accepted": False,
        "refused": True,
        "reason": reason,
        "decision": decision,
        "executed": False,
    }
    updated["human_approval"] = None
    updated["executed"] = False
    updated["actions_taken"] = []
    for key in PROHIBITED_FLAGS:
        updated["flags"][key] = False
    updated["flags"]["user_confirmed"] = False
    updated["flags"]["analyst_accepted_handover"] = False
    return updated


def record_review(draft: dict, review: dict) -> dict:
    """Record a separate review. Confirmation does not execute anything."""

    if not isinstance(draft, dict) or not isinstance(review, dict):
        raise TypeError("draft and review must be JSON objects")
    decision = review.get("decision")
    actor = review.get("actor")
    actor_id = review.get("actor_id")
    if not isinstance(decision, str):
        return _review_refused(draft, "", "decision_missing")
    if decision in PROHIBITED_DECISIONS:
        return _review_refused(draft, decision, "prohibited_decision")
    if draft.get("outcome") == "refused_not_synthetic":
        return _review_refused(draft, decision, "not_synthetic")
    if draft.get("human_approval") is not None:
        return _review_refused(draft, decision, "already_reviewed")
    if draft.get("executed") is True or any(draft.get("flags", {}).get(key) for key in PROHIBITED_FLAGS):
        return _review_refused(draft, decision, "prohibited_flag")

    requester = (draft.get("identity") or {}).get("requester_staff_id")
    identity = draft.get("identity") or {}
    proposed = draft.get("proposed_fix") or {}
    diagnostics = draft.get("diagnostics") or {}
    social = (draft.get("social_engineering") or {}).get("detected") is True

    allowed = False
    if decision == "user_confirm_standard_fix":
        allowed = (
            actor == "user"
            and actor_id == requester
            and draft.get("outcome") == "standard_fix_proposed"
            and identity.get("trusted") is True
            and not identity.get("third_party")
            and not social
            and proposed.get("privileged") is False
            and proposed.get("would_change_device") is False
            and proposed.get("would_change_account") is False
            and proposed.get("executed") is False
        )
    elif decision == "user_confirm_device_change":
        allowed = (
            actor == "user"
            and actor_id == requester
            and draft.get("outcome") == "device_change_proposed"
            and identity.get("trusted") is True
            and identity.get("requester_is_subject") is True
            and not identity.get("third_party")
            and not social
            and diagnostics.get("complete") is True
            and proposed.get("privileged") is False
            and proposed.get("would_change_device") is True
            and proposed.get("would_change_account") is False
            and proposed.get("user_may_confirm") is True
            and proposed.get("executed") is False
        )
    elif decision == "analyst_take_handover":
        allowed = actor == "analyst" and isinstance(actor_id, str) and ANALYST_ID.match(actor_id) is not None
    elif decision == "reject_draft":
        user_ok = actor == "user" and actor_id == requester
        analyst_ok = actor == "analyst" and isinstance(actor_id, str) and ANALYST_ID.match(actor_id) is not None
        allowed = user_ok or analyst_ok
    else:
        return _review_refused(draft, decision, "unknown_decision")

    if not allowed:
        return _review_refused(draft, decision, "preconditions_not_met")

    updated = deepcopy(draft)
    updated["human_approval"] = {
        "decision": decision,
        "actor": actor,
        "actor_id": actor_id,
        "executed": False,
        "production_record_changed": False,
        "message_sent": False,
    }
    updated["executed"] = False
    updated["actions_taken"] = []
    updated["flags"]["user_confirmed"] = decision in {
        "user_confirm_standard_fix",
        "user_confirm_device_change",
    }
    updated["flags"]["analyst_accepted_handover"] = decision == "analyst_take_handover"
    for key in PROHIBITED_FLAGS:
        updated["flags"][key] = False
    if updated["proposed_fix"] is not None:
        updated["proposed_fix"]["executed"] = False
    updated["review"] = {
        "accepted": True,
        "refused": False,
        "reason": "recorded",
        "decision": decision,
        "executed": False,
    }
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft one synthetic IT ticket")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", dest="as_of")
    parser.add_argument("--review", type=Path)
    args = parser.parse_args(argv)
    try:
        ticket = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        sys.stderr.write("Could not read the ticket JSON\n")
        return 2
    as_of = args.as_of
    if as_of is None and isinstance(ticket, dict):
        as_of = ticket.get("as_of")
    if not isinstance(as_of, str):
        sys.stderr.write("as_of must be YYYY-MM-DD\n")
        return 2
    try:
        draft = triage(ticket, as_of)
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
