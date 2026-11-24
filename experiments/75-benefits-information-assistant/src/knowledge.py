"""Pinned synthetic pages. A caller-supplied page is not this set."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    from dates import as_date, parse_date
else:
    from .dates import as_date, parse_date

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "fixtures" / "knowledge_base.json"
DIRECTORY = ROOT / "fixtures" / "directory.json"

# A page is stale on its review-due date, including that date. Starter rule, not a statute.
STALE_ON_DUE_DATE = True


def load_pages() -> list[dict]:
    payload = json.loads(PAGES.read_text(encoding="utf-8"))
    pages = payload.get("pages")
    if not isinstance(pages, list):
        raise ValueError("pinned knowledge base has no pages")
    return pages


def load_directory() -> dict:
    payload = json.loads(DIRECTORY.read_text(encoding="utf-8"))
    if payload.get("synthetic") is not True or payload.get("fictional") is not True:
        raise ValueError("directory is not marked synthetic")
    return payload


def review_status(page: dict, on: date) -> dict:
    """Read the pinned dates. Unreadable dates are not replaced and are not quoted."""

    reviewed = parse_date(page.get("last_reviewed") if isinstance(page, dict) else None)
    due = parse_date(page.get("review_due") if isinstance(page, dict) else None)
    if reviewed.get("unparseable") or reviewed.get("ambiguous") or due.get("unparseable") or due.get("ambiguous"):
        return {
            "stale": True,
            "unreadable": True,
            "coerced": False,
            "quote": False,
            "last_reviewed": None,
            "review_due": None,
            "reason": reviewed.get("reason") or due.get("reason"),
        }
    due_day = as_date(due)
    reviewed_day = as_date(reviewed)
    if due_day is None or reviewed_day is None:
        return {
            "stale": True,
            "unreadable": True,
            "coerced": False,
            "quote": False,
            "last_reviewed": None,
            "review_due": None,
            "reason": "unreadable",
        }
    stale = on >= due_day
    return {
        "stale": stale,
        "unreadable": False,
        "coerced": False,
        "quote": not stale,
        "last_reviewed": reviewed_day.isoformat(),
        "review_due": due_day.isoformat(),
        "reason": "on_or_after_review_due" if stale else None,
    }


def find_pages(pages: list[dict], benefit: str, kind: str) -> list[dict]:
    found = [
        page
        for page in pages
        if page.get("benefit") == benefit and page.get("kind") == kind
    ]
    return sorted(found, key=lambda page: str(page.get("page_id")))


def page_diff(caller: object, pinned: list[dict]) -> list[dict]:
    """Describe a caller copy. Nothing here is applied."""

    if caller is None:
        return []
    if not isinstance(caller, list):
        return [{"kind": "caller_pages_not_a_list", "applied": False, "text_copied": False}]
    pinned_rows = {page.get("page_id"): page for page in pinned}
    diffs = []
    for row in caller:
        if not isinstance(row, dict):
            diffs.append({"kind": "caller_page_not_object", "applied": False, "text_copied": False})
            continue
        page_id = row.get("page_id")
        pinned_row = pinned_rows.get(page_id)
        if pinned_row is None:
            diffs.append({"page_id": page_id, "kind": "not_in_pinned", "applied": False, "text_copied": False})
            continue
        for field in ("body", "boundary", "review_due", "last_reviewed", "publisher", "url"):
            if row.get(field) != pinned_row.get(field):
                diffs.append(
                    {
                        "page_id": page_id,
                        "kind": "field_differs",
                        "field": field,
                        "applied": False,
                        "text_copied": False,
                    }
                )
    return diffs
