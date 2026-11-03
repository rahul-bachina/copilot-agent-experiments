#!/usr/bin/env python3
"""Deterministic smoke test for the cost and capacity report.

This is not a model evaluation and it is not a Microsoft invoice.
Case costs are not added together. Two cases that describe the same
month would double-count if a grand total were taken.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.report import evaluate  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _materialise(case: dict, dataset_path: Path) -> tuple[dict, dict]:
    base = dataset_path.parent
    if "bundle" in case:
        bundle = copy.deepcopy(case["bundle"])
    else:
        bundle = _load((base / case["bundle_file"]).resolve())
    if "rate_card" in case:
        rate_card = copy.deepcopy(case["rate_card"])
    else:
        rate_card = _load((base / case["rate_card_file"]).resolve())
    return bundle, rate_card


def _expect(expect: dict, report: dict) -> list[str]:
    problems = []
    totals = report["totals"]
    checks = {
        "totals_cost": totals["cost"],
        "partial_cost": totals["partial_cost"],
        "copilot_credits": totals["copilot_credits"],
        "priced_tokens_on_credit_agents": report["priced_tokens_on_credit_agents"],
        "added_rollup": report["added_rollup"],
        "rates_validated": report["rates_validated"],
        "forecast_validated": report["forecast_validated"],
        "quota_changed": report["quota_changed"],
        "budget_changed": report["budget_changed"],
        "subscription_changed": report["subscription_changed"],
        "do_not_rely": report["do_not_rely"],
        "refused": report["refused"],
        "forecast_point": report["forecast"].get("point"),
        "forecast_low": report["forecast"].get("low"),
        "forecast_high": report["forecast"].get("high"),
        "forecast_validated_inside": report["forecast"].get("validated"),
        "injection_followed": report["prompt_injection"]["followed"],
        "injection_detected": report["prompt_injection"]["detected"],
        "prohibited_taken": report["prohibited_actions"]["taken"],
        "duplicates_dropped": totals.get("agent_rows_dropped_as_duplicates"),
    }
    for key, actual in checks.items():
        if key in expect and actual != expect[key]:
            problems.append(f"{key}: expected {expect[key]!r}, got {actual!r}")
    if expect.get("agent_cost_sum_matches_total"):
        if totals["cost"] is None:
            problems.append("total is null")
        else:
            agent_sum = sum(int(row["cost"].replace(".", "")) for row in report["agents"])
            total_units = int(totals["cost"].replace(".", ""))
            if agent_sum != total_units:
                problems.append(f"agent lines {agent_sum} != total {total_units}")
            if totals["partial_cost"] != totals["cost"]:
                problems.append("partial_cost differs from cost on a complete report")
    if "anomaly" in expect:
        ids = [row["id"] for row in report["anomalies"]]
        if expect["anomaly"] not in ids:
            problems.append(f"missing anomaly {expect['anomaly']}")
    if "anomaly_absent" in expect and any(row["id"] == expect["anomaly_absent"] for row in report["anomalies"]):
        problems.append(f"unexpected anomaly {expect['anomaly_absent']}")
    if expect.get("foundry_input_used"):
        quota = next(row for row in report["capacity"] if row["quota_id"] == "foundry-input")
        if quota["used"] != expect["foundry_input_used"]:
            problems.append(f"foundry input used {quota['used']}")
    if "phrase_absent" in expect and expect["phrase_absent"] in json.dumps(report):
        problems.append("injected phrase was echoed")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic cost smoke test.")
    parser.add_argument("--dataset", default=str(Path(__file__).with_name("synthetic_dataset.json")))
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    dataset_path = Path(args.dataset)
    dataset = _load(dataset_path)
    cases = []
    failed = 0
    errors = 0
    for case in dataset["cases"]:
        try:
            bundle, rate_card = _materialise(case, dataset_path)
            report = evaluate(bundle, rate_card, as_of=case["as_of"])
            problems = _expect(case.get("expect") or {}, report)
        except Exception as exc:  # noqa: BLE001 — one bad case must not hide the rest
            errors += 1
            failed += 1
            cases.append({"id": case.get("id"), "error": f"{exc.__class__.__name__}: {exc}"})
            continue
        if problems:
            failed += 1
        cases.append(
            {
                "id": case["id"],
                "passed": not problems,
                "problems": problems,
                "totals_cost": report["totals"]["cost"],
                "partial_cost": report["totals"]["partial_cost"],
                "added_rollup": report["added_rollup"],
                "priced_tokens_on_credit_agents": report["priced_tokens_on_credit_agents"],
                "rates_validated": report["rates_validated"],
                "forecast_validated": report["forecast_validated"],
                "quota_changed": report["quota_changed"],
                "do_not_rely": report["do_not_rely"],
                "refused": report["refused"],
                "model_called": report["model_called"],
                "network_called": report["network_called"],
                "microsoft_prices_used": report["microsoft_prices_used"],
            }
        )
    passed = len(cases) - failed
    summary = {
        "total_cases": len(cases),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "agreement_rate": round((passed / len(cases)) * 100, 1) if cases else 0,
    }
    # No grand total. Summing case costs would count the same synthetic month more than once.
    if "grand_total" in summary:
        raise SystemExit("smoke summary must not total the cases")
    out = {
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_microsoft_invoice": True,
        "evaluation_label": "DETERMINISTIC SMOKE TEST",
        "summary": summary,
        "cases": cases,
    }
    text = json.dumps(out, indent=2) + "\n"
    destination = Path(args.output) if args.output else Path(__file__).with_name("smoke_report.json")
    destination.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if failed or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
