"""The normaliser decides the class. These cases are the rules, not a model."""

import pytest

from src.normalise import classify_values, normalise_value
from src.compare import compare
from tests.support import pair

CASES = [
    ("name", "Northfen Supplies Ltd", "NORTHFEN SUPPLIES LTD", "match", "same_display"),
    ("name", "Northfen Supplies Limited", "Northfen Supplies Ltd", "immaterial_difference", "formatting_or_abbreviation"),
    ("name", "Ms A Example", "A Example", "immaterial_difference", "formatting_or_abbreviation"),
    ("name", "Dr Martens Ltd", "Martens Ltd", "material_discrepancy", "normalised_values_differ"),
    ("name", "Northfen Supplies Ltd", "Northfen Trading Ltd", "material_discrepancy", "normalised_values_differ"),
    ("address", "1 Example Street", "1 Example St", "immaterial_difference", "formatting_or_abbreviation"),
    ("address", "1 Example Street", "1 Example Road", "material_discrepancy", "normalised_values_differ"),
    ("date", "1 March 2026", "2026-03-01", "immaterial_difference", "formatting_or_abbreviation"),
    ("date", "01/02/2026", "2026-01-02", "material_discrepancy", "normalised_values_differ"),
    ("date", "01/02/2026", "2026-02-01", "immaterial_difference", "formatting_or_abbreviation"),
    ("date", "29/02/2026", "2026-02-28", "material_discrepancy", "unparseable"),
    ("date", "next Tuesday", "next Tuesday", "match", "same_unparsed_text"),
    ("date", "next Tuesday", "next Wednesday", "material_discrepancy", "unparseable"),
    ("currency", "GBP 1,250.00", "GBP 1250", "immaterial_difference", "formatting_or_abbreviation"),
    ("currency", "GBP 1250.00", "GBP 1250.50", "material_discrepancy", "normalised_values_differ"),
    ("currency", "\u00a31250.00", "GBP 1250.00", "immaterial_difference", "formatting_or_abbreviation"),
    ("postcode", "SW1A 1AA", "sw1a1aa", "immaterial_difference", "formatting_or_abbreviation"),
    ("postcode", "SW1A 1AA", "SW1A 2AA", "material_discrepancy", "normalised_values_differ"),
    ("company_number", "88990011", "8899 0011", "immaterial_difference", "formatting_or_abbreviation"),
    ("company_number", "08899001", "8899001", "immaterial_difference", "formatting_or_abbreviation"),
    ("company_number", "88990011", "88990022", "material_discrepancy", "normalised_values_differ"),
    ("company_number", "SC991122", "sc 991122", "immaterial_difference", "formatting_or_abbreviation"),
    ("company_number", "ZZ123456", "ZZ123456", "match", "same_unparsed_text"),
    ("company_number", "ZZ123456", "ZZ 123456", "material_discrepancy", "unparseable"),
    ("figure", "30 days", "30 day", "immaterial_difference", "formatting_or_abbreviation"),
    ("figure", "30 days", "45 days", "material_discrepancy", "normalised_values_differ"),
    ("figure", "30 days", "30", "material_discrepancy", "normalised_values_differ"),
    ("reference", "NF-1001", "nf-1001", "match", "same_display"),
    ("reference", "NF-1001", "NF-1002", "material_discrepancy", "normalised_values_differ"),
]


@pytest.mark.parametrize("field_type,left,right,expected_class,expected_reason", CASES)
def test_pair_class(field_type, left, right, expected_class, expected_reason):
    draft = compare(pair(field_type, left, right), "2026-11-05")
    fact = draft["facts"][0]
    assert fact["classification"] == expected_class
    assert fact["reason"] == expected_reason
    assert fact["agent_chose_source"] is False
    assert fact["correct_value"] is None
    assert draft["model_called"] is False


def test_company_prefix_comes_from_experiment_08():
    from src.siblings import load

    prefixes = load()["identifiers"].CRN_PREFIXES
    assert "SC" in prefixes
    assert "ZZ" not in prefixes
    canonical, accepted = normalise_value("company_number", "SC991122")
    assert accepted and canonical == "SC991122"


def test_day_first_date_is_not_a_us_date():
    february, accepted = normalise_value("date", "01/02/2026")
    assert accepted and february == "2026-02-01"
    january, accepted = normalise_value("date", "2026-01-02")
    assert accepted and january == "2026-01-02"
    assert february != january


def test_classify_refuses_a_single_value():
    with pytest.raises(ValueError):
        classify_values([("a", "a", True)])
