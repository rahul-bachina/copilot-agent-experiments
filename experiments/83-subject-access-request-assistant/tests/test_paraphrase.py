"""Paraphrase recall. A miss is a failure. Negation is not a positive exemption."""

from src.cues import (
    complaint_hit,
    distress_hit,
    grievance_hit,
    litigation_hit,
    safeguarding_hit,
    sensitive_categories,
    whistleblowing_hit,
)
from src.exemptions import phrase_hits
from src.paraphrases import CATEGORIES
from src.sar import reset_held, scope
from tests.support import AS_OF, request


HITS = {
    "distress": distress_hit,
    "safeguarding": safeguarding_hit,
    "whistleblowing": whistleblowing_hit,
    "complaint": complaint_hit,
    "grievance": grievance_hit,
    "litigation": litigation_hit,
    "privilege": lambda text: any(row["paragraph"] == "19" for row in phrase_hits(text)),
    "unrelated": lambda text: bool(sensitive_categories(text)) or bool(phrase_hits(text)),
    "exemption_negation": lambda text: bool(phrase_hits(text)),
}


def test_reworded_categories_report_full_recall_and_negative_controls_do_not_match():
    for name, spec in CATEGORIES.items():
        sentences = spec["sentences"]
        assert len(sentences) >= 20, name
        hit = HITS[name]
        matched = sum(1 for sentence in sentences if hit(sentence))
        if spec["expect_match"]:
            assert matched == len(sentences), name
            recall = matched / len(sentences)
            assert recall == 1.0
        else:
            assert matched == 0, name


def test_a_reworded_distress_sentence_is_routed_and_not_copied():
    reset_held()
    sentence = CATEGORIES["distress"]["sentences"][7]
    result = scope(
        request(case_id="SAR-8330", text=sentence + " Reference CUS-4401."),
        as_of=AS_OF,
    )
    assert result["outcome"] == "route_to_human"
    assert "distress" in result["sensitive"]["categories"]
    assert result["sensitive"]["cue_copied"] is False
    assert "alive" not in json_blob(result)


def json_blob(result) -> str:
    import json
    return json.dumps(result)
