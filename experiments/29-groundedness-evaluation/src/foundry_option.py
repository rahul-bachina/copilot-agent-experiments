"""Describe the Microsoft Foundry groundedness evaluator. Do not call it.

The sentences are the ones stored in src/sources.py after the page was opened
on 3 November 2026. Nothing here is a score from that service.
"""

from __future__ import annotations

from typing import Any


def describe() -> dict[str, Any]:
    return {
        "called": False,
        "option": "builtin.groundedness",
        "preview_option": "Groundedness Pro",
        "preview_option_is_preview": True,
        "page_id": "foundry-rag-evaluators",
        "page": "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators",
        "opened_on": "2026-11-03",
        "documented_default_pass_threshold_on_1_to_5_scale": 3,
        "applied_to_this_report": False,
        "local_score_is_not_a_foundry_score": True,
        "foundry_score": None,
        "foundry_passed": None,
        "uk_region_on_the_page": False,
        "uk_region_availability": "unverified",
        "what_the_page_says": (
            "Groundedness is an LLM-judge. It needs a deployment_name. "
            "The page says scores run from 1 to 5 and the default pass threshold is 3. "
            "Groundedness Pro is marked preview, uses Azure AI Content Safety, and "
            "returns a boolean rather than that numeric score. This report does not "
            "call either one."
        ),
    }
