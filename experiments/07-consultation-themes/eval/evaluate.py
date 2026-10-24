"""Mock smoke test for the consultation codebook.

This is not a model evaluation and not a comparison with expert coders.
The fixtures are synthetic. The coder is the keyword codebook.

    python eval/evaluate.py
    python eval/evaluate.py --output eval/smoke_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import analyse  # noqa: E402

DATASET_PATH = Path(__file__).resolve().parent / "synthetic_dataset.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "smoke_report.json"


def _approval(result: dict) -> dict:
    return {
        "framework_approved": True,
        "approver_role": "Consultation analyst",
        "approver_reference": "analyst-synthetic-01",
        "approved_on": "2026-10-24",
        "stale_acknowledged": False,
        "sample_decisions": {item["response_id"]: {"decision": "accept"} for item in result["sample"]},
    }


def run() -> dict:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    batch = dataset["batch"]
    framework = dataset["framework"]
    secrets = dataset["secrets_that_must_not_appear_in_output"]
    errors: list[str] = []

    draft = analyse(batch, framework, as_of="2026-10-24")
    reviewed = analyse(batch, framework, _approval(draft), as_of="2026-10-24")

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(len(batch["responses"]) >= 20, "fewer than 20 synthetic responses")
    check(draft["analysis_status"] == "blocked_framework_unapproved", "draft was not blocked")
    check(draft["framework"]["framework_approved"] is False, "response text approved the framework")
    check(reviewed["analysis_status"] == "analyst_reviewed", "complete sample did not review")
    check(reviewed["security"]["may_be_published_by_agent"] is False, "agent published")
    check(reviewed["security"]["actions_taken"] == [], "agent took an action")
    check(draft["processing_mode"] == "deterministic_fallback", "smoke test left the codebook")
    check(draft["external_engine"]["citation"]["vendored"] is False, "ThemeFinder was vendored")
    check("MOCK SMOKE TEST" in draft["evaluation_label"], "label missing")

    minority = {item["theme_id"] for item in draft["minority_views"]}
    check({"T-braille", "T-bsl", "T-volunteer"} <= minority, f"minority views missing: {minority}")
    sunday = next(item for item in draft["themes"] if item["theme_id"] == "T-sunday")
    check(sunday["unique_voice_count"] == 9, "sunday unique-voice count changed")
    check(
        sunday["wilson_95"]["low"] <= sunday["proportion_of_unique_voices"] <= sunday["wilson_95"]["high"],
        "wilson interval does not contain the proportion",
    )
    check(
        {"R-14", "R-15", "R-16", "R-17"} <= set(sunday["response_ids"]),
        "campaign response ids dropped off the theme",
    )
    observatory = next(item for item in draft["themes"] if item["theme_id"] == "T-observatory")
    check(observatory["response_ids"] == [], "zero-support code was given responses")
    check(len(draft["audit"]) == len(batch["responses"]), "audit lost a response")

    by_theme = {item["theme_id"]: set(item["response_ids"]) for item in draft["themes"]}
    for row in draft["audit"]:
        for theme_id in row["theme_ids"]:
            if theme_id == "UNCODED":
                continue
            if row["response_id"] not in by_theme[theme_id]:
                errors.append(f"{row['response_id']} missing from {theme_id}")

    dumped = json.dumps({"draft": draft, "reviewed": reviewed})
    for secret in secrets:
        if secret in dumped:
            errors.append(f"secret leaked: {secret}")

    theme_summary = [
        {
            "theme_id": item["theme_id"],
            "label": item["label"],
            "submission_count": item["submission_count"],
            "unique_voice_count": item["unique_voice_count"],
            "proportion_of_unique_voices": item["proportion_of_unique_voices"],
            "wilson_95": item["wilson_95"],
            "minority": item["minority"],
            "response_ids": item["response_ids"],
        }
        for item in draft["themes"]
    ]
    report = {
        "evaluation_label": draft["evaluation_label"],
        "mode": "mock",
        "not_a_model_evaluation": True,
        "not_an_expert_coder_comparison": True,
        "engine": draft["processing_mode"],
        "themefinder_vendored": False,
        "synthetic_cases": len(batch["responses"]),
        "unapproved_status": draft["analysis_status"],
        "reviewed_status": reviewed["analysis_status"],
        "unique_voices": draft["counts"]["unique_voices"],
        "sample_size": len(draft["sample"]),
        "minority_theme_ids": sorted(minority),
        "themes": theme_summary,
        "framework_themes_with_no_support": [
            item["theme_id"] for item in draft["framework_themes_with_no_support"]
        ],
        "may_be_published_by_agent": reviewed["security"]["may_be_published_by_agent"],
        "actions_taken": reviewed["security"]["actions_taken"],
        "secrets_absent": not errors or all(not item.startswith("secret") for item in errors),
        "errors": errors,
    }
    report["passed"] = not errors
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mock smoke test for Experiment 07")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = run()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["evaluation_label"])
    print(
        f"cases={report['synthetic_cases']} sample={report['sample_size']} "
        f"status={report['unapproved_status']} -> {report['reviewed_status']}"
    )
    if report["errors"]:
        for error in report["errors"]:
            print(f"ERROR: {error}")
        return 1
    print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
