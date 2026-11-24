"""A sentence is supporting only when it states the requirement."""

from src.mapping import supports_registered_charity
from src.paraphrases import NEGATIVES, POSITIVES


def test_reworded_requirements_are_recalled():
    sentences = POSITIVES["registered_charity"]
    assert len(sentences) >= 20
    missed = [sentence for sentence in sentences if not supports_registered_charity(sentence)]
    assert not missed, missed


def test_negative_controls_are_not_support():
    sentences = NEGATIVES["registered_charity"]
    assert len(sentences) >= 20
    false = [sentence for sentence in sentences if supports_registered_charity(sentence)]
    assert not false, false
    caught = len(POSITIVES["registered_charity"])
    precision = caught / (caught + len(false))
    assert precision == 1.0


def test_shared_words_do_not_count_as_support():
    assert supports_registered_charity("The funder likes charities that work in England.") is False
    assert supports_registered_charity(
        "The registered office is in England and the charity number box is blank."
    ) is False
    assert supports_registered_charity(
        "Any group is eligible except where it is a registered charity in England."
    ) is False
