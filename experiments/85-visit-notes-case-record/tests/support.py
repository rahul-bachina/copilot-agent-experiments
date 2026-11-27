"""Shared synthetic visits for the tests."""

from __future__ import annotations

from copy import deepcopy


def visit(**overrides) -> dict:
    payload = {
        "synthetic": True,
        "visit_id": "VIS-UNIT",
        "service": "adult-social-care",
        "practitioner_ref": "PRAC-8501",
        "question_date": "2026-11-20",
        "visit_date": "2026-11-18",
        "subject_name": "Pat Example",
        "recording_consent": {"status": "given"},
        "protective_marking": "OFFICIAL-SENSITIVE",
        "retention": "Retain with the adult social care case file",
        "legal_hold": False,
        "lines": [
            {"n": 1, "speaker": "practitioner", "audio": "clear", "text": "Present: Alex Rowan, social worker, and Pat Example."},
            {"n": 2, "speaker": "person", "audio": "clear", "text": "I agree to this visit being recorded."},
            {"n": 3, "speaker": "person", "audio": "clear", "text": "I want to stay in my own home."},
            {"n": 4, "speaker": "practitioner", "audio": "clear", "text": "I observed that the hallway was clear."},
            {"n": 5, "speaker": "practitioner", "audio": "clear", "text": "We agreed that the social worker will phone the duty team by 19 November 2026. Owner: duty team."},
        ],
    }
    payload.update(overrides)
    return deepcopy(payload)


def approval(result: dict, **extra) -> dict:
    payload = {
        "item": "case-note",
        "decision": "approve",
        "approver_ref": "PRAC-8501",
        "visit_id": result["visit_id"],
        "content_hash": result["content_hash"],
        "pins_seen": True,
    }
    for key in result.get("required_acknowledgements") or []:
        payload[key] = True
    payload.update(extra)
    return payload
