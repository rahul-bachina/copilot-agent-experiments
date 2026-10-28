#!/usr/bin/env python3
"""Deterministic smoke test of the evidence pack builder.

The fixtures are synthetic. The checker is the Python under src/, which calls
Experiment 12 and, through it, Experiment 08. This is not a model score and
it does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pack import (  # noqa: E402
    LABEL,
    NotSynthetic,
    PackApprovalRefused,
    PackForbidden,
    build_pack,
    produce_export,
    record_export_approval,
    send_external,
)

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which calls Experiment 12 and Experiment 08. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _date(value):
    if value is None:
        return None
    return date.fromisoformat(value)


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
    try:
        result = build_pack(
            case["request"],
            as_of=as_of,
            pack_type=case["pack_type"],
            authorised_scopes=case["authorised_scopes"],
            search_from=_date(case.get("search_from")),
            search_to=_date(case.get("search_to")),
            rules_as_of=_date(case.get("rules_as_of")),
        )
    except NotSynthetic as exc:
        message = str(exc)
        if expect.get("outcome") == "refused":
            add("refused", True, "NotSynthetic")
            for index, token in enumerate(expect.get("absent", []), start=1):
                add(f"absent planted value {index}", token not in message, "not in the refusal")
            return finish("passed")
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": f"NotSynthetic: {message}",
            "checks": checks,
        }
    except Exception as exc:  # noqa: BLE001 — one bad fixture must not hide the rest
        return {
            "case_id": case["id"],
            "name": case.get("name", ""),
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "checks": checks,
        }

    if expect.get("outcome") == "refused":
        add("refused", False, "build_pack returned a draft")
        return finish("failed")

    serialised = json.dumps(result)
    add("label", result["label"] == LABEL, result["label"])
    add("export_approved", result["export_approved"] is False, "false")
    add("redactions_approved", result["redactions_approved"] is False, "false")
    add("approver_name", result["approver_name"] is None, "null")
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("injection_followed", result["prompt_injection"]["followed"] is False, "false")
    add("exemption_applied", result["law"]["exemption_applied"] is False, "false")
    add("search_decided", result["law"]["reasonable_and_proportionate_search_decided"] is False, "false")
    add("anonymised", result["gateway"]["output_is_anonymised"] is False, "false")
    add("may_release", result["gateway"]["agent_may_release"] is False, "false")
    add("external_sent", result["flags"]["external_sent"] is False, "false")
    add("disclosed", result["flags"]["disclosed_to_requester"] is False, "false")

    rows = {row["item_id"]: row for row in result["items"]}

    if "injection_detected" in expect:
        actual = result["prompt_injection"]["detected"]
        add("injection_detected", actual is expect["injection_detected"], str(actual))
    if "hidden_in" in expect:
        found = {signal["hidden_in"] for signal in result["prompt_injection"]["signals"]}
        add("hidden_in", expect["hidden_in"] in found, ",".join(sorted(found)) or "none")
    if "proposed_ids" in expect:
        actual = [row["item_id"] for row in result["proposed_index"]]
        add("proposed_ids", actual == expect["proposed_ids"], ",".join(actual) or "none")
    if "held_ids" in expect:
        actual = [row["item_id"] for row in result["held_for_review"]]
        add("held_ids", actual == expect["held_ids"], ",".join(actual) or "none")
    if "intake_called" in expect:
        add("intake_called", result["intake"]["called"] is expect["intake_called"], str(result["intake"]["called"]))
    if "intake_purpose" in expect:
        actual = result["intake"]["purpose_preview"]
        add("intake_purpose", actual == expect["intake_purpose"], str(actual))
    if "pack_type" in expect:
        add("pack_type", result["pack_type"] == expect["pack_type"], result["pack_type"])
    if "authorised_scopes" in expect:
        add("authorised_scopes", result["authorised_scopes"] == expect["authorised_scopes"], ",".join(result["authorised_scopes"]))
    if "sources_stale" in expect:
        add("sources_stale", result["sources_stale"] is expect["sources_stale"], str(result["sources_stale"]))
    if "search_period_set" in expect:
        actual = result["search_period"]["set"]
        add("search_period_set", actual is expect["search_period_set"], str(actual))

    for item_id, reason in expect.get("excluded_reason", {}).items():
        excluded = next(row for row in result["excluded"] if row["item_id"] == item_id)
        add(f"excluded {item_id}", reason in excluded["reasons"], ",".join(excluded["reasons"]))
    for item_id, flag in expect.get("possible_privilege", {}).items():
        add(f"privilege {item_id}", rows[item_id]["possible_privilege"] is flag, str(rows[item_id]["possible_privilege"]))
        add(f"exemption {item_id}", rows[item_id]["exemption_applied"] is False, "false")
    for item_id, types in expect.get("entity_types_include", {}).items():
        actual = rows[item_id]["entity_types"]
        missing = [name for name in types if name not in actual]
        add(f"entity_types {item_id}", not missing, ",".join(actual) or "none")
    for item_id, position in expect.get("date_position", {}).items():
        add(f"date {item_id}", rows[item_id]["date_position"] == position, rows[item_id]["date_position"])
    for item_id, flag in expect.get("eligible", {}).items():
        add(f"eligible {item_id}", rows[item_id]["eligible_for_approval"] is flag, str(rows[item_id]["eligible_for_approval"]))
    for item_id, earlier in expect.get("duplicate_of", {}).items():
        add(f"duplicate {item_id}", rows[item_id]["duplicate_of"] == earlier, str(rows[item_id]["duplicate_of"]))
    for item_id, status in expect.get("read_status", {}).items():
        add(f"read {item_id}", rows[item_id]["read_status"] == status, str(rows[item_id]["read_status"]))
    if "checksum_matches" in expect:
        item_id, flag = next(iter(expect["checksum_matches"].items()))
        add("checksum", rows[item_id]["checksum_matches"] is flag, str(rows[item_id]["checksum_matches"]))
    for index, token in enumerate(expect.get("absent", []), start=1):
        omitted = token not in serialised and token.replace(" ", "") not in serialised
        add(f"absent planted value {index}", omitted, "omitted")

    approval = case.get("approval")
    if approval:
        kwargs = {
            "role": approval["role"],
            "approver_name": approval["approver_name"],
            "approved_item_ids": approval["approved_item_ids"],
            "redaction_decisions": approval.get("redaction_decisions") or {},
            "acknowledge_stale": approval.get("acknowledge_stale", False),
        }
        try:
            approved = record_export_approval(result, **kwargs)
        except PackApprovalRefused:
            add("approval", approval["expect"] == "refused", "refused")
            return finish("passed" if approval["expect"] == "refused" else "failed")
        add("approval", approval["expect"] == "approved", "approved")
        if approval["expect"] != "approved":
            return finish("failed")
        add("still_not_sent", approved["flags"]["external_sent"] is False, "false")
        add("still_not_exempt", approved["law"]["exemption_applied"] is False, "false")
        if approval.get("then_export"):
            export = produce_export(approved)
            add("export_sent", export["sent"] is False, "false")
            add("bodies_included", export["bodies_included"] is False, "false")
            add("export_anonymised", export["output_is_anonymised"] is False, "false")
            if "export_order" in approval:
                actual = [page["item_id"] for page in export["pages"]]
                add("export_order", actual == approval["export_order"], ",".join(actual))
            export_text = json.dumps(export)
            for index, token in enumerate(expect.get("absent", []), start=1):
                add(f"absent from export {index}", token not in export_text, "omitted")
        if approval.get("then_send"):
            try:
                send_external(approved)
            except PackForbidden:
                add("send_blocked", True, "PackForbidden")
            else:
                add("send_blocked", False, "send returned")
    if expect.get("export_before_approval"):
        try:
            produce_export(result)
        except PackForbidden:
            add("export_before_approval", True, "refused")
        else:
            add("export_before_approval", False, "produced")

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
    parser = argparse.ArgumentParser(description="Deterministic smoke test of the evidence pack builder")
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
    if summary["total_cases"] < 16:
        sys.stderr.write("Fewer than 16 synthetic cases\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
