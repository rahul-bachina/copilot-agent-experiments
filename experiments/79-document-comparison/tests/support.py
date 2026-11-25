"""Shared builders for synthetic comparison requests."""

from __future__ import annotations


def clause(clause_id: str, number: str, text: str, heading: str = "Clause") -> dict:
    return {"clause_id": clause_id, "number": number, "heading": heading, "text": text}


def request(left: list[dict], right: list[dict], **overrides) -> dict:
    payload = {
        "synthetic": True,
        "comparison_id": "CMP-7901",
        "reader_ref": "RDR-7901",
        "document_kind": "contract",
        "suggested_baseline_id": "v1",
        "versions": [
            {
                "version_id": "v1",
                "title": "Reedmarsh facilities agreement",
                "effective_date": "2024-04-01",
                "review_date": "2027-04-01",
                "protective_marking": "OFFICIAL",
                "legal_hold": False,
                "retention": ["keep 6 years from the end of the contract"],
                "clauses": left,
            },
            {
                "version_id": "v2",
                "title": "Reedmarsh facilities agreement",
                "effective_date": "2024-04-01",
                "review_date": "2027-04-01",
                "protective_marking": "OFFICIAL",
                "legal_hold": False,
                "retention": ["keep 6 years from the end of the contract"],
                "clauses": right,
            },
        ],
    }
    payload.update(overrides)
    return payload
