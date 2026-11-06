"""Load the synthetic Mereholt pack and small variants. No live firm is used."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_pack.json"


def load_sample() -> dict:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def pack_with(paragraphs: list[tuple[str, str]]) -> dict:
    """One current profile file plus the paragraphs named (field, text)."""
    payload = load_sample()
    payload.pop("comparisons", None)
    payload["files"] = [
        {
            "file_id": "profile",
            "filename": "company-profile.txt",
            "media_type": "text/plain",
            "document_date": "2026-10-20",
            "content": "The profile names the applicant as Mereholt Components Ltd.\n",
        }
    ]
    payload["documents"] = [
        {
            "document_id": "profile",
            "file_id": "profile",
            "title": "Company profile",
            "status": "current",
            "reviewed_on": "2026-10-20",
            "pages": [
                {
                    "page": 1,
                    "paragraphs": [
                        {
                            "paragraph": 1,
                            "fact_key": "company_profile",
                            "lines": [
                                {
                                    "line": 1,
                                    "text": "The profile names the applicant as Mereholt Components Ltd.",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ]
    if not paragraphs:
        return payload
    lines = [text for _field, text in paragraphs]
    payload["files"].append(
        {
            "file_id": "extra",
            "filename": "extra.txt",
            "media_type": "text/plain",
            "document_date": "2026-10-20",
            "content": "\n".join(lines) + "\n",
        }
    )
    extra_paragraphs = []
    for index, (field, text) in enumerate(paragraphs, start=1):
        extra_paragraphs.append(
            {
                "paragraph": index,
                "fact_key": field,
                "lines": [{"line": 1, "text": text}],
            }
        )
    payload["documents"].append(
        {
            "document_id": "extra",
            "file_id": "extra",
            "title": "Extra",
            "status": "current",
            "reviewed_on": "2026-10-20",
            "pages": [{"page": 1, "paragraphs": extra_paragraphs}],
        }
    )
    return payload


def without_comparisons(payload: dict | None = None) -> dict:
    copied = copy.deepcopy(payload or load_sample())
    copied.pop("comparisons", None)
    return copied
