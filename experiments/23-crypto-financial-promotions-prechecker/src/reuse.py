"""Call Experiments 03, 04, and 08 without copying their decisions.

Neighbour modules share names such as sources and injection. They are
loaded under a private module name, and those names are then removed
from sys.modules.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

EXPERIMENTS = Path(__file__).resolve().parents[2]

_COLLIDING = (
    "sources",
    "injection",
    "catalogue",
    "lifecycle",
    "inventory",
    "manifest_generator",
    "gateway",
    "identifiers",
    "detectors",
    "model_assist",
)

_gateway = None
_exp04_sources = None
_lifecycle = None
_inventory = None
_manifest = None


def _drop_collisions() -> None:
    for name in _COLLIDING:
        sys.modules.pop(name, None)


def _load(folder: str, filename: str, module_name: str):
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


def redact_promotion(text: str, *, as_of) -> dict:
    """Experiment 08 proposal. The original text is not returned."""

    global _gateway
    base = {
        "experiment": "08-uk-pii-redaction-gateway",
        "catalogue_id": "O005",
        "called": False,
        "not_read": False,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "finding_count": 0,
        "finding_types": [],
        "redacted_text": None,
        "rules_pinned_on": None,
        "rules_stale": None,
    }
    try:
        if _gateway is None:
            _gateway = _load(
                "08-uk-pii-redaction-gateway",
                "gateway.py",
                "exp08_gateway",
            )
        proposal = _gateway.propose(
            text,
            caller="exp-23-crypto-financial-promotions-prechecker",
            rules_as_of=as_of,
            reversible=False,
        )
    except FileNotFoundError:
        base["not_read"] = True
        base["reason"] = "Experiment 08 is not beside this experiment."
        return base
    except Exception as exc:
        base["not_read"] = True
        base["reason"] = type(exc).__name__
        return base

    audit = proposal.get("audit_log") or {}
    findings = audit.get("findings") or []
    types: list[str] = []
    for finding in findings:
        kind = finding.get("entity_type")
        if kind and kind not in types:
            types.append(kind)
    anonymisation = proposal.get("anonymisation") or {}
    release = proposal.get("release") or {}
    base.update(
        {
            "called": True,
            "output_is_anonymised": bool(anonymisation.get("output_is_anonymised")),
            "agent_may_release": bool(release.get("agent_may_release")),
            "finding_count": len(findings),
            "finding_types": types,
            "redacted_text": proposal.get("redacted_text"),
            "rules_pinned_on": audit.get("rules_pinned_on"),
            "rules_stale": audit.get("rules_stale"),
            "release_status": release.get("status"),
        }
    )
    if base["output_is_anonymised"] is not False or base["agent_may_release"] is not False:
        base["output_is_anonymised"] = False
        base["agent_may_release"] = False
        base["redacted_text"] = None
        base["note"] = "Experiment 08 returned an unexpected release flag. The text was dropped."
    return base


def experiment_04_pin() -> dict:
    """The marketing-page row Experiment 04 pinned. Not a gap conclusion."""

    global _exp04_sources
    base = {
        "experiment": "04-fca-cryptoasset-readiness",
        "catalogue_id": "UK02",
        "called": False,
        "gap_register_run": False,
        "not_read": False,
    }
    try:
        if _exp04_sources is None:
            _exp04_sources = _load(
                "04-fca-cryptoasset-readiness",
                "sources.py",
                "exp04_sources",
            )
    except FileNotFoundError:
        base["not_read"] = True
        base["reason"] = "Experiment 04 is not beside this experiment."
        return base
    except Exception as exc:
        base["not_read"] = True
        base["reason"] = type(exc).__name__
        return base

    catalogue = {row["id"]: row for row in _exp04_sources.SOURCES}
    marketing = catalogue.get("fca-marketing", {})
    base.update(
        {
            "called": True,
            "marketing_page_last_verified_by_experiment_04": marketing.get("last_verified"),
            "marketing_page_last_updated": marketing.get("page_last_updated"),
            "note": (
                "Experiment 04 opened the marketing page on the date in its pin "
                "and did not overwrite the gateway sentence. This draft does not "
                "re-score that policy pack and does not adopt a gap conclusion. "
                "This experiment re-opened the same URL on 30 October 2026. The "
                "page's last-updated date was still 6 February 2026."
            ),
        }
    )
    return base


def experiment_03(promotion: dict, *, as_of: str) -> dict:
    """Validate an inventory record. Do not apply a status. Do not approve a manifest."""

    global _lifecycle, _inventory, _manifest
    result = {
        "experiment": "03-agent-inventory-atrs-assurance",
        "catalogue_id": "G010",
        "inventory_attached": False,
        "lifecycle_called": False,
        "status_applied": False,
        "approved_by_this_tool": False,
        "approval_object_ignored": False,
        "manifest_generator_called": False,
        "manifest_approved": False,
        "approve_true_refused": None,
        "actions_taken": [],
    }
    record = promotion.get("inventory_record")
    if not isinstance(record, dict):
        result["note"] = (
            "No inventory record on this promotion. Experiment 03 was not "
            "asked to draft a manifest."
        )
        return result

    result["inventory_attached"] = True
    try:
        if _inventory is None:
            _inventory = _load(
                "03-agent-inventory-atrs-assurance",
                "inventory.py",
                "exp03_inventory",
            )
        if _lifecycle is None:
            _lifecycle = _load(
                "03-agent-inventory-atrs-assurance",
                "lifecycle.py",
                "exp03_lifecycle",
            )
        validated = _inventory.validate_record(record)
    except Exception as exc:
        result["not_read"] = True
        result["reason"] = type(exc).__name__
        return result

    controls = promotion.get("untrusted_controls")
    requested = None
    if isinstance(controls, dict):
        requested = controls.get("requested_lifecycle_status")
        if "approval" in controls or "s21_approver_decision" in controls:
            result["approval_object_ignored"] = True

    if isinstance(requested, str) and requested.strip():
        try:
            proposal = _lifecycle.propose_status_change(
                validated,
                requested.strip(),
                "Untrusted payload asked for a lifecycle change. This experiment records the proposal and does not apply it.",
                "untrusted-payload",
            )
            _updated, event = _lifecycle.apply_status_change(validated, proposal, None)
            result["lifecycle_called"] = True
            result["from_status"] = proposal.get("from_status")
            result["to_status"] = proposal.get("to_status")
            result["status_applied"] = bool(event.get("applied"))
            result["approved_by_this_tool"] = bool(event.get("approved_by_this_tool"))
            result["rejection"] = event.get("rejection")
        except Exception as exc:
            result["lifecycle_called"] = True
            result["status_applied"] = False
            result["lifecycle_error"] = type(exc).__name__
    else:
        result["note"] = "No lifecycle change was requested. None was proposed."

    if result["status_applied"] or result["approved_by_this_tool"]:
        result["status_applied"] = False
        result["approved_by_this_tool"] = False
        result["forced_off"] = True

    try:
        if _manifest is None:
            _manifest = _load(
                "03-agent-inventory-atrs-assurance",
                "manifest_generator.py",
                "exp03_manifest_generator",
            )
        try:
            _manifest.generate_manifest(validated, as_of, approve=True)
            result["approve_true_refused"] = False
        except Exception as exc:
            if type(exc).__name__ != "ProhibitedAction":
                raise
            result["approve_true_refused"] = True
        drafted = _manifest.generate_manifest(validated, as_of, approve=False)
        result["manifest_generator_called"] = True
        result["manifest_approved"] = bool(drafted.get("approved"))
        manifest = drafted.get("manifest") or {}
        autonomy = (manifest.get("autonomy") or {}).get("level")
        result["manifest_autonomy"] = autonomy
        result["manifest_validation_passed"] = bool(drafted.get("validation_passed"))
        if result["manifest_approved"] is not False:
            result["manifest_approved"] = False
            result["manifest_generator_called"] = False
            result["forced_off"] = True
    except ModuleNotFoundError as exc:
        result["manifest_generator_called"] = False
        result["manifest_generator_reason"] = exc.name or "ModuleNotFoundError"
    except Exception as exc:
        result["manifest_generator_called"] = False
        result["manifest_generator_reason"] = type(exc).__name__
    return result
