#!/usr/bin/env python3
"""Deterministic smoke test of the knowledge gap detector.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaps import LABEL, detect_gaps, record_confirmation  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _pack(case: dict, dataset: dict) -> dict:
    if case.get("use_sample"):
        return json.loads((ROOT / "examples" / "sample_pack.json").read_text(encoding="utf-8"))
    return case["pack"]


def _run(case: dict, dataset: dict) -> dict:
    library = case.get("library")
    result = detect_gaps(_pack(case, dataset), case["as_of"], library=library)
    if "review" in case:
        result = record_confirmation(result, case["review"])
    return result


def evaluate_case(case: dict, dataset: dict) -> dict:
    expect = case["expect"]
    try:
        result = _run(case, dataset)
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": str(exc),
            "checks": [],
        }

    checks: list[dict] = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    text = json.dumps(result)
    add("label", result["label"] == LABEL, result["label"])
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("executed", result["executed"] is False, "false")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("echoed", result["source_text_echoed"] is False, "false")
    add("published", result["published"] is False, "false")
    add("edited", result["articles_edited"] is False, "false")
    add("followed", result["prompt_injection"]["followed"] is False, "false")
    add("human_route", result["human_route"]["offered"] is True, "true")
    add("agent_publishes", result["human_route"]["agent_publishes"] is False, "false")
    add("outcome_met", result["regulatory"]["consumer_duty"]["outcome_met"] is False, "false")
    add("duty_met", result["regulatory"]["equality_act"]["duty_met"] is False, "false")
    add("minimisation_met", result["regulatory"]["uk_gdpr"]["data_minimisation_met"] is False, "false")
    add("not_anonymised", result["pii_gateway"].get("output_is_anonymised") is False, "false")
    add("not_released", result["pii_gateway"].get("agent_may_release") is not True, "false")
    gaps = result["gaps"]
    topics = [gap["topic"] for gap in gaps]
    add("unique_gaps", len(topics) == len(set(topics)), str(topics))
    add(
        "gap_count_matches",
        result["counts"]["content_gaps"] == len(gaps),
        str(result["counts"]["content_gaps"]),
    )

    if "outcome" in expect:
        add("outcome", result["outcome"] == expect["outcome"], result["outcome"])
    if "gap_topics" in expect:
        add("gap_topics", topics == expect["gap_topics"], str(topics))
    if "content_gaps" in expect:
        add("content_gaps", result["counts"]["content_gaps"] == expect["content_gaps"], str(result["counts"]["content_gaps"]))
    if "evidence_rows" in expect:
        add(
            "evidence_rows",
            result["counts"]["evidence_rows_on_gaps"] == expect["evidence_rows"],
            str(result["counts"]["evidence_rows_on_gaps"]),
        )
    if "rules_current" in expect:
        add("rules_current", result["stale"]["rules_current"] is expect["rules_current"], str(result["stale"]["rules_current"]))
    if "injection_detected" in expect:
        add(
            "injection_detected",
            result["prompt_injection"]["detected"] is expect["injection_detected"],
            str(result["prompt_injection"]["detected"]),
        )
    if "signal" in expect:
        add("signal", expect["signal"] in result["prompt_injection"]["signals"], str(result["prompt_injection"]["signals"]))
    if "hints_dropped" in expect:
        add("hints_dropped", result["prompt_injection"]["hints_dropped"] == expect["hints_dropped"], str(result["prompt_injection"]["hints_dropped"]))
    if "duty_applied" in expect:
        add(
            "duty_applied",
            result["regulatory"]["consumer_duty"]["applied"] is expect["duty_applied"],
            str(result["regulatory"]["consumer_duty"]["applied"]),
        )
    if "exp21_called" in expect:
        called = result["related_catalogues"]["experiment_21"]["called"]
        add("exp21_called", called is expect["exp21_called"], str(called))
    if "exp40_called" in expect:
        called = result["related_catalogues"]["experiment_40"]["called"]
        add("exp40_called", called is expect["exp40_called"], str(called))
    if "related_current" in expect:
        ids = []
        for gap in gaps:
            ids.extend(gap["related_current_ids"])
        for item in result["items"]:
            ids.extend(item["related_current_ids"])
        add("related_current", expect["related_current"] in ids, str(sorted(set(ids))))
    if "related_stale" in expect:
        ids = []
        for gap in gaps:
            ids.extend(gap["related_stale_ids"])
        add("related_stale", expect["related_stale"] in ids, str(sorted(set(ids))))
    if "finding_kind" in expect:
        kinds = {finding["kind"] for finding in result["findings"]}
        add("finding_kind", expect["finding_kind"] in kinds, str(sorted(kinds)))
    if "winner_chosen" in expect:
        conflicts = [finding for finding in result["findings"] if finding["kind"] == "conflict"]
        add(
            "winner_chosen",
            bool(conflicts) and all(finding["winner_chosen"] is expect["winner_chosen"] for finding in conflicts),
            str([finding.get("winner_chosen") for finding in conflicts]),
        )
    if "entity_type" in expect:
        add("entity_type", expect["entity_type"] in result["pii_gateway"]["entity_types"], str(result["pii_gateway"]["entity_types"]))
    if "outlines_empty" in expect:
        empty = result["outlines"] == []
        add("outlines_empty", empty is expect["outlines_empty"], str(empty))
    if "human_approval_null" in expect:
        add("human_approval", (result["human_approval"] is None) is expect["human_approval_null"], str(result["human_approval"] is None))
    if "gap_confirmed" in expect:
        add("gap_confirmed", result["gap_confirmed"] is expect["gap_confirmed"], str(result["gap_confirmed"]))
    if "review" in case:
        add("review_executed", result["review"]["executed"] is False, "false")
        add("review_published", result["review"]["published"] is False, "false")
        if "review_reason" in expect:
            add("review_reason", result["review"]["reason"] == expect["review_reason"], result["review"]["reason"])
        if expect.get("review_accepted") is True:
            add("review_accepted", result["review"]["accepted"] is True, result["review"]["reason"])
            if result.get("human_approval"):
                add("approval_not_publish", result["human_approval"]["published"] is False, "false")
                add("approval_not_executed", result["human_approval"]["executed"] is False, "false")
        elif expect.get("review_accepted") is False:
            add("review_refused", result["review"]["refused"] is True, result["review"]["reason"])
    elif expect.get("human_approval_null", True) is True and "human_approval_null" not in expect:
        add("human_approval", result["human_approval"] is None, "null")
    for snippet in expect.get("absent", []):
        add(f"absent {snippet[:24]}", snippet not in text, snippet[:24])

    failed = [item for item in checks if not item["passed"]]
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "failed" if failed else "passed",
        "checks": checks,
    }


def summarise(results: list[dict]) -> dict:
    """Count each case once. Check rows are not added to the case total."""
    errors = [item for item in results if item["status"] == "error"]
    failed = [item for item in results if item["status"] == "failed"]
    passed = [item for item in results if item["status"] == "passed"]
    total = len(results)
    if len(passed) + len(failed) + len(errors) != total:
        raise RuntimeError("case statuses were counted more than once")
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the knowledge gap detector")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset)
    ids = [case["id"] for case in dataset["cases"]]
    if len(ids) != len(set(ids)):
        sys.stderr.write("Duplicate case ids\n")
        return 1
    results = [evaluate_case(case, dataset) for case in dataset["cases"]]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "dataset_label": dataset.get("label"),
        "organisation_in_fixtures": dataset.get("organisation"),
        "summary": summary,
        "cases": results,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if summary["failed"] or summary["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
