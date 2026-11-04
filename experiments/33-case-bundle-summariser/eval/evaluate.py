#!/usr/bin/env python3
"""Deterministic smoke test of the case-bundle citation checker.

The dataset is synthetic. The scorer is the Python under src/. This is not a
model score and it does not call Microsoft Foundry. Case totals count cases
once. Sentence verdicts stay inside each case and are not added to total_cases.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.summarise import SummaryForbidden, summarise  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The scorer is the Python in src/. "
    "Not a measure of model accuracy. No model was called. "
    "Not a Microsoft Foundry groundedness score. "
    "Not a case outcome."
)
DATASET = ROOT / "eval" / "synthetic_dataset.json"
LIBRARY = ROOT / "fixtures" / "library.json"


def load_dataset(path: Path | None = None) -> dict:
    return json.loads((path or DATASET).read_text(encoding="utf-8"))


def expand(case: dict, library: dict) -> tuple[dict, list | None]:
    spec = case["spec"]
    documents = []
    for ref in spec["documents"]:
        if isinstance(ref, str):
            documents.append(json.loads(json.dumps(library["documents"][ref])))
        else:
            row = json.loads(json.dumps(library["documents"][ref["id"]]))
            row.update(ref.get("set") or {})
            documents.append(row)
    bundle = {
        "bundle_id": spec["bundle_id"],
        "organisation": spec["organisation"],
        "matter_type": spec["matter_type"],
        "synthetic": spec.get("synthetic", True),
        "documents": documents,
    }
    if "expected_fact_keys" in spec:
        bundle["expected_fact_keys"] = spec["expected_fact_keys"]
    extra = spec.get("extra") or {}
    bundle.update(extra)
    proposed = spec.get("proposed_sentences")
    return bundle, proposed


def check(case: dict, draft: dict | None, error: str | None) -> list[str]:
    expect = case["expect"]
    problems: list[str] = []
    if expect.get("refused"):
        if error is None:
            problems.append("expected a refusal")
        elif expect.get("error_contains") and expect["error_contains"] not in (error or ""):
            problems.append(f"refusal text did not contain {expect['error_contains']!r}")
        return problems
    if error is not None:
        return [error]
    assert draft is not None
    if draft["label"] != "DRAFT FOR THE DECISION-MAKER. NOT A DECISION.":
        problems.append("label")
    if draft["catalogue_id"] != "UK09" or draft["autonomy"] != "A0":
        problems.append("identity")
    for key in (
        "case_outcome",
        "disclosure_decision",
        "credibility_finding",
    ):
        if draft[key] is not None:
            problems.append(key)
    if draft["outcome_recommended"] is not False or draft["summary_accepted_as_reading_aid"] is not False:
        problems.append("acceptance")
    if draft["summary_is_not_a_decision"] is not True or draft["actions_taken"] != []:
        problems.append("actions")
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
    combined = summary["sentence_count"] + summary["extractive_sentence_count"] + summary["gap_count"]
    if "total_cases" in summary or summary.get("total") == combined:
        problems.append("sentence counts were collapsed into a case total")
    if "sentence_count" in expect and summary["sentence_count"] != expect["sentence_count"]:
        problems.append(f"sentence_count {summary['sentence_count']} != {expect['sentence_count']}")
    if "failure_count" in expect and summary["failure_count"] != expect["failure_count"]:
        problems.append("failure_count")
    if "verdicts" in expect:
        for name, count in expect["verdicts"].items():
            if summary["verdicts"].get(name) != count:
                problems.append(f"{name} is {summary['verdicts'].get(name)} not {count}")
    if "checker_passed" in expect and draft["checker_passed"] is not expect["checker_passed"]:
        problems.append("checker_passed")
    if "do_not_rely" in expect and draft["do_not_rely"] is not expect["do_not_rely"]:
        problems.append("do_not_rely")
    if "gap_count" in expect and summary["gap_count"] != expect["gap_count"]:
        problems.append("gap_count")
    if "contradiction_count" in expect and summary["contradiction_count"] != expect["contradiction_count"]:
        problems.append("contradiction_count")
    if expect.get("other_failures") is not None:
        if draft["sentences"][0]["other_failures"] != expect["other_failures"]:
            problems.append(f"other_failures {draft['sentences'][0]['other_failures']}")
    if expect.get("signals_include"):
        found = {row["code"] for row in draft["prompt_injection"]["signals"]}
        missing = [code for code in expect["signals_include"] if code not in found]
        if missing:
            problems.append(f"missing signals {missing}")
    if expect.get("signals_empty") and draft["prompt_injection"]["signals"]:
        problems.append("signals were recorded on a refusal sentence")
    if expect.get("hidden_in") and not any(
        row["hidden_in"] == expect["hidden_in"] for row in draft["prompt_injection"]["signals"]
    ):
        problems.append("hidden_in")
    if expect.get("ignored_keys") and not draft["prompt_injection"]["ignored_keys"]:
        problems.append("expected ignored keys")
    if expect.get("token_absent") and expect["token_absent"] in json.dumps(draft):
        problems.append("token was echoed")
    if "pins_stale" in expect and draft["pins_stale"] is not expect["pins_stale"]:
        problems.append("pins_stale")
    if expect.get("sentence_absent"):
        blob = " ".join(row["text"] for row in draft["sentences"]).casefold()
        if expect["sentence_absent"].casefold() in blob:
            problems.append("held-out text was copied into the summary")
    if draft["differences"]["experiment_18"].find("Experiment 18") < 0:
        problems.append("difference from 18")
    if "contiguous" not in draft["differences"]["experiment_29"]:
        problems.append("difference from 29")
    return problems


def evaluate(dataset: dict | None = None) -> dict:
    data = dataset or load_dataset()
    library = json.loads(LIBRARY.read_text(encoding="utf-8"))
    rows = []
    for case in data["cases"]:
        error = None
        drafted = None
        try:
            bundle, proposed = expand(case, library)
            drafted = summarise(
                bundle,
                case.get("as_of", data["as_of"]),
                case.get("stale_after_days", data.get("stale_after_days", 90)),
                proposed_sentences=proposed,
            )
        except (SummaryForbidden, ValueError) as exc:
            error = str(exc)
        problems = check(case, drafted, error)
        rows.append(
            {
                "id": case["id"],
                "name": case["name"],
                "passed": not problems,
                "problems": problems,
                "sentence_count": None if drafted is None else drafted["summary"]["sentence_count"],
                "failure_count": None if drafted is None else drafted["summary"]["failure_count"],
                "gap_count": None if drafted is None else drafted["summary"]["gap_count"],
                "refused": error is not None,
            }
        )
    failed = [row for row in rows if not row["passed"]]
    passed = len(rows) - len(failed)
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_foundry_score": True,
        "not_a_case_outcome": True,
        "model_called": False,
        "network_called": False,
        "foundry_called": False,
        "sentences_added_to_total_cases": False,
        "as_of": data["as_of"],
        "summary": {
            "total_cases": len(rows),
            "passed": passed,
            "failed": len(failed),
            "agreement_rate": round(100 * passed / len(rows), 1) if rows else 0.0,
        },
        "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test for Experiment 33.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = evaluate(load_dataset(args.dataset))
    summary = result["summary"]
    if summary["passed"] + summary["failed"] != summary["total_cases"]:
        raise SystemExit("Smoke totals do not add up to the case count.")
    sentence_sum = sum(row["sentence_count"] or 0 for row in result["cases"])
    if sentence_sum == summary["total_cases"]:
        raise SystemExit("Sentence counts and case counts were collapsed.")
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
