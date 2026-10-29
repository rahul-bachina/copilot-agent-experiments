"""Pins match the pages opened on 29 October 2026."""

from src.sources import NOT_OPENED, QUOTES, SOURCES, SOURCES_PINNED_ON, UKFIU_REASON_CHAR_LIMIT


def test_every_opened_source_is_dated():
    assert SOURCES_PINNED_ON.isoformat() == "2026-10-29"
    assert UKFIU_REASON_CHAR_LIMIT == 8000
    ids = [row["id"] for row in SOURCES]
    assert ids == [
        "poca-2002-s330",
        "poca-2002-s331",
        "poca-2002-s333a",
        "mlr-2017-reg-19",
        "mlr-2017-reg-21",
        "fca-mlr-application",
        "fca-regime-overview",
        "ukfiu-chapter-2",
        "copilot-studio-harnesses",
    ]
    assert all(row["body_opened"] is True for row in SOURCES)
    assert all(row["last_verified"] == "2026-10-29" for row in SOURCES)


def test_operative_words_are_the_ones_that_were_read():
    assert "nominated officer" in QUOTES["mlr_21_3"]
    assert "likely to prejudice" in QUOTES["poca_333a_1"]
    assert "on-chain" in QUOTES["fca_onchain_tool"]
    assert "large UK QCATPs" in QUOTES["fca_marc_onchain"]
    assert "Director General of the National Crime Agency" in QUOTES["poca_330_4"]


def test_unopened_authorities_are_named():
    joined = " ".join(NOT_OPENED)
    assert "333B" in joined
    assert "chapter 3" in joined
    assert "glossary" in joined
    assert "Financial Crime Guide" in joined
    assert "Terrorism Act" in joined
