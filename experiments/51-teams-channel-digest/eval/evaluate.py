#!/usr/bin/env python3
"""Deterministic smoke test of the Teams channel digest.

The fixtures are synthetic. The checker is the Python under src/. This is not
a model score and it does not call a model. Each case is counted once.
Section counts are not added to the case count.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from digest import LABEL, run  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle(case: dict) -> dict:
    channels = []
    for channel in case.get("channels") or [
        {
            "channel_id": "SYN-CH-CABINET",
            "display_name": "Cabinet forward plan",
            "available": True,
            "messages": case.get("messages") or [],
        }
    ]:
        messages = []
        for item in channel.get("messages") or []:
            messages.append(
                {
                    "message_id": item["message_id"],
                    "sent_on": item.get("sent_on", "2026-11-03"),
                    "author_display_name": item.get("author_display_name", "Alex Wren"),
                    "body": item.get("body", ""),
                    **({"sensitivity": item["sensitivity"]} if "sensitivity" in item else {}),
                }
            )
        channels.append(
            {
                "channel_id": channel["channel_id"],
                "display_name": channel.get("display_name", channel["channel_id"]),
                "available": channel.get("available", True),
                "messages": messages,
            }
        )
    requested = case.get("requested") or [row["channel_id"] for row in channels]
    accessible = case.get("accessible")
    if accessible is None:
        accessible = [row["channel_id"] for row in channels]
    period = case.get("period") or ["2026-11-01", "2026-11-12"]
    return {
        "synthetic": case.get("synthetic", True),
        "organisation": case.get("organisation", "Northmere Borough Council"),
        "sector": case.get("sector", "public_body"),
        "export_id": case.get("export_id", "SYN-EXP-051"),
        "retrieved_on": case.get("retrieved_on", "2026-11-10"),
        "requesting_user": {
            "user_id": "SYN-USER-051",
            "display_name": case.get("display_name", "Rowan Hale"),
            "accessible_channel_ids": accessible,
        },
        "request": {
            "channel_ids": requested,
            "period_start": period[0],
            "period_end": period[1],
        },
        "channels": channels,
    }


def _review(case: dict) -> dict | None:
    if not case.get("confirm"):
        return None
    period = case.get("period") or ["2026-11-01", "2026-11-12"]
    review = {
        "decision": case.get("decision", "confirm_channels_and_period"),
        "actor_role": "Requesting user",
        "actor_id": "SYN-USER-051",
        "export_id": case.get("export_id", "SYN-EXP-051"),
        "channel_ids": case.get("confirm_channels") or case.get("requested") or ["SYN-CH-CABINET"],
        "period_start": period[0],
        "period_end": period[1],
    }
    review.update(case.get("review_flags") or {})
    return review


def evaluate_case(case: dict) -> dict:
    expect = case["expect"]
    try:
        result = run(_bundle(case), case.get("as_of", "2026-11-12"), _review(case))
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
    add("posted", (result.get("flags") or {}).get("posted") is False, "false")
    add("replied", (result.get("flags") or {}).get("replied") is False, "false")
    add("reacted", (result.get("flags") or {}).get("reacted") is False, "false")
    add("mentioned", (result.get("flags") or {}).get("mentioned") is False, "false")
    add("forwarded", (result.get("flags") or {}).get("forwarded") is False, "false")
    add("graph", result.get("graph_called") is False, "false")
    add("network", result.get("network_called") is False, "false")
    add("model", result.get("model_called") is False, "false")
    add("foundry", result.get("foundry_called") is False, "false")
    add("approval", result.get("human_approval") is None, "null")
    add("human_route", (result.get("human_route") or {}).get("offered") is True, "true")
    add("a3", result.get("a3_recommended") is False, "false")
    regulatory = result.get("regulatory") or {}
    if regulatory:
        add("purpose_met", regulatory.get("purpose_limitation_met") is False, "false")
        add("minimisation_met", regulatory.get("data_minimisation_met") is False, "false")
        add("monitoring", regulatory.get("monitoring_decided") is False, "false")
        add("held", regulatory.get("held_information_decided") is False, "false")

    if "digest_produced" in expect:
        add("digest_produced", result.get("digest_produced") is expect["digest_produced"], str(result.get("digest_produced")))
    if "outcome" in expect:
        add("outcome", result.get("outcome") == expect["outcome"], str(result.get("outcome")))
    digest = result.get("digest") or {}
    decisions = digest.get("decisions") or []
    if "decision" in expect:
        got = decisions[0]["text"] if decisions else None
        add("decision", got == expect["decision"], str(got))
    if "decision_count" in expect:
        add("decision_count", len(decisions) == expect["decision_count"], str(len(decisions)))
    if "owner" in expect:
        actions = digest.get("actions") or []
        got = actions[0]["owner"] if actions else None
        add("owner", got == expect["owner"], str(got))
    if "withheld_reason" in expect:
        reasons = [row.get("reason") for row in (digest.get("withheld") or [])]
        add("withheld_reason", expect["withheld_reason"] in reasons, str(reasons))
    if "negation_reason" in expect:
        reasons = [row.get("reason") for row in ((digest.get("negation") or {}).get("rows") or [])]
        add("negation_reason", expect["negation_reason"] in reasons, str(reasons))
    if "confirmation_reason" in expect:
        got = (result.get("scope_confirmation") or {}).get("reason")
        add("confirmation_reason", got == expect["confirmation_reason"], str(got))
    if "injection_followed" in expect:
        got = (result.get("prompt_injection") or {}).get("followed")
        add("injection_followed", got is expect["injection_followed"], str(got))
    if "entity" in expect:
        types = ((result.get("reuse") or {}).get("experiment_08") or {}).get("entity_types") or []
        add("entity", expect["entity"] in types, str(types))
    if "sources_current" in expect:
        got = regulatory.get("sources_current")
        add("sources_current", got is expect["sources_current"], str(got))
    if "channel_status" in expect:
        statuses = [row.get("status") for row in (result.get("channels") or [])]
        add("channel_status", expect["channel_status"] in statuses, str(statuses))
    if "absent" in expect:
        add("absent", expect["absent"] not in blob, "present" if expect["absent"] in blob else "absent")
    if "stale_export" in expect:
        got = (result.get("stale_export") or {}).get("stale")
        add("stale_export", got is expect["stale_export"], str(got))

    counts = digest.get("counts") or {}
    if counts:
        add(
            "no_combined_total",
            "total" not in counts and counts.get("section_counts_are_not_added_to_message_count") is True,
            "separate",
        )

    passed = all(item["passed"] for item in checks)
    return {
        "case_id": case["id"],
        "name": case.get("name", ""),
        "status": "passed" if passed else "failed",
        "checks": checks,
    }


def evaluate(dataset: dict | None = None) -> dict:
    if dataset is None:
        dataset = load_dataset()
    cases = [evaluate_case(case) for case in dataset["cases"]]
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = sum(1 for case in cases if case["status"] == "failed")
    errors = sum(1 for case in cases if case["status"] == "error")
    total = len(cases)
    if passed + failed + errors != total:
        raise RuntimeError("Smoke totals do not add up.")
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Case ids are not one row each.")
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "catalogue_id": "M002",
        "experiment": "51-teams-channel-digest",
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "agreement_rate": round(100 * passed / total, 2) if total else None,
            "each_case_counted_once": True,
            "section_counts_are_not_added_to_case_count": True,
        },
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the deterministic digest smoke test.")
    parser.add_argument("--output", default=None)
    parser.add_argument("--dataset", default=None)
    args = parser.parse_args(argv)
    dataset = load_dataset(Path(args.dataset) if args.dataset else None)
    report = evaluate(dataset)
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    print(
        f"{summary['passed']} passed, {summary['failed']} failed, {summary['errors']} errors, {summary['total_cases']} cases",
        file=sys.stderr,
    )
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
