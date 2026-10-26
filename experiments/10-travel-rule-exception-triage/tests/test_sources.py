"""The pinned catalogue uses £800 and does not use the JMLSG euro figure."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.sources import (  # noqa: E402
    JMLSG_THRESHOLD_WORDS_NOT_USED,
    LAST_VERIFIED,
    SOURCES,
    THRESHOLD_GBP,
    UNVERIFIED,
)


def test_operative_threshold_is_800_pounds():
    assert THRESHOLD_GBP == 800
    assert JMLSG_THRESHOLD_WORDS_NOT_USED == "1,000 euros"
    assert "800" not in JMLSG_THRESHOLD_WORDS_NOT_USED


def test_every_source_was_opened_on_the_catalogue_date():
    assert LAST_VERIFIED == "2026-10-26"
    ids = [source["id"] for source in SOURCES]
    assert ids == [
        "mlr-part-7a",
        "si-2022-860",
        "si-2026-621-reg-32",
        "fca-travel-rule",
        "jmlsg-annex-i-2023",
        "jmlsg-revisions",
        "jmlsg-hmt-approval",
    ]
    for source in SOURCES:
        assert source["last_verified"] == LAST_VERIFIED
        assert source["body_opened"] is True
        assert source["url"].startswith("https://")
    hosts = " ".join(source["url"] for source in SOURCES)
    assert "legislation.gov.uk" in hosts
    assert "fca.org.uk" in hosts
    assert "jmlsg.org.uk" in hosts


def test_unverified_items_are_explicit():
    ids = {item["id"] for item in UNVERIFIED}
    assert "reasonable-time" in ids
    assert "jmlsg-approval-date" in ids
    assert "fca-statement-not-a-waiver" in ids
    assert "sanctions-and-poca-not-opened" in ids
