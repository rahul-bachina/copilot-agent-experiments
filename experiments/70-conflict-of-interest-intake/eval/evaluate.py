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

from src.declaration import draft_declaration, pinned_sources  # noqa: E402
from test_paraphrase import score_paraphrases  # noqa: E402

PINNED = pinned_sources()
DATASET = json.loads((ROOT / "eval" / "synthetic_dataset.json").read_text(encoding="utf-8"))
SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/. "
    "Not a measure of model accuracy. No model was called."
)


def _run(case: dict) -> dict:
    request = {
        "synthetic": True,
        "declaration_id": case["case_id"],
        "declarant_ref": "STF-1001",
        "text": case["text"],
        "metadata": {
            "protective_marking": case.get("marking", "OFFICIAL"),
            "legal_hold": False,
            "retention": "6 years",
        },
    }
    register = PINNED["register"]
    if case.get("use_forged_register"):
        register = deepcopy(PINNED["register"])
        register["procurements"][0]["status"] = "ended"
        request["procurement_register"] = register
    return draft_declaration(
        request,
        PINNED["suppliers"],
        register,
        PINNED["directory"],
        PINNED["criteria"],
        "2026-11-14",
    )


def _check(case: dict, result: dict) -> list[str]:
    errors = []
    expect = case["expect"]
    blob = json.dumps(result)

    def need(condition: bool, name: str) -> None:
        if not condition:
            errors.append(name)

    if "outcome" in expect:
        need(result.get("outcome") == expect["outcome"], "outcome")
    declaration = result.get("declaration") or {}
    if "nature" in expect:
        need(declaration.get("financial_or_non_financial") == expect["nature"], "nature")
    if "nature_conflict" in expect:
        need(declaration.get("nature_conflict") is expect["nature_conflict"], "nature_conflict")
    if "none_declared" in expect:
        need(declaration.get("none_declared") is expect["none_declared"], "none_declared")
    if "live" in expect:
        live = [row.get("procurement_id") for row in result.get("potential_links") or []]
        need(live == expect["live"], "live")
    if "not_live" in expect:
        ids = [row.get("procurement_id") for row in result.get("not_live") or []]
        need(expect["not_live"] in ids, "not_live")
    if "absent_supplier" in expect:
        need(expect["absent_supplier"] not in blob, "absent_supplier")
    if "question" in expect:
        need(expect["question"] in (result.get("missing_question_ids") or []), "question")
    if "amounts" in expect:
        need(len(declaration.get("amounts") or []) == expect["amounts"], "amounts")
    if "amount_unparseable" in expect:
        need(declaration.get("amount_unparseable_count") == expect["amount_unparseable"], "amount_unparseable")
    if "dates" in expect:
        need(len(declaration.get("dates") or []) == expect["dates"], "dates")
    if "date_unparseable" in expect:
        need(declaration.get("date_unparseable_count") == expect["date_unparseable"], "date_unparseable")
    if "reason" in expect:
        need((result.get("human_route") or {}).get("reason_code") == expect["reason"], "reason")
    if "absent" in expect:
        need(expect["absent"] not in blob, "absent")
    if "special" in expect:
        need(expect["special"] in (result.get("minimisation") or {}).get("special_category", []), "special")
    if "family" in expect:
        need((result.get("minimisation") or {}).get("family_link") is expect["family"], "family")
    if "family_article_9" in expect:
        need((result.get("minimisation") or {}).get("family_is_article_9") is expect["family_article_9"], "family_article_9")
    if "carve_out" in expect:
        need(result.get("carve_out") is expect["carve_out"], "carve_out")
    if "marked_acceptable" in expect:
        need(result.get("marked_acceptable") is expect["marked_acceptable"], "marked_acceptable")
    if "person_cleared" in expect:
        need(result.get("person_cleared") is expect["person_cleared"], "person_cleared")
    if "criteria_flagged" in expect:
        need(result.get("criteria_flagged") is expect["criteria_flagged"], "criteria_flagged")
    if "criteria_applied" in expect:
        need(result.get("criteria_applied") is expect["criteria_applied"], "criteria_applied")
    if "followed" in expect:
        need(result.get("instructions_followed") is expect["followed"], "followed")
        need((result.get("prompt_injection") or {}).get("followed") is False, "injection_followed")
    if "staged" in expect:
        need(result.get("staged") is expect["staged"], "staged")
    if "directory_role" in expect:
        need(result.get("directory_role") == expect["directory_role"], "directory_role")
    if "role_ignored" in expect:
        need(result.get("self_declared_role_ignored") is expect["role_ignored"], "role_ignored")
    if "clearance_ignored" in expect:
        need(result.get("self_declared_clearance_ignored") is expect["clearance_ignored"], "clearance_ignored")
    if "sources_differ" in expect:
        need(result.get("caller_sources", {}).get("differs") is expect["sources_differ"], "sources_differ")
    if "applied" in expect:
        need((result.get("marking") or {}).get("applied") == expect["applied"], "applied")
    if "legal_hold" in expect:
        need(result.get("legal_hold") is expect["legal_hold"], "legal_hold")
    if "coerced" in expect:
        need(result.get("coerced") is expect["coerced"], "coerced")
    if "conflict_exists" in expect:
        need(result.get("conflict_exists") is expect["conflict_exists"], "conflict_exists")
    need(result.get("sent") is False, "sent")
    need(result.get("production_written") is False, "production_written")
    need(result.get("human_approval") is None, "human_approval")
    need(result.get("may_be_relied_on") is False, "may_be_relied_on")
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
