"""Shared builders. Organisations and addresses are fictional."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_submission.json"


def load_sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def file_row(file_id: str, content: str, document_date: str = "2026-10-20") -> dict:
    return {
        "file_id": file_id,
        "filename": f"{file_id}.txt",
        "media_type": "text/plain",
        "document_date": document_date,
        "content": content,
    }


def document(file_id: str, paragraphs: list[tuple[str, str]], *, reviewed_on: str = "2026-10-20", status: str = "current") -> dict:
    return {
        "document_id": file_id,
        "file_id": file_id,
        "title": file_id,
        "status": status,
        "reviewed_on": reviewed_on,
        "pages": [
            {
                "page": 1,
                "paragraphs": [
                    {
                        "paragraph": index,
                        "fact_key": field,
                        "lines": [{"line": 1, "text": text}],
                    }
                    for index, (field, text) in enumerate(paragraphs, start=1)
                ],
            }
        ],
    }


def submission_with(paragraphs: list[tuple[str, str]], **extra) -> dict:
    text = "\n".join(line for _field, line in paragraphs)
    payload = {
        "synthetic": True,
        "submission_id": "NF-SUB-TEST",
        "organisation": "Northfen Wharf Ltd",
        "market": "commercial_non_consumer",
        "files": [file_row("doc", text + "\nThis text is synthetic.\n")],
        "documents": [document("doc", paragraphs)],
    }
    payload.update(extra)
    return payload


def clone(payload: dict) -> dict:
    return copy.deepcopy(payload)
