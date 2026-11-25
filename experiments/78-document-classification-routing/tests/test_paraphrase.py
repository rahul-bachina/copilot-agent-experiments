"""Reworded risk sentences are recalled. Negatives are not counted."""

from src.cues import category_hit
from src.paraphrases import NEGATIVES, POSITIVES


def test_each_risk_category_has_twenty_reworded_sentences():
    for name, sentences in POSITIVES.items():
        assert len(sentences) >= 20, name
        missed = [sentence for sentence in sentences if not category_hit(name, sentence)]
        assert missed == [], (name, missed)
        false = [sentence for sentence in NEGATIVES[name] if category_hit(name, sentence)]
        assert false == [], (name, false)
        caught = len(sentences)
        precision = caught / (caught + len(false))
        assert precision == 1.0
