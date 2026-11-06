"""A stale document is not quoted. A stale pin is not cleared by the agent."""

from src.draft import draft_memo
from tests.support import load_sample

AS_OF = "2026-11-06"


def test_the_old_extract_is_not_quoted():
    draft = draft_memo(load_sample(), as_of=AS_OF)
    unused = draft["not_used"]
    assert any(row["document_id"] == "oldbureau" and row["quoted"] is False for row in unused)
    blob = " ".join(fact["text"] for fact in draft["facts"])
    assert "999999" not in blob
    assert "intake_or_document_not_current" in draft["do_not_rely_reasons"]
    assert draft["credit_decision"] is None


def test_a_stale_only_section_is_not_treated_as_current_evidence():
    payload = load_sample()
    payload["files"].append(
        {
            "file_id": "oldcovenant",
            "filename": "old-covenant.txt",
            "media_type": "text/plain",
            "document_date": "2024-01-01",
            "content": "The old note states a covenant to keep a ratio.\n",
        }
    )
    payload["documents"].append(
        {
            "document_id": "oldcovenant",
            "file_id": "oldcovenant",
            "title": "Old covenant",
            "status": "current",
            "reviewed_on": "2024-01-01",
            "pages": [
                {
                    "page": 1,
                    "paragraphs": [
                        {
                            "paragraph": 1,
                            "fact_key": "covenants",
                            "lines": [
                                {"line": 1, "text": "The old note states a covenant to keep a ratio."}
                            ],
                        }
                    ],
                }
            ],
        }
    )
    draft = draft_memo(payload, as_of=AS_OF)
    item = next(row for row in draft["checklist"]["items"] if row["id"] == "covenants")
    assert item["status"] == "evidenced_but_stale"
    assert item["sufficient"] is False
    assert item["decides_the_duty"] is False
    assert draft["sections"]["covenants"]["status"] == "not_stated"


def test_a_stale_pin_is_flagged_and_not_cleared():
    draft = draft_memo(load_sample(), as_of="2027-02-10", stale_after_days=90)
    assert draft["do_not_rely"] is True
    assert "source_pin_stale" in draft["do_not_rely_reasons"]
    opened = next(row for row in draft["sources"] if row["id"] == "uk-gdpr-article-22a")
    assert opened["stale"] is True
    boundary = next(row for row in draft["sources"] if row["id"] == "catalogue-boundary")
    assert boundary["stale"] is False
    unopened = next(row for row in draft["sources"] if row["id"] == "prin-2a-2-not-retrieved")
    assert unopened["opened"] is False
    assert unopened["quote"] is None
    assert unopened["stale"] is False
    assert draft["limit_set"] is None
    assert draft["network_called"] is False
