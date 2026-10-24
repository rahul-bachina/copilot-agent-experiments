"""G006 prompt-injection findings and G007 groundedness findings.

Both evaluations return findings for a person. Neither clears the agent.
G006's checkpoint in the catalogue is a security reviewer. G007's checkpoint
is an evaluation owner approving thresholds. Those approvals are not recorded.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from catalogue import GAP_TEXT, STALE_AFTER_DAYS

INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"ignore (all |any |the )?(previous|prior) instructions", re.I)),
    ("mark_approved", re.compile(r"mark (this )?(agent|record|manifest|pack|status)?\s*approved", re.I)),
    ("set_lifecycle", re.compile(r"set (the )?lifecycle", re.I)),
    ("role_override", re.compile(r"you are now", re.I)),
    ("disregard_owner", re.compile(r"disregard the governance", re.I)),
    ("send_record", re.compile(r"\b(email|send) (this|the record|it)\b", re.I)),
    ("system_prompt", re.compile(r"system prompt", re.I)),
    ("exfiltrate", re.compile(r"exfiltrat", re.I)),
)


def evaluate_injection(record: dict[str, Any], extra_text: str = "") -> dict[str, Any]:
    findings = []
    for path, text in _strings(record):
        findings.extend(_match("inventory:" + path, text))
    if extra_text:
        findings.extend(_match("untrusted_instruction", extra_text))
    return {
        "catalogue_id": "G006",
        "name": "Prompt injection test",
        "autonomy": "A0",
        "checkpoint": "Security reviewer assesses findings",
        "security_review_status": "awaiting_security_reviewer",
        "cleared": False,
        "approved": False,
        "finding_count": len(findings),
        "findings": findings,
        "actions_taken": [],
    }


def evaluate_groundedness(
    record: dict[str, Any],
    atrs: dict[str, Any],
    playbook: dict[str, Any],
    as_of: str,
) -> dict[str, Any]:
    unsupported: list[dict[str, str]] = []
    for field in atrs["fields"]:
        state = field["answer_state"]
        key = field["inventory_key"]
        if state == "gap":
            if field["answer"] != GAP_TEXT or field["grounded_in"]:
                unsupported.append({"reference": field["reference"], "reason": "gap_text_mismatch"})
        elif state == "rejected_not_in_template_list":
            source = record.get(key)
            source_text = source.strip() if isinstance(source, str) else str(source)
            if field["answer"] != GAP_TEXT or field.get("source_value") != source_text:
                unsupported.append({"reference": field["reference"], "reason": "rejected_value_mismatch"})
        elif state == "draft_from_inventory":
            source = record.get(key)
            source_text = source.strip() if isinstance(source, str) else str(source).strip()
            if field["answer"] != source_text or field["grounded_in"] != [key]:
                unsupported.append({"reference": field["reference"], "reason": "not_copied_from_inventory"})
        else:
            unsupported.append({"reference": field["reference"], "reason": "unknown_answer_state"})

    for principle in playbook["principles"]:
        for item in principle["evidence"]:
            source = record.get(item["inventory_key"])
            source_text = source.strip() if isinstance(source, str) else str(source).strip()
            if item["quote"] != source_text:
                unsupported.append(
                    {
                        "reference": f"playbook-{principle['number']}",
                        "reason": "playbook_quote_not_in_inventory",
                    }
                )

    stale, stale_reason, age = _stale(record, as_of)
    return {
        "catalogue_id": "G007",
        "name": "Groundedness evaluation",
        "autonomy": "A0",
        "checkpoint": "Evaluation owner approves thresholds",
        "threshold_days": STALE_AFTER_DAYS,
        "threshold_approved_by_evaluation_owner": False,
        "stale": stale,
        "stale_reason": stale_reason,
        "age_days": age,
        "as_of": as_of,
        "unsupported_claim_count": len(unsupported),
        "unsupported_claims": unsupported,
        "groundedness_clearance": False,
        "approved": False,
        "actions_taken": [],
    }


def handle_untrusted(record: dict[str, Any], instruction: str, pack: dict[str, Any]) -> dict[str, Any]:
    """An instruction in free text is data. It is never executed."""
    findings = evaluate_injection(record, extra_text=instruction)
    return {
        "actions_taken": [],
        "approved": False,
        "sent": False,
        "published": False,
        "dataverse_written": False,
        "lifecycle_changed": False,
        "instruction_findings": findings["finding_count"],
        "pack_approved": pack["approved"],
    }


def _match(where: str, text: str) -> list[dict[str, str]]:
    found = []
    for code, pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            found.append({"where": where, "code": code})
    return found


def _strings(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((prefix or "value", value))
    elif isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found.extend(_strings(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_strings(item, f"{prefix}[{index}]"))
    return found


def _stale(record: dict[str, Any], as_of: str) -> tuple[bool, str, int | None]:
    reviewed = record.get("source_reviewed_on")
    try:
        reviewed_on = date.fromisoformat(reviewed)
        as_of_date = date.fromisoformat(as_of)
    except (TypeError, ValueError):
        return True, "review_date_missing_or_invalid", None
    age = (as_of_date - reviewed_on).days
    if age > STALE_AFTER_DAYS:
        return True, "older_than_draft_threshold", age
    if age < 0:
        return True, "review_date_after_as_of", age
    return False, "within_draft_threshold", age
