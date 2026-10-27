"""Shared builders for synthetic customer files. No real person or firm."""

from __future__ import annotations

from datetime import date

AS_OF = date(2026, 10, 27)


def file_row(
    file_id: str,
    content: str,
    *,
    filename: str = "note.txt",
    media_type: str = "text/plain",
    document_date: str = "2026-09-15",
    sha256: str | None = None,
) -> dict:
    row = {
        "file_id": file_id,
        "filename": filename,
        "media_type": media_type,
        "document_date": document_date,
        "content": content,
    }
    if sha256 is not None:
        row["sha256"] = sha256
    return row


def customer_file(files: list[dict], **extra) -> dict:
    body = {
        "synthetic": True,
        "firm": {
            "name": "Marrowgate Payments Limited",
            "firm_reference": "SYN-FRN-440016",
            "note": "Fictional firm. Not an authorised person. The reference is not an FCA FRN.",
        },
        "customer_file_id": "MG-KYC-014",
        "customer_ref": "SYN-CUST-014",
        "customer_type": "natural_person",
        "relationship": "business_relationship",
        "relationship_status": "ongoing",
        "files": files,
    }
    body.update(extra)
    return body


PASSPORT = (
    "Passport\n"
    "Synthetic customer SYN-CUST-014.\n"
    "National Insurance number QQ 12 34 56 A is not allocatable.\n"
    "This text is synthetic.\n"
)
ADDRESS = (
    "Proof of address\n"
    "Council tax bill for the synthetic household at 1 Example Street.\n"
    "NHS number 999 000 0018.\n"
    "Postcode ZZ99 9ZZ.\n"
    "Sort code 00-00-00.\n"
    "Purpose of the relationship: paying household bills.\n"
    "This text is synthetic. It is not a real bill.\n"
)
