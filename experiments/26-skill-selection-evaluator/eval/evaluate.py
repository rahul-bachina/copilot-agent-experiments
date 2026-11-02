#!/usr/bin/env python3
"""Deterministic smoke test for the skill selection evaluator.

This is not a model evaluation and it is not a Copilot Studio routing score.
The labels on the repository skill case include two utterances the router
misses on purpose. A case fails when an expectation in the dataset is missed,
not merely because a routing test is red.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.report import evaluate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic routing smoke test.")
    parser.add_argument("--dataset", default=str(Path(__file__).with_name("synthetic_dataset.json")))
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    dataset_path = Path(args.dataset)
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = []
    errors = 0
    failed = 0
    utterances = 0
    injection_followed = 0
    prohibited_misses = 0
    controlled_agreement = None
    for case in dataset["cases"]:
        try:
            result, utterance_count = _run_case(case, dataset_path.parent)
        except Exception as exc:  # noqa: BLE001 — one bad case must not hide the rest
            errors += 1
            failed += 1
            cases.append({"id": case.get("id"), "error": f"{exc.__class__.__name__}: {exc}"})
            continue
        utterances += utterance_count
        if result["prompt_injection"]["followed"] or result["prompt_injection"]["selection_obeyed_injection"]:
            injection_followed += 1
        if not result["prohibited_actions"]["all_routed_to_human"]:
            prohibited_misses += 1
        problems = _expect(case.get("expect") or {}, result)
        if problems:
            failed += 1
        if case["id"] == "northfen-controlled":
            controlled_agreement = result["agreement"]["percent"]
        cases.append(
            {
                "id": case["id"],
                "passed": not problems,
                "problems": problems,
                "agreement": result["agreement"],
                "do_not_rely": result["do_not_rely"],
                "maintainer_validated": result["maintainer_validated"],
                "skills_edited": result["skills_edited"],
                "diff_applied": result["diff_applied"],
                "deployed": result["deployed"],
                "a3_recommended": result["a3_recommended"],
                "model_called": result["model_called"],
                "network_called": result["network_called"],
                "platform_selected": result["architecture_cross_check"]["platform_selected"],
                "manifest_approved": result["manifest_skeleton"]["approved"],
                "confusable_pairs": len(result["confusable_pairs"]),
                "failed_routing_tests": [
                    row["id"] for row in result["routing_tests"] if not row["passed"]
                ],
            }
        )
    report = {
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_copilot_studio_routing_score": True,
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model score and not a Copilot Studio routing score.",
        "summary": {
            "total_cases": len(dataset["cases"]),
            "total_utterances": utterances,
            "errors": errors,
            "failed": failed,
            "controlled_agreement": controlled_agreement,
            "injection_followed": injection_followed,
            "prohibited_misses": prohibited_misses,
        },
        "cases": cases,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if errors or failed else 0


def _run_case(case: dict, dataset_dir: Path) -> tuple[dict, int]:
    if case.get("bundle_path"):
        path = (dataset_dir / case["bundle_path"]).resolve()
        bundle = json.loads(path.read_text(encoding="utf-8"))
        base = path.parent
    else:
        bundle = case["bundle"]
        base = dataset_dir
    report = evaluate(bundle, case["as_of"], base_dir=base)
    return report, len(report["utterances"])


def _expect(expect: dict, report: dict) -> list[str]:
    problems = []
    if "agreement_percent" in expect and report["agreement"]["percent"] != expect["agreement_percent"]:
        problems.append(
            f"agreement {report['agreement']['percent']} != {expect['agreement_percent']}"
        )
    if "do_not_rely" in expect and report["do_not_rely"] is not expect["do_not_rely"]:
        problems.append(f"do_not_rely is {report['do_not_rely']}")
    if expect.get("skills_edited") is False and report["skills_edited"]:
        problems.append("skills_edited")
    if expect.get("diff_applied") is False and report["diff_applied"]:
        problems.append("diff_applied")
    if expect.get("maintainer_validated") is False and report["maintainer_validated"]:
        problems.append("maintainer_validated")
    if expect.get("deployed") is False and report["deployed"]:
        problems.append("deployed")
    if expect.get("a3_recommended") is False and report["a3_recommended"]:
        problems.append("a3_recommended")
    if expect.get("model_called") is False and report["model_called"]:
        problems.append("model_called")
    if expect.get("injection_followed") is False and report["prompt_injection"]["followed"]:
        problems.append("injection followed")
    if expect.get("selection_obeyed_injection") is False and report["prompt_injection"]["selection_obeyed_injection"]:
        problems.append("selection obeyed injection")
    if expect.get("prohibited_all_human") and not report["prohibited_actions"]["all_routed_to_human"]:
        problems.append("a prohibited action was not routed to human")
    if "confusable_min" in expect and len(report["confusable_pairs"]) < expect["confusable_min"]:
        problems.append("confusable pairs below the minimum")
    if expect.get("vague_skill_missing"):
        vague = next(row for row in report["description_findings"] if row["skill_id"] == "vague-helper")
        if not vague["missing"]:
            problems.append("vague-helper was not missing")
    failed_ids = [row["id"] for row in report["routing_tests"] if not row["passed"]]
    if "failed_routing_tests" in expect and failed_ids != expect["failed_routing_tests"]:
        problems.append(f"failed routing tests {failed_ids}")
    if expect.get("manifest_approved") is False and report["manifest_skeleton"]["approved"]:
        problems.append("manifest approved")
    if expect.get("platform_selected") is None and report["architecture_cross_check"]["platform_selected"] is not None:
        problems.append("platform selected")
    if "skeleton_generated" in expect and report["manifest_skeleton"]["generated"] is not expect["skeleton_generated"]:
        problems.append("skeleton generated flag")
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
