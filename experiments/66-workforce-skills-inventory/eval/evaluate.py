#!/usr/bin/env python3
"""Deterministic smoke test. Not a model score. Each case is counted once.

Paraphrase recall is reported beside the cases. It is not added into
total_cases, passed, failed, or errors.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inventory import propose_inventory  # noqa: E402
from words import family_hit  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def _load(folder: str, name: str) -> dict:
    return json.loads((ROOT / folder / name).read_text(encoding="utf-8"))


def _case_inputs(case: dict) -> tuple[dict, dict, dict, dict, str]:
    request = _load("examples", "sample_request.json")
    evidence = _load("fixtures", "evidence.json")
    framework = _load("fixtures", "framework.json")
    transparency = _load("fixtures", "transparency.json")
    as_of = case.get("as_of", "2026-11-18")
    if case.get("request"):
        request.update(case["request"])
    if case.get("transparency"):
        transparency.update(case["transparency"])
    return request, evidence, framework, transparency, as_of


def _check(result: dict, expect: dict) -> list[str]:
    failed = []

    def need(condition: bool, name: str) -> None:
        if not condition:
            failed.append(name)

    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], "outcome")
    ids = [row.get("skill_id") for row in result.get("proposals") or []]
    for skill_id in expect.get("present") or []:
        need(skill_id in ids, f"present:{skill_id}")
    for skill_id in expect.get("absent") or []:
        need(skill_id not in ids, f"absent:{skill_id}")
    if "proposals" in expect:
        need(len(result.get("proposals") or []) == expect["proposals"], "proposals")
    if "employee_confirmed" in expect:
        need(
            all(row.get("employee_confirmed") is expect["employee_confirmed"] for row in result.get("proposals") or []),
            "employee_confirmed",
        )
    flags = result.get("flags") or {}
    for key in ("wrote_to_hr_system", "article_13_met"):
        if key in expect:
            need(flags.get(key) is expect[key], key)
    for key in ("sources_current", "may_be_relied_on", "coerced"):
        if key in expect:
            need(result.get(key) is expect[key], key)
    if "cue_absent" in expect:
        need(expect["cue_absent"] not in json.dumps(result), "cue_absent")
    return failed


def _recall() -> dict:
    data = json.loads((ROOT / "eval" / "paraphrases.json").read_text(encoding="utf-8"))
    categories = []
    for name, block in data.items():
        positive = block["positive"]
        missed = [sentence for sentence in positive if not family_hit(sentence, block["family"])]
        caught = len(positive) - len(missed)
        leaked = [sentence for sentence in block["negative"] if family_hit(sentence, block["family"])]
        categories.append(
            {
                "category": name,
                "caught": caught,
                "total": len(positive),
                "recall": caught / len(positive) if positive else 0,
                "missed": missed,
                "negatives": len(block["negative"]),
                "negatives_leaked": len(leaked),
            }
        )
    return {
        "note": "Not included in summary.total_cases. These are reworded variants, not extra smoke cases.",
        "categories": categories,
    }


def evaluate(dataset: dict | None = None) -> dict:
    if dataset is None:
        dataset = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
    directory = _load("fixtures", "directory.json")
    cases = []
    passed = failed = errors = 0
    for case in dataset["cases"]:
        try:
            request, evidence, framework, transparency, as_of = _case_inputs(case)
            result = propose_inventory(request, evidence, framework, directory, transparency, as_of)
            problems = _check(result, case["expect"])
        except Exception as exc:  # noqa: BLE001 — a smoke row must count an error once
            problems = [f"error:{type(exc).__name__}"]
            errors += 1
            cases.append({"case_id": case["id"], "status": "error", "problems": problems})
            continue
        if problems:
            failed += 1
            status = "failed"
        else:
            passed += 1
            status = "passed"
        cases.append({"case_id": case["id"], "status": status, "problems": problems})
    total = len(dataset["cases"])
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "summary": {
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_cases": total,
        },
        "cases": cases,
        "paraphrase_recall": _recall(),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args()
    report = evaluate()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"Smoke test {summary['passed']}/{summary['total_cases']} passed "
        f"({summary['failed']} failed, {summary['errors']} errors)"
    )
    for row in report["paraphrase_recall"]["categories"]:
        print(f"Paraphrase {row['category']} {row['caught']}/{row['total']}")
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
