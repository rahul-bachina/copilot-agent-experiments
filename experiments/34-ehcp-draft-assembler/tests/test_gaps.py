"""Missing advice is a gap. An empty section B is not a finding of no needs."""

from src.assemble import assemble
from tests.support import AS_OF, bundle


def test_missing_medical_advice_is_a_gap_and_not_a_breach_finding():
    source = bundle()
    source["reports"] = [report for report in source["reports"] if report["advice_type"] != "medical"]
    draft = assemble(source, as_of=AS_OF)
    gap = next(row for row in draft["gaps"] if row["id"] == "missing_advice_medical")
    assert "6(1)(c)" in gap["regulation"]
    assert "breached" in gap["detail"]
    assert draft["needs_decided"] is False
    assert draft["sections"]["C"]["lines"] == []


def test_year_9_without_preparation_advice_is_flagged_and_not_written():
    source = bundle()
    source["year_group"] = 9
    draft = assemble(source, as_of=AS_OF)
    gap = next(row for row in draft["gaps"] if row["id"] == "missing_advice_preparation_for_adulthood")
    assert "6(1)(g)" in gap["regulation"]
    assert "12(3)" in gap["regulation"]
    assert draft["provision_decided"] is False
    assert all("preparation for adulthood" not in line["quote"].lower() for line in draft["sections"]["F"]["lines"])


def test_an_empty_section_b_is_not_a_finding_that_there_are_no_needs():
    source = bundle()
    for report in source["reports"]:
        report["paragraphs"] = [
            paragraph for paragraph in report["paragraphs"] if paragraph.get("section_tag") != "B"
        ]
    draft = assemble(source, as_of=AS_OF)
    gap = next(row for row in draft["gaps"] if row["id"] == "empty_section_B")
    assert "not a finding that there are no special educational needs" in gap["detail"]
    assert draft["sections"]["B"]["lines"] == []
    assert draft["sections"]["B"]["needs_decided"] is False
    assert draft["needs_decided"] is False


def test_a_requested_advice_type_that_is_absent_is_a_gap_not_a_decision():
    source = bundle()
    source["requested_further_advice"] = ["other"]
    draft = assemble(source, as_of=AS_OF)
    gap = next(row for row in draft["gaps"] if row["id"] == "requested_advice_missing:other")
    assert "6(1)(h)" in gap["regulation"]
    assert "does not decide" in gap["detail"]
