"""Tool schemas stay least-privilege. The agent cannot take a decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _tools() -> list[dict]:
    payload = json.loads((ROOT / "schema" / "tools.json").read_text(encoding="utf-8"))
    return payload["tools"]


def test_callable_tools_do_not_write_or_send():
    callable_names = {
        "extract_cited_summary",
        "check_pinpoint_citations",
        "list_gaps_and_contradictions",
    }
    by_name = {tool["name"]: tool for tool in _tools()}
    assert set(by_name) >= callable_names
    for name in callable_names:
        tool = by_name[name]
        assert tool["callable_by_agent"] is True
        assert tool["writes"] is False
        assert tool["sends"] is False
        assert tool["human_approval_to_rely_on_output"] is True


def test_prohibited_tools_are_not_callable():
    by_name = {tool["name"]: tool for tool in _tools()}
    for name in (
        "recommend_outcome",
        "decide_disclosure",
        "find_credibility",
        "accept_summary",
        "send_external",
        "write_production_record",
    ):
        tool = by_name[name]
        assert tool["callable_by_agent"] is False
        assert tool["always_raises"] is True
        assert tool["writes"] is False
        assert tool["sends"] is False
    review = by_name["record_sentence_review"]
    assert review["callable_by_agent"] is False
    assert review["always_raises"] is False
