#!/usr/bin/env python3
"""UK identifier redaction gateway.

Other experiments call ``propose``. The return value is a proposal.
``output_is_anonymised`` is always false. ``agent_may_release`` is always
false. ``release`` raises. A privacy reviewer may record a decision in the
returned JSON. That decision does not release the text.

Nothing in this module reads the network or writes a store.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path

from detectors import detect
from identifiers import RULES_PINNED_ON
from model_assist import NullModel

BANNER = (
    "[REDACTION PROPOSAL. Not anonymised. "
    "Not for release until a privacy reviewer approves it outside this agent.]"
)

PLACEHOLDERS = {
    "nino": "NINO",
    "nhs_number": "NHS_NUMBER",
    "sort_code": "SORT_CODE",
    "account_number": "ACCOUNT_NUMBER",
    "postcode": "POSTCODE",
    "crn": "CRN",
    "iban": "IBAN",
    "utr": "UTR",
    "model_suggestion": "MODEL",
}

INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the above",
    "do not redact",
    "don't redact",
    "do not detect",
    "fully anonymised",
    "fully anonymized",
    "this is anonymised",
    "this is anonymized",
    "release the output",
    "release this",
    "send the redacted",
    "send this to",
    "system prompt",
    "you are now",
)

STALE_PHRASES = (
    "disregard the rules",
    "rules no longer apply",
    "old format is fine",
    "do not use the pinned rules",
    "ignore the pinned rules",
)

LIMITATIONS = (
    "This output is not anonymised. Redacting a detected identifier does not make the rest of the text anonymous.",
    "Names, email addresses, telephone numbers, dates of birth, and free-text descriptions are not detected by the deterministic rules.",
    "An unlabelled continuous NHS number is not redacted, including one that passes modulus 11.",
    "An unlabelled account number that is not next to a redacted sort code is not redacted.",
    "A postcode with no space, GIR 0AA, and BFPO forms are not detected. The six shapes are the 2015 ILR annex.",
    "An eight-digit company number with no label is not redacted. VAT numbers are not detected.",
    "A hyphenated day-and-month that is also a sort code is left in place unless the text labels it.",
    "A grouped 3-3-4 value that passes modulus 11 is redacted even when it is not an NHS number.",
    "Sort codes are not checked against the Pay.UK modulus specification.",
    "The ISO 13616 text was not purchased. The IBAN check is the published rearrangement and mod 97.",
    "Scottish CHI numbers and Northern Ireland Health and Care Numbers are not separate detectors.",
    "A model suggestion has no checksum. It is not applied unless the caller opts in, and it still needs a privacy reviewer.",
)

DECISIONS = ("approve", "reject", "return_for_edit")
REVIEWER_ROLE = "Privacy reviewer"


class ReleaseForbidden(RuntimeError):
    """The gateway has no release or send path."""


def _now(moment: datetime | None) -> str:
    if moment is None:
        moment = datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _signals(text: str, phrases: tuple[str, ...]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase in lower]


def _placeholders(findings: list[dict]) -> None:
    counts: dict[str, int] = {}
    for finding in findings:
        label = PLACEHOLDERS[finding["entity_type"]]
        counts[label] = counts.get(label, 0) + 1
        finding["placeholder"] = f"[{label}-{counts[label]}]"
        finding["applied"] = True
        finding["value_recorded"] = False


def _redact(text: str, findings: list[dict]) -> str:
    pieces = []
    cursor = 0
    for finding in findings:
        pieces.append(text[cursor:finding["start"]])
        pieces.append(finding["placeholder"])
        cursor = finding["end"]
    pieces.append(text[cursor:])
    body = "".join(pieces)
    return BANNER + "\n" + body


def _audit_finding(finding: dict) -> dict:
    return {
        "entity_type": finding["entity_type"],
        "start": finding["start"],
        "end": finding["end"],
        "detector": finding["detector"],
        "checksum": finding["checksum"],
        "confidence": finding["confidence"],
        "detail": finding.get("detail", {}),
        "placeholder": finding["placeholder"],
        "applied": finding["applied"],
        "method": finding.get("method", "deterministic"),
        "value_recorded": False,
    }


def _suggestion_rows(text: str, model, deterministic: list[dict]) -> tuple[list[dict], list[str]]:
    notes: list[str] = []
    try:
        raw = model.suggest(text)
    except Exception as exc:  # noqa: BLE001 — a failed adapter must not skip detection
        return [], [f"model_error:{type(exc).__name__}"]
    rows = []
    for item in raw:
        try:
            start = int(item["start"])
            end = int(item["end"])
            label = str(item.get("label", "unspecified"))
        except (KeyError, TypeError, ValueError):
            notes.append("model_suggestion_rejected:malformed")
            continue
        if not (0 <= start < end <= len(text)):
            notes.append("model_suggestion_rejected:out_of_range")
            continue
        if any(token in label.lower() for token in ("release", "send", "anonymis", "anonymiz")):
            notes.append("model_suggestion_rejected:instruction")
            continue
        if len(label) > 40 or "\n" in label:
            notes.append("model_suggestion_rejected:label")
            continue
        row = {
            "entity_type": "model_suggestion",
            "start": start,
            "end": end,
            "detector": "model_suggestion",
            "checksum": "not_applicable",
            "confidence": "model",
            "detail": {"label": label},
            "method": "model_suggestion",
            "applied": False,
            "placeholder": "",
            "value_recorded": False,
        }
        if any(row["start"] < earlier["end"] and earlier["start"] < row["end"] for earlier in deterministic):
            notes.append("model_suggestion_ignored:overlaps_deterministic")
            continue
        rows.append(row)
    return rows, notes


def _force_safe(proposal: dict) -> None:
    proposal["anonymisation"]["output_is_anonymised"] = False
    proposal["anonymisation"]["claim_forbidden"] = True
    proposal["release"]["agent_may_release"] = False
    proposal["release"]["agent_may_send"] = False
    proposal["release"]["performed_by_agent"] = False
    proposal["security"]["actions_taken"] = []


def propose(
    text: str,
    *,
    caller: str = "unspecified",
    now: datetime | None = None,
    rules_as_of: date | None = None,
    model=None,
    apply_model_suggestions: bool = False,
    reversible: bool = False,
) -> dict:
    """Propose redactions for one text.

    The caller already holds ``text``. The proposal does not repeat each
    matched value, except inside ``token_vault`` when ``reversible`` is true.
    That vault is not part of the audit record and is not persisted here.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    adapter = model if model is not None else NullModel()
    detected = detect(text)
    findings = detected["findings"]
    for finding in findings:
        finding["method"] = "deterministic"
    suggestions, model_notes = _suggestion_rows(text, adapter, findings)
    _placeholders(findings)
    applied = list(findings)
    if apply_model_suggestions and suggestions:
        _placeholders(suggestions)
        for suggestion in suggestions:
            suggestion["applied"] = True
        applied = sorted(findings + suggestions, key=lambda item: item["start"])
    elif suggestions:
        for index, suggestion in enumerate(suggestions, start=1):
            suggestion["placeholder"] = f"[MODEL-{index}]"
            suggestion["applied"] = False

    rules_stale = rules_as_of is not None and rules_as_of < RULES_PINNED_ON
    limitations = list(LIMITATIONS)
    if rules_stale:
        limitations.append(
            "The caller supplied a rules date before the pinned sources. "
            "Detection still used the pinned rules."
        )
    if suggestions and not apply_model_suggestions:
        limitations.append(
            "A model suggested extra spans. They were not applied. "
            "A privacy reviewer decides whether they are redactions."
        )
    if apply_model_suggestions and suggestions:
        limitations.append(
            "Model suggestions were applied because the caller opted in. "
            "They have no checksum and are not anonymisation."
        )

    vault = None
    if reversible:
        vault = {
            "warning": (
                "Not a DPO audit record. Do not write this object to the log. "
                "This starter does not persist it."
            ),
            "persisted": False,
            "entries": [
                {"placeholder": finding["placeholder"], "value": text[finding["start"]:finding["end"]]}
                for finding in applied
                if finding["applied"]
            ],
        }

    proposal = {
        "gateway": "exp-08-uk-pii-redaction-gateway",
        "catalogue_id": "O005",
        "redacted_text": _redact(text, [item for item in applied if item["applied"]]),
        "anonymisation": {
            "output_is_anonymised": False,
            "claim_forbidden": True,
            "reason": (
                "Replacing a detected UK identifier is not anonymisation. "
                "Residual text and missed identifiers can still identify a person. "
                "A reversible map, held separately, would be pseudonymisation at best."
            ),
        },
        "release": {
            "status": "pending_privacy_reviewer",
            "agent_may_release": False,
            "agent_may_send": False,
            "performed_by_agent": False,
            "approver": REVIEWER_ROLE,
        },
        "audit_log": {
            "log_type": "dpo_redaction_audit",
            "raw_values_logged": False,
            "timestamp": _now(now),
            "caller": caller,
            "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "input_char_count": len(text),
            "rules_pinned_on": RULES_PINNED_ON.isoformat(),
            "rules_as_of": rules_as_of.isoformat() if rules_as_of else None,
            "rules_stale": rules_stale,
            "model_assist": getattr(adapter, "name", "unnamed"),
            "model_notes": model_notes,
            "findings": [_audit_finding(item) for item in applied],
            "model_suggestions": [_audit_finding(item) for item in suggestions],
            "not_redacted": detected["not_redacted"],
            "review": {
                "required": True,
                "approver": REVIEWER_ROLE,
                "decision": None,
            },
        },
        "security": {
            "prompt_injection_signals": _signals(text, INJECTION_PATTERNS),
            "stale_data_signals": _signals(text, STALE_PHRASES),
            "actions_taken": [],
            "decisions_not_taken": ["release", "send", "anonymisation_claim", "production_write"],
        },
        "limitations": limitations,
    }
    if vault is not None:
        proposal["token_vault"] = vault
    _force_safe(proposal)
    return proposal


def record_reviewer_decision(
    proposal: dict,
    *,
    reviewer_role: str,
    decision: str,
    note: str = "",
    now: datetime | None = None,
) -> dict:
    """Record a privacy reviewer's decision on a copy of the proposal.

    The agent must not call this to approve its own output. Approval does
    not release the text and does not send it.
    """

    if reviewer_role != REVIEWER_ROLE:
        raise ValueError("only a Privacy reviewer can record this decision")
    if decision not in DECISIONS:
        raise ValueError("decision must be approve, reject, or return_for_edit")
    if not isinstance(proposal, dict) or "release" not in proposal:
        raise ValueError("proposal is not a gateway result")
    updated = deepcopy(proposal)
    status = {
        "approve": "approved_for_human_release",
        "reject": "rejected",
        "return_for_edit": "returned_for_edit",
    }[decision]
    updated["release"]["status"] = status
    updated["audit_log"]["review"] = {
        "required": True,
        "approver": REVIEWER_ROLE,
        "decision": decision,
        "note": note[:200],
        "timestamp": _now(now),
    }
    _force_safe(updated)
    return updated


def release(_proposal: dict) -> None:
    """Refuse to release. There is no successful return."""

    raise ReleaseForbidden("the gateway does not release redacted output")


def send(_proposal: dict) -> None:
    """Refuse to send. There is no successful return."""

    raise ReleaseForbidden("the gateway does not send redacted output")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose UK identifier redactions. Does not release.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--caller", default="cli")
    parser.add_argument("--reversible", action="store_true")
    args = parser.parse_args(argv)
    text = args.input.read_text(encoding="utf-8")
    proposal = propose(text, caller=args.caller, reversible=args.reversible)
    json.dump(proposal, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
