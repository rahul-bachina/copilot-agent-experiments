#!/usr/bin/env python3
"""Draft a resolution for one synthetic invoice that failed a match.

``triage`` calls Experiment 12 ``intake``. That intake calls Experiment 08.
This module does not re-implement either, and it does not add an accounts
payable purpose to Experiment 12. The intake purpose on the call is
``general_records``, which is a preview, not a confirmation.

The return value is a draft. It does not post, approve, hold, or pay the
invoice, and it does not change supplier bank details. A bank-detail flag
is a route to a separate verifier. ``record_ap_reviewer_decision`` and
``record_bank_route`` check a role. They still do not post, pay, or change
a bank record. The forbid functions always raise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ap_injection import bank_phrases_in, merge_scans, scan_text, visible_body
    from rules import (
        ACT_IN_FORCE_ON,
        AP_REVIEWER_ROLE,
        ASK_CORRECTED,
        ASK_PO,
        BANK_VERIFIER_ROLE,
        BUYER_KINDS,
        CATALOGUE_ID,
        CLASS_ORDER,
        CONTRACT_EXCEPTIONS,
        DECISIONS,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        FULL_INVOICE_FIELDS,
        INSUFFICIENT,
        INTAKE_EXPERIMENT_ID,
        INTAKE_PURPOSE,
        LABELS,
        MATCH_TYPES,
        PCR_REVOKED_ON,
        QUOTES,
        RECOMMENDATION_FOR,
        REFER_DUPLICATE,
        REFER_VARIANCE,
        RETURN_MATCHING,
        ROUTE_BANK,
        SECTION_68_MINIMUM,
        SIMPLIFIED_FIELDS,
        SIMPLIFIED_GROSS_CEILING_PENCE,
        SOURCES,
        SOURCES_PINNED_ON,
        WITHIN_TOLERANCE,
    )
else:
    from .ap_injection import bank_phrases_in, merge_scans, scan_text, visible_body
    from .rules import (
        ACT_IN_FORCE_ON,
        AP_REVIEWER_ROLE,
        ASK_CORRECTED,
        ASK_PO,
        BANK_VERIFIER_ROLE,
        BUYER_KINDS,
        CATALOGUE_ID,
        CLASS_ORDER,
        CONTRACT_EXCEPTIONS,
        DECISIONS,
        DEFAULT_STALE_AFTER_DAYS,
        EXPERIMENT_ID,
        FULL_INVOICE_FIELDS,
        INSUFFICIENT,
        INTAKE_EXPERIMENT_ID,
        INTAKE_PURPOSE,
        LABELS,
        MATCH_TYPES,
        PCR_REVOKED_ON,
        QUOTES,
        RECOMMENDATION_FOR,
        REFER_DUPLICATE,
        REFER_VARIANCE,
        RETURN_MATCHING,
        ROUTE_BANK,
        SECTION_68_MINIMUM,
        SIMPLIFIED_FIELDS,
        SIMPLIFIED_GROSS_CEILING_PENCE,
        SOURCES,
        SOURCES_PINNED_ON,
        WITHIN_TOLERANCE,
    )

LABEL = "DRAFT FOR AP REVIEW"
NOT_CURRENT = frozenset({"stale", "missing", "future", "invalid"})
NAME_TOKEN = re.compile(r"[A-Za-z0-9 '&.,-]{1,80}\Z")
REF_TOKEN = re.compile(r"[A-Za-z0-9-]{1,40}\Z")
FINGERPRINT_TOKEN = re.compile(r"[A-Za-z0-9_-]{1,40}\Z")
VAT_SHAPE = re.compile(r"GB[0-9]{9}\Z")
CURRENCY_TOKEN = re.compile(r"[A-Z]{3}\Z")
MONEY_TOKEN = re.compile(r"£?\d{1,9}(?:\.\d{2})?\Z")
QTY_TOKEN = re.compile(r"\d{1,7}\Z")
RATE_TOKEN = re.compile(r"\d{1,2}%?\Z")
DISCOUNT_TOKEN = re.compile(r"[A-Za-z0-9 .%]{1,20}\Z")
SAFE_TEXT = re.compile(r"[A-Za-z0-9 '&.,-]{1,80}\Z")

PROHIBITED_KEYS = frozenset(
    {
        "posted",
        "approved",
        "held",
        "paid",
        "pay",
        "post",
        "hold",
        "approve",
        "send",
        "bank_details_changed",
        "bank_details_verified",
        "resolution_approved",
        "invoice_valid",
        "undisputed",
        "invoice_posted",
        "invoice_paid",
        "invoice_held",
        "invoice_approved",
    }
)

LIMITATIONS = (
    "This draft does not post, approve, hold, or pay an invoice.",
    "A recommended resolution is a draft. Approving it, outside this agent, still does not post or pay.",
    "Supplier bank details are never changed here. A bank-detail flag is only a route to a separate verifier.",
    "A fingerprint is a caller-supplied token. This starter does not read a sort code or an account number into the draft.",
    "Experiment 12 inventories the file. Its purpose list has no accounts-payable purpose. The call uses general_records as a preview.",
    "UK identifier spans come from Experiment 08, through Experiment 12. The text is not anonymised.",
    "Labelled lines only. A price written in a sentence, or after a form feed, is not extracted.",
    "One invoice line. A second line is not matched.",
    "The £250 figure is the simplified-invoice ceiling in VAT Notice 700/21 sections 4.4 and 4.5. It is not applied to a currency other than GBP, and no exchange rate is used.",
    "The VAT number shape stored here is GB and nine digits. It is not an HMRC lookup and not a checksum.",
    "Public Contracts Regulations 2015 regulation 113 is revoked. It is not applied. Saving provisions in SI 2024/716 regulations 5 and 6 were not encoded.",
    "The 30-day figure is arithmetic on dates the caller typed. It is not a finding that a sum is due, or that an invoice is valid or undisputed.",
    "The 90-day window is a freshness flag. It is not the six-year VAT record period in Notice 700/21 section 2.4.",
    "No model was called.",
)


class TriageForbidden(RuntimeError):
    """The triage has no post, approve, hold, pay, or bank-change path."""


class NotSynthetic(ValueError):
    """The case was not marked synthetic. The message does not include the body."""


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise TriageForbidden(
            "Experiment 12 is not beside this experiment. Triage will not invent an inventory."
        )
    inserted = str(intake_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import intake as intake_module

    if intake_module.EXPERIMENT_ID != INTAKE_EXPERIMENT_ID:
        raise TriageForbidden("the intake module is not Experiment 12")
    return intake_module


def _strip_prohibited(mapping: dict, prefix: str) -> list[str]:
    found = []
    for key in list(mapping):
        if key in PROHIBITED_KEYS:
            found.append(f"{prefix}{key}" if prefix else key)
            del mapping[key]
    return found


def _parse_iso(raw) -> date | None:
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _pence(raw: str) -> int | None:
    if not isinstance(raw, str):
        return None
    text = raw.strip().replace(",", "")
    if not MONEY_TOKEN.fullmatch(text):
        return None
    text = text[1:] if text.startswith("£") else text
    if "." in text:
        pounds, pence = text.split(".")
        return int(pounds) * 100 + int(pence)
    return int(text) * 100


def _quantity(raw: str) -> int | None:
    if isinstance(raw, str) and QTY_TOKEN.fullmatch(raw.strip()):
        return int(raw.strip())
    return None


def _rate(raw: str) -> int | None:
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not RATE_TOKEN.fullmatch(text):
        return None
    return int(text[:-1] if text.endswith("%") else text)


def _safe_name(raw: str) -> str | None:
    if isinstance(raw, str) and NAME_TOKEN.fullmatch(raw.strip()) and not bank_phrases_in(raw):
        if scan_text(raw, file_id="field").get("detected"):
            return None
        return " ".join(raw.split())
    return None


def _safe_ref(raw: str) -> str | None:
    if isinstance(raw, str) and REF_TOKEN.fullmatch(raw.strip()):
        return raw.strip()
    return None


def _vat_shape(raw: str) -> str | None:
    if not isinstance(raw, str):
        return None
    compact = raw.replace(" ", "").upper()
    if VAT_SHAPE.fullmatch(compact):
        return compact
    return None


def _norm_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _will_read(raw: dict, intake_module) -> bool:
    media = raw.get("media_type", "")
    if not isinstance(media, str):
        return False
    content = raw.get("content", "")
    if not isinstance(content, str) or content == "":
        return False
    return media.strip().lower() in intake_module.ALLOWED_MEDIA and len(content) <= intake_module.MAX_CHARS


def _labelled(visible: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in visible.splitlines():
        if ":" not in line:
            continue
        label, _, value = line.strip().partition(":")
        key = LABELS.get(label.strip().casefold())
        if key and key not in found:
            found[key] = value.strip()
    return found


def _fingerprints(text: str) -> tuple[list[str], bool]:
    """Safe fingerprint tokens, and whether an unsafe value was seen."""

    safe: list[str] = []
    unsafe = False
    stripped = text
    for line in stripped.splitlines():
        if ":" not in line:
            continue
        label, _, value = line.strip().partition(":")
        if label.strip().casefold() != "bank fingerprint":
            continue
        token = value.strip()
        if FINGERPRINT_TOKEN.fullmatch(token):
            if token not in safe:
                safe.append(token)
        elif token:
            unsafe = True
    return safe, unsafe


def _extract(files: list[dict], intake_module) -> dict:
    fields: dict[str, dict] = {}
    fingerprints: list[str] = []
    fingerprint_unsafe = False
    bank_hits: list[str] = []
    receipt_ignored = False
    for raw in files:
        if not isinstance(raw, dict) or not _will_read(raw, intake_module):
            continue
        content = raw.get("content", "")
        file_id = raw.get("file_id", "?")
        visible = visible_body(content)
        if re.search(r"(?im)^received on\s*:", visible):
            receipt_ignored = True
        for key, value in _labelled(visible).items():
            if key not in fields:
                fields[key] = {"value": value, "file_id": file_id}
        found, unsafe = _fingerprints(content.translate({ord(char): None for char in "\u200b\u200c\u200d\ufeff\u2060"}))
        fingerprint_unsafe = fingerprint_unsafe or unsafe
        for token in found:
            if token not in fingerprints:
                fingerprints.append(token)
        for phrase in bank_phrases_in(content):
            if phrase not in bank_hits:
                bank_hits.append(phrase)

    def raw_of(key: str) -> str | None:
        item = fields.get(key)
        return None if item is None else item["value"]

    def file_of(key: str) -> str | None:
        item = fields.get(key)
        return None if item is None else item["file_id"]

    supplier_name = _safe_name(raw_of("supplier_name") or "")
    customer_name = _safe_name(raw_of("customer_name") or "")
    description = raw_of("description")
    description_present = bool(description)
    description_stored = bool(description) and SAFE_TEXT.fullmatch(description) and _safe_name(description)
    invoice_date = _parse_iso(raw_of("invoice_date") or "")
    time_of_supply = _parse_iso(raw_of("time_of_supply") or "")
    date_of_issue = _parse_iso(raw_of("date_of_issue") or "")
    currency_raw = (raw_of("currency") or "").strip().upper()
    currency = currency_raw if CURRENCY_TOKEN.fullmatch(currency_raw) else None
    discount_raw = raw_of("cash_discount")
    address_present = bool(raw_of("supplier_address"))
    customer_address_present = bool(raw_of("customer_address"))
    vat = _vat_shape(raw_of("supplier_vat") or "")
    vat_present = bool(raw_of("supplier_vat"))

    return {
        "invoice_number": _safe_ref(raw_of("invoice_number") or ""),
        "invoice_date": invoice_date.isoformat() if invoice_date else None,
        "time_of_supply": time_of_supply.isoformat() if time_of_supply else None,
        "date_of_issue": date_of_issue.isoformat() if date_of_issue else None,
        "supplier_name": supplier_name,
        "supplier_name_present": bool(raw_of("supplier_name")),
        "supplier_address_present": address_present,
        "supplier_vat": vat,
        "supplier_vat_present": vat_present,
        "supplier_vat_status": (
            "stored_shape_only" if vat else ("present_not_stored" if vat_present else "missing")
        ),
        "customer_name": customer_name,
        "customer_name_present": bool(raw_of("customer_name")),
        "customer_address_present": customer_address_present,
        "po_number": _safe_ref(raw_of("po_number") or ""),
        "po_number_present": bool(raw_of("po_number")),
        "description_present": description_present,
        "description": description if description_stored else None,
        "quantity": _quantity(raw_of("quantity") or ""),
        "unit_price_pence": _pence(raw_of("unit_price") or ""),
        "net_pence": _pence(raw_of("net") or ""),
        "vat_rate_percent": _rate(raw_of("vat_rate") or ""),
        "vat_amount_pence": _pence(raw_of("vat_amount") or ""),
        "gross_pence": _pence(raw_of("gross") or ""),
        "currency": currency,
        "currency_labelled": bool(raw_of("currency")),
        "cash_discount_stated": bool(discount_raw) and bool(DISCOUNT_TOKEN.fullmatch(discount_raw)),
        "field_file_ids": {key: file_of(key) for key in fields},
        "bank_fingerprints": fingerprints,
        "bank_fingerprint_unsafe": fingerprint_unsafe,
        "bank_phrases": bank_hits,
        "receipt_date_in_invoice_ignored": receipt_ignored,
        "values_of_bank_accounts_recorded": False,
    }


def _present_map(extracted: dict) -> dict[str, bool]:
    dated = bool(extracted["time_of_supply"] or extracted["invoice_date"] or extracted["date_of_issue"])
    return {
        "invoice_number": extracted["invoice_number"] is not None,
        "supply_or_issue_date": dated,
        "supplier_name": extracted["supplier_name"] is not None,
        "supplier_address": extracted["supplier_address_present"] is True,
        "supplier_vat": extracted["supplier_vat"] is not None,
        "customer_name": extracted["customer_name"] is not None,
        "customer_address": extracted["customer_address_present"] is True,
        "description": extracted["description_present"] is True and extracted["description"] is not None,
        "quantity": extracted["quantity"] is not None,
        "unit_price": extracted["unit_price_pence"] is not None,
        "net": extracted["net_pence"] is not None,
        "vat_rate": extracted["vat_rate_percent"] is not None,
        "vat_amount": extracted["vat_amount_pence"] is not None,
        "gross": extracted["gross_pence"] is not None,
        "sum_requested": extracted["gross_pence"] is not None or extracted["net_pence"] is not None,
    }


def _vat_section(extracted: dict, master: dict | None) -> dict:
    present = _present_map(extracted)
    gross = extracted["gross_pence"]
    currency = extracted["currency"]
    simplified_possible = (
        currency == "GBP" and gross is not None and gross <= SIMPLIFIED_GROSS_CEILING_PENCE
    )
    full_required = not simplified_possible
    required = FULL_INVOICE_FIELDS if full_required else SIMPLIFIED_FIELDS
    missing = [field for field in required if not present[field]]
    reasons = []
    if missing:
        reasons.append("required_fields_missing")
    name_match = None
    vat_match = None
    if master:
        master_name = master.get("name") if isinstance(master.get("name"), str) else ""
        if extracted["supplier_name"] and _safe_name(master_name):
            name_match = _norm_name(extracted["supplier_name"]) == _norm_name(master_name)
            if name_match is False:
                reasons.append("supplier_name_differs_from_master")
        elif extracted["supplier_name_present"] and not extracted["supplier_name"]:
            reasons.append("supplier_name_not_confirmed")
        master_vat = _vat_shape(master.get("vat_number") or "")
        if extracted["supplier_vat"] and master_vat:
            vat_match = extracted["supplier_vat"] == master_vat
            if vat_match is False:
                reasons.append("supplier_vat_differs_from_master")
        elif extracted["supplier_vat_status"] == "present_not_stored":
            reasons.append("supplier_vat_not_confirmed")
    elif extracted["supplier_vat_status"] == "present_not_stored":
        reasons.append("supplier_vat_not_confirmed")

    arithmetic = "not_checked"
    net = extracted["net_pence"]
    rate = extracted["vat_rate_percent"]
    vat_amount = extracted["vat_amount_pence"]
    if net is not None and rate is not None and vat_amount is not None:
        nearest = (net * rate + 50) // 100
        if abs(vat_amount - nearest) > 1:
            arithmetic = "differs_by_more_than_one_penny"
            reasons.append("vat_amount_arithmetic")
        else:
            arithmetic = "within_one_penny"

    timing = "not_checked"
    supply = _parse_iso(extracted["time_of_supply"] or "")
    issued = _parse_iso(extracted["date_of_issue"] or "")
    if supply and issued:
        timing = "later_than_30_days" if (issued - supply).days > 30 else "within_30_days"

    return {
        "notice": "VAT Notice 700/21",
        "sections": ["2.4", "3.1", "3.2", "4.1", "4.4", "4.5"],
        "decides_input_tax": False,
        "simplified_invoice_may_apply": simplified_possible,
        "simplified_ceiling_pence": SIMPLIFIED_GROSS_CEILING_PENCE,
        "ceiling_applied": currency == "GBP" and gross is not None,
        "currency_converted": False,
        "full_invoice_list_applied": full_required,
        "missing_fields": missing,
        "supplier_name_matches_master": name_match,
        "supplier_vat_matches_master": vat_match,
        "vat_arithmetic": arithmetic,
        "issue_against_section_3_1": timing,
        "cash_discount_stated": extracted["cash_discount_stated"],
        "cash_discount_absence_is_not_a_gap": True,
        "retention_quote": QUOTES["vat_700_21_2_4"],
        "destruction_date_calculated": False,
        "reasons": reasons,
        "quotes": {
            "section_4_1": QUOTES["vat_700_21_4_1"],
            "section_4_5": QUOTES["vat_700_21_4_5"],
            "section_3_1": QUOTES["vat_700_21_3_1_issue"],
            "section_3_2": QUOTES["vat_700_21_3_2"],
        },
    }


def _non_negative_int(value, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _master(value) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("supplier_master must be an object or null")
    return value


def _po(value) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("purchase_order must be an object or null")
    number = value.get("number")
    if not isinstance(number, str) or not REF_TOKEN.fullmatch(number):
        raise ValueError("purchase order number must be a short reference")
    unit = value.get("unit_price_pence")
    quantity = value.get("quantity")
    if type(unit) is not int or unit < 0:
        raise ValueError("purchase order unit price must be an integer number of pence")
    if type(quantity) is not int or quantity < 0:
        raise ValueError("purchase order quantity must be a non-negative integer")
    net = value.get("net_pence")
    if net is not None and (type(net) is not int or net < 0):
        raise ValueError("purchase order net must be an integer number of pence")
    return {"number": number, "unit_price_pence": unit, "quantity": quantity, "net_pence": net}


def _gr(value) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("goods_receipt must be an object or null")
    number = value.get("number", "")
    if not isinstance(number, str) or not REF_TOKEN.fullmatch(number):
        raise ValueError("goods receipt number must be a short reference")
    quantity = value.get("quantity")
    if type(quantity) is not int or quantity < 0:
        raise ValueError("goods receipt quantity must be a non-negative integer")
    return {"number": number, "quantity": quantity}


def _classify(extracted: dict, controls: dict, intake_files: list[dict], vat: dict) -> dict:
    classes: list[str] = []
    evidence: list[dict] = []
    price_compared = False
    quantity_compared = False
    any_read = any(file.get("read_status") == "read" for file in intake_files)

    def add(class_id: str, detail: str) -> None:
        if class_id not in classes:
            classes.append(class_id)
        evidence.append({"id": f"E{len(evidence) + 1}", "class": class_id, "detail": detail})

    fingerprints = extracted["bank_fingerprints"]
    master_fp = controls["master_fingerprint"]
    bank_flag = False
    if any_read:
        bank_flag = bool(extracted["bank_phrases"]) or extracted["bank_fingerprint_unsafe"]
    if master_fp and any(token != master_fp for token in fingerprints):
        bank_flag = True
    if len(set(fingerprints)) > 1:
        bank_flag = True
    if fingerprints and not master_fp:
        bank_flag = True
    if bank_flag:
        detail = "A bank-detail phrase or fingerprint does not confirm the supplier master."
        if extracted["bank_phrases"]:
            detail = "The invoice text contains a bank-detail change phrase. The account value is not recorded."
        add("bank_detail_change", detail)

    invoice_number = extracted["invoice_number"]
    if any_read and invoice_number and invoice_number in controls["known_invoice_numbers"]:
        add("duplicate_suspicion", "The invoice number is on the caller-supplied list of earlier numbers.")
    if any_read and controls["stated_duplicate_of"]:
        add("duplicate_suspicion", "The case states a duplicate reference. That statement is not confirmed.")
    for file in intake_files:
        if file.get("duplicate_of"):
            add(
                "duplicate_suspicion",
                f"File {file['file_id']} repeats the hash of {file['duplicate_of']}.",
            )
            break

    po = controls["purchase_order"]
    po_number = extracted["po_number"]
    po_aligned = bool(any_read and po and po_number and po["number"] == po_number)
    if any_read and (po is None or not po_number or (po and po_number and po["number"] != po_number)):
        if po is None:
            why = "No purchase order was supplied with the case."
        elif not po_number:
            why = "The invoice has no purchase-order number on a labelled line."
        else:
            why = "The purchase-order number on the invoice does not match the purchase order supplied."
        add("missing_po", why)
    if any_read and vat["reasons"]:
        add(
            "vat_supplier_mismatch",
            "VAT notice fields or the supplier master do not line up. Input tax is not decided. "
            + ", ".join(vat["reasons"]),
        )

    currency = extracted["currency"]
    # A stated non-GBP currency is not converted, and the prices are not compared.
    compare_money = currency in {None, "GBP"}
    if po_aligned and compare_money:
        tolerance = controls["price_pence"]
        unit = extracted["unit_price_pence"]
        if unit is not None:
            price_compared = True
            gap = abs(unit - po["unit_price_pence"])
            if gap > tolerance:
                add(
                    "price_variance",
                    f"Unit price {unit} pence against purchase order {po['unit_price_pence']} pence. "
                    f"Difference {gap} pence. Tolerance {tolerance} pence.",
                )
        net = extracted["net_pence"]
        if net is not None and po["net_pence"] is not None:
            price_compared = True
            gap = abs(net - po["net_pence"])
            if gap > tolerance:
                add(
                    "price_variance",
                    f"Net {net} pence against purchase order {po['net_pence']} pence. "
                    f"Difference {gap} pence. Tolerance {tolerance} pence.",
                )
    elif po_aligned and not compare_money:
        add_note = (
            f"Currency {currency} was labelled. Prices were not compared and were not converted."
        )
        evidence.append({"id": f"E{len(evidence) + 1}", "class": None, "detail": add_note})

    match_type = controls["match_type"]
    if not any_read:
        match_type = "unread"
    if match_type == "three_way":
        gr = controls["goods_receipt"]
        if gr is None:
            add("quantity_variance", "A 3-way match needs a goods receipt. None was supplied.")
        elif extracted["quantity"] is not None:
            quantity_compared = True
            gap = abs(extracted["quantity"] - gr["quantity"])
            if gap > controls["quantity_tolerance"]:
                add(
                    "quantity_variance",
                    f"Quantity {extracted['quantity']} against goods receipt {gr['quantity']}. "
                    f"Difference {gap}. Tolerance {controls['quantity_tolerance']}.",
                )
    elif match_type == "two_way" and po_aligned and extracted["quantity"] is not None:
        quantity_compared = True
        gap = abs(extracted["quantity"] - po["quantity"])
        if gap > controls["quantity_tolerance"]:
            add(
                "quantity_variance",
                f"Quantity {extracted['quantity']} against purchase order {po['quantity']}. "
                f"Difference {gap}. Tolerance {controls['quantity_tolerance']}.",
            )

    ordered = [class_id for class_id in CLASS_ORDER if class_id in classes]
    comparisons_complete = po_aligned and price_compared and (
        match_type == "two_way" or quantity_compared
    )
    return {
        "classes": ordered,
        "evidence": evidence,
        "duplicate_confirmed": False,
        "price_compared": price_compared,
        "quantity_compared": quantity_compared,
        "comparisons_complete": comparisons_complete and not ordered,
    }


def _recommend(classes: list[str], *, match_failed: bool, comparisons_complete: bool) -> dict:
    if classes:
        primary_class = classes[0]
        code = RECOMMENDATION_FOR[primary_class]
    elif not match_failed:
        code = RETURN_MATCHING
        primary_class = None
    elif comparisons_complete:
        code = WITHIN_TOLERANCE
        primary_class = None
    else:
        code = INSUFFICIENT
        primary_class = None
    return {
        "code": code,
        "primary_class": primary_class,
        "also_present": classes[1:] if classes else [],
        "draft_only": True,
        "approved_by_reviewer": False,
        "executed": False,
        "must_not": ["post", "approve", "hold", "pay", "change_supplier_bank_details", "send"],
        "asks_are_not_sent": True,
    }


def _prompt_payment(controls: dict) -> dict:
    base = {
        "duty_decided": False,
        "invoice_valid_decided": False,
        "invoice_undisputed_decided": False,
        "payment_instructed": False,
        "notification_sent": False,
        "pcr_2015_reg_113_in_force": False,
        "pcr_2015_reg_113_revoked_on": PCR_REVOKED_ON.isoformat(),
        "revocation": QUOTES["pcr2015_reg113_revoked"],
        "savings_not_encoded": "SI 2024/716 regulations 5 and 6",
        "act_sections_in_force_on": ACT_IN_FORCE_ON.isoformat(),
        "section_67_not_encoded": True,
        "section_73_text_not_encoded": True,
        "buyer_kind": controls["buyer_kind"],
        "exceptions_stated": controls["exceptions"],
        "unrecognised_exceptions": controls["unrecognised_exceptions"],
        "last_day_of_period": None,
        "period_start": None,
        "start_reason": None,
        "status": "reviewer_must_decide_whether_a_duty_applies",
        "rely_on_clock": False,
        "receipt_date_in_invoice_ignored": controls["receipt_ignored"],
    }
    kind = controls["buyer_kind"]
    if kind == "not_a_public_contract":
        base["status"] = "not_applied"
        base["note"] = (
            "The case says this is not a public contract. Sections 68 and 88 were not applied. "
            "The Late Payment of Commercial Debts (Interest) Act 1998 was not opened."
        )
        return base
    if kind == "unspecified":
        base["note"] = "The case does not say whether the buyer is a contracting authority."
        return base
    if kind not in {"contracting_authority", "regulated_below_threshold"}:
        return base

    section = "68" if kind == "contracting_authority" else "88"
    base["section"] = section
    base["quote"] = QUOTES["pa2023_s68_2"] if section == "68" else QUOTES["pa2023_s88_2"]
    base["invalid_or_disputed_quote"] = QUOTES["pa2023_s68_3"]
    base["notify_quote"] = QUOTES["pa2023_s68_4"]
    if section == "68" and controls["exceptions"]:
        base["status"] = "section_68_not_applied_exception_stated"
        base["note"] = (
            "Section 68(1) does not imply the payment term into a concession contract, "
            "a utilities contract awarded by a private utility, or a contract awarded by a school. "
            "The case states one of those. This draft does not decide that the exception is made out."
        )
        return base

    received = controls["received_on"]
    if received is None:
        base["status"] = "receipt_date_missing" if controls["received_raw"] in {None, ""} else "receipt_date_invalid"
        base["note"] = "The clock uses received_on on the case. A date inside the invoice is ignored."
        return base
    start = received
    reason = "day_invoice_received"
    due = controls["payment_due_on_invoice"]
    if due is not None and due > received:
        start = due
        reason = "later_day_on_the_invoice" if section == "68" else "later_day_sum_first_became_due"
    last = start + timedelta(days=29)
    base["period_start"] = start.isoformat()
    base["start_reason"] = reason
    base["last_day_of_period"] = last.isoformat()
    base["period_length_days"] = 30
    base["counting"] = "30 days beginning with the start date. The last day of that period is start plus 29 days."
    if section == "88" and controls["exceptions"]:
        base["status"] = "section_88_arithmetic_exception_not_in_that_section"
        base["note"] = (
            "Section 88, as read on 28 October 2026, does not list the section 68(1) exceptions. "
            "The case states one. The arithmetic is shown and must not be treated as a payment date."
        )
        return base
    base["status"] = "arithmetic_only"
    base["note"] = (
        "Arithmetic on the dates supplied. Not a finding that a sum is due, that the invoice is valid, "
        "or that the invoice is undisputed. Nothing is paid."
    )
    return base


def _minimum_information(extracted: dict) -> dict:
    present = _present_map(extracted)
    rows = []
    for field in SECTION_68_MINIMUM:
        rows.append({"field": field, "present": present[field], "decides_validity": False})
    return {
        "section": "68(9) and 88(7)",
        "quote": QUOTES["pa2023_s68_9"],
        "fields": rows,
        "valid_decided": False,
        "electronic_form_checked": False,
    }


def _controls(working: dict, extracted: dict) -> dict:
    buyer = working.get("buyer_kind", "unspecified")
    if buyer is None or buyer == "":
        buyer = "unspecified"
    if not isinstance(buyer, str) or buyer not in BUYER_KINDS:
        buyer = "unspecified"
    raw_exceptions = working.get("contract_exceptions", [])
    if raw_exceptions is None:
        raw_exceptions = []
    if not isinstance(raw_exceptions, list):
        raise ValueError("contract_exceptions must be a list")
    exceptions = []
    unrecognised = 0
    for item in raw_exceptions:
        if isinstance(item, str) and item in CONTRACT_EXCEPTIONS and item not in exceptions:
            exceptions.append(item)
        else:
            unrecognised += 1
    match = working.get("match")
    if not isinstance(match, dict):
        raise ValueError("match must be an object")
    match_type = match.get("type")
    if match_type not in MATCH_TYPES:
        raise ValueError("match type must be two_way or three_way")
    if type(match.get("failed")) is not bool:
        raise ValueError("match.failed must be a boolean")
    tolerances = working.get("tolerances") or {}
    if not isinstance(tolerances, dict):
        raise ValueError("tolerances must be an object")
    price = _non_negative_int(tolerances.get("price_pence", 0), "price tolerance")
    quantity = _non_negative_int(tolerances.get("quantity", 0), "quantity tolerance")
    known = working.get("known_invoice_numbers", [])
    if known is None:
        known = []
    if not isinstance(known, list):
        raise ValueError("known_invoice_numbers must be a list")
    safe_known = []
    for item in known:
        token = _safe_ref(item) if isinstance(item, str) else None
        if token and token not in safe_known:
            safe_known.append(token)
    stated = working.get("stated_duplicate_of")
    stated_token = _safe_ref(stated) if isinstance(stated, str) else None
    master = _master(working.get("supplier_master"))
    master_fp = None
    if master and isinstance(master.get("bank_fingerprint"), str):
        if FINGERPRINT_TOKEN.fullmatch(master["bank_fingerprint"]):
            master_fp = master["bank_fingerprint"]
    received_raw = working.get("received_on")
    due_raw = working.get("payment_due_on_invoice")
    return {
        "buyer_kind": buyer,
        "exceptions": exceptions,
        "unrecognised_exceptions": unrecognised,
        "match_type": match_type,
        "match_failed": match["failed"],
        "price_pence": price,
        "quantity_tolerance": quantity,
        "known_invoice_numbers": safe_known,
        "stated_duplicate_of": stated_token,
        "purchase_order": _po(working.get("purchase_order")),
        "goods_receipt": _gr(working.get("goods_receipt")),
        "master": master,
        "master_fingerprint": master_fp,
        "received_raw": received_raw,
        "received_on": _parse_iso(received_raw) if isinstance(received_raw, str) else None,
        "payment_due_on_invoice": _parse_iso(due_raw) if isinstance(due_raw, str) else None,
        "receipt_ignored": extracted["receipt_date_in_invoice_ignored"],
    }


def _recommendation_text(code: str) -> str:
    texts = {
        ROUTE_BANK: (
            "Route the bank-detail flag to the bank-detail verifier. "
            "Do not pay, and do not change the supplier bank record, on the strength of this draft."
        ),
        REFER_DUPLICATE: (
            "Ask the AP reviewer to look at the duplicate suspicion. "
            "This draft does not confirm a duplicate and does not hold the invoice."
        ),
        ASK_PO: (
            "Ask the buyer to confirm the purchase order. The question is not sent by this agent."
        ),
        ASK_CORRECTED: (
            "Ask the supplier for a corrected invoice. The question is not sent by this agent. "
            "Input tax is not decided."
        ),
        REFER_VARIANCE: (
            "Refer the price or quantity difference to the buyer. This draft does not accept the difference."
        ),
        WITHIN_TOLERANCE: (
            "The labelled amounts are inside the tolerance the caller supplied, and the case says the match failed. "
            "The reviewer decides what to do with that. Nothing is posted."
        ),
        RETURN_MATCHING: (
            "The case says the automated match did not fail, and this comparison found no exception class. "
            "Return it to the matching process. This draft does not post the invoice."
        ),
        INSUFFICIENT: (
            "The case says the match failed, and this comparison did not have enough labelled fields to classify it. "
            "The reviewer decides. Nothing is posted."
        ),
    }
    return texts[code]


def _flags() -> dict:
    return {
        "invoice_posted": False,
        "invoice_approved": False,
        "invoice_held": False,
        "invoice_paid": False,
        "supplier_bank_details_changed": False,
        "bank_details_verified": False,
        "external_sent": False,
        "production_record_written": False,
        "resolution_executed": False,
        "duplicate_confirmed": False,
        "invoice_valid_decided": False,
        "invoice_undisputed_decided": False,
        "purpose_taken_from_document": False,
    }


def _force_inert(draft: dict) -> None:
    draft["actions_taken"] = []
    draft["model_called"] = False
    draft["network_called"] = False
    draft["flags"] = _flags()
    draft["resolution"]["draft_only"] = True
    draft["resolution"]["executed"] = False
    draft["resolution"]["approved_by_reviewer"] = False
    draft["prompt_injection"]["followed"] = False
    for signal in draft["prompt_injection"]["signals"]:
        signal["followed"] = False
    draft["prompt_payment"]["payment_instructed"] = False
    draft["prompt_payment"]["duty_decided"] = False
    draft["prompt_payment"]["invoice_valid_decided"] = False
    draft["prompt_payment"]["invoice_undisputed_decided"] = False
    draft["prompt_payment"]["notification_sent"] = False
    draft["prompt_payment"]["pcr_2015_reg_113_in_force"] = False
    draft["vat_invoice"]["decides_input_tax"] = False
    draft["vat_invoice"]["destruction_date_calculated"] = False
    draft["minimum_information"]["valid_decided"] = False
    draft["extracted"]["values_of_bank_accounts_recorded"] = False
    draft["bank_route_acknowledged"] = False
    draft["human_approval"]["resolution"]["recorded"] = False
    draft["human_approval"]["bank_route"]["recorded"] = False
    draft["human_approval"]["bank_route"]["changes_bank_details"] = False
    intake = draft["document_intake"]
    intake["files_confirmed"] = False
    intake["purpose_confirmed"] = False


def _blockers(intake_files: list[dict]) -> list[str]:
    reasons = []
    for file in intake_files:
        if file["read_status"] != "read":
            reasons.append(f"{file['file_id']}:{file['read_status']}")
        elif file["checksum_matches"] is False:
            reasons.append(f"{file['file_id']}:checksum_mismatch")
    return reasons


def triage(
    case: dict,
    *,
    as_of: date,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    rules_as_of: date | None = None,
) -> dict:
    """Return a draft resolution. Approval flags stay false."""

    if not isinstance(case, dict):
        raise TypeError("case must be an object")
    if not isinstance(as_of, date) or isinstance(as_of, datetime):
        raise TypeError("as_of must be a date")
    if type(stale_after_days) is not int or stale_after_days < 0:
        raise ValueError("stale_after_days must be a non-negative integer")
    if rules_as_of is not None and (not isinstance(rules_as_of, date) or isinstance(rules_as_of, datetime)):
        raise TypeError("rules_as_of must be a date")
    if case.get("synthetic") is not True:
        raise NotSynthetic("record is not marked synthetic")

    intake_module = _load_intake()
    working = dict(case)
    prohibited = _strip_prohibited(working, "")
    files_in = working.get("files")
    if not isinstance(files_in, list) or not files_in:
        raise ValueError("case has no files")

    case_id = working.get("case_id", "unspecified")
    if not isinstance(case_id, str) or not case_id or len(case_id) > 80 or "\n" in case_id:
        case_id = "unspecified"

    scans = []
    cleaned = []
    for raw in files_in:
        if not isinstance(raw, dict):
            raise ValueError("each file must be an object")
        file_copy = dict(raw)
        file_id = file_copy.get("file_id", "?")
        prohibited.extend(_strip_prohibited(file_copy, f"file:{file_id}:"))
        content = file_copy.get("content", "")
        if not isinstance(content, str):
            content = ""
        filename = file_copy.get("filename", "")
        if not isinstance(filename, str):
            filename = ""
        label = file_id if isinstance(file_id, str) else "?"
        scans.append(scan_text(filename, file_id=label, where="filename"))
        if content and len(content) <= intake_module.MAX_CHARS:
            scans.append(scan_text(content, file_id=label, where="body"))
        cleaned.append(file_copy)

    extracted = _extract(cleaned, intake_module)
    controls = _controls(working, extracted)
    vat = _vat_section(extracted, controls["master"])
    batch = {
        "synthetic": True,
        "batch_id": case_id,
        "requested_purpose": INTAKE_PURPOSE,
        "files": cleaned,
    }
    intake_draft = intake_module.intake(
        batch,
        as_of=as_of,
        stale_after_days=stale_after_days,
        rules_as_of=rules_as_of,
    )
    classified = _classify(extracted, controls, intake_draft["files"], vat)
    recommendation = _recommend(
        classified["classes"],
        match_failed=controls["match_failed"],
        comparisons_complete=classified["comparisons_complete"],
    )
    recommendation["text"] = _recommendation_text(recommendation["code"])
    recommendation["reasons"] = [item["id"] for item in classified["evidence"] if item["class"]]
    payment = _prompt_payment(controls)
    sources_age = (as_of - SOURCES_PINNED_ON).days
    sources_stale = sources_age > stale_after_days
    any_document_stale = any(file["date_status"] in NOT_CURRENT for file in intake_draft["files"])
    if extracted["invoice_date"]:
        status, _, _ = _date_status(extracted["invoice_date"], as_of, stale_after_days)
        if status in NOT_CURRENT:
            any_document_stale = True
    gateway_rules_stale = bool(intake_draft.get("gateway_rules_stale"))
    material_warning = sources_stale or any_document_stale or gateway_rules_stale
    if material_warning:
        payment["rely_on_clock"] = False

    draft = {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment_id": EXPERIMENT_ID,
        "autonomy": "A1",
        "case_id": case_id,
        "synthetic": True,
        "as_of": as_of.isoformat(),
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_stale": sources_stale,
        "any_document_stale": any_document_stale,
        "gateway_rules_stale": gateway_rules_stale,
        "rules_current": not material_warning,
        "stale_after_days": stale_after_days,
        "match": {
            "type": controls["match_type"],
            "failed": controls["match_failed"],
            "stated_codes_adopted": False,
        },
        "exceptions": classified["classes"],
        "evidence": classified["evidence"],
        "duplicate_confirmed": False,
        "resolution": recommendation,
        "prompt_payment": payment,
        "vat_invoice": vat,
        "minimum_information": _minimum_information(extracted),
        "extracted": extracted,
        "document_intake": intake_draft,
        "prompt_injection": merge_scans(scans),
        "prohibited_keys_removed": prohibited,
        "bank_detail_change": "bank_detail_change" in classified["classes"],
        "bank_route_acknowledged": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "flags": _flags(),
        "human_approval": {
            "resolution": {
                "required": True,
                "approver": AP_REVIEWER_ROLE,
                "recorded": False,
                "decision": None,
            },
            "bank_route": {
                "required": "bank_detail_change" in classified["classes"],
                "approver": BANK_VERIFIER_ROLE,
                "recorded": False,
                "changes_bank_details": False,
                "verifies_bank_details": False,
            },
            "stale_material": {
                "required": material_warning,
                "approver": AP_REVIEWER_ROLE,
                "recorded": False,
            },
        },
        "sources": [
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "retrieved": source["retrieved"],
                "applied_as_a_decision": False,
            }
            for source in SOURCES
        ],
        "limitations": list(LIMITATIONS),
        "blockers": _blockers(intake_draft["files"]),
    }
    _force_inert(draft)
    return draft


def _date_status(raw: str, as_of: date, window: int) -> tuple[str, str | None, int | None]:
    parsed = _parse_iso(raw)
    if parsed is None:
        return "invalid", None, None
    age = (as_of - parsed).days
    if age < 0:
        return "future", parsed.isoformat(), age
    if age > window:
        return "stale", parsed.isoformat(), age
    return "within_window", parsed.isoformat(), age


def _require_draft(draft: dict) -> dict:
    if not isinstance(draft, dict) or draft.get("label") != LABEL:
        raise ValueError("draft was not produced by triage")
    if draft.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("draft was not produced by triage")
    return deepcopy(draft)


def record_bank_route(draft: dict, *, role: str) -> dict:
    """Record that a bank-detail verifier saw the route.

    The agent must not call this. The record does not verify the bank
    details and does not change them.
    """

    if role != BANK_VERIFIER_ROLE:
        raise ValueError("only a Bank-detail verifier can record this route")
    updated = _require_draft(draft)
    if updated["bank_detail_change"] is not True:
        raise ValueError("no bank-detail change is flagged")
    updated["bank_route_acknowledged"] = True
    updated["human_approval"]["bank_route"]["recorded"] = True
    updated["flags"]["supplier_bank_details_changed"] = False
    updated["flags"]["bank_details_verified"] = False
    updated["human_approval"]["bank_route"]["changes_bank_details"] = False
    updated["human_approval"]["bank_route"]["verifies_bank_details"] = False
    return updated


def record_ap_reviewer_decision(
    draft: dict,
    *,
    role: str,
    decision: str,
    acknowledge_stale: bool = False,
) -> dict:
    """Record an AP reviewer's decision on the draft resolution.

    The agent must not call this. Approving the resolution does not post,
    hold, pay, or change a bank record.
    """

    if role != AP_REVIEWER_ROLE:
        raise ValueError("only an AP reviewer can record this decision")
    if decision not in DECISIONS:
        raise ValueError("decision must be approve_resolution, return_for_edit, or reject_resolution")
    if acknowledge_stale is not True and acknowledge_stale is not False:
        raise TypeError("acknowledge_stale must be a boolean")
    updated = _require_draft(draft)
    if decision == "approve_resolution":
        if updated["blockers"]:
            raise ValueError("a file was not read or a checksum does not match")
        material = (
            updated["sources_stale"] or updated["any_document_stale"] or updated["gateway_rules_stale"]
        )
        if material and acknowledge_stale is not True:
            raise ValueError("stale material must be acknowledged by a person")
        if updated["bank_detail_change"] and updated["bank_route_acknowledged"] is not True:
            raise ValueError("the bank-detail route has not been recorded by the verifier")
        updated["resolution"]["approved_by_reviewer"] = True
        updated["human_approval"]["stale_material"]["recorded"] = bool(material)
    updated["resolution"]["executed"] = False
    updated["resolution"]["draft_only"] = True
    updated["human_approval"]["resolution"]["recorded"] = True
    updated["human_approval"]["resolution"]["decision"] = decision
    updated["flags"]["invoice_posted"] = False
    updated["flags"]["invoice_approved"] = False
    updated["flags"]["invoice_held"] = False
    updated["flags"]["invoice_paid"] = False
    updated["flags"]["supplier_bank_details_changed"] = False
    updated["flags"]["resolution_executed"] = False
    updated["actions_taken"] = []
    return updated


def post_invoice(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not post an invoice")


def approve_invoice(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not approve an invoice")


def hold_invoice(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not hold an invoice")


def pay_invoice(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not pay an invoice")


def change_supplier_bank_details(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not change supplier bank details")


def send_external(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not send")


def write_production_record(*_args, **_kwargs) -> None:
    raise TriageForbidden("the agent does not write a production record")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft an invoice exception resolution.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--rules-as-of", default=None)
    args = parser.parse_args(argv)
    case = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rules_as_of = date.fromisoformat(args.rules_as_of) if args.rules_as_of else None
    draft = triage(
        case,
        as_of=date.fromisoformat(args.as_of),
        stale_after_days=args.stale_after_days,
        rules_as_of=rules_as_of,
    )
    json.dump(draft, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except NotSynthetic as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
