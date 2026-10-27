"""The catalogue is fictional, and every page refuses to decide."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.catalogue import ARTICLES, COUNCIL  # noqa: E402

_DECIDES = re.compile(r"you (qualify|are eligible|have been awarded|are entitled)", re.IGNORECASE)
_PHONE = re.compile(r"\b0\d{4,}\b")


def test_council_is_fictional():
    assert COUNCIL["fictional"] is True
    assert COUNCIL["name"] == "Northmarsh Borough Council"


def test_every_page_is_a_quotation_source_not_a_decision():
    ids = [article["id"] for article in ARTICLES]
    assert len(ids) == len(set(ids))
    for article in ARTICLES:
        assert article["url"].startswith("https://www.northmarsh.example.gov.uk/")
        assert article["kind"] in {"routine", "statutory_contact"}
        assert _DECIDES.search(article["body"]) is None
        assert _PHONE.search(article["body"]) is None
        assert "collected on Wednesday" not in article["body"] or article["id"] == "waste-example-ward"
