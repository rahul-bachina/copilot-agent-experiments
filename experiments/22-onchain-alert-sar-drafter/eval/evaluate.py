#!/usr/bin/env python3
"""Deterministic smoke test of the on-chain alert draft.

The fixtures are synthetic. The checker is the Python under src/, which can
call Experiments 04, 08, 10, and 16. This is not a model score and it does
not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.investigate import LABEL, NotSynthetic, investigate  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which can call Experiments 04, 08, 10, and 16. "
    "Not a measure of model accuracy. No model was called."
)

FALSE_FLAGS = (
    "sar_filed",
    "nca_contacted",
    "daml_requested",
    "customer_contacted",
    "account_frozen",
    "crypto_moved",
    "suspicion_recorded_by_agent",
    "mlro_decision_recorded",
    "glossary_codes_assigned",
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
            investigate(case["alert_case"], as_of=as_of, stale_after_days=window)
        except NotSynthetic as exc:
            message = str(exc)
            add("refused", True, "NotSynthetic")
            for index, token in enumerate(expect.get("absent", []), start=1):
                add(f"absent planted value {index}", token not in message, "not in the refusal")
            return finish("passed")
        except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
            return {
                "case_id": case["id"],
                "name": case.get("name", ""),
                "status": "error",
                "error": f"{type(exc).__name__}: {exc}",
                "checks": checks,
            }
        add("refused", False, "investigate returned a draft")
        return finish("failed")

    try:
        result = investigate(case["alert_case"], as_of=as_of, stale_after_days=window)
    except Exception as exc:  # noqa: BLE001
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "checks": [],
        }

    serialised = json.dumps(result)
    narrative = result["sar_narrative"]["reason_for_suspicion_draft"]
    lowered = narrative.casefold()
    add("label", result["label"] == LABEL, result["label"])
    add("catalogue", result["catalogue_id"] == "UK07", result["catalogue_id"])
    add("mlro_decision", result["mlro_decision"] is None, "null")
    add("sar_filed", result["sar_filed"] is False, "false")
    add("nca_contacted", result["nca_contacted"] is False, "false")
    add("daml_requested", result["daml_requested"] is False, "false")
    add("customer_told", result["customer_told"] is False, "false")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("chain_queried", result["chain_queried"] is False, "false")
    add("glossary", result["glossary_codes_assigned"] is False, "false")
    add("suspicion_recorded", result["suspicion_recorded_by_agent"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("customer_text", result["customer_facing"]["text"] is None, "null")
    add("customer_drafted", result["customer_facing"]["drafted"] is False, "false")
    add("customer_not_sent", result["customer_facing"]["may_be_sent_by_agent"] is False, "false")
    add("request_not_echoed", result["customer_facing"]["request_echoed"] is False, "false")
    add("not_a_disclosure", result["sar_narrative"]["not_a_disclosure"] is True, "true")
    add("not_submitted", result["sar_narrative"]["not_submitted"] is True, "true")
    add("statutory_test", result["sar_narrative"]["statutory_test_applied"] is False, "false")
    add("marc_not_applied", result["sar_narrative"]["marc_sentence_applied"] is False, "false")
    add("no we suspect", "we suspect" not in lowered and "i suspect" not in lowered, "absent")
    add("grounds not made out", "reasonable grounds are made out" not in lowered, "absent")
    add("statutory quotation kept", "knows or suspects" in narrative, "quoted")
    for flag in FALSE_FLAGS:
        add(f"flag {flag}", result["flags"][flag] is False, "false")
    for indicator in result["indicators_for_a_person"]:
        add(
            f"indicator {indicator['id']} is not a suspicion",
            indicator["is_a_suspicion"] is False and indicator["decided_by_agent"] is False,
            "false",
        )

    if "sources_stale" in expect:
        add("sources_stale", result["sources_stale"] is expect["sources_stale"], str(result["sources_stale"]))
    if "rules_current" in expect:
        add("rules_current", result["rules_current"] is expect["rules_current"], str(result["rules_current"]))
    if "alert_context_stale" in expect:
        add(
            "alert_context_stale",
            result["alert_context_stale"] is expect["alert_context_stale"],
            str(result["alert_context_stale"]),
        )
    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "signals_include" in expect:
        actual = result["prompt_injection"]["signals"]
        missing = [item for item in expect["signals_include"] if item not in actual]
        add("signals_include", not missing, ",".join(actual) or "none")
    if "prohibited_includes" in expect:
        actual = result["prompt_injection"]["prohibited_payload_keys_ignored"]
        missing = [item for item in expect["prohibited_includes"] if item not in actual]
        add("prohibited_keys", not missing, ",".join(actual) or "none")
    if "indicator_ids" in expect:
        actual = [item["id"] for item in result["indicators_for_a_person"]]
        missing = [item for item in expect["indicator_ids"] if item not in actual]
        add("indicator_ids", not missing, ",".join(actual) or "none")
    if "travel_called" in expect:
        travel = result["travel_rule"]
        called = bool(travel and travel.get("called"))
        add("travel_called", called is expect["travel_called"], str(called))
        if travel:
            add("travel_decision", travel.get("analyst_decision") is None, "null")
    if "travel_categories_include" in expect:
        categories = (result["travel_rule"] or {}).get("exception_categories") or []
        missing = [item for item in expect["travel_categories_include"] if item not in categories]
        add("travel_categories", not missing, ",".join(categories) or "none")
    if "kyc_called" in expect:
        kyc = result["kyc"]
        called = bool(kyc and kyc.get("called"))
        add("kyc_called", called is expect["kyc_called"], str(called))
        if kyc and kyc.get("called"):
            add("kyc_documents", kyc["documents_confirmed"] is False, "false")
            add("kyc_note_not_copied", kyc["customer_facing_copied"] is False, "false")
    if "future_hop" in expect:
        hops = [event for event in result["evidence_timeline"] if event["kind"] == "on_chain_hop"]
        future = any(event["future"] and not event["placed"] for event in hops)
        add("future_hop", future is expect["future_hop"], str(future))
    if "omitted_field_contains" in expect:
        fields = [item["field"] for item in result["omitted_identifiers"]]
        add(
            "omitted_field",
            any(expect["omitted_field_contains"] in field for field in fields),
            ",".join(fields) or "none",
        )
        reasons = {item["reason"] for item in result["omitted_identifiers"]}
        add("omitted_reason", "not_a_synthetic_token" in reasons, ",".join(sorted(reasons)) or "none")
    if "text_not_fully_read_contains" in expect:
        unread = result["text_not_fully_read"]
        add(
            "text_not_fully_read",
            any(expect["text_not_fully_read_contains"] in item for item in unread),
            ",".join(unread) or "none",
        )
    if "narrative_contains" in expect:
        missing = [item for item in expect["narrative_contains"] if item not in narrative]
        add("narrative_contains", not missing, "present" if not missing else ",".join(missing))
    if "over_limit" in expect:
        actual = result["sar_narrative"]["over_ukfiu_reason_field_limit"]
        add("over_limit", actual is expect["over_limit"], str(actual))
    if "gateway_called" in expect:
        actual = result["identifier_gateway"]["called"]
        add("gateway_called", actual is expect["gateway_called"], str(actual))
    if "gateway_types_include" in expect:
        types = result["identifier_gateway"].get("entity_types") or []
        missing = [item for item in expect["gateway_types_include"] if item not in types]
        add("gateway_types", not missing, ",".join(types) or "none")
    for index, token in enumerate(expect.get("absent", []), start=1):
        add(f"absent planted value {index}", token not in serialised, "omitted")

    return finish("passed")


def summarise(results: list[dict]) -> dict:
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
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the alert draft")
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
    sys.stdout.write(text)
    if summary["failed"] or summary["errors"]:
        return 1
    if summary["total_cases"] < 24:
        sys.stderr.write("Fewer than 24 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
