"""Shared synthetic case builder for the invoice tests. Not a real supplier."""

from __future__ import annotations

from src.rules import BANK_FINGERPRINT, SUPPLIER_NAME, SUPPLIER_VAT, render_invoice


def make_case(content: str | None = None, **kwargs) -> dict:
    if content is None:
        content = render_invoice()
    case = {
        "synthetic": True,
        "case_id": "syn-ap-001",
        "buyer_kind": "contracting_authority",
        "contract_exceptions": [],
        "match": {"type": "three_way", "failed": True},
        "received_on": "2026-10-01",
        "tolerances": {"price_pence": 0, "quantity": 0},
        "supplier_master": {
            "name": SUPPLIER_NAME,
            "vat_number": SUPPLIER_VAT,
            "bank_fingerprint": BANK_FINGERPRINT,
        },
        "purchase_order": {
            "number": "SYN-PO-44",
            "unit_price_pence": 500,
            "quantity": 10,
            "net_pence": 5000,
        },
        "goods_receipt": {"number": "SYN-GR-9", "quantity": 10},
        "known_invoice_numbers": [],
        "files": [
            {
                "file_id": "inv-1",
                "filename": "invoice.txt",
                "media_type": "text/plain",
                "document_date": "2026-10-01",
                "content": content,
            }
        ],
    }
    for key, value in kwargs.items():
        case[key] = value
    return case
