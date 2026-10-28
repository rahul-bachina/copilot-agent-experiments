#!/usr/bin/env python3
"""Deterministic smoke test of invoice exception triage.

The fixtures are synthetic. The checker is the Python under src/, which calls
Experiment 12, which calls Experiment 08. This is not a model score and it
does not call a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rules import BANK_FINGERPRINT, SUPPLIER_NAME, SUPPLIER_VAT, render_invoice  # noqa: E402
from src.triage import LABEL, NotSynthetic, triage  # noqa: E402

SMOKE_LABEL = (
    "DETERMINISTIC SMOKE TEST. The checker is the Python in src/, "
    "which calls Experiment 12 intake and, through it, Experiment 08. "
    "Not a measure of model accuracy. No model was called."
)


def load_dataset(path: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).parent / "synthetic_dataset.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _case(spec: dict) -> dict:
    content = render_invoice(spec.get("overrides"), extra=spec.get("extra", ""))
    if spec.get("media_type") == "application/pdf":
        content = "not read"
    case = {
        "synthetic": spec.get("synthetic", True),
        "case_id": spec["id"],
        "buyer_kind": spec.get("buyer_kind", "contracting_authority"),
        "contract_exceptions": spec.get("contract_exceptions", []),
        "match": spec.get("match", {"type": "three_way", "failed": True}),
        "received_on": "2026-10-01",
        "tolerances": {"price_pence": 0, "quantity": 0},
        "supplier_master": {
            "name": SUPPLIER_NAME,
            "vat_number": SUPPLIER_VAT,
            "bank_fingerprint": BANK_FINGERPRINT,
        },
        "purchase_order": spec["purchase_order"] if "purchase_order" in spec else {
            "number": "SYN-PO-44",
            "unit_price_pence": 500,
            "quantity": 10,
            "net_pence": 5000,
        },
        "goods_receipt": spec["goods_receipt"] if "goods_receipt" in spec else {
            "number": "SYN-GR-9",
            "quantity": spec.get("goods_receipt_quantity", 10),
        },
        "known_invoice_numbers": spec.get("known_invoice_numbers", []),
        "files": [
            {
                "file_id": "inv-1",
                "filename": "invoice.txt",
                "media_type": spec.get("media_type", "text/plain"),
                "document_date": "2026-10-01",
                "content": content if spec.get("synthetic", True) else "Supplier name: Secret Person\n",
            }
        ],
    }
    if spec.get("payment_due_on_invoice"):
        case["payment_due_on_invoice"] = spec["payment_due_on_invoice"]
    if spec.get("pay") is True:
        case["pay"] = True
    return case


def evaluate_case(spec: dict) -> dict:
    expect = spec["expect"]
    checks: list[dict] = []

    def add(field: str, passed: bool, detail: str) -> None:
        checks.append({"field": field, "passed": passed, "detail": detail})

    def finish(status: str) -> dict:
        if any(not item["passed"] for item in checks):
            status = "failed"
        return {"case_id": spec["id"], "name": spec.get("name", ""), "status": status, "checks": checks}

    as_of = date.fromisoformat(spec["as_of"])
    case = _case(spec)
    if expect.get("outcome") == "refused":
        try:
            triage(case, as_of=as_of)
        except NotSynthetic as exc:
            message = str(exc)
            add("refused", True, "NotSynthetic")
            for index, token in enumerate(expect.get("absent", []), start=1):
                add(f"absent {index}", token not in message, "not in the refusal")
            return finish("passed")
        except Exception as exc:  # noqa: BLE001
            return {"case_id": spec["id"], "name": spec.get("name", ""), "status": "error", "error": str(exc), "checks": checks}
        add("refused", False, "triage returned a draft")
        return finish("failed")

    try:
        result = triage(case, as_of=as_of)
    except Exception as exc:  # noqa: BLE001
        return {"case_id": spec["id"], "name": spec.get("name", ""), "status": "error", "error": f"{type(exc).__name__}: {exc}", "checks": []}

    serialised = json.dumps(result)
    add("label", result["label"] == LABEL, result["label"])
    add("actions_taken", result["actions_taken"] == [], "[]")
    add("model_called", result["model_called"] is False, "false")
    add("network_called", result["network_called"] is False, "false")
    add("followed", result["prompt_injection"]["followed"] is False, "false")
    add("intake", result["document_intake"]["experiment_id"] == "exp-12-document-intake", "exp-12")
    add("not_anonymised", result["document_intake"]["gateway"]["output_is_anonymised"] is False, "false")
    add("posted", result["flags"]["invoice_posted"] is False, "false")
    add("paid", result["flags"]["invoice_paid"] is False, "false")
    add("held", result["flags"]["invoice_held"] is False, "false")
    add("bank_changed", result["flags"]["supplier_bank_details_changed"] is False, "false")
    add("pcr", result["prompt_payment"]["pcr_2015_reg_113_in_force"] is False, "false")
    add("not_instructed", result["prompt_payment"]["payment_instructed"] is False, "false")
    add("input_tax", result["vat_invoice"]["decides_input_tax"] is False, "false")

    if "classes" in expect:
        add("classes", result["exceptions"] == expect["classes"], str(result["exceptions"]))
    if "absent_classes" in expect:
        for class_id in expect["absent_classes"]:
            add(f"absent {class_id}", class_id not in result["exceptions"], class_id)
    if "code" in expect:
        add("code", result["resolution"]["code"] == expect["code"], result["resolution"]["code"])
    if "last_day" in expect:
        add("last_day", result["prompt_payment"]["last_day_of_period"] == expect["last_day"], str(result["prompt_payment"]["last_day_of_period"]))
    if "payment_status" in expect:
        add("payment_status", result["prompt_payment"]["status"] == expect["payment_status"], result["prompt_payment"]["status"])
    if "start_reason" in expect:
        add("start_reason", result["prompt_payment"]["start_reason"] == expect["start_reason"], str(result["prompt_payment"]["start_reason"]))
    if "sources_stale" in expect:
        add("sources_stale", result["sources_stale"] is expect["sources_stale"], str(result["sources_stale"]))
    if "simplified" in expect:
        add("simplified", result["vat_invoice"]["simplified_invoice_may_apply"] is expect["simplified"], str(result["vat_invoice"]["simplified_invoice_may_apply"]))
    if "missing_field" in expect:
        add("missing_field", expect["missing_field"] in result["vat_invoice"]["missing_fields"], str(result["vat_invoice"]["missing_fields"]))
    if "currency_converted" in expect:
        add("currency_converted", result["vat_invoice"]["currency_converted"] is expect["currency_converted"], "false")
    if "duplicate_confirmed" in expect:
        add("duplicate_confirmed", result["duplicate_confirmed"] is expect["duplicate_confirmed"], str(result["duplicate_confirmed"]))
    if "injection" in expect:
        add("injection", result["prompt_injection"]["detected"] is expect["injection"], str(result["prompt_injection"]["detected"]))
    if "undisputed" in expect:
        add("undisputed", result["prompt_payment"]["invoice_undisputed_decided"] is expect["undisputed"], "false")
    if "read_status" in expect:
        actual = result["document_intake"]["files"][0]["read_status"]
        add("read_status", actual == expect["read_status"], actual)
    if "removed" in expect:
        add("removed", expect["removed"] in result["prohibited_keys_removed"], str(result["prohibited_keys_removed"]))
    if "pcr_in_force" in expect:
        add("pcr_in_force", result["prompt_payment"]["pcr_2015_reg_113_in_force"] is expect["pcr_in_force"], "false")
    if "payment_instructed" in expect:
        add("payment_instructed", result["prompt_payment"]["payment_instructed"] is expect["payment_instructed"], "false")
    for token in expect.get("absent_text", []):
        add(f"absent text {token}", token not in serialised, token)
    if expect.get("paid") is False:
        add("paid flag", result["flags"]["invoice_paid"] is False, "false")
    if expect.get("posted") is False:
        add("posted flag", result["flags"]["invoice_posted"] is False, "false")
    return finish("passed")


def evaluate(dataset: dict | None = None) -> dict:
    if dataset is None:
        dataset = load_dataset()
    cases = [evaluate_case(spec) for spec in dataset["cases"]]
    failed = [case for case in cases if case["status"] == "failed"]
    errors = [case for case in cases if case["status"] == "error"]
    passed = [case for case in cases if case["status"] == "passed"]
    total = len(cases)
    return {
        "evaluation_label": SMOKE_LABEL,
        "mode": "deterministic",
        "not_a_model_evaluation": True,
        "model_called": False,
        "summary": {
            "total_cases": total,
            "passed": len(passed),
            "failed": len(failed),
            "errors": len(errors),
            "agreement_rate": round(100 * len(passed) / total, 2) if total else 0,
        },
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic smoke test.")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    report = evaluate()
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    summary = report["summary"]
    print(
        f"{summary['passed']}/{summary['total_cases']} passed "
        f"({summary['agreement_rate']}%). Smoke test, not a model score.",
        file=sys.stderr,
    )
    return 1 if summary["failed"] or summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
