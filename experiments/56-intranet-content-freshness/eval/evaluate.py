#!/usr/bin/env python3
"""Deterministic smoke test of the intranet freshness report.

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

from freshness import create_approved_tasks, record_approval, review_inventory  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)

_CACHE: dict[str, dict] = {}


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _sample(as_of: str) -> dict:
    if as_of not in _CACHE:
        inventory = json.loads((ROOT / "examples" / "sample_inventory.json").read_text(encoding="utf-8"))
        selection = json.loads((ROOT / "examples" / "sample_selection.json").read_text(encoding="utf-8"))
        _CACHE[as_of] = review_inventory(inventory, as_of, selection)
    return json.loads(json.dumps(_CACHE[as_of]))


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    try:
        result = _sample(case.get("as_of", "2026-11-16"))
        if case.get("mode") == "approve":
            task_id = next(task["task_id"] for task in result["proposed_tasks"] if task["type"] == "overdue_review")
            result = record_approval(result, {
                "decision": "approve_tasks",
                "actor_role": "Content owner",
                "actor_id": result["content_owner_id"],
                "inventory_id": result["inventory_id"],
                "task_ids": [task_id],
                "queue_reviewed": True,
            })
            result = create_approved_tasks(result)
        elif case.get("mode") == "prohibited":
            result = record_approval(result, {
                "decision": "message_staff",
                "actor_role": "Content owner",
                "actor_id": result["content_owner_id"],
                "inventory_id": result["inventory_id"],
                "queue_reviewed": True,
            })
        blob = json.dumps(result)
        types = {item["type"] for item in result.get("findings") or []}
        if "outcome" in expect:
            add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
        if "catalogue_id" in expect:
            add("catalogue_id", result.get("catalogue_id") == expect["catalogue_id"], str(result.get("catalogue_id")))
        if "autonomy" in expect:
            add("autonomy", result.get("autonomy") == expect["autonomy"], str(result.get("autonomy")))
        if "label" in expect:
            add("label", result.get("label") == expect["label"], str(result.get("label")))
        if expect.get("human_approval_null") is True:
            add("human_approval", result.get("human_approval") is None, "null")
        if "finding" in expect:
            add("finding", expect["finding"] in types, str(sorted(types)))
        if "finding_absent" in expect:
            add("finding_absent", expect["finding_absent"] not in types, expect["finding_absent"])
        if "finding_count" in expect:
            count = sum(1 for item in result.get("findings") or [] if item["type"] == expect["finding_count"]["type"])
            add("finding_count", count == expect["finding_count"]["count"], str(count))
        if "duplicate_pages" in expect:
            found = any(
                item["type"] == "likely_duplicate" and item.get("page_ids") == expect["duplicate_pages"]
                for item in result.get("findings") or []
            )
            add("duplicate_pages", found, str(expect["duplicate_pages"]))
        if "approval_reason" in expect:
            add("approval_reason", (result.get("approval") or {}).get("reason") == expect["approval_reason"], str((result.get("approval") or {}).get("reason")))
        if expect.get("stub") is True:
            stubs = result.get("tasks_created") or []
            add("stub", len(stubs) == 1 and stubs[0].get("created_in_planner") is False, str(len(stubs)))
            add("planner", (result.get("flags") or {}).get("planner_called") is False, "flag")
            add("pages_edited", (result.get("flags") or {}).get("pages_edited") is False, "flag")
            add("executed", result.get("executed") is False, "flag")
        if "page_id" in expect:
            summary = next((item for item in result.get("page_summaries") or [] if item.get("page_id") == expect["page_id"]), None)
            add("page", summary is not None, expect["page_id"])
            if summary is not None and "marking" in expect:
                add("marking", summary.get("marking") == expect["marking"], str(summary.get("marking")))
            if summary is not None and "legal_hold" in expect:
                add("legal_hold", summary.get("legal_hold") is expect["legal_hold"], str(summary.get("legal_hold")))
            if summary is not None and "retention_label" in expect:
                add("retention_label", summary.get("retention_label") == expect["retention_label"], str(summary.get("retention_label")))
            if summary is not None and expect.get("no_task") is True:
                tasked = any(expect["page_id"] in task.get("page_ids", []) for task in result.get("proposed_tasks") or [])
                add("no_task", tasked is False, str(tasked))
        if "mask_kind" in expect:
            add("mask_kind", expect["mask_kind"] in ((result.get("copying") or {}).get("mask_kinds_applied") or []), "kinds")
        if "signal" in expect:
            signals = [item.get("signal") for item in (result.get("injection") or {}).get("signals") or []]
            add("signal", expect["signal"] in signals, str(signals))
            add("followed", (result.get("injection") or {}).get("followed") is False, "false")
        if "rules_current" in expect:
            add("rules_current", (result.get("stale") or {}).get("rules_current") is expect["rules_current"], "stale")
            add("quotes_withheld", all(row.get("taken") is None for row in result.get("sources") or []), "taken")
        if "queue_reason" in expect:
            reasons = []
            for item in result.get("human_queue") or []:
                reasons.extend(item.get("reasons") or [])
            add("queue_reason", expect["queue_reason"] in reasons, str(reasons))
        if "not_permitted" in expect:
            add("not_permitted", (result.get("withheld") or {}).get("not_permitted", 0) >= expect["not_permitted"], "count")
        if "messages_sent" in expect:
            add("messages_sent", (result.get("flags") or {}).get("messages_sent") is expect["messages_sent"], "flag")
        if "accuracy_met" in expect:
            add("accuracy_met", (result.get("regulatory") or {}).get("accuracy_met") is False, "flag")
        for snippet in expect.get("absent", []):
            add(f"absent {snippet[:24]}", snippet not in blob, "present" if snippet in blob else "absent")
        if '"page_views": 0' in blob and expect.get("views_not_zero") is True:
            add("views_not_zero", False, "coerced")
        elif expect.get("views_not_zero") is True:
            add("views_not_zero", True, "absent")
    except Exception as exc:  # noqa: BLE001 - one case, one error row
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "checks": [{"name": "raised", "passed": False, "detail": f"{type(exc).__name__}: {exc}"}],
        }

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the intranet freshness report")
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    dataset = load_dataset(args.dataset)
    ids = [case["id"] for case in dataset["cases"]]
    if len(ids) != len(set(ids)):
        sys.stderr.write("Duplicate case ids\n")
        return 1
    results = [evaluate_case(case) for case in dataset["cases"]]
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
    text = json.dumps(report, indent=2) + "\n"
    destination = args.output or Path(__file__).parent / "smoke_report.json"
    destination.write_text(text, encoding="utf-8")
    print(
        f"Smoke test: {summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['errors']} errors, {summary['total_cases']} cases"
    )
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
