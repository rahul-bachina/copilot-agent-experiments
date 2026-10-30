"""The pin matches the pages opened on 30 October 2026."""

from src.sources import (
    LAST_VERIFIED,
    RISK_WARNING_CRYPTO,
    RISK_WARNING_CRYPTO_SHORT,
    SOURCES,
    source_by_id,
)


def test_every_source_was_opened_on_the_pin_date():
    assert LAST_VERIFIED == "2026-10-30"
    ids = [source["id"] for source in SOURCES]
    assert ids == [
        "fsma-s21",
        "fsma-s25",
        "fpo-26f",
        "fpo-73za",
        "fca-marketing",
        "cobs-4-2",
        "cobs-4-12a",
        "fca-foi-alerts-2026",
    ]
    for source in SOURCES:
        assert source["last_verified"] == LAST_VERIFIED
        assert source["body_opened"] is True
        assert source["url"].startswith("https://")


def test_crypto_warning_is_not_the_securities_warning():
    crypto = source_by_id()["cobs-4-12a"]
    assert "4.12A.11R(1)(d)" in crypto["notes"]
    assert "should not expect to be protected" in RISK_WARNING_CRYPTO
    assert "unlikely to be protected" not in RISK_WARNING_CRYPTO
    assert RISK_WARNING_CRYPTO.startswith(RISK_WARNING_CRYPTO_SHORT)


def test_marketing_page_gateway_sentence_is_not_overwritten():
    notes = source_by_id()["fca-marketing"]["notes"]
    assert "does not overwrite" in notes
    assert "Parliament" in notes or "parliament" in notes.lower()
    assert source_by_id()["fca-marketing"]["page_last_updated"] == "2026-02-06"


def test_sections_not_opened_stay_named_as_not_opened():
    notes = source_by_id()["fsma-s21"]["notes"] + source_by_id()["cobs-4-12a"]["notes"]
    assert "not opened" in notes
    assert "55NA" in notes
    assert "Annex 1R" in notes
