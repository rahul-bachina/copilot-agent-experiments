"""Shared builders for the synthetic request tests."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-10-20"


def requester(**overrides):
    row = {
        "name": "Alex North",
        "email": "alex.north@example.test",
        "date_of_birth": "1990-04-12",
        "address": "14 Harbour Lane",
        "postcode": "RM1 2AB",
        "reference": "CUS-4401",
        "phone": "07700900111",
    }
    row.update(overrides)
    return row


def document(document_id="DOC-1001", content="Case note for Alex North, reference CUS-4401.", **overrides):
    row = {
        "document_id": document_id,
        "filename": "case-note.txt",
        "system": "casework",
        "document_date": "2026-02-01",
        "protective_marking": "OFFICIAL",
        "legal_hold": False,
        "retention": "Keep until the case is closed",
        "about_ref": "CUS-4401",
        "content": content,
    }
    row.update(overrides)
    return row


def request(text="Please send all personal data you hold about me. My reference is CUS-4401.", **overrides):
    row = {
        "synthetic": True,
        "case_id": "SAR-8301",
        "channel": "email",
        "received_on": "2026-10-03",
        "officer_ref": "IGO-8301",
        "made_by": "data_subject",
        "identity_evidence_supplied": True,
        "requester": requester(),
        "text": text,
        "records": [document()],
    }
    row.update(overrides)
    return row


def approval_for(result, **overrides):
    body = {
        "item": "disclosure-approval",
        "decision": "approve_disclosure",
        "approver_ref": "IGO-8301",
        "case_id": result["case_id"],
        "content_hash": result["content_hash"],
        "redaction_decisions": {row["redaction_id"]: "accept" for row in result["redactions"]},
        "exemption_decisions": {row["exemption_id"]: "reject" for row in result["exemptions"]},
    }
    for key in result["required_acknowledgements"]:
        body[key] = True
    body.update(overrides)
    return body


def load_sample():
    return json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
