"""Call Experiments 04, 08, 10, and 16 without copying their decisions.

Each neighbour keeps its own module names. Those names collide if they are
left on sys.modules, so a neighbour is loaded once under a private name and
the top-level names it imported are removed afterwards. Already-bound
functions inside the neighbour keep their own references.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime, timezone
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "intake",
    "gateway",
    "identifiers",
    "detectors",
    "model_assist",
    "kyc_injection",
    "tipping_off",
    "triage",
    "review",
)

_triage_mod = None
_review_mod = None
_gateway_mod = None
_exp04_sources = None


def _drop_collisions() -> None:
    for name in _COLLIDING:
        sys.modules.pop(name, None)


def _load(folder: str, filename: str, module_name: str):
    """Load one neighbour. Its folder is on sys.path only while it imports."""

    _drop_collisions()
    src = EXPERIMENTS / folder / "src"
    path = src / filename
    if not path.is_file():
        raise FileNotFoundError(folder)
    sys.path.insert(0, str(src))
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(module_name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        while str(src) in sys.path:
            sys.path.remove(str(src))
        _drop_collisions()
    return module


def experiment_04_pin() -> dict:
    """The registration-page row Experiment 04 pinned. Not a gap conclusion."""

    global _exp04_sources
    if _exp04_sources is None:
        _exp04_sources = _load(
            "04-fca-cryptoasset-readiness",
            "sources.py",
            "exp04_sources",
        )
    catalogue = {row["id"]: row for row in _exp04_sources.SOURCES}
    row = catalogue.get("fca-mlr-application", {})
    overview = catalogue.get("fca-regime-overview", {})
    return {
        "experiment": "04-fca-cryptoasset-readiness",
        "catalogue_id": "UK02",
        "called": True,
        "gap_register_run": False,
        "registration_page_last_verified_by_experiment_04": row.get("last_verified"),
        "regime_overview_last_verified_by_experiment_04": overview.get("last_verified"),
        "note": (
            "Experiment 04 opened the same FCA URLs on the date in its pin. "
            "This draft does not re-score that policy pack and does not adopt "
            "a gap conclusion."
        ),
    }


def travel_rule_summary(transfer: dict, *, as_of: date, stale_after_days: int) -> dict:
    """Categories from Experiment 10. Party names are not copied."""

    global _triage_mod
    base = {
        "experiment": "10-travel-rule-exception-triage",
        "catalogue_id": "UK05",
        "attached": True,
        "called": False,
        "refused": False,
        "not_read": False,
        "exception_categories": [],
        "options": [],
        "analyst_decision": None,
        "sources_stale": None,
        "injection_detected": False,
        "injection_followed": False,
    }
    try:
        if _triage_mod is None:
            _triage_mod = _load(
                "10-travel-rule-exception-triage",
                "triage.py",
                "exp10_triage",
            )
        draft = _triage_mod.triage(transfer, as_of=as_of, stale_after_days=stale_after_days)
    except FileNotFoundError:
        base["not_read"] = True
        base["reason"] = "Experiment 10 is not beside this experiment."
        return base
    except Exception as exc:
        base["not_read"] = True
        base["reason"] = type(exc).__name__
        return base

    base["called"] = True
    base["refused"] = bool(draft.get("refused"))
    base["label"] = draft.get("label")
    base["exception_categories"] = list(draft.get("exception_categories") or [])
    base["options"] = [
        {"id": option.get("id"), "proposed": bool(option.get("proposed")), "agent_will_not_take": True}
        for option in (draft.get("options") or [])
        if isinstance(option, dict)
    ]
    base["analyst_decision"] = draft.get("analyst_decision")
    base["sources_stale"] = bool(draft.get("any_source_stale"))
    injection = draft.get("prompt_injection") or {}
    base["injection_detected"] = bool(injection.get("detected"))
    base["injection_followed"] = False
    base["actions_taken"] = []
    if draft.get("analyst_decision") is not None:
        base["analyst_decision"] = None
        base["note"] = "Experiment 10 returned a decision. This draft cleared it."
    return base


def kyc_summary(customer_file: dict, *, as_of: date, stale_after_days: int) -> dict:
    """Missing-item ids from Experiment 16. The customer note is not copied."""

    global _review_mod
    base = {
        "experiment": "16-kyc-evidence-intake",
        "catalogue_id": "B004",
        "attached": True,
        "called": False,
        "not_read": False,
        "documents_confirmed": False,
        "purpose_confirmed": False,
        "final_risk_rating": None,
        "sar_filed": False,
        "missing": [],
        "sources_stale": None,
        "injection_detected": False,
        "injection_followed": False,
        "customer_facing_copied": False,
    }
    try:
        if _review_mod is None:
            _review_mod = _load(
                "16-kyc-evidence-intake",
                "review.py",
                "exp16_review",
            )
        draft = _review_mod.review(
            customer_file,
            as_of=as_of,
            stale_after_days=stale_after_days,
        )
    except FileNotFoundError:
        base["not_read"] = True
        base["reason"] = "Experiment 16 is not beside this experiment."
        return base
    except Exception as exc:
        base["not_read"] = True
        base["reason"] = type(exc).__name__
        return base

    checklist = draft.get("checklist") or {}
    injection = draft.get("prompt_injection") or {}
    base.update(
        {
            "called": True,
            "documents_confirmed": False,
            "purpose_confirmed": False,
            "final_risk_rating": None,
            "sar_filed": False,
            "missing": list(checklist.get("missing") or []),
            "evidenced_ids": [row.get("id") for row in (checklist.get("evidenced") or []) if isinstance(row, dict)],
            "sources_stale": bool(draft.get("sources_stale")),
            "injection_detected": bool(injection.get("detected")),
            "injection_followed": False,
            "customer_facing_copied": False,
            "actions_taken": [],
        }
    )
    return base


def redact_note(text: str, *, as_of: date) -> dict:
    """Experiment 08 proposal for one note. Raw values are not copied."""

    global _gateway_mod
    summary = {
        "experiment": "08-uk-pii-redaction-gateway",
        "catalogue_id": "O005",
        "called": False,
        "not_read": False,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "finding_count": 0,
        "entity_types": [],
        "redacted_text": None,
        "rules_stale": None,
    }
    if not text:
        summary["called"] = False
        summary["reason"] = "No analyst note was supplied."
        return summary
    try:
        if _gateway_mod is None:
            _gateway_mod = _load(
                "08-uk-pii-redaction-gateway",
                "gateway.py",
                "exp08_gateway",
            )
        moment = datetime(as_of.year, as_of.month, as_of.day, 12, 0, tzinfo=timezone.utc)
        proposal = _gateway_mod.propose(
            text,
            caller="exp-22-onchain-alert-sar-drafter",
            now=moment,
            rules_as_of=as_of,
            reversible=False,
        )
    except FileNotFoundError:
        summary["not_read"] = True
        summary["reason"] = "Experiment 08 is not beside this experiment."
        return summary
    except Exception as exc:
        summary["not_read"] = True
        summary["reason"] = type(exc).__name__
        return summary

    audit = proposal.get("audit_log") or {}
    types = []
    for finding in audit.get("findings") or []:
        if isinstance(finding, dict) and finding.get("entity_type"):
            types.append(finding["entity_type"])
    summary.update(
        {
            "called": True,
            "output_is_anonymised": False,
            "agent_may_release": False,
            "finding_count": len(types),
            "entity_types": types,
            "redacted_text": proposal.get("redacted_text"),
            "rules_stale": bool(audit.get("rules_stale")),
            "rules_pinned_on": audit.get("rules_pinned_on"),
            "raw_values_logged": False,
        }
    )
    return summary
