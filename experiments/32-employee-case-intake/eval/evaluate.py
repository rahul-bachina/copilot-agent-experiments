#!/usr/bin/env python3
"""Deterministic smoke test of the employee-case intake.

One row in ``cases`` is one synthetic case. ``total_cases`` is that count.
It is not the number of checks, and it is not added to the unit-test count.
The checker is the Python in src/, which calls Experiments 15, 12, and 08.
This is not a model score.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.draft import LABEL, NotSynthetic, draft_case  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which calls Experiment 15, Experiment 12, and Experiment 08. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    checks: list[dict] = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    def finish(status: str) -> dict:
        if any(not item["passed"] for item in checks):
            status = "failed"
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": status,
            "checks": checks,
        }

    as_of = date.fromisoformat(case["as_of"])
    window = case.get("stale_after_days", 90)

    if expect.get("outcome") == "refused":
        try:
            draft_case(case["case"], as_of=as_of, stale_after_days=window)
        except NotSynthetic as exc:
            message = str(exc)
            add("refused", True, "NotSynthetic")
            for index, token in enumerate(expect.get("absent", []), start=1):
                add(f"absent {index}", token not in message, "not in the refusal")
            return finish("passed")
        except Exception as exc:  # noqa: BLE001
            return {
                "case_id": case["id"],
                "name": case.get("name", ""),
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "checks": checks,
            }
        add("refused", False, "draft_case returned a draft")
        return finish("failed")

    try:
        result = draft_case(case["case"], as_of=as_of, stale_after_days=window)
    except Exception as exc:  # noqa: BLE001
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "checks": [],
        }

    serialised = json.dumps(result)
    add("label", result["label"] == LABEL, result["label"])
    add("narrative_stored", result["narrative_stored"] is False, "false")
    add("outcome", result["outcome"] is None, "null")
    add("merits", result["merits_advice"] is None, "null")
    add("actions", result["actions_taken"] == [], "[]")
    add("model", result["model_called"] is False, "false")
    add("network", result["network_called"] is False, "false")
    add("hr_write", result["hr_system_written"] is False, "false")
    add("contacted_employee", result["contacted_employee"] is False, "false")
    add("contacted_manager", result["contacted_manager"] is False, "false")
    add("confirmed", result["hr_confirmation"]["classification_confirmed"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("article_9", result["special_category"]["article_9_condition_asserted"] is False, "false")
    add("policy_doc", result["special_category"]["appropriate_policy_document_checked"] is False, "false")
    add("automated", result["automated_decision"]["solely_automated_decision"] is False, "false")
    add("significant", result["automated_decision"]["significant_decision"] is False, "false")
    add("anonymised", result["pii_gateway"]["output_is_anonymised"] is False, "false")
    add("queue", result["routing"]["queue_priority_changed"] is False, "false")

    if "category" in expect:
        actual = result["classification"]["proposed_category"]
        add("category", actual == expect["category"], actual)
    if "route" in expect:
        actual = result["routing"]["proposed_route"]
        add("route", actual == expect["route"], actual)
    if "urgency" in expect:
        actual = result["urgency"]["proposed_flag"]
        add("urgency", actual == expect["urgency"], actual)
    if "sources_stale" in expect:
        add("sources_stale", result["sources_stale"] is expect["sources_stale"], str(result["sources_stale"]))
    if "confidential" in expect:
        actual = result["whistleblowing_confidentiality"]["applies"]
        add("confidential", actual is expect["confidential"], str(actual))
    if "gb_sources" in expect:
        actual = result["jurisdiction"]["gb_sources_applied"]
        add("gb_sources", actual is expect["gb_sources"], str(actual))
    if "health" in expect:
        present = "data_concerning_health" in result["special_category"]["indicators"]
        add("health", present is expect["health"], str(present))
    if "time_reference" in expect:
        ids = [row["id"] for row in result["time_references"]]
        add("time_reference", expect["time_reference"] in ids, ",".join(ids))
    if "deadline_encoded" in expect:
        encoded = any(row["days_encoded"] is not None for row in result["time_references"])
        add("deadline_encoded", encoded is expect["deadline_encoded"], str(encoded))
    if "last_day_calculated" in expect:
        row = next(item for item in result["time_references"] if item["id"] == "era_80g_1b")
        add("last_day", row["last_day_calculated"] is False, "false")
    if "application_made_on" in expect:
        add(
            "application_made_on",
            result["application_made_on"] == expect["application_made_on"],
            str(result["application_made_on"]),
        )
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "gateway_called" in expect:
        actual = result["pii_gateway"]["called"]
        add("gateway_called", actual is expect["gateway_called"], str(actual))
    if "scanner_called" in expect:
        actual = result["vulnerability_scanner"]["called"]
        add("scanner_called", actual is expect["scanner_called"], str(actual))
    if "intake_called" in expect:
        called = result["document_intake"] is not None
        add("intake_called", called is expect["intake_called"], str(called))
        if called and expect["intake_called"]:
            add(
                "intake_id",
                result["document_intake"]["experiment_id"] == "exp-12-document-intake",
                result["document_intake"]["experiment_id"],
            )
            add(
                "files_confirmed",
                result["document_intake"]["files_confirmed"] is False,
                "false",
            )
    if "protected_decided" in expect:
        actual = result["whistleblowing_confidentiality"]["protected_disclosure_decided"]
        add("protected_decided", actual is False, "false")
    for index, token in enumerate(expect.get("absent", []), start=1):
        add(f"absent {index}", token not in serialised, "omitted")

    return finish("passed")


def summarise(results: list[dict]) -> dict:
    """Count cases once. Checks stay inside each case and are not a second total."""

    errors = [item for item in results if item["status"] == "error"]
    failed = [item for item in results if item["status"] == "failed"]
    passed = [item for item in results if item["status"] == "passed"]
    total = len(results)
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
        "count_note": "total_cases is the number of synthetic cases. It is not the number of checks.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the HR case intake")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    dataset = load_dataset(args.dataset)
    results = [evaluate_case(case) for case in dataset["cases"]]
    summary = summarise(results)
    report = {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_live_recall_rate": True,
        "dataset_label": dataset.get("label"),
        "summary": summary,
        "cases": results,
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        out = Path(__file__).parent / "smoke_report.json"
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["total_cases"] < 16:
        sys.stderr.write("Fewer than 16 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
