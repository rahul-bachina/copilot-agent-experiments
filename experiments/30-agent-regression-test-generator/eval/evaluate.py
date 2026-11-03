#!/usr/bin/env python3
"""Deterministic smoke test of the regression-case generator.

The dataset is synthetic. The scorer is the Python under src/. This is not
a model score, not a Microsoft Foundry run, and it does not call a model.

passed, failed, and errored are disjoint. Their sum is total_cases.
A row is not counted in two of those buckets.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.generate import ProhibitedAction, generate  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called. "
    "Not a Microsoft Foundry evaluation."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"
SAMPLE = ROOT / "examples" / "sample_bundle.json"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def load_bundle(case: dict) -> dict:
    if case.get("base") == "sample":
        bundle = json.loads(SAMPLE.read_text(encoding="utf-8"))
    else:
        bundle = copy.deepcopy(case["bundle"])
    for key, value in (case.get("set") or {}).items():
        bundle[key] = value
    return bundle


def check(case: dict, report: dict | None, error: str | None) -> list[str]:
    expect = case["expect"]
    problems: list[str] = []
    if expect.get("refused"):
        if error is None:
            problems.append("expected a refusal")
        elif expect.get("error_contains") and expect["error_contains"] not in (error or ""):
            problems.append("refusal text did not match")
        return problems
    if error is not None:
        return [error]
    assert report is not None
    if report["label"] != "DRAFT FOR MAINTAINER REVIEW":
        problems.append("label")
    if report["maintainer_approved"] is not False or report["merged"] is not False or report["pushed"] is not False:
        problems.append("action flags")
    if report["agent_under_test_edited"] is not False or report["pr_opened"] is not False:
        problems.append("edit or pull request")
    if report["foundry_evaluation_called"] is not False or report["a3_recommended"] is not False:
        problems.append("foundry or autonomy")
    if report["model_called"] is not False or report["network_called"] is not False:
        problems.append("model or network")
    if report["prompt_injection"]["followed"] is not False:
        problems.append("injection followed")
    summary = report["summary"]
    if summary["drafted"] + summary["skipped_duplicate"] != summary["considered"]:
        problems.append("case totals double-count or drop a row")
    for key, expected in (expect.get("summary") or {}).items():
        if summary[key] != expected:
            problems.append(f"summary {key}")
    if "detected" in expect and report["prompt_injection"]["detected"] is not expect["detected"]:
        problems.append("injection detected")
    if "do_not_rely" in expect and report["do_not_rely"] is not expect["do_not_rely"]:
        problems.append("do_not_rely")
    if "push_request_refused" in expect and report["push_request_refused"] is not expect["push_request_refused"]:
        problems.append("push refused")
    if "protected_branch_targeted" in expect and report["protected_branch_targeted"] is not expect["protected_branch_targeted"]:
        problems.append("protected branch targeted")
    if expect.get("skeleton_approved") is False and report["manifest_skeleton"]["approved"] is not False:
        problems.append("skeleton approved")
    if expect.get("skeleton_called") is False and report["manifest_skeleton"]["experiment_03_called"] is not False:
        problems.append("skeleton called")
    if expect.get("case_id"):
        match = next((item for item in report["cases"] if item["id"] == expect["case_id"]), None)
        if match is None or match["status"] != expect.get("case_status", "drafted"):
            problems.append("case id")
    return problems


def evaluate(dataset: dict | None = None) -> dict:
    data = dataset or load_dataset()
    rows = []
    for case in data["cases"]:
        error = None
        report = None
        problems: list[str] = []
        try:
            report = generate(load_bundle(case), case.get("as_of", data["as_of"]), case.get("stale_after_days", 90))
            problems = check(case, report, None)
        except (ProhibitedAction, ValueError) as exc:
            error = str(exc)
            problems = check(case, None, error)
        except Exception as exc:  # noqa: BLE001 — an unexpected error is its own bucket
            rows.append(
                {
                    "id": case["id"],
                    "name": case["name"],
                    "passed": False,
                    "failed": False,
                    "errored": True,
                    "problems": [f"{exc.__class__.__name__}: {exc}"],
                }
            )
            continue
        failed = bool(problems)
        rows.append(
            {
                "id": case["id"],
                "name": case["name"],
                "passed": not failed,
                "failed": failed,
                "errored": False,
                "problems": problems,
                "refused": error is not None,
            }
        )
    passed = sum(1 for row in rows if row["passed"])
    failed = sum(1 for row in rows if row["failed"])
    errored = sum(1 for row in rows if row["errored"])
    if passed + failed + errored != len(rows):
        raise RuntimeError("Smoke totals are not disjoint.")
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_foundry_evaluation": True,
        "model_called": False,
        "network_called": False,
        "foundry_evaluation_called": False,
        "as_of": data["as_of"],
        "summary": {
            "total_cases": len(rows),
            "passed": passed,
            "failed": failed,
            "errored": errored,
            "agreement_rate": round(100 * passed / len(rows), 1) if rows else 0.0,
        },
        "invariant": "passed + failed + errored = total_cases. A row is in one bucket.",
        "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for Experiment 30.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = evaluate(load_dataset(args.dataset))
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    summary = report["summary"]
    return 0 if summary["failed"] == 0 and summary["errored"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
