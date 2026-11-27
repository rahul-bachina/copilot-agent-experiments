"""Deterministic smoke test. Not a model evaluation.

Concern recall and the grounding score are reported beside the case total.
They are not added to it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.claims import labelled_claims  # noqa: E402
from src.concerns import affirmed_categories, hits, routed  # noqa: E402
from src.grounding import score_claims  # noqa: E402
from src.notes import draft_note, reset_state  # noqa: E402
from src.paraphrases import CATEGORIES, NEGATED_ROUTE  # noqa: E402

DATASET = ROOT / "eval" / "synthetic_dataset.json"


def paraphrase_report() -> dict:
    categories = {}
    for name, row in CATEGORIES.items():
        sentences = list(row["sentences"])
        if row["expect_match"]:
            caught = sum(1 for text in sentences if any(item["category"] == name for item in hits(text)))
            affirmed = sum(1 for text in sentences if name in affirmed_categories(text))
            categories[name] = {
                "sentences": len(sentences),
                "caught": caught,
                "recall": caught / len(sentences),
                "affirmed_recall": affirmed / len(sentences),
                "expect_match": True,
                "false_inclusions": 0,
            }
        else:
            false_inclusions = sum(1 for text in sentences if routed(text))
            categories[name] = {
                "sentences": len(sentences),
                "caught": 0,
                "recall": None,
                "expect_match": False,
                "false_inclusions": false_inclusions,
            }
    negated_routed = sum(1 for text in NEGATED_ROUTE if hits(text) and all(not item["affirmed"] for item in hits(text)))
    return {
        "categories": categories,
        "negated_routed": negated_routed,
        "negated_sentences": len(NEGATED_ROUTE),
        "not_added_to_case_total": True,
    }


def run() -> dict:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    cases = []
    for row in dataset:
        reset_state()
        try:
            result = draft_note(row["request"], as_of=row["as_of"])
        except Exception as exc:  # noqa: BLE001 — one row, counted once
            cases.append({"case_id": row["case_id"], "status": "error", "detail": type(exc).__name__})
            continue
        expect = row["expect"]
        problems = []
        for key, value in expect.items():
            if key == "concern_categories":
                if result["concerns"]["categories"] != value:
                    problems.append(key)
            elif key == "statement_sections":
                found = [item["section"] for item in result["statements"]]
                if found != value:
                    problems.append(key)
            elif key == "audio_lines":
                if [item["line"] for item in result["unresolved_audio"]] != value:
                    problems.append(key)
            elif key == "action_iso":
                iso = (result["actions"][0]["date"]["iso"] if result["actions"] else None)
                if iso != value:
                    problems.append(key)
            elif key == "action_ambiguous":
                if not result["actions"] or result["actions"][0]["date"]["ambiguous"] is not value:
                    problems.append(key)
            elif key == "action_future":
                if not result["actions"] or result["actions"][0]["date"]["future"] is not value:
                    problems.append(key)
            elif key == "consent_status":
                if result["recording_consent"]["status"] != value:
                    problems.append(key)
            elif result.get(key) != value:
                problems.append(key)
        if result["case_record_written"] or result["note_shared"] or result["assessment_made"]:
            problems.append("consequential")
        if result["human_approval"] is not None:
            problems.append("approval")
        cases.append({
            "case_id": row["case_id"],
            "status": "passed" if not problems else "failed",
            "problems": problems,
        })
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = sum(1 for case in cases if case["status"] == "failed")
    errors = sum(1 for case in cases if case["status"] == "error")
    return {
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a live model score.",
        "summary": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_cases": len(cases),
        },
        "cases": cases,
        "paraphrase_recall": paraphrase_report(),
        "grounding_score": score_claims(labelled_claims()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = run()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"Smoke test {summary['passed']}/{summary['total_cases']} passed")
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
