#!/usr/bin/env python3
"""Draft a checklist for one synthetic cryptoasset promotion.

The function does not approve a promotion, publish one, rewrite copy, or
give a compliance opinion. s21_approver_decision is null.

No network. No model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from checks import build_checklist
    from injection import PROHIBITED_PAYLOAD_KEYS, scan_document
    from reuse import experiment_03, experiment_04_pin, redact_promotion
    from sources import DEFAULT_STALE_AFTER_DAYS, LAST_VERIFIED, SOURCES
else:
    from .checks import build_checklist
    from .injection import PROHIBITED_PAYLOAD_KEYS, scan_document
    from .reuse import experiment_03, experiment_04_pin, redact_promotion
    from .sources import DEFAULT_STALE_AFTER_DAYS, LAST_VERIFIED, SOURCES

LABEL = "DRAFT CHECKLIST FOR THE S21 APPROVER"
CATALOGUE_ID = "UK08"


class NotSynthetic(Exception):
    """The promotion was not marked synthetic. The body is not echoed."""


class ProhibitedAction(RuntimeError):
    """The caller asked this tool to approve, publish, or opine."""


def approve_promotion(*_args, **_kwargs) -> None:
    raise ProhibitedAction(
        "The section 21 approver signs off. This agent does not approve a promotion."
    )


def publish_promotion(*_args, **_kwargs) -> None:
    raise ProhibitedAction("This agent does not publish a promotion.")


def give_compliance_opinion(*_args, **_kwargs) -> None:
    raise ProhibitedAction("This agent does not give a compliance opinion.")


def _parse_as_of(value: date | str) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _currency(as_of: date, stale_after_days: int) -> list[dict]:
    verified = datetime.strptime(LAST_VERIFIED, "%Y-%m-%d").date()
    age = (as_of - verified).days
    if age < 0:
        state = "as_of_before_verification"
    elif age > stale_after_days:
        state = "stale"
    else:
        state = "within_threshold"
    rows = []
    for source in SOURCES:
        rows.append(
            {
                "source_id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "page_last_updated": source["page_last_updated"],
                "last_verified": source["last_verified"],
                "age_days": age,
                "stale_after_days": stale_after_days,
                "currency": state,
                "body_opened": source["body_opened"],
            }
        )
    return rows


def _prohibited(promotion: dict) -> dict:
    found: list[str] = []
    for key in PROHIBITED_PAYLOAD_KEYS:
        if key in promotion:
            found.append(key)
    controls = promotion.get("untrusted_controls")
    if isinstance(controls, dict):
        for key in PROHIBITED_PAYLOAD_KEYS:
            if key in controls and key not in found:
                found.append(key)
        if controls.get("requested_lifecycle_status"):
            if "requested_lifecycle_status" not in found:
                found.append("requested_lifecycle_status")
    return {"keys": found, "followed": False}


def precheck(
    promotion: dict,
    *,
    as_of: date | str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> dict:
    """Return one draft checklist. The approver's decision stays null."""

    if not isinstance(promotion, dict):
        raise TypeError("promotion must be an object")
    if promotion.get("synthetic") is not True:
        raise NotSynthetic(
            "Refused. The promotion is not marked synthetic. The body was not read into the result."
        )
    raw_text = promotion.get("text")
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("text must be a non-empty string")
    if stale_after_days < 0:
        raise ValueError("stale_after_days must be zero or positive")

    as_of_date = _parse_as_of(as_of)
    prohibited = _prohibited(promotion)
    gateway = redact_promotion(raw_text, as_of=as_of_date)
    if gateway.get("redacted_text") is None:
        shown = None
        usable_source = ""
        injection = {
            "detected": False,
            "followed": False,
            "quarantine_document": True,
            "signals": [],
            "findings": [],
        }
    else:
        shown = gateway["redacted_text"]
        injection = scan_document(shown)
        usable_source = injection["usable_text"]

    checklist = build_checklist(usable_source, promotion)
    currency = _currency(as_of_date, stale_after_days)
    stale = any(row["currency"] == "stale" for row in currency)
    before = any(row["currency"] == "as_of_before_verification" for row in currency)
    if stale or before:
        for row in checklist:
            row["rely_before_reopen"] = False

    exp03 = experiment_03(promotion, as_of=as_of_date.isoformat())
    exp04 = experiment_04_pin()

    firm = promotion.get("firm") if isinstance(promotion.get("firm"), str) else None
    channel = promotion.get("channel") if isinstance(promotion.get("channel"), str) else None
    promotion_id = promotion.get("promotion_id") if isinstance(promotion.get("promotion_id"), str) else None

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "23-crypto-financial-promotions-prechecker",
        "autonomy": "A0",
        "promotion_id": promotion_id,
        "firm": firm,
        "channel": channel,
        "promotion_approved": False,
        "published": False,
        "compliance_opinion": False,
        "s21_approver_decision": None,
        "rewrite_drafted": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "sources_pinned_on": LAST_VERIFIED,
        "sources_stale": stale or before,
        "rules_current": not stale and not before,
        "source_currency": currency,
        "checklist": checklist,
        "prompt_injection": {
            "detected": injection["detected"],
            "followed": False,
            "quarantine_document": injection["quarantine_document"],
            "signals": injection["signals"],
            "findings": injection["findings"],
        },
        "prohibited_requests": prohibited,
        "text_shown_to_reviewer": shown,
        "identifier_gateway": {
            key: value for key, value in gateway.items() if key != "redacted_text"
        },
        "experiment_03": exp03,
        "experiment_04": exp04,
        "limitations": [
            "This checklist is not a compliance opinion and it is not an approval.",
            "Phrase matching misses paraphrase, images, and video.",
            "COBS 4 Annex 1R, COBS 4.12A.36R, COBS 4.12A.38R, section 55NA, COBS 10, and COBS 10A were not opened.",
            "The Handbook lists a future version of COBS 4.12A dated 25 October 2027. That version was not opened.",
            "Paragraph 26F's substitution is marked prospective except for specified purposes. Those purposes were not opened.",
            "Article 73ZA was read as originally made. A later consolidation was not opened.",
            "The marketing-page gateway sentence and section 21(2A) are both recorded and not reconciled.",
        ],
    }
    _force_safe(draft)
    return draft


def _force_safe(draft: dict) -> None:
    draft["promotion_approved"] = False
    draft["published"] = False
    draft["compliance_opinion"] = False
    draft["s21_approver_decision"] = None
    draft["rewrite_drafted"] = False
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["autonomy"] = "A0"
    draft["prompt_injection"]["followed"] = False
    draft["prohibited_requests"]["followed"] = False
    gateway = draft["identifier_gateway"]
    gateway["output_is_anonymised"] = False
    gateway["agent_may_release"] = False
    exp03 = draft["experiment_03"]
    exp03["status_applied"] = False
    exp03["approved_by_this_tool"] = False
    exp03["manifest_approved"] = False
    exp03["actions_taken"] = []
    for row in draft["checklist"]:
        row["compliance_finding"] = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a cryptoasset promotion checklist.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    try:
        draft = precheck(payload, as_of=args.as_of, stale_after_days=args.stale_after_days)
    except NotSynthetic as exc:
        json.dump(
            {"refused": True, "reason": str(exc), "body_echoed": False},
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 2
    json.dump(draft, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
