"""Small synthetic packs for the tests. No real personal data."""

from __future__ import annotations


def document(document_id, kind, value, fact="fact", line=None, extra_lines=(), reviewed_on="2026-10-12", status="current"):
    text = f"{fact}: {value}" if line is None else line
    lines = [{"line": 1, "text": text}]
    for offset, extra in enumerate(extra_lines, start=2):
        lines.append({"line": offset, "text": extra})
    return {
        "document_id": document_id,
        "title": document_id,
        "kind": kind,
        "status": status,
        "reviewed_on": reviewed_on,
        "pages": [{"page": 1, "paragraphs": [{"paragraph": 1, "lines": lines}]}],
        "fields": [{"fact_key": fact, "page": 1, "paragraph": 1, "line": 1, "value": value}],
    }


def pair(field_type, left, right, **overrides):
    pack = {
        "synthetic": True,
        "pack_id": "case-1",
        "facts": [{"fact_key": "fact", "field_type": field_type}],
        "documents": [
            document("left-doc", "form", left),
            document("right-doc", "contract", right),
        ],
    }
    pack.update(overrides)
    return pack
