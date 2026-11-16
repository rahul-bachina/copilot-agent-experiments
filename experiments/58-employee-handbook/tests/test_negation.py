"""Negation is about the phrase, not a bag of words."""

from src.handbook import source_denies, source_includes


def test_not_true_that_includes_is_not_an_inclusion():
    text = "It is not true that the expenses policy includes client entertainment."
    assert "includes client entertainment" in text
    assert source_includes(text, "client entertainment") is False
    assert source_denies(text, "client entertainment") is True


def test_a_later_positive_sentence_can_still_include_a_different_phrase():
    text = (
        "It is not true that the expenses policy includes client entertainment. "
        "The policy includes travel and subsistence."
    )
    assert source_includes(text, "client entertainment") is False
    assert source_includes(text, "travel") is True
    assert source_denies(text, "travel") is False


def test_is_not_part_of_denies_the_phrase_before_it():
    text = "Buying extra days is not part of this policy."
    assert source_includes(text, "buying extra days") is False
    assert source_denies(text, "buying extra days") is True
