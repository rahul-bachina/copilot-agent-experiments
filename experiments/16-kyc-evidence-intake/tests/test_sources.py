"""The checklist cites words that were read, and does not apply what was not opened."""

from __future__ import annotations

from src.review import review
from src.sources import QUOTES, SOURCES
from tests.support import AS_OF, PASSPORT, customer_file, file_row


def test_pinned_sources_match_the_pages_opened_on_27_october_2026():
    by_id = {source["id"]: source for source in SOURCES}
    assert by_id["mlr-2017-reg-28"]["body_opened"] is True
    assert by_id["mlr-2017-reg-33"]["body_opened"] is True
    assert by_id["mlr-2017-reg-40"]["body_opened"] is True
    assert by_id["poca-2002-s-333a"]["body_opened"] is True
    assert by_id["fca-ai-live-testing-cohort-2"]["body_opened"] is True
    assert by_id["si-2026-621-reg-19"]["body_opened"] is True
    assert by_id["jmlsg-part-i"]["body_opened"] is False
    assert by_id["jmlsg-part-i"]["title"] == "JMLSG Guidance, Part I"
    assert "FATF call for action country" in QUOTES["reg33_3_a"]
    assert "high-risk third country" in QUOTES["si_2026_621_reg19_b"]
    assert "five years" in QUOTES["reg40_3"]
    assert "paragraph (3)(b)(i)" in QUOTES["reg40_4"]
    assert "10 years" in QUOTES["reg40_4"]
    assert "ceiling" not in QUOTES["reg40_4"].lower()
    assert "likely to prejudice" in QUOTES["poca_333a_1_b"]
    for source in SOURCES:
        assert source["applied_as_a_decision"] is False
        assert source["last_verified"] == "2026-10-27"


def test_draft_carries_the_pin_and_does_not_apply_jmlsg():
    draft = review(
        customer_file([file_row("ID-014", PASSPORT, filename="passport.txt")]),
        as_of=AS_OF,
    )
    assert draft["sources_pinned_on"] == "2026-10-27"
    assert draft["sources_last_verified"] == "2026-10-27"
    assert draft["jmlsg_part_i_opened"] is False
    assert draft["regulation_35_opened"] is False
    assert draft["fatf_list_downloaded"] is False
    opened = {row["id"]: row["body_opened"] for row in draft["sources"]}
    assert opened["jmlsg-part-i"] is False
    assert opened["fca-ai-live-testing-cohort-2"] is True
    assert all(row["applied_as_a_decision"] is False for row in draft["sources"])
    identify = next(item for item in draft["checklist"]["cdd"] if item["id"] == "reg_28_2_a_identify")
    assert identify["requirement_words"] == QUOTES["reg28_2_a"]
