"""Theme assignment. One theme per record. The owner still has to validate it."""

from classify import classify_energy, classify_housing


def test_housing_damp_beats_a_later_repairs_word():
    result = classify_housing("There is mould and the heating has failed.")
    assert result["theme"] == "damp_mould"
    assert result["matched_phrase"] == "mould"
    assert result["source"] == "housing_starter_lexicon"


def test_housing_without_a_phrase_is_unassigned():
    result = classify_housing("The close is quiet.")
    assert result["theme"] == "unassigned"
    assert result["assignment_reason"] == "no_lexicon_phrase"


def test_energy_billing_on_a_classic_meter_is_b13():
    result = classify_energy(
        "The bill is wrong and it is not a smart meter.",
        None,
    )
    assert result["theme"] == "B13"
    assert result["meter_context"] == "classic_credit"
    assert result["meter_context_source"] == "narrative_hint"


def test_energy_billing_without_a_meter_is_not_forced_into_b22():
    result = classify_energy("The bill is wrong.", None)
    assert result["theme"] == "unassigned"
    assert result["assignment_reason"] == "meter_context_required"


def test_energy_record_meter_overrides_a_contradictory_hint():
    result = classify_energy(
        "The bill is wrong and it is not a smart meter.",
        "smart_credit",
    )
    assert result["theme"] == "B14"
    assert result["meter_context_source"] == "record"


def test_energy_customer_service_does_not_need_a_meter():
    result = classify_energy("I was on hold for an hour.", None)
    assert result["theme"] == "B9"


def test_energy_unknown_meter_value_is_not_echoed_as_a_category():
    result = classify_energy("The bill is wrong.", "some other meter")
    assert result["theme"] == "unassigned"
    assert result["meter_context"] is None
    assert result["meter_context_source"] == "record_not_in_closed_list"
