"""Shared builders. The organisation and the wordings are fictional."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_pack.json"

COVERAGE = (
    "The wording covers physical loss of or damage to the buildings at "
    "Example Wharf during the period of insurance."
)
FLOOD = "The wording excludes loss or damage caused by flood."


def load_sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def _file(file_id: str, content: str, document_date: str = "2026-10-20") -> dict:
    return {
        "file_id": file_id,
        "filename": f"{file_id}.txt",
        "media_type": "text/plain",
        "document_date": document_date,
        "content": content,
    }


def _document(file_id: str, paragraphs: list[dict], *, reviewed_on: str = "2026-10-20") -> dict:
    return {
        "document_id": file_id,
        "file_id": file_id,
        "title": file_id,
        "status": "current",
        "reviewed_on": reviewed_on,
        "pages": [{"page": 1, "paragraphs": paragraphs}],
    }


def clause(paragraph: int, topic: str, subject: str, clause_ref: str, text: str) -> dict:
    return {
        "paragraph": paragraph,
        "topic": topic,
        "subject": subject,
        "clause_ref": clause_ref,
        "lines": [{"line": 1, "text": text}],
    }


def wording(wording_id: str, paragraphs: list[dict], *, role: str, extra_content: str = "") -> dict:
    lines = [paragraph["lines"][0]["text"] for paragraph in paragraphs]
    content = (
        f"Synthetic wording {wording_id}. Northfen Wharf Ltd is fictional.\n"
        + "\n".join(lines)
        + "\n"
        + extra_content
    )
    return {
        "wording_id": wording_id,
        "role": role,
        "caller_label": wording_id,
        "files": [_file(f"{wording_id}-file", content)],
        "documents": [_document(f"{wording_id}-file", paragraphs)],
    }


def pack_with(*wordings: dict, market: str | None = "commercial_non_consumer", pack_id: str = "NF-WORD-TEST") -> dict:
    payload = {
        "synthetic": True,
        "pack_id": pack_id,
        "organisation": "Northfen Wharf Ltd",
        "wordings": list(wordings),
    }
    if market is not None:
        payload["market"] = market
    return payload


def pair(expiring_paragraphs: list[dict], renewal_paragraphs: list[dict], **kwargs) -> dict:
    return pack_with(
        wording("expiring", expiring_paragraphs, role="expiring"),
        wording("renewal", renewal_paragraphs, role="renewal_quote"),
        **kwargs,
    )
