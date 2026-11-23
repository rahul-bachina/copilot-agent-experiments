#!/usr/bin/env python3
"""Deterministic smoke test. Not a model evaluation.

Each case is one row. Paraphrase recall is reported beside the cases and is
not added to the case total.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from src.register import propose_register  # noqa: E402
from test_paraphrase import score_paraphrases  # noqa: E402

SAMPLE = json.loads((ROOT / "examples" / "sample_request.json").read_text(encoding="utf-8"))
DATASET = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def _run(case: dict) -> dict:
    request = deepcopy(SAMPLE)
    if "note" in case:
        request["note"] = case["note"]
    if "cover" in case:
        request["cover"] = case["cover"]
    if "marking" in case:
        request["marking"] = case["marking"]
    if "legal_hold" in case:
        request["legal_hold"] = case["legal_hold"]
    return propose_register(request, case.get("as_of", "2026-11-14"))


def _change(result: dict, obligation_id: str) -> dict | None:
    return next((row for row in result.get("changes") or [] if row.get("obligation_id") == obligation_id), None)


def _check(case: dict, result: dict) -> list[str]:
    errors = []
    expect = case["expect"]
    blob = json.dumps(result)

    def need(condition: bool, name: str) -> None:
        if not condition:
            errors.append(name)

    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], "outcome")
    if "owner" in expect:
        need(result.get("proposed_owner_ref") == expect["owner"], "owner")
    if "applied" in expect:
        need((result.get("marking") or {}).get("applied") == expect["applied"], "applied")
    if "unchanged" in expect:
        need(expect["unchanged"] in (result.get("unchanged") or []), "unchanged")
    if "absent" in expect:
        need(expect["absent"] not in blob, "absent")
    if "used_caller" in expect:
        need((result.get("caller_sources") or {}).get("used_caller") is expect["used_caller"], "used_caller")
    if "changes" in expect:
        need(len(result.get("changes") or []) == expect["changes"], "changes")
    if "cue" in expect:
        need(expect["cue"] in (result.get("cues") or {}).get("categories", []), "cue")
    if "held" in expect:
        need((result.get("legal_hold") or {}).get("held") is expect["held"], "held")
    if "followed" in expect:
        need(result.get("instructions_followed") is expect["followed"], "followed")
        need((result.get("prompt_injection") or {}).get("followed") is False, "injection")
    if "unreadable" in expect:
        need((result.get("people_count") or {}).get("unreadable") is expect["unreadable"], "unreadable")
    if "number_stored" in expect:
        need((result.get("people_count") or {}).get("number_stored") is expect["number_stored"], "number_stored")
    if "retention" in expect:
        labels = (result.get("retention") or {}).get("labels") or []
        need(any(expect["retention"] in label for label in labels), "retention")
    if "as_of" in expect:
        need(result.get("as_of") == expect["as_of"], "as_of")
    if "withheld" in expect:
        texts = [row.get("after", {}).get("obligation_text") for row in result.get("changes") or []]
        need(bool(texts) and all(text == "not copied" for text in texts), "withheld")
    if "pins_final_advice" in expect:
        pins = result.get("context_pins") or []
        need(bool(pins) and all(pin.get("final_advice") is expect["pins_final_advice"] for pin in pins), "pins")
    if "statutory_minimum_stated" in expect:
        need(result.get("statutory_minimum_stated") is expect["statutory_minimum_stated"], "statutory")
    if "marked_acceptable" in expect:
        need(result.get("marked_acceptable") is expect["marked_acceptable"], "acceptable")
    if "change" in expect:
        spec = expect["change"]
        row = _change(result, spec["id"])
        need(row is not None, "change_missing")
        if row is not None:
            after = row.get("after") or {}
            if "action" in spec:
                need(row.get("action") == spec["action"], "action")
            if "covered" in spec:
                need(after.get("covered") is spec["covered"], "covered")
            if "included" in spec:
                need(after.get("included") is spec["included"], "included")
            if "qualified" in spec:
                need(after.get("qualified") is spec["qualified"], "qualified")
            if "in_force" in spec:
                need(after.get("in_force") is spec["in_force"], "in_force")
            if "status" in spec:
                need(after.get("status") == spec["status"], "status")
            if "applicability" in spec:
                need(after.get("applicability") == spec["applicability"], "applicability")
            if "stale" in spec:
                need(after.get("review_stale") is spec["stale"], "stale")
            if "below" in spec:
                need(after.get("below_internal_minimum") is spec["below"], "below")
            if "duplicate" in spec:
                need(after.get("possible_duplicate_of") == spec["duplicate"], "duplicate")
            if "review_date" in spec:
                need(after.get("review_date") == spec["review_date"], "review_date")
            if "links" in spec:
                need(after.get("linked_controls") == spec["links"], "links")
    need(result.get("sent") is False, "sent")
    need(result.get("production_written") is False, "production_written")
    need(result.get("human_approval") is None, "human_approval")
    need(result.get("staged") is False, "staged")
    need(result.get("final_advice") is False, "final_advice")
    need(result.get("may_be_relied_on") is False, "may_be_relied_on")
    need(result.get("coerced") is False, "coerced")
    need(result.get("accountability_assigned_by_agent") is False, "accountability")
    return errors


def evaluate() -> dict:
    cases = []
    for case in DATASET["cases"]:
        try:
            result = _run(case)
            errors = _check(case, result)
            status = "passed" if not errors else "failed"
        except Exception as exc:  # noqa: BLE001 — smoke must count an error once
            errors = [exc.__class__.__name__]
            status = "error"
        cases.append({"case_id": case["case_id"], "status": status, "errors": errors})
    passed = sum(1 for row in cases if row["status"] == "passed")
    failed = sum(1 for row in cases if row["status"] == "failed")
    errors = sum(1 for row in cases if row["status"] == "error")
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "summary": {
            "total_cases": len(cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
        "cases": cases,
        "paraphrase_recall": score_paraphrases(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "eval" / "smoke_report.json"))
    args = parser.parse_args(argv)
    report = evaluate()
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(f"Smoke test {summary['passed']}/{summary['total_cases']} passed")
    if summary["failed"] or summary["errors"]:
        print(json.dumps(report["cases"], indent=2))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
