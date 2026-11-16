"""Protective markings come from metadata and from the page. The higher label wins."""

from src.handbook import higher_marking, legal_hold, markings_in, retention_labels


def test_secret_on_the_cover_outranks_official_metadata():
    labels = markings_in("OFFICIAL", "PROTECTIVE MARKING: SECRET\nA salary line.")
    assert higher_marking(labels) == "SECRET"


def test_a_conflict_takes_the_higher_label():
    labels = markings_in(
        "OFFICIAL-SENSITIVE",
        "PROTECTIVE MARKING: OFFICIAL\nPROTECTIVE MARKING: SECRET",
    )
    assert "OFFICIAL" in labels
    assert "SECRET" in labels
    assert higher_marking(labels) == "SECRET"


def test_official_sensitive_is_not_downgraded_to_official():
    labels = markings_in("OFFICIAL-SENSITIVE", "Ordinary handbook page.")
    assert labels == ["OFFICIAL-SENSITIVE"]
    assert higher_marking(labels) == "OFFICIAL-SENSITIVE"


def test_legal_hold_and_retention_are_kept_from_both_places():
    document = {"legal_hold": False, "retention_label": "Finance schedule"}
    text = "RETENTION: 7 years. LEGAL HOLD. Do not dispose."
    assert legal_hold(document, text) is True
    assert retention_labels(document, text) == [
        "Finance schedule",
        "7 years. LEGAL HOLD. Do not dispose.",
    ]
