#!/usr/bin/env python3
"""Deterministic smoke test of the contact-centre case summary.

The dataset is synthetic. The scorer is the Python under src/. This is not a
model score and it does not call Microsoft Foundry. Case totals count cases
once. Sentence verdicts stay on each case and are not added to total_cases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import CaseSummaryForbidden, summarise  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called. "
    "Not a Microsoft Foundry score. "
    "Not a customer contact and not a record change."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def check(case: dict, draft: dict | None, error: str | None) -> list[str]:
    expect = case["expect"]
    problems: list[str] = []
    if error is not None:
        problems.append(error)
        return problems
    assert draft is not None
    if expect.get("refused"):
        if draft.get("refused") is not True:
            problems.append("expected a refusal")
        elif draft.get("reason") != expect.get("reason"):
            problems.append(f"reason {draft.get('reason')}")
        if expect.get("token_absent") and expect["token_absent"] in json.dumps(draft):
            problems.append("token was echoed")
        return problems
    if draft.get("refused"):
        return [f"unexpected refusal {draft.get('reason')}"]
    if not str(draft["label"]).startswith("DRAFT FOR THE SERVICE REPRESENTATIVE"):
        problems.append("label")
    if draft["catalogue_id"] != "C002" or draft["autonomy"] != "A0":
        problems.append("identity")
    if draft["case_outcome"] is not None or draft["customer_contacted"] or draft["record_changed"]:
        problems.append("action flag")
    if draft["complaint_closed"] or draft["redress_offered"] or draft["customer_labelled_vulnerable"]:
        problems.append("outcome flag")
    if draft["accuracy_checked"] or draft["human_approval"] is not None or draft["actions_taken"] != []:
        problems.append("approval")
    if draft["model_called"] or draft["network_called"] or draft["foundry_called"] or draft["a3_recommended"]:
        problems.append("boundary flag")
    if draft["prompt_injection"]["followed"] is not False:
        problems.append("injection followed")
    summary = draft["summary"]
    if summary["verdict_total"] != summary["sentence_count"]:
        problems.append("verdict total does not match the sentence count")
    if sum(summary["verdicts"].values()) != summary["sentence_count"]:
        problems.append("verdict buckets do not sum to the sentence count")
    if summary["failure_count"] != summary["sentence_count"] - summary["verdicts"]["supported"]:
        problems.append("failure_count double-counts")
    if "total" in summary or "total_cases" in summary:
        problems.append("sentence counts were collapsed into a case total")
    combined = (
        summary["sentence_count"]
        + summary["extractive_sentence_count"]
        + summary["gap_count"]
        + summary["withheld_line_count"]
    )
    if summary.get("total") == combined:
        problems.append("counts were added together")
    for key in (
        "sentence_count",
        "extractive_sentence_count",
        "failure_count",
        "gap_count",
        "contradiction_count",
        "withheld_line_count",
    ):
        if key in expect and summary[key] != expect[key]:
            problems.append(f"{key} {summary[key]} != {expect[key]}")
    if "verdict" in expect and draft["sentences"][0]["verdict"] != expect["verdict"]:
        problems.append(f"verdict {draft['sentences'][0]['verdict']}")
    if expect.get("other_failures") is not None:
        if draft["sentences"][0]["other_failures"] != expect["other_failures"]:
            problems.append(f"other_failures {draft['sentences'][0]['other_failures']}")
    if "checker_passed" in expect and draft["checker_passed"] is not expect["checker_passed"]:
        problems.append("checker_passed")
    if "do_not_rely" in expect and draft["do_not_rely"] is not expect["do_not_rely"]:
        problems.append(f"do_not_rely {draft['do_not_rely_reasons']}")
    if expect.get("reason_includes") and expect["reason_includes"] not in draft["do_not_rely_reasons"]:
        problems.append(f"missing reason {expect['reason_includes']}")
    if expect.get("not_used_reason") and not any(
        row["reason"] == expect["not_used_reason"] for row in draft["not_used"]
    ):
        problems.append("not_used reason")
    if expect.get("signals_include"):
        found = {row["code"] for row in draft["prompt_injection"]["signals"]}
        missing = [code for code in expect["signals_include"] if code not in found]
        if missing:
            problems.append(f"missing signals {missing}")
    if expect.get("hidden_in") and not any(
        row["hidden_in"] == expect["hidden_in"] for row in draft["prompt_injection"]["signals"]
    ):
        problems.append("hidden_in")
    if expect.get("signals_empty") and draft["prompt_injection"]["signals"]:
        problems.append("signals were recorded")
    if expect.get("ignored_key") and expect["ignored_key"] not in draft["prompt_injection"]["ignored_keys"]:
        problems.append("expected ignored key")
    if expect.get("token_absent") and expect["token_absent"] in json.dumps(draft):
        problems.append("token was echoed")
    if "pins_stale" in expect and draft["pins_stale"] is not expect["pins_stale"]:
        problems.append("pins_stale")
    if expect.get("sentence_text") and expect["sentence_text"] not in [row["text"] for row in draft["sentences"]]:
        problems.append("sentence text")
    if expect.get("fact_key_absent") and any(row["fact_key"] == expect["fact_key_absent"] for row in draft["sentences"]):
        problems.append("fact key was quoted")
    if expect.get("sector_note_contains") and expect["sector_note_contains"] not in draft["sector_note"]:
        problems.append("sector note")
    if expect.get("line_end") and draft["sentences"][0]["citation"]["line_end"] != expect["line_end"]:
        problems.append("line_end")
    if expect.get("entity_type") and expect["entity_type"] not in draft["pii_gateway"]["entity_types"]:
        problems.append("entity type")
    if draft["pii_gateway"]["output_is_anonymised"] or draft["pii_gateway"]["redacted_text_copied"]:
        problems.append("redaction boundary")
    if draft["regulatory"]["ico_ai_accuracy_page_opened"] or draft["regulatory"]["ico_ai_accuracy_quoted"]:
        problems.append("ICO page was treated as opened")
    if draft["regulatory"]["disp_clock_calculated"] or draft["regulatory"]["significant_decision_taken"]:
        problems.append("regulatory flag")
    if "Experiment 33" not in draft["differences"]["experiment_33"] or "contiguous" not in draft["differences"]["experiment_33"]:
        problems.append("difference from 33")
    if "propose()" not in draft["differences"]["experiment_08"]:
        problems.append("difference from 08")
    return problems


def _status(problems: list[str], error: str | None) -> str:
    if error is not None:
        return "error"
    if problems:
        return "failed"
    return "passed"


def evaluate(dataset: dict | None = None) -> dict:
    data = dataset or load_dataset()
    rows = []
    seen: set[str] = set()
    for case in data["cases"]:
        if case["id"] in seen:
            raise ValueError(f"Duplicate case id {case['id']}")
        seen.add(case["id"])
        error = None
        drafted = None
        try:
            drafted = summarise(
                case["case"],
                case.get("as_of", data["as_of"]),
                case.get("stale_after_days", 90),
                proposed_sentences=case.get("proposed_sentences"),
            )
        except (CaseSummaryForbidden, ValueError) as exc:
            error = str(exc)
        problems = check(case, drafted, error)
        status = _status(problems, error)
        summary = None if drafted is None else drafted["summary"]
        rows.append(
            {
                "case_id": case["id"],
                "status": status,
                "passed": status == "passed",
                "problems": problems,
                "sentence_count": None if summary is None else summary["sentence_count"],
                "failure_count": None if summary is None else summary["failure_count"],
                "gap_count": None if summary is None else summary["gap_count"],
            }
        )
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    errors = sum(1 for row in rows if row["status"] == "error")
    total = len(rows)
    if passed + failed + errors != total:
        raise RuntimeError("Smoke totals double-count or do not add up.")
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_foundry_score": True,
        "not_a_customer_contact": True,
        "not_a_record_change": True,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "sentences_added_to_total_cases": False,
        "as_of": data["as_of"],
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "agreement_rate": round(100 * passed / total, 1) if total else 0.0,
        },
        "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for Experiment 41.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = evaluate(load_dataset(args.dataset))
    summary = result["summary"]
    if summary["passed"] + summary["failed"] + summary["errors"] != summary["total_cases"]:
        raise SystemExit("Smoke totals do not add up to the case count.")
    ids = [row["case_id"] for row in result["cases"]]
    if len(ids) != len(set(ids)) or len(ids) != summary["total_cases"]:
        raise SystemExit("Case ids are not one row each.")
    sentence_sum = sum(row["sentence_count"] or 0 for row in result["cases"])
    if sentence_sum == summary["total_cases"] or "sentence_sum" in summary:
        raise SystemExit("Sentence counts and case counts were collapsed.")
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    print(
        f"Smoke test cases: {summary['total_cases']} passed: {summary['passed']} "
        f"failed: {summary['failed']} errors: {summary['errors']} "
        f"agreement: {summary['agreement_rate']}",
        file=sys.stderr,
    )
    return 0 if summary["failed"] == 0 and summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
