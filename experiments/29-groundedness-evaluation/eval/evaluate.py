#!/usr/bin/env python3
"""Deterministic smoke test of the groundedness checker.

The dataset is synthetic. The scorer is the Python under src/. This is not a
model score and it does not call Microsoft Foundry. Case totals count cases
once. Claim verdicts stay inside each case and are not added to total_cases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report import ProhibitedAction, report  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called. "
    "Not a Microsoft Foundry groundedness score."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"
LIBRARY = ROOT / "fixtures" / "library.json"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def expand(case: dict, library: dict) -> dict:
    if case.get("bundle_file"):
        return json.loads((ROOT / case["bundle_file"]).read_text(encoding="utf-8"))
    spec = case["spec"]
    passages = []
    for ref in spec["passages"]:
        if isinstance(ref, str):
            passages.append(dict(library["passages"][ref]))
        else:
            row = dict(library["passages"][ref["id"]])
            row.update(ref.get("set") or {})
            passages.append(row)
    bundle = {
        "bundle_id": spec["bundle_id"],
        "organisation": spec["organisation"],
        "sector": spec["sector"],
        "synthetic": spec.get("synthetic", True),
        "agent_under_test": spec["agent_under_test"],
        "passages": passages,
        "answers": spec["answers"],
    }
    if "draft_thresholds" in spec:
        bundle["draft_thresholds"] = spec["draft_thresholds"]
    if spec.get("request_manifest_skeleton"):
        bundle["request_manifest_skeleton"] = True
    if "requested_autonomy" in spec:
        bundle["requested_autonomy"] = spec["requested_autonomy"]
    extra = spec.get("extra") or {}
    bundle.update(extra)
    return bundle


def _signals(draft: dict) -> set[str]:
    found: set[str] = set()
    for row in draft["prompt_injection"]["signals"]:
        found.update(row["codes"])
    return found


def check(case: dict, draft: dict | None, error: str | None) -> list[str]:
    expect = case["expect"]
    problems: list[str] = []
    if expect.get("refused"):
        if error is None:
            problems.append("expected a refusal")
        elif expect.get("error_contains") and expect["error_contains"] not in (error or ""):
            problems.append(f"refusal text did not contain {expect['error_contains']!r}")
        return problems
    if error is not None:
        return [error]
    assert draft is not None
    if draft["label"] != "DRAFT FOR EVALUATION OWNER":
        problems.append("label")
    if draft["threshold_approved_by_evaluation_owner"] is not False:
        problems.append("threshold approved")
    if draft["release_decision"] is not None or draft["pass_fail_released"] is not False:
        problems.append("release")
    if draft["groundedness_clearance"] is not False or draft["actions_taken"] != []:
        problems.append("clearance")
    if draft["model_called"] is not False or draft["network_called"] is not False:
        problems.append("model or network")
    if draft["foundry_evaluator_called"] is not False or draft["foundry_option"]["called"] is not False:
        problems.append("foundry called")
    if draft["a3_recommended"] is not False or draft["prompt_injection"]["followed"] is not False:
        problems.append("injection or autonomy")
    summary = draft["summary"]
    if summary["verdict_total"] != summary["claim_count"]:
        problems.append("verdict total double-counts or drops a claim")
    if sum(summary["verdicts"].values()) != summary["claim_count"]:
        problems.append("verdict buckets do not sum to the claim count")
    if "stale_source" in summary["verdicts"]:
        problems.append("stale was counted as a verdict")
    if summary["answer_count"] + summary["claim_count"] == summary.get("total"):
        problems.append("answers and claims were added into one total")
    if "claim_count" in expect and summary["claim_count"] != expect["claim_count"]:
        problems.append(f"claim_count {summary['claim_count']} != {expect['claim_count']}")
    if "answer_count" in expect and summary["answer_count"] != expect["answer_count"]:
        problems.append("answer_count")
    if "verdicts" in expect:
        for name, count in expect["verdicts"].items():
            if summary["verdicts"].get(name) != count:
                problems.append(f"{name} is {summary['verdicts'].get(name)} not {count}")
    if "stale_claim_count" in expect and summary["stale_claim_count"] != expect["stale_claim_count"]:
        problems.append("stale_claim_count")
    if "draft_bar_met" in expect and draft["draft_bar_met"] is not expect["draft_bar_met"]:
        problems.append("draft_bar_met")
    if "do_not_rely" in expect and draft["do_not_rely"] is not expect["do_not_rely"]:
        problems.append("do_not_rely")
    if "pins_stale" in expect and draft["pins_stale"] is not expect["pins_stale"]:
        problems.append("pins_stale")
    if "passages_stale" in expect and draft["passages_stale"] is not expect["passages_stale"]:
        problems.append("passages_stale")
    if expect.get("other_failures") is not None:
        if draft["claims"][0]["other_failures"] != expect["other_failures"]:
            problems.append(f"other_failures {draft['claims'][0]['other_failures']}")
    if expect.get("signals_include"):
        found = _signals(draft)
        missing = [code for code in expect["signals_include"] if code not in found]
        if missing:
            problems.append(f"missing signals {missing}")
    if expect.get("signals_empty") and draft["prompt_injection"]["signals"]:
        problems.append("signals were recorded on a refusal sentence")
    if expect.get("ignored_keys") and not draft["prompt_injection"]["ignored_keys"]:
        problems.append("expected ignored keys")
    if expect.get("skeleton_approved") is False and draft["manifest_skeleton"]["approved"] is not False:
        problems.append("skeleton approved")
    if "skeleton_generator" in expect and draft["manifest_skeleton"]["generator"] != expect["skeleton_generator"]:
        problems.append("skeleton generator")
    if draft["draft_thresholds"]["approved_by_evaluation_owner"] is not False:
        problems.append("nested threshold flag")
    return problems


def evaluate(dataset: dict | None = None) -> dict:
    data = dataset or load_dataset()
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))
    rows = []
    for case in data["cases"]:
        error = None
        drafted = None
        try:
            bundle = expand(case, library)
            drafted = report(
                bundle,
                case.get("as_of", data["as_of"]),
                case.get("stale_after_days", 90),
            )
        except (ProhibitedAction, ValueError) as exc:
            error = str(exc)
        problems = check(case, drafted, error)
        rows.append(
            {
                "id": case["id"],
                "name": case["name"],
                "passed": not problems,
                "problems": problems,
                "claim_count": None if drafted is None else drafted["summary"]["claim_count"],
                "verdict_total": None if drafted is None else drafted["summary"]["verdict_total"],
                "refused": error is not None,
            }
        )
    failed = [row for row in rows if not row["passed"]]
    passed = len(rows) - len(failed)
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_foundry_score": True,
        "model_called": False,
        "network_called": False,
        "foundry_evaluator_called": False,
        "claims_added_to_total_cases": False,
        "as_of": data["as_of"],
        "summary": {
            "total_cases": len(rows),
            "passed": passed,
            "failed": len(failed),
            "agreement_rate": round(100 * passed / len(rows), 1) if rows else 0.0,
        },
        "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for Experiment 29.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = evaluate(load_dataset(args.dataset))
    summary = result["summary"]
    if summary["passed"] + summary["failed"] != summary["total_cases"]:
        raise SystemExit("Smoke totals do not add up to the case count.")
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
