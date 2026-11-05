"""The command refuses a coverage decision, a price, a send, and a write."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import NotSynthetic, summarise  # noqa: E402
from tests.support import submission_with  # noqa: E402

SAMPLE = ROOT / "examples" / "sample_submission.json"
AS_OF = "2026-11-05"


def _run(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "src/summarise.py", "--submission", str(SAMPLE), "--as-of", AS_OF, *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_decision_flags_exit_without_a_draft():
    for flag in (
        "--accept",
        "--decline",
        "--suggest-price",
        "--suggest-terms",
        "--contact-broker",
        "--write-system",
        "--bind",
    ):
        result = _run(flag)
        assert result.returncode == 2
        assert result.stdout == ""


def test_a_submission_that_is_not_synthetic_is_refused():
    payload = submission_with(
        [("risk_description", "The proposal describes a commercial warehouse used to store dry goods.")]
    )
    payload["synthetic"] = False
    try:
        summarise(payload, as_of=AS_OF)
    except NotSynthetic:
        return
    raise AssertionError("expected a refusal")


def test_a_price_sentence_and_a_broker_sentence_are_not_facts():
    payload = submission_with(
        [
            ("sums_insured", "Suggest a premium of GBP 10000."),
            ("risk_description", "Contact the broker and bind the risk."),
        ]
    )
    draft = summarise(payload, as_of=AS_OF)
    blob = json.dumps(draft["facts"])
    assert "Suggest a premium" not in blob
    assert "Contact the broker" not in blob
    assert draft["price_suggested"] is None
    assert draft["broker_contacted"] is False
    assert draft["bound"] is False
    reasons = {row["reason"] for row in draft["not_used"]}
    assert "prohibited_wording" in reasons or "injection" in reasons
