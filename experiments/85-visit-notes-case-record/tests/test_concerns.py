"""At least 20 paraphrases per concern. Recall is reported, not assumed."""

from src.concerns import affirmed_categories, hits, routed
from src.paraphrases import CATEGORIES, NEGATED_ROUTE


def test_each_category_has_twenty_paraphrases_and_full_recall():
    scored = {}
    for name, row in CATEGORIES.items():
        sentences = row["sentences"]
        assert len(sentences) >= 20, name
        if not row["expect_match"]:
            false_inclusions = [text for text in sentences if routed(text)]
            assert false_inclusions == [], false_inclusions
            scored[name] = {"recall": None, "false_inclusions": 0}
            continue
        caught = 0
        affirmed = 0
        for text in sentences:
            found = hits(text)
            if any(item["category"] == name for item in found):
                caught += 1
            if name in affirmed_categories(text):
                affirmed += 1
        recall = caught / len(sentences)
        affirmed_recall = affirmed / len(sentences)
        assert recall == 1.0, name
        assert affirmed_recall == 1.0, name
        scored[name] = {"recall": recall, "affirmed_recall": affirmed_recall}
    assert set(scored) >= {
        "safeguarding",
        "self_neglect",
        "domestic_abuse",
        "distress",
        "suicidal",
        "financial_abuse",
        "capacity",
        "negative_control",
    }


def test_a_negated_stem_is_routed_and_not_affirmed():
    assert len(NEGATED_ROUTE) >= 7
    for text in NEGATED_ROUTE:
        found = hits(text)
        assert found, text
        assert all(item["affirmed"] is False for item in found), text
        assert all(item["assessment_made"] is False for item in found)


def test_negative_controls_are_not_a_weak_match():
    for text in CATEGORIES["negative_control"]["sentences"]:
        assert routed(text) is False
        assert "diagnosis of dementia" not in affirmed_categories(text)
