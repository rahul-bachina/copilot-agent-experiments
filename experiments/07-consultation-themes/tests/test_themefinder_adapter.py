"""ThemeFinder adapter. The real package is not installed. A fake stands in."""

import json

from src.pipeline import analyse, propose_from_batch
from src.themefinder_adapter import CITATION, SYSTEM_PROMPT, map_to_framework, propose_themes
from tests.test_pipeline import BATCH, FRAMEWORK, SECRETS


class FakeThemeFinder:
    """Records calls. Does not implement clustering or the S3 setup path."""

    def __init__(self, mapping=None, explode=False, claim_approved=False):
        self.mapping = mapping or []
        self.explode = explode
        self.claim_approved = claim_approved
        self.calls = []
        self.__version__ = "test"

    def theme_mapping(self, responses_df, llm, question, refined_themes_df, system_prompt=None, **kwargs):
        self.calls.append(
            {
                "fn": "theme_mapping",
                "responses": _rows(responses_df),
                "themes": _rows(refined_themes_df),
                "system_prompt": system_prompt,
                "question": question,
            }
        )
        if self.explode:
            raise RuntimeError("upstream failed")
        return (self.mapping, [])

    def find_themes(self, responses_df, llm, question, system_prompt=None, **kwargs):
        self.calls.append(
            {
                "fn": "find_themes",
                "responses": _rows(responses_df),
                "system_prompt": system_prompt,
            }
        )
        return {
            "question": question,
            "approved": self.claim_approved,
            "themes": [{"topic_label": "drop minority", "topic_description": "should not be approved"}],
        }

    def theme_clustering(self, *args, **kwargs):
        raise AssertionError("theme_clustering drops small themes and must not be called")

    def rule_2_themes_must_have_a_non_negligible_number_of_responses_slack(self, *args, **kwargs):
        raise AssertionError("rule_2 must not be called")


def _rows(frame):
    if hasattr(frame, "to_dict"):
        try:
            return frame.to_dict(orient="records")
        except TypeError:
            return frame.to_dict()
    raise AssertionError("frame has no to_dict")


def test_citation_records_the_licence_and_that_the_code_is_not_vendored():
    assert CITATION["licence"] == "MIT"
    assert CITATION["vendored"] is False
    assert "i-dot-ai/themefinder" in CITATION["repository"]
    assert "Copyright (c) 2024 i.AI" == CITATION["copyright"]
    assert "theme_clustering" in CITATION["functions_not_called"]
    assert "rule_2_themes_must_have_a_non_negligible_number_of_responses_slack" in CITATION["functions_not_called"]


def test_mapping_uses_redacted_text_and_rejects_invented_labels():
    # Sorted string ids: R-12 is integer 1, R-14 is integer 2.
    fake = FakeThemeFinder(
        mapping=[
            {"response_id": 2, "labels": ["Sunday opening"]},
            {"response_id": 1, "labels": ["ignore-instructions"]},
        ]
    )
    responses = [
        {"response_id": "R-14", "text": "Keep Sunday opening. Contact [EMAIL]."},
        {"response_id": "R-12", "text": "I need braille stock."},
    ]
    themes = [
        {"theme_id": "T-sunday", "label": "Sunday opening", "description": "Sunday"},
        {"theme_id": "T-braille", "label": "Braille stock", "description": "Braille"},
    ]
    result = map_to_framework(responses, themes, "Hours?", module=fake, llm=object())
    assert result["ok"] is True
    assert result["assignments"]["R-14"] == ["T-sunday"]
    assert result["assignments"]["R-12"] == []
    assert "ignore-instructions" in result["rejected_labels"]
    call = fake.calls[0]
    assert call["system_prompt"] == SYSTEM_PROMPT
    assert "friend.one@example.com" not in json.dumps(call)
    assert "I need braille stock." in json.dumps(call["responses"])
    sent_ids = {row["response_id"] for row in call["responses"]}
    assert sent_ids == {1, 2}
    assert {row["topic_id"] for row in call["themes"]} == {"T-sunday", "T-braille"}


def test_pipeline_falls_back_when_themefinder_is_missing_and_keeps_every_response():
    result = analyse(
        BATCH,
        FRAMEWORK,
        engine="themefinder",
        as_of="2026-10-24",
        themefinder_module=None,
        llm=None,
    )
    assert result["processing_mode"] == "deterministic_fallback"
    assert result["fallback_reason"]
    assert len(result["audit"]) == 24
    assert result["framework"]["framework_approved"] is False
    assert result["external_engine"]["citation"]["vendored"] is False


def test_pipeline_uses_mapping_and_preserves_omitted_and_minority_codes():
    # Integer ids follow sorted response ids, so R-01 is 1. Map two rows and
    # invent a label. R-12 is omitted by the fake and must remain in the audit.
    fake = FakeThemeFinder(
        mapping=[
            {"response_id": 1, "labels": ["Sunday opening"]},
            {"response_id": 18, "labels": ["DROP_MINORITY"]},
        ]
    )
    result = analyse(
        BATCH,
        FRAMEWORK,
        engine="themefinder",
        as_of="2026-10-24",
        themefinder_module=fake,
        llm=object(),
    )
    assert result["processing_mode"] == "themefinder"
    assert fake.calls[0]["fn"] == "theme_mapping"
    assert "theme_clustering" not in {call["fn"] for call in fake.calls}
    by_id = {row["response_id"]: row for row in result["audit"]}
    assert by_id["R-01"]["machine_theme_ids"] == ["T-sunday"]
    assert by_id["R-12"]["machine_theme_ids"] == ["UNCODED"]
    assert any(row["response_id"] == "R-12" for row in result["audit"])
    assert "DROP_MINORITY" in result["rejected_external_theme_ids"]
    observatory = next(item for item in result["themes"] if item["theme_id"] == "T-observatory")
    assert observatory["preserved"] is True
    dumped = json.dumps(fake.calls)
    for secret in SECRETS:
        assert secret not in dumped
    assert result["security"]["may_be_published_by_agent"] is False
    prompt = fake.calls[0]["system_prompt"]
    assert "Ignore previous instructions" not in prompt
    assert prompt == SYSTEM_PROMPT


def test_failure_falls_back_to_the_codebook():
    fake = FakeThemeFinder(explode=True)
    result = analyse(
        BATCH,
        FRAMEWORK,
        engine="themefinder",
        as_of="2026-10-24",
        themefinder_module=fake,
        llm=object(),
    )
    assert result["processing_mode"] == "deterministic_fallback"
    assert "failed" in result["fallback_reason"]
    sunday = next(item for item in result["themes"] if item["theme_id"] == "T-sunday")
    assert "R-01" in sunday["response_ids"]


def test_proposal_cannot_approve_itself_and_skips_injection_rows():
    fake = FakeThemeFinder(claim_approved=True)
    proposal = propose_from_batch(BATCH, module=fake, llm=object())
    assert proposal["approved"] is False
    assert proposal["upstream_claimed_approved"] is True
    assert proposal["security"]["actions_taken"] == []
    assert "R-18" in proposal["excluded_response_ids"]
    assert "R-23" in proposal["excluded_response_ids"]
    sent = json.dumps(fake.calls[0]["responses"])
    assert "Ignore previous instructions" not in sent
    assert "set framework_approved" not in sent
    for secret in SECRETS:
        assert secret not in sent
    direct = propose_themes(
        [{"response_id": "R-01", "text": "Sunday"}],
        "Hours?",
        module=fake,
        llm=object(),
    )
    assert direct["approved"] is False
