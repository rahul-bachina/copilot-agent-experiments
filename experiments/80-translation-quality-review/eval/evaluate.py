"""Deterministic smoke test. Not a model evaluation.

Each case is one row. Seeded-error precision and recall, paraphrase
recall, and the alignment score are separate blocks and are not added
to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.review import prepare_review, reset_held  # noqa: E402
from src.seeded import alignment_report, paraphrase_report, seeded_report  # noqa: E402

DATASET = ROOT / "eval" / "synthetic_dataset.json"
LABEL = "DETERMINISTIC SMOKE TEST. Not a model evaluation. Not a translation-quality score."


def _run_case(case: dict) -> dict:
    reset_held()
    result = prepare_review(case["request"], as_of=case["as_of"])
    expect = case["expect"]
    errors = []
    observed_flags = sorted({row["type"] for row in result["flags"]})
    checks = {
        "outcome": result["outcome"],
        "no_issues": result["no_issues"],
        "published": result["published"],
        "sent": result["sent"],
        "overwritten": result["overwritten"],
        "translation_owned": result["translation_owned"],
        "instructions_followed": result["instructions_followed"],
        "sources_current": result["sources_current"],
        "bodies_withheld": result["bodies_withheld"],
        "caller_glossary_applied": result["caller_glossary_applied"],
        "marking": result["marking"]["applied"],
        "legal_hold": result["legal_hold"],
        "high_risk": bool(result["high_risk"]),
        "distress": result["distress"]["categories"],
        "cue_copied": result["distress"]["cue_copied"],
        "low_confidence_count": result["low_confidence_count"],
        "flags": observed_flags,
        "quality_score": result["quality_estimation"]["quality_score"],
        "checks": len(result["checks_performed"]),
    }
    for key, wanted in expect.items():
        if checks.get(key) != wanted:
            errors.append(f"{key}: {checks.get(key)!r} != {wanted!r}")
    if not result["checks_performed"]:
        errors.append("checks were not listed")
    if result["no_issues"]:
        if result["statement"] != "No issues found in the checks that were run.":
            errors.append("no-issues statement did not list that the checks were run")
    elif "no issues" in result["statement"].casefold():
        errors.append("statement said no issues")
    if result["quality_estimation"]["limited"] is not True:
        errors.append("quality estimation was not marked limited")
    if result["quality_estimation"]["score_used_to_clear_high_risk"] is not False:
        errors.append("a score was allowed to clear high-risk content")
    blob = json.dumps(result)
    if "07700900123" in blob or "desk@reedmarsh.example" in blob:
        errors.append("a phone number or email was copied")
    if result["distress"]["categories"] and "end my life" in json.dumps(result["excerpts"]):
        errors.append("a distress cue was copied")
    if result["human_approval"] is not None or result["translation_owned"] is not False:
        errors.append("the agent owned or approved the translation")
    return {
        "case_id": case["case_id"],
        "passed": not errors,
        "errors": errors,
    }


def evaluate() -> dict:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    cases = [_run_case(case) for case in dataset]
    passed = sum(1 for case in cases if case["passed"])
    # A case is one row. An error string is a failed case, not a third total.
    failed = sum(1 for case in cases if case["errors"])
    errors = 0
    summary = {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total_cases": len(cases),
    }
    return {
        "evaluation_label": LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "automatic_quality_estimation_limited": True,
        "summary": summary,
        "cases": cases,
        "seeded_errors": seeded_report(),
        "paraphrase_recall": paraphrase_report(),
        "alignment_score": alignment_report(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic translation-review smoke test.")
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = evaluate()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"{report['evaluation_label']}")
    print(f"Smoke test {summary['passed']}/{summary['total_cases']} passed")
    if summary["failed"] or summary["errors"] or summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        for case in report["cases"]:
            if case["errors"]:
                print(case["case_id"], case["errors"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
