#!/usr/bin/env python3
"""Deterministic smoke test of the OneDrive finder.

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

from find import acknowledge_results, find_documents  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs(case: dict) -> tuple[dict, dict, dict, str]:
    index = json.loads((ROOT / "examples" / "sample_index.json").read_text(encoding="utf-8"))
    request = {"query": case.get("query", "Find housing repairs documents")}
    selection = json.loads((ROOT / "examples" / "sample_selection.json").read_text(encoding="utf-8"))
    if "clearance" in case:
        selection["clearance"] = case["clearance"]
    if "confirmed" in case:
        selection["confirmed"] = case["confirmed"]
    if case.get("synthetic") is False:
        index["synthetic"] = False
    if case.get("only_file") == "no-readers":
        index["files"] = [
            {
                "file_id": "SYN-OD-0021",
                "location_id": "LOC-HOUSING",
                "title": "CANARY-NO-READERS housing repairs",
                "last_modified": "2026-09-01",
                "sensitivity_label": "OFFICIAL",
                "extract": "Housing repairs with no reader list.",
            }
        ]
    return index, request, selection, case.get("as_of", "2026-11-13")


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    try:
        index, request, selection, as_of = _inputs(case)
        result = find_documents(index, request, selection, as_of)
        if "acknowledge" in case:
            result = acknowledge_results(
                result,
                {
                    "decision": case["acknowledge"],
                    "actor_role": "Requesting user",
                    "index_id": result["index_id"],
                    "queue_reviewed": case["acknowledge"] == "acknowledge",
                },
            )
        blob = json.dumps(result)
        if "outcome" in expect:
            add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
        if "catalogue_id" in expect:
            add("catalogue_id", result.get("catalogue_id") == expect["catalogue_id"], str(result.get("catalogue_id")))
        if "autonomy" in expect:
            add("autonomy", result.get("autonomy") == expect["autonomy"], str(result.get("autonomy")))
        if "statement" in expect:
            add("statement", result.get("plain_statement") == expect["statement"], str(result.get("plain_statement")))
        if "match_count" in expect:
            add("match_count", len(result.get("matches") or []) == expect["match_count"], str(len(result.get("matches") or [])))
        if expect.get("human_approval_null") is True:
            add("human_approval", result.get("human_approval") is None, "null")
        matches = result.get("matches") or []
        if "file_present" in expect:
            add("file_present", any(item["file_id"] == expect["file_present"] for item in matches), expect["file_present"])
        if "file_absent" in expect:
            add("file_absent", all(item["file_id"] != expect["file_absent"] for item in matches), expect["file_absent"])
        focus_id = expect.get("file_present")
        focus = next((item for item in matches if item["file_id"] == focus_id), None) if focus_id else None
        if "legal_hold" in expect and focus is not None:
            add("legal_hold", focus.get("legal_hold") is expect["legal_hold"], str(focus.get("legal_hold")))
        if "retention_label" in expect and focus is not None:
            add("retention_label", focus.get("retention_label") == expect["retention_label"], str(focus.get("retention_label")))
        if "human_flag" in expect and focus is not None:
            add("human_flag", focus.get("human_flag") == expect["human_flag"], str(focus.get("human_flag")))
            add("snippet_withheld", focus.get("snippet") is None, "null")
        if "routine" in expect and focus is not None:
            add("routine", focus.get("routine") is expect["routine"], str(focus.get("routine")))
        if "superseded_by" in expect and focus is not None:
            add("superseded_by", focus.get("superseded_by") == expect["superseded_by"], str(focus.get("superseded_by")))
        if "likely_stale" in expect and focus is not None:
            add("likely_stale", focus.get("likely_stale") is expect["likely_stale"], str(focus.get("likely_stale")))
        if "later_hidden" in expect and focus is not None:
            add("later_hidden", focus.get("later_version_not_in_view") is True, str(focus.get("later_version_not_in_view")))
            add("hidden_id_absent", focus.get("superseded_by") is None, "null")
        if "duplicate_file" in expect:
            duplicate = next((item for item in matches if item["file_id"] == expect["duplicate_file"]), None)
            add("duplicate", bool(duplicate and duplicate.get("likely_duplicate")), expect["duplicate_file"])
        if "injection_followed" in expect:
            add("followed", (result.get("injection") or {}).get("followed") is False, "false")
        if "signal" in expect:
            signals = [item.get("signal") for item in (result.get("injection") or {}).get("signals") or []]
            add("signal", expect["signal"] in signals, str(signals))
        if "rules_current" in expect:
            add("rules_current", (result.get("stale") or {}).get("rules_current") is expect["rules_current"], "stale")
        if "not_permitted" in expect:
            add("not_permitted", (result.get("withheld") or {}).get("not_permitted") == expect["not_permitted"], "count")
        if "deleted" in expect:
            add("deleted", (result.get("flags") or {}).get("deleted") is expect["deleted"], "flag")
        if "moved" in expect:
            add("moved", (result.get("flags") or {}).get("moved") is False, "flag")
        if "shared" in expect:
            add("shared", (result.get("flags") or {}).get("shared") is False, "flag")
        if "ack_reason" in expect:
            add("ack_reason", (result.get("acknowledgement") or {}).get("reason") == expect["ack_reason"], str((result.get("acknowledgement") or {}).get("reason")))
        if expect.get("acknowledged") is True:
            add("acknowledged", (result.get("human_approval") or {}).get("decision") == "acknowledge", "decision")
        if "executed" in expect:
            add("executed", (result.get("human_approval") or {}).get("executed") is False, "false")
        for snippet in expect.get("absent", []):
            add(f"absent {snippet}", snippet not in blob, snippet)
        if result.get("flags", {}).get("access_widened") is not False:
            add("access_widened", False, "true")
    except Exception as exc:  # noqa: BLE001 - one case, one error row
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "checks": [{"name": "raised", "passed": False, "detail": type(exc).__name__}],
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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the OneDrive finder")
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
