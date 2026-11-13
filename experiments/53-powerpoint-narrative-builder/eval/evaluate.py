#!/usr/bin/env python3
"""Deterministic smoke test of the narrative outline.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from narrative import LABEL, produce_slides, propose_outline, record_presenter_approval  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = propose_outline(case["pack"], case["as_of"])
        if "review" in case:
            result = record_presenter_approval(result, case["review"])
        if case.get("produce"):
            with tempfile.TemporaryDirectory() as folder:
                result = produce_slides(result, Path(folder) / "deck.pptx")
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
    add("label", result.get("label") == LABEL, str(result.get("label")))
    add("actions_taken", result.get("actions_taken") == [], "[]")
    add("executed", result.get("executed") is False, "false")
    add("model_called", result.get("model_called") is False, "false")
    add("network_called", result.get("network_called") is False, "false")
    add("text_recorded", result.get("request_text_recorded") is False, "false")
    flags = result.get("flags") or {}
    add("shared", flags.get("shared") is False, "false")
    add("published", flags.get("published") is False, "false")
    add("sent", flags.get("sent") is False, "false")
    add("graph", flags.get("graph_called") is False, "false")
    add("logo", flags.get("logo_added") is False, "false")
    add("figure_invented", flags.get("figure_invented") is False, "false")
    route = result.get("human_route") or {}
    add("human_route", route.get("offered") is True, "true")
    add("agent_shares", route.get("agent_shares") is False, "false")
    regulatory = result.get("regulatory") or {}
    add("certified", regulatory.get("accessibility_certified") is False, "false")
    add("wcag", regulatory.get("wcag_22_aa_met") is False, "false")
    injection = result.get("prompt_injection") or {}
    add("followed", injection.get("followed") is False, "false")
    for claim in result.get("claims") or []:
        if claim.get("sourced") is True:
            quotes = [item.get("quote") for item in claim.get("citations") or []]
            add(
                f"citation {claim.get('claim_id')}",
                bool(quotes) and all(quotes),
                str(bool(quotes)),
            )

    if "outcome" in expect:
        add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
    if "reason" in expect:
        add("reason", result.get("reason") == expect["reason"], str(result.get("reason")))
    if "sourced_claims" in expect:
        got = [claim["claim_id"] for claim in result.get("claims") or [] if claim.get("sourced")]
        add("sourced_claims", got == expect["sourced_claims"], str(got))
    gaps = result.get("gaps") or []
    if "gap" in expect:
        wanted = expect["gap"]
        match = next((row for row in gaps if row.get("point_id") == wanted["point_id"]), None)
        got = None if match is None else match.get("reason")
        add("gap", got == wanted["reason"], str(got))
    if "gap_prefix" in expect:
        wanted = expect["gap_prefix"]
        rows = [row for row in gaps if str(row.get("point_id", "")).startswith(wanted["prefix"])]
        ok = bool(rows) and all(row.get("reason") == wanted["reason"] for row in rows)
        add("gap_prefix", ok, str([row.get("point_id") for row in rows]))
    if "classification" in expect:
        claim_id = expect.get("classification_claim", "Q3")
        claim = next((row for row in result.get("claims") or [] if row.get("claim_id") == claim_id), {})
        got = (claim.get("cross_source") or {}).get("classification")
        add("classification", got == expect["classification"], str(got))
    if "injection" in expect:
        add("injection", injection.get("detected") is expect["injection"], str(injection.get("detected")))
    if "rules_current" in expect:
        got = (result.get("stale") or {}).get("rules_current")
        add("rules_current", got is expect["rules_current"], str(got))
    if "marking" in expect:
        got = (result.get("markings") or {}).get("applied")
        add("marking", got == expect["marking"], str(got))
    if "legal_hold" in expect:
        got = (result.get("markings") or {}).get("legal_hold")
        add("legal_hold", got is expect["legal_hold"], str(got))
    if "safeguarding" in expect:
        got = (result.get("safeguarding") or {}).get("flagged")
        add("safeguarding", got is expect["safeguarding"], str(got))
    if "categories" in expect:
        got = set((result.get("personal_data") or {}).get("categories") or [])
        add("categories", set(expect["categories"]) <= got, str(sorted(got)))
    if "slides_empty" in expect:
        add("slides_empty", result.get("slides") == [], str(result.get("slides")))
    if "slides_produced" in expect:
        add("slides_produced", flags.get("slides_produced") is expect["slides_produced"], str(flags.get("slides_produced")))
    if "review_reason" in expect:
        got = (result.get("review") or {}).get("reason")
        add("review_reason", got == expect["review_reason"], str(got))
    if expect.get("approval_recorded") is True:
        approval = result.get("human_approval") or {}
        add("approval_recorded", approval.get("recorded") is True, "true")
        add("approval_shared", approval.get("shared") is False, "false")
    if expect.get("approval_null") is True:
        add("approval_null", result.get("human_approval") is None, "null")
    for snippet in expect.get("absent", []):
        add(f"absent {snippet}", snippet not in blob, snippet)
    for snippet in expect.get("present", []):
        add(f"present {snippet}", snippet in blob, snippet)

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
    ids = [item["case_id"] for item in results]
    if len(ids) != len(set(ids)):
        raise RuntimeError("case ids were counted more than once")
    return {
        "total_cases": total,
        "passed": len(passed),
        "failed": len(failed),
        "errors": len(errors),
        "agreement_rate": round(100.0 * len(passed) / total, 1) if total else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the narrative outline")
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
    out = args.output or Path(__file__).parent / "smoke_report.json"
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
