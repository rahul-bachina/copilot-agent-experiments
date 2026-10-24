"""Pinned catalogue: FCA hosts only, stages stay pinned, PDFs stay closed."""

from datetime import date

from src.checklist import REQUIREMENTS
from src.sources import LAST_VERIFIED, SOURCES, source_by_id

ALLOWED_STAGES = {
    "in_force_expectation",
    "final_not_yet_in_force",
    "consultation",
    "planned_consultation",
}


def test_every_source_is_an_fca_page_opened_on_the_verification_date():
    assert LAST_VERIFIED == "2026-10-24"
    ids = []
    for source in SOURCES:
        ids.append(source["id"])
        assert source["url"].startswith("https://www.fca.org.uk/"), source["id"]
        assert source["last_verified"] == LAST_VERIFIED
        assert source["body_opened"] is True
        assert source["pdf_opened"] is False
        date.fromisoformat(source["page_published"])
        date.fromisoformat(source["page_last_updated"])
    assert len(ids) == len(set(ids))


def test_requirements_cite_only_pinned_sources_and_known_stages():
    catalogue = source_by_id()
    assert REQUIREMENTS
    for requirement in REQUIREMENTS:
        assert requirement["rule_stage"] in ALLOWED_STAGES
        assert requirement["source_ids"], requirement["id"]
        for source_id in requirement["source_ids"]:
            assert source_id in catalogue, requirement["id"]
        if requirement["rule_stage"] in {"consultation", "planned_consultation"}:
            assert requirement.get("mention_aliases")
            assert "signal_groups" not in requirement


def test_key_dates_are_the_ones_read_on_the_fca_pages():
    from src.sources import KEY_DATES

    by_id = {item["id"]: item for item in KEY_DATES}
    window = by_id["application-window"]
    assert window["opens"] == "2026-09-30"
    assert window["closes"] == "2027-02-28"
    assert by_id["regime-commencement"]["date"] == "2027-10-25"
    assert "expected" in by_id["regime-commencement"]["statement"]
    assert "starts" in by_id["regime-commencement"]["statement"]
    assert by_id["travel-rule-in-force"]["date"] == "2023-09-01"
    assert by_id["financial-promotions-regime"]["date"] == "2023-10-08"
