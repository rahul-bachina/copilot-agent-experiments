#!/usr/bin/env python3
"""Deterministic smoke test of the SharePoint curation draft.

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

from curate import apply_approved_action, curate_site, record_approval  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _snapshot(case: dict) -> dict:
    if "fixture" in case:
        snapshot = json.loads((ROOT / case["fixture"]).read_text(encoding="utf-8"))
    else:
        snapshot = json.loads(json.dumps(case["snapshot"]))
    overlay = case.get("set") or {}
    for key, value in overlay.items():
        if key == "principals":
            snapshot.setdefault("requesting_user", {})["principals"] = value
        else:
            snapshot[key] = value
    return snapshot


def _run(case: dict) -> dict:
    result = curate_site(_snapshot(case), case["as_of"])
    approve = case.get("approve")
    if approve:
        wanted = None
        for proposal in result.get("proposals") or []:
            if proposal["type"] != approve["type"]:
                continue
            item_id = approve.get("item_id")
            if item_id is not None and item_id not in proposal["item_ids"]:
                continue
            wanted = proposal
            break
        if wanted is None:
            raise RuntimeError("approve target was not in the draft")
        review = {
            "decision": approve.get("decision", "approve_actions"),
            "actor_role": "Site owner",
            "actor_id": "SYN-SO-050",
            "site_id": result.get("site_id"),
            "proposal_ids": [wanted["proposal_id"]],
            "queue_reviewed": approve.get("queue_reviewed", False),
        }
        result = record_approval(result, review)
    if case.get("apply") is True:
        result = apply_approved_action(result)
    return result


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = _run(case)
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

    blob = json.dumps(result)
    add("catalogue", result.get("catalogue_id") == "M001", str(result.get("catalogue_id")))
    add("autonomy", result.get("autonomy") == "A1", str(result.get("autonomy")))
    add("executed", result.get("executed") is False, "false")
    add("model_called", result.get("model_called") is False, "false")
    add("network_called", result.get("network_called") is False, "false")
    add("sharepoint_called", result.get("sharepoint_called") is False, "false")
    add("graph_called", result.get("graph_called") is False, "false")
    add("text_recorded", result.get("text_recorded") is False, "false")
    flags = result.get("flags") or {}
    add("deleted", flags.get("deleted") is False, "false")
    add("unpublished", flags.get("unpublished") is False, "false")
    add("moved", flags.get("moved") is False, "false")
    add("permissions_changed", flags.get("permissions_changed") is False, "false")
    add("metadata_applied_in_tenant", flags.get("metadata_applied_in_tenant") is False, "false")
    route = result.get("human_route") or {}
    add("human_route", route.get("offered") is True, "true")
    add("agent_curates_sensitive", route.get("agent_curates_sensitive") is False, "false")
    regulatory = result.get("regulatory") or {}
    if regulatory:
        add("accuracy_met", regulatory.get("accuracy_met") is False, "false")
        add("storage_met", regulatory.get("storage_limitation_met") is False, "false")
        add("code_complied", regulatory.get("code_complied") is False, "false")
    injection = result.get("prompt_injection") or {}
    if injection:
        add("injection_followed", injection.get("followed") is False, "false")

    if "outcome" in expect:
        add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
    if "withheld_count" in expect:
        add("withheld_count", result.get("withheld_count") == expect["withheld_count"], str(result.get("withheld_count")))
    if "visible_count" in expect:
        add("visible_count", result.get("visible_count") == expect["visible_count"], str(result.get("visible_count")))
    types = [proposal["type"] for proposal in result.get("proposals") or []]
    for proposal_type in expect.get("has_type") or []:
        add(f"has {proposal_type}", proposal_type in types, str(sorted(set(types))))
    for proposal_type in expect.get("lacks_type") or []:
        add(f"lacks {proposal_type}", proposal_type not in types, str(sorted(set(types))))
    if "rules_current" in expect:
        got = (result.get("stale") or {}).get("rules_current")
        add("rules_current", got is expect["rules_current"], str(got))
    if expect.get("quotes_withheld") is True:
        taken = [row.get("taken") for row in result.get("sources") or []]
        add("quotes_withheld", taken and all(value is None for value in taken), str(taken[:1]))
    if "injection" in expect:
        add("injection", injection.get("detected") is expect["injection"], str(injection.get("detected")))
    if "signal" in expect:
        signals = injection.get("signals") or []
        add("signal", expect["signal"] in signals, str(signals))
    item_expect = expect.get("item")
    if item_expect:
        match = next((item for item in result.get("items") or [] if item["item_id"] == item_expect["id"]), None)
        add("item_present", match is not None, item_expect["id"])
        if match is not None and "queued" in item_expect:
            add("item_queued", match.get("queued") is item_expect["queued"], str(match.get("queued")))
    if "review_reason" in expect:
        got = (result.get("approval_review") or {}).get("reason")
        add("review_reason", got == expect["review_reason"], str(got))
    if "stub" in expect:
        got = (result.get("curation_stub") or {}).get("stub")
        add("stub", got is expect["stub"], str(got))
    if expect.get("applied_in_tenant") is False:
        receipts = (result.get("curation_stub") or {}).get("receipts") or []
        actions = result.get("actions_taken") or []
        add(
            "applied_in_tenant",
            all(row.get("applied_in_tenant") is False for row in receipts + actions),
            "false",
        )
    if expect.get("human_approval_null") is True:
        add("human_approval", result.get("human_approval") is None, "null")
    if expect.get("approved") is True:
        add("approved", (result.get("human_approval") or {}).get("approved") is True, "true")
        add("approval_executed", (result.get("human_approval") or {}).get("executed") is False, "false")
    for snippet in expect.get("absent", []):
        add(f"absent {snippet}", snippet not in blob, snippet)

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the curation draft")
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
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        out = Path(__file__).parent / "smoke_report.json"
        out.write_text(text, encoding="utf-8")
    print(SMOKE_LABEL)
    print(
        f"{summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['errors']} errors, {summary['total_cases']} cases"
    )
    if summary["failed"] or summary["errors"]:
        for row in results:
            if row["status"] != "passed":
                print(row["case_id"], row["status"], row.get("error", ""))
                for check in row.get("checks", []):
                    if not check["passed"]:
                        print(" ", check["field"], check["detail"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
