"""Shared loaders for Experiment 30 tests."""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_sample() -> dict:
    return json.loads((ROOT / "examples" / "sample_bundle.json").read_text(encoding="utf-8"))


def bundle(**overrides) -> dict:
    data = load_sample()
    data.update(overrides)
    return data


def run_bundle(as_of: str = "2026-11-03", stale_after_days: int = 90, **overrides):
    from src.generate import generate

    return generate(bundle(**overrides), as_of, stale_after_days)


def safety(report: dict) -> None:
    assert report["label"] == "DRAFT FOR MAINTAINER REVIEW"
    assert report["catalogue_id"] == "G008"
    assert report["autonomy"] == "A1"
    assert report["maintainer_approved"] is False
    assert report["merged"] is False
    assert report["pushed"] is False
    assert report["protected_branch_targeted"] is False
    assert report["agent_under_test_edited"] is False
    assert report["agent_under_test"]["edited"] is False
    assert report["pr_opened"] is False
    assert report["tests_applied"] is False
    assert report["foundry_evaluation_called"] is False
    assert report["foundry_option"]["called"] is False
    assert report["foundry_option"]["threshold_set"] is False
    assert report["model_called"] is False
    assert report["network_called"] is False
    assert report["a3_recommended"] is False
    assert report["actions_taken"] == []
    assert report["prompt_injection"]["followed"] is False
    assert report["draft_pr"]["opened"] is False
    assert report["draft_pr"]["merged"] is False
    assert report["draft_pr"]["base_branch"] is None
    summary = report["summary"]
    assert summary["drafted"] + summary["skipped_duplicate"] == summary["considered"]
    assert summary["observations_not_drafted"] == len(report["not_drafted"])
    drafted = [case for case in report["cases"] if case["status"] == "drafted"]
    skipped = [case for case in report["cases"] if case["status"] == "skipped_duplicate"]
    assert len(drafted) == summary["drafted"]
    assert len(skipped) == summary["skipped_duplicate"]
    case_files = [item for item in report["proposed_changes"]["files"] if item["role"] == "case"]
    assert len(case_files) == summary["drafted"]
    assert report["foundry_option"]["query_count"] == summary["drafted"]
    assert report["proposed_changes"]["written_into_agent_tree"] is False
    queries = next(item["content"] for item in report["proposed_changes"]["files"] if item["role"] == "foundry_queries")
    lines = [json.loads(line) for line in queries.splitlines() if line.strip()]
    assert len(lines) == summary["drafted"]
    assert all(set(line) == {"query"} for line in lines)
    skipped_inputs = {case["input"] for case in skipped}
    assert skipped_inputs.isdisjoint({line["query"] for line in lines})


def minimal(**overrides) -> dict:
    data = {
        "bundle_id": "syn-minimal",
        "agent_under_test": {
            "id": "syn-minimal-agent",
            "path": "agents/syn-minimal-agent",
            "skills": [],
            "tool_contract": {"operations": []},
        },
        "observations": [],
        "existing_tests": [],
    }
    data.update(copy.deepcopy(overrides))
    return data
