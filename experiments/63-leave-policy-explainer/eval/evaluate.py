#!/usr/bin/env python3
"""Deterministic smoke test. Not a model evaluation. Each case is counted once."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.explain import explain  # noqa: E402

AS_OF = "2026-11-18"


def _load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def _check(result: dict, expect: dict) -> list[str]:
    errors: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    need(result.get("entitlement_decision") is None, "entitlement_decision was set")
    need(result.get("pay_decision") is None, "pay_decision was set")
    need(result.get("pay_rate") is None, "pay_rate was set")
    need(result.get("leave_booked") is False, "leave was booked")
    need(result.get("leave_recorded") is False, "leave was recorded")
    need(result.get("approved") is False, "the explanation was approved")
    need(result.get("coerced") is False, "an input was coerced")
    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], f"outcome {result.get('outcome')}")
    row = (result.get("policy") or [None])[0]
    if "section_id" in expect:
        need(isinstance(row, dict) and row.get("section_id") == expect["section_id"], "section")
    if "quote_contains" in expect:
        need(isinstance(row, dict) and expect["quote_contains"] in (row.get("quote") or ""), "quote missing")
    if "quote_excludes" in expect:
        need(isinstance(row, dict) and expect["quote_excludes"] not in (row.get("quote") or ""), "quote included a denied figure")
    if "answer_excludes" in expect:
        need(expect["answer_excludes"] not in (result.get("answer") or ""), "answer included a withheld figure")
    if "superseded_on_as_of" in expect:
        need(isinstance(row, dict) and row.get("superseded_on_as_of") is expect["superseded_on_as_of"], "superseded flag")
    if "review_overdue" in expect:
        need(isinstance(row, dict) and row.get("review_overdue") is expect["review_overdue"], "review flag")
    if "may_be_relied_on" in expect:
        need(result.get("may_be_relied_on") is expect["may_be_relied_on"], "may_be_relied_on")
    if expect.get("no_pay_rate"):
        need(result.get("pay_rate") is None, "rate")
        need(all(item.get("pay_rate") is None for item in result.get("statutory") or []), "statutory rate")
    if "statutory_id" in expect:
        ids = [item.get("id") for item in result.get("statutory") or []]
        need(expect["statutory_id"] in ids, "statutory id")
    if "in_force" in expect:
        match = next((item for item in result.get("statutory") or [] if item.get("id") == expect.get("statutory_id")), None)
        need(isinstance(match, dict) and match.get("in_force") == expect["in_force"], "in_force")
    if "claim_denied" in expect or "claim_not_included" in expect:
        claims = {item["phrase"]: item for item in result.get("claims") or []}
        phrase = expect.get("claim_denied") or expect.get("claim_not_included")
        claim = claims.get(phrase)
        need(isinstance(claim, dict), "claim missing")
        if isinstance(claim, dict) and "claim_denied" in expect:
            need(claim["denied"] is True and claim["included"] is False, "denial counted as inclusion")
        if isinstance(claim, dict) and "claim_not_included" in expect:
            need(claim["included"] is False, "phrase counted as included")
    if "care" in expect:
        signals = (result.get("care_route") or {}).get("signals") or []
        need(expect["care"] in signals, "care signal")
    if "care_any" in expect:
        signals = (result.get("care_route") or {}).get("signals") or []
        need(any(name in signals for name in expect["care_any"]), "care signal")
    if expect.get("no_care"):
        need(result.get("care_route") is None, "care route")
    if "input_problem" in expect:
        need(result.get("input_problem") == expect["input_problem"], "input problem")
    if "coerced" in expect:
        need(result.get("coerced") is expect["coerced"], "coerced")
    if "withheld_marking" in expect:
        markings = [item.get("marking") for item in result.get("withheld") or []]
        need(expect["withheld_marking"] in markings, "marking")
        need(all(item.get("body_copied") is False for item in result.get("withheld") or []), "body copied")
    if "body_absent" in expect:
        need(expect["body_absent"] not in json.dumps(result), "withheld body copied")
    if expect.get("depends_on_facts"):
        need(bool(result.get("depends_on_facts")), "facts")
    if "human_approval" in expect:
        need(result.get("human_approval") is expect["human_approval"], "approval")
    if "self_declared_role_trusted" in expect:
        need(result.get("self_declared_role_trusted") is False, "role trusted")
    if "instructions_followed" in expect:
        need(result.get("instructions", {}).get("followed") is False, "instruction followed")
    return errors


def run() -> dict:
    policies = _load("fixtures/policies.json")
    baseline = _load("fixtures/baseline.json")
    scope = _load("examples/sample_scope.json")
    directory = _load("fixtures/directory.json")
    dataset = _load("eval/synthetic_dataset.json")
    cases = []
    seen: set[str] = set()
    for case in dataset["cases"]:
        case_id = case["case_id"]
        if case_id in seen:
            cases.append({"case_id": case_id, "status": "error", "errors": ["duplicate case id"]})
            continue
        seen.add(case_id)
        question = {"synthetic": True, "text": case["text"], "about_date": case.get("about_date")}
        if "stated_balance" in case:
            question["stated_balance"] = case["stated_balance"]
        try:
            result = explain(question, policies, scope, baseline, directory, AS_OF)
            errors = _check(result, case["expect"])
        except Exception as exc:  # noqa: BLE001
            cases.append({"case_id": case_id, "status": "error", "errors": [type(exc).__name__]})
            continue
        cases.append(
            {
                "case_id": case_id,
                "status": "passed" if not errors else "failed",
                "errors": errors,
                "outcome": result.get("outcome"),
            }
        )
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = sum(1 for case in cases if case["status"] == "failed")
    errors = sum(1 for case in cases if case["status"] == "error")
    return {
        "evaluation_label": "DETERMINISTIC SMOKE TEST. Not a model evaluation.",
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "model_called": False,
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the leave policy explainer.")
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = run()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"DETERMINISTIC SMOKE TEST {summary['passed']}/{summary['total_cases']} passed. "
        "Not a model evaluation."
    )
    if summary["failed"] or summary["errors"]:
        print(json.dumps(report["cases"], indent=2))
        return 1
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        print("Smoke totals do not add up.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
