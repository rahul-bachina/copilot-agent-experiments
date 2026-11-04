#!/usr/bin/env python3
"""Deterministic smoke test for the EHCP draft assembler.

This is not a model evaluation and it is not an EHCP. Quote counts are
recorded on each case. They are not added together. Two cases that use
the same bundle would double-count if a grand total were taken.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.assemble import evaluate  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _materialise(case: dict, dataset: dict, dataset_path: Path) -> tuple[dict, dict | None]:
    base_name = dataset["base_bundle"]
    base_path = (dataset_path.parent / base_name).resolve()
    bundle = copy.deepcopy(_load(base_path))
    if "set_field" in case:
        bundle.update(case["set_field"])
    if "set_report" in case:
        wanted = case["set_report"]["report_id"]
        for report in bundle["reports"]:
            if report["report_id"] == wanted:
                report.update({key: value for key, value in case["set_report"].items() if key != "report_id"})
    if "set_paragraph" in case:
        change = case["set_paragraph"]
        for report in bundle["reports"]:
            if report["report_id"] != change["report_id"]:
                continue
            for paragraph in report["paragraphs"]:
                if paragraph["paragraph_id"] != change["paragraph_id"]:
                    continue
                paragraph["text"] = change["text"]
                if change.get("clear_claims"):
                    paragraph["claims"] = []
    if "drop_advice_type" in case:
        bundle["reports"] = [
            report for report in bundle["reports"] if report["advice_type"] != case["drop_advice_type"]
        ]
    signoff = copy.deepcopy(case["signoff"]) if "signoff" in case else None
    return bundle, signoff


def _expect(expect: dict, draft: dict) -> list[str]:
    problems = []
    checks = {
        "refused": draft.get("refused"),
        "placed_quotes": draft.get("placed_quotes"),
        "exported": draft.get("exported"),
        "export_blocked": draft.get("export_blocked"),
        "needs_decided": draft.get("needs_decided"),
        "provision_decided": draft.get("provision_decided"),
        "placement_decided": draft.get("placement_decided"),
        "sent_to_parents": draft.get("sent_to_parents"),
        "final_plan_edited": draft.get("final_plan_edited"),
        "text_copied": draft.get("text_copied"),
        "do_not_rely": draft.get("do_not_rely"),
        "injection_detected": (draft.get("prompt_injection") or {}).get("detected"),
        "injection_followed": (draft.get("prompt_injection") or {}).get("followed"),
        "output_is_anonymised": draft.get("output_is_anonymised"),
        "days_since_request": (draft.get("timescale") or {}).get("days_since_request"),
        "twenty_week_marker_passed": (draft.get("timescale") or {}).get("twenty_week_marker_passed"),
        "breach_found": (draft.get("timescale") or {}).get("breach_found"),
        "exceptions_applied": (draft.get("timescale") or {}).get("exceptions_applied"),
    }
    for key, actual in checks.items():
        if key in expect and actual != expect[key]:
            problems.append(f"{key}: expected {expect[key]!r}, got {actual!r}")
    if "conflicts" in expect:
        actual = len(draft.get("conflicts") or [])
        if actual != expect["conflicts"]:
            problems.append(f"conflicts: expected {expect['conflicts']}, got {actual}")
    if expect.get("conflict_resolved") is False:
        if any(row.get("resolved") for row in draft.get("conflicts") or []):
            problems.append("a conflict was resolved")
        if any(row.get("chosen_value") is not None for row in draft.get("conflicts") or []):
            problems.append("a conflict has a chosen value")
    if "unsupported" in expect:
        actual = len(draft.get("unsupported_statements") or [])
        if actual != expect["unsupported"]:
            problems.append(f"unsupported: expected {expect['unsupported']}, got {actual}")
    if "section_i_lines" in expect and not draft.get("refused"):
        actual = len(draft["sections"]["I"]["lines"])
        if actual != expect["section_i_lines"]:
            problems.append(f"section I lines: expected {expect['section_i_lines']}, got {actual}")
    if "section_i_withheld" in expect and not draft.get("refused"):
        actual = len(draft["sections"]["I"]["lines_withheld"])
        if actual != expect["section_i_withheld"]:
            problems.append(f"section I withheld: {actual}")
    if "section_a_lines" in expect and not draft.get("refused"):
        actual = len(draft["sections"]["A"]["lines"])
        if actual != expect["section_a_lines"]:
            problems.append(f"section A lines: {actual}")
    if "section_c_lines" in expect and not draft.get("refused"):
        actual = len(draft["sections"]["C"]["lines"])
        if actual != expect["section_c_lines"]:
            problems.append(f"section C lines: {actual}")
    if "stale_report" in expect:
        rows = [row for row in draft.get("stale_reports") or [] if row["report_id"] == expect["stale_report"]]
        if not rows or rows[0]["problem"] != "stale":
            problems.append("stale report was not marked")
    if expect.get("quote_kept") and not draft.get("refused"):
        if not draft["sections"]["A"]["lines"]:
            problems.append("the stale quote was dropped")
    if "gap" in expect and not draft.get("refused"):
        ids = [row["id"] for row in draft["gaps"]]
        if expect["gap"] not in ids:
            problems.append(f"gap {expect['gap']} missing")
    if "identifier_findings_at_least" in expect:
        actual = draft["pii_gateway"]["finding_count"]
        if actual < expect["identifier_findings_at_least"]:
            problems.append(f"identifier findings {actual}")
    blob = json.dumps(draft)
    for needle in expect.get("absent") or []:
        if needle in blob:
            problems.append(f"output contains {needle!r}")
    return problems


def run(dataset_path: Path) -> dict:
    dataset = _load(dataset_path)
    cases = []
    for case in dataset["cases"]:
        bundle, signoff = _materialise(case, dataset, dataset_path)
        draft = evaluate(bundle, as_of=case.get("as_of", dataset["as_of_default"]), signoff=signoff)
        problems = _expect(case["expect"], draft)
        cases.append(
            {
                "id": case["id"],
                "passed": not problems,
                "problems": problems,
                "placed_quotes": draft.get("placed_quotes"),
                "exported": draft.get("exported"),
                "export_blocked": draft.get("export_blocked"),
                "needs_decided": draft.get("needs_decided"),
                "sent_to_parents": draft.get("sent_to_parents"),
                "refused": draft.get("refused"),
                "do_not_rely": draft.get("do_not_rely"),
                "model_called": draft.get("model_called"),
                "network_called": draft.get("network_called"),
            }
        )
    failed = [case for case in cases if not case["passed"]]
    total = len(cases)
    passed = total - len(failed)
    return {
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "not_a_plan": True,
        "evaluation_label": "DETERMINISTIC SMOKE TEST",
        "summary": {
            "total_cases": total,
            "passed": passed,
            "failed": len(failed),
            "errors": 0,
            "agreement_rate": round((passed / total) * 100, 1) if total else 0.0,
            "quotes_are_not_summed": True,
        },
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EHCP assembler smoke test.")
    parser.add_argument("--dataset", default=str(Path(__file__).with_name("synthetic_dataset.json")))
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    report = run(Path(args.dataset))
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    print(
        f"Smoke test agreement: {report['summary']['agreement_rate']}% "
        f"({report['summary']['passed']}/{report['summary']['total_cases']})",
        file=sys.stderr,
    )
    if report["summary"]["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
