"""Shared builders for synthetic evidence-pack tests."""

from datetime import date

AS_OF = date(2026, 10, 28)
PERIOD_FROM = date(2026, 1, 1)
PERIOD_TO = date(2026, 10, 28)


def item(
    item_id,
    content,
    *,
    scope="correspondence",
    document_date="2026-10-01",
    title=None,
    source="Reedbank Borough Council case SYN-RB-100",
    media_type="text/plain",
    sha256=None,
):
    row = {
        "item_id": item_id,
        "title": title or f"{item_id}.txt",
        "source": source,
        "source_scope": scope,
        "document_date": document_date,
        "media_type": media_type,
        "content": content,
    }
    if sha256 is not None:
        row["sha256"] = sha256
    return row


def request(items, **extra):
    payload = {
        "synthetic": True,
        "request_id": "SYN-EP-001",
        "items": items,
    }
    payload.update(extra)
    return payload
