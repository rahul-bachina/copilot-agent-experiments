#!/usr/bin/env python3
"""Deterministic smoke test of the prompt-injection runner.

The dataset is synthetic, plus instruction files already in this repository.
The scorer is the Python under src/. This is not a model score, not an
Attack Success Rate, and it does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.run import ProhibitedAction, run  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called. "
    "Not an Attack Success Rate."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def rule_map(report: dict) -> dict[str, str]:
    found: dict[str, str] = {}
    for row in report["results"]:
        rule = row.get("rule_id")
        if not rule:
            continue
        previous = found.get(rule)
        if previous is not None and previous != row["result"]:
            found[rule] = "mixed"
        else:
            found[rule] = row["result"]
    return found


def check(case: dict, report: dict | None, error: str | None) -> list[str]:
    expect = case["expect"]
    problems: list[str] = []
    if expect.get("refused"):
        if error is None:
            problems.append("expected a refusal")
        elif expect.get("error_contains") and expect["error_contains"] not in error:
            problems.append(f"refusal text did not contain {expect['error_contains']!r}")
        return problems
    if error is not None:
        return [error]
    assert report is not None
    if report["label"] != "DRAFT FOR SECURITY REVIEWER":
        problems.append("label")
    if report["reviewer_assessed"] is not False or report["remediation_applied"] is not False:
        problems.append("assessment flags")
    if report["published"] is not False or report["actions_taken"] != []:
        problems.append("action flags")
    if report["model_called"] is not False or report["network_called"] is not False:
        problems.append("model or network")
    if report["foundry_red_team_called"] is not False or report["a3_recommended"] is not False:
        problems.append("foundry or autonomy")
    if report["prompt_injection"]["followed"] is not False:
        problems.append("injection followed")
    if "passed" in expect and report["summary"]["passed"] != expect["passed"]:
        problems.append(f"passed {report['summary']['passed']} != {expect['passed']}")
    if "failed" in expect and report["summary"]["failed"] != expect["failed"]:
        problems.append(f"failed {report['summary']['failed']} != {expect['failed']}")
    if "do_not_rely" in expect and report["do_not_rely"] is not expect["do_not_rely"]:
        problems.append("do_not_rely")
    if "scoring_double" in expect and report["scoring_double"] is not expect["scoring_double"]:
        problems.append("scoring_double")
    if "suite_executed" in expect and report["suite_executed"] is not expect["suite_executed"]:
        problems.append("suite_executed")
    if expect.get("rules"):
        actual = rule_map(report)
        for rule, result in expect["rules"].items():
            if actual.get(rule) != result:
                problems.append(f"{rule} is {actual.get(rule)} not {result}")
    core = report.get("sandbox_core")
    if expect.get("core_result"):
        if not core or core.get("result") != expect["core_result"]:
            problems.append("sandbox core result")
    if expect.get("injection_followed") is False and core and core.get("injection_followed") is not False:
        problems.append("core followed an injection")
    if expect.get("identifier_absent") and "QQ 12 34 56 A" in json.dumps(report):
        problems.append("synthetic identifier was copied into the report")
    if expect.get("draft_approved") is False and report["manifest_skeleton"]["approved"] is not False:
        problems.append("skeleton approved")
    return problems


def evaluate(dataset: dict | None = None) -> dict:
    data = dataset or load_dataset()
    rows = []
    for case in data["cases"]:
        error = None
        report = None
        try:
            report = run(case["bundle"], case.get("as_of", data["as_of"]), case.get("stale_after_days", 90))
        except (ProhibitedAction, ValueError) as exc:
            error = str(exc)
        problems = check(case, report, error)
        rows.append(
            {
                "id": case["id"],
                "name": case["name"],
                "passed": not problems,
                "problems": problems,
                "summary": None if report is None else report["summary"],
                "rules": None if report is None else rule_map(report),
                "refused": error is not None,
            }
        )
    failed = [row for row in rows if not row["passed"]]
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_an_attack_success_rate": True,
        "model_called": False,
        "network_called": False,
        "foundry_red_team_called": False,
        "as_of": data["as_of"],
        "summary": {
            "total_cases": len(rows),
            "passed": len(rows) - len(failed),
            "failed": len(failed),
            "errors": len(failed),
            "agreement_rate": round(100 * (len(rows) - len(failed)) / len(rows), 1) if rows else 0.0,
        },
        "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for Experiment 28.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = evaluate(load_dataset(args.dataset))
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
