"""Check every evidence item. Do not choose between conflicting values.

Expired, superseded, unsigned, wrong version, stale, and conflicting items
stay visible. A sentence that denies a required phrase is not support.
A carve-out after acceptable wording is not treated as acceptable.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from cues import carve_out, text_says_acceptable
    from dates import as_date, currency_status, parse_date, with_question_date
    from marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from mask import mask_text
    from negate import affirmed, sentences
    from routing import parse_pence, version_key
else:
    from .cues import carve_out, text_says_acceptable
    from .dates import as_date, currency_status, parse_date, with_question_date
    from .marking import (
        above_ceiling,
        content_markings,
        higher_marking,
        legal_hold,
        metadata_markings,
        retention_labels,
    )
    from .mask import mask_text
    from .negate import affirmed, sentences
    from .routing import parse_pence, version_key


def _checklist_map(checklist: dict) -> dict[str, dict]:
    rows = checklist.get("items") if isinstance(checklist, dict) else None
    if not isinstance(rows, list):
        return {}
    return {
        row.get("evidence_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("evidence_id"), str)
    }


def _first_sentence(text: str) -> str:
    parts = sentences(text or "")
    if not parts:
        return ""
    return parts[0][:240]


def review_evidence(
    items: object,
    checklist: dict,
    *,
    request_type: object,
    routing_pence: int | None,
    severity: object,
    change_class: object,
    supplier_name: object,
    as_of,
    requester_ref: object,
    ceiling: str | None,
    digest,
) -> dict:
    """Return public rows. Raw evidence text is not copied into the result."""

    required = _required_ids(
        checklist,
        request_type,
        routing_pence,
        severity=severity,
        change_class=change_class,
    )
    by_check = _checklist_map(checklist)
    raw_items = [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
    prepared = [_prepare(item, by_check, as_of, requester_ref, supplier_name, digest) for item in raw_items]
    _mark_relationships(prepared)
    rows = []
    present: list[str] = []
    missing: list[str] = []
    stale: list[str] = []
    expired: list[str] = []
    superseded: list[str] = []
    unsigned: list[str] = []
    wrong_version: list[str] = []
    conflicting: list[dict] = []
    support_gaps: list[str] = []
    carve_outs: list[str] = []
    markings: list[str] = []
    retention: list[str] = []
    hold_ids: list[str] = []
    dates_unreadable = False
    pack_hold = False
    for row in prepared:
        if row["marking"]:
            markings.append(row["marking"])
        for label in row["retention"]:
            if label not in retention:
                retention.append(label)
        if row["legal_hold"]:
            pack_hold = True
            hold_ids.append(row["evidence_id"])
        if row["checks"]["stale"]:
            stale.append(row["evidence_id"])
        if row["checks"]["expired"]:
            expired.append(row["evidence_id"])
        if row["checks"]["superseded"]:
            superseded.append(row["evidence_id"])
        if row["checks"]["unsigned"]:
            unsigned.append(row["evidence_id"])
        if row["checks"]["wrong_version"]:
            wrong_version.append(row["evidence_id"])
        if row["checks"]["carve_out"]:
            carve_outs.append(row["evidence_id"])
        if row["dates_unreadable"]:
            dates_unreadable = True
        if row["checklist_id"] and row["checklist_id"] not in present:
            present.append(row["checklist_id"])
        rows.append(_public(row))
    for check_id, group in _groups(prepared).items():
        values = {row["value_pence"] for row in group if row["value_pence"] is not None and not row["checks"]["superseded"]}
        if len(values) > 1:
            conflicting.append(
                {
                    "checklist_id": check_id,
                    "evidence_ids": [row["evidence_id"] for row in group],
                    "kind": "duplicate_values",
                    "chosen": None,
                }
            )
    if routing_pence is not None:
        for row in prepared:
            if row["value_pence"] is not None and row["value_pence"] != routing_pence and not row["checks"]["superseded"]:
                conflicting.append(
                    {
                        "checklist_id": row["checklist_id"],
                        "evidence_ids": [row["evidence_id"]],
                        "kind": "evidence_value_differs_from_request",
                        "chosen": None,
                    }
                )
    for check_id in required:
        if check_id not in present:
            missing.append(check_id)
        else:
            currents = [
                row for row in prepared
                if row["checklist_id"] == check_id and not row["checks"]["superseded"] and not row["checks"]["conflicting"]
            ]
            if not any(row["checks"]["support"] for row in currents):
                if any(row["must_mention"] for row in currents):
                    support_gaps.append(check_id)
    applied = higher_marking(markings)
    withheld = above_ceiling(applied, ceiling) if applied else False
    if withheld:
        for row in rows:
            row["body_withheld"] = True
            row["citation"]["excerpt"] = None
            row["citation"]["raw_excerpt_stored"] = False
    return {
        "items": rows,
        "present": present,
        "missing": missing,
        "stale": stale,
        "expired": expired,
        "superseded": superseded,
        "unsigned": unsigned,
        "wrong_version": wrong_version,
        "conflicting": conflicting,
        "support_gaps": support_gaps,
        "carve_outs": carve_outs,
        "marking": {
            "applied": applied,
            "labels": list(dict.fromkeys(markings)),
            "higher_of_conflict": len(set(markings)) > 1,
            "from_metadata_and_content": True,
            "self_declared_clearance_used": False,
        },
        "legal_hold": pack_hold,
        "legal_hold_items": hold_ids,
        "retention": retention,
        "body_withheld": withheld,
        "dates_unreadable": dates_unreadable,
        "coerced": False,
        "value_chosen_on_conflict": False,
        "treated_as_acceptable": False,
    }


def _required_ids(
    checklist: dict,
    request_type: object,
    routing_pence: int | None,
    *,
    severity: object,
    change_class: object,
) -> list[str]:
    rows = checklist.get("items") if isinstance(checklist, dict) else None
    if not isinstance(rows, list):
        return []
    found = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("evidence_id"), str):
            continue
        rules = row.get("required_for") if isinstance(row.get("required_for"), list) else []
        for rule in rules:
            if not isinstance(rule, dict) or rule.get("request_type") != request_type:
                continue
            if request_type == "spend":
                minimum = rule.get("min_pence")
                maximum = rule.get("max_pence")
                if routing_pence is None or type(minimum) is not int or routing_pence < minimum:
                    continue
                if maximum is not None and (type(maximum) is not int or routing_pence >= maximum):
                    continue
            if request_type == "policy_exception" and "severity" in rule and rule.get("severity") != severity:
                continue
            if request_type == "change" and "change_class" in rule and rule.get("change_class") != change_class:
                continue
            found.append(row["evidence_id"])
            break
    return found


def _prepare(item: dict, by_check: dict, as_of, requester_ref, supplier_name, digest) -> dict:
    evidence_id = item.get("evidence_id") if isinstance(item.get("evidence_id"), str) else "unreadable"
    checklist_id = item.get("checklist_id") if isinstance(item.get("checklist_id"), str) else None
    spec = by_check.get(checklist_id) if checklist_id else None
    content = item.get("content") if isinstance(item.get("content"), str) else ""
    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    meta_marks, _meta_bad = metadata_markings(metadata.get("marking"))
    content_marks = content_markings(content)
    marking = higher_marking(meta_marks + content_marks)
    held, _hold_bad = legal_hold(metadata.get("legal_hold"), content)
    labels, _ret_bad = retention_labels(metadata.get("retention"), content)
    document = with_question_date(parse_date(item.get("document_date")), as_of)
    expiry = with_question_date(parse_date(item.get("expiry_date")), as_of) if item.get("expiry_date") not in (None, "") else {
        "iso": None, "unparseable": False, "ambiguous": False, "future": False, "reason": "absent", "coerced": False,
    }
    currency_days = spec.get("currency_days") if isinstance(spec, dict) else None
    currency = currency_status(item.get("document_date"), as_of=as_of, currency_days=currency_days if type(currency_days) is int else None)
    expired = False
    expiry_day = as_date(expiry)
    if expiry_day is not None and expiry_day < as_of:
        expired = True
    version = item.get("version") if isinstance(item.get("version"), str) else None
    readable_version = version_key(version) is not None
    required_version = spec.get("required_version") if isinstance(spec, dict) else None
    wrong_version = False
    if isinstance(spec, dict) and required_version is not None:
        wrong_version = version != required_version or not readable_version
    elif isinstance(spec, dict) and not readable_version and version not in (None, ""):
        wrong_version = True
    signed = item.get("signed") is True
    needs_signature = bool(isinstance(spec, dict) and spec.get("requires_signature") is True)
    unsigned = needs_signature and not signed
    status = item.get("status") if isinstance(item.get("status"), str) else "current"
    value = parse_pence(item.get("value_gbp")) if "value_gbp" in item else {"pence": None, "unparseable": False, "coerced": False}
    must_mention = None
    support = True
    if isinstance(spec, dict) and spec.get("must_mention_field") == "supplier_name" and isinstance(supplier_name, str) and supplier_name:
        must_mention = supplier_name
        support = affirmed(content, supplier_name)
    excerpt_source = _first_sentence(content)
    masked, mask_report = mask_text(excerpt_source)
    dates_unreadable = bool(document.get("unparseable") or document.get("ambiguous") or document.get("future") or expiry.get("unparseable") or expiry.get("ambiguous"))
    return {
        "evidence_id": evidence_id,
        "checklist_id": checklist_id,
        "version": version,
        "version_readable": readable_version,
        "status": status,
        "signed": signed,
        "signature_is_requester": signed and item.get("signed_by_ref") == requester_ref,
        "document_date": document,
        "expiry_date": expiry,
        "value_pence": value.get("pence"),
        "value_unreadable": bool(value.get("unparseable")),
        "marking": marking,
        "legal_hold": held,
        "retention": labels,
        "must_mention": must_mention,
        "content_digest": digest({"content": content}),
        "mask": {
            "counts": mask_report["counts"],
            "any": mask_report["any"],
            "values_stored": False,
            "values_copied": False,
            "described_as_anonymised": False,
            "raw_excerpt_stored": False,
        },
        "excerpt": masked,
        "excerpt_is_substring_before_mask": excerpt_source in content if excerpt_source else False,
        "dates_unreadable": dates_unreadable,
        "checks": {
            "present": True,
            "expired": expired,
            "superseded": status == "superseded",
            "unsigned": unsigned,
            "wrong_version": wrong_version,
            "stale": bool(currency.get("stale")),
            "conflicting": False,
            "support": support,
            "carve_out": carve_out(content),
            "treated_as_acceptable": False,
            "text_says_acceptable": text_says_acceptable(content),
            "coerced": False,
        },
    }


def _groups(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        if row["checklist_id"]:
            groups.setdefault(row["checklist_id"], []).append(row)
    return groups


def _mark_relationships(rows: list[dict]) -> None:
    for group in _groups(rows).values():
        live = [row for row in group if row["status"] != "superseded"]
        values = {row["value_pence"] for row in live if row["value_pence"] is not None}
        if len(live) >= 2 and len(values) > 1:
            for row in live:
                row["checks"]["conflicting"] = True
            continue
        keyed = [(row, version_key(row["version"])) for row in live]
        if any(key is None for _row, key in keyed):
            for row, key in keyed:
                if key is None:
                    row["checks"]["wrong_version"] = True
            continue
        if len(keyed) >= 2:
            best = max(key for _row, key in keyed)
            at_best = [row for row, key in keyed if key == best]
            for row, key in keyed:
                if key < best:
                    row["checks"]["superseded"] = True
            if len(at_best) > 1:
                for row in at_best:
                    row["checks"]["duplicate_same_value"] = True


def _public(row: dict) -> dict:
    return {
        "evidence_id": row["evidence_id"],
        "checklist_id": row["checklist_id"],
        "version": row["version"],
        "version_readable": row["version_readable"],
        "status": row["status"],
        "signed": row["signed"],
        "signature_is_requester": row["signature_is_requester"],
        "document_date": row["document_date"],
        "expiry_date": row["expiry_date"],
        "value_pence": row["value_pence"],
        "value_unreadable": row["value_unreadable"],
        "checks": row["checks"],
        "marking": row["marking"],
        "legal_hold": row["legal_hold"],
        "retention": list(row["retention"]),
        "body_withheld": False,
        "citation": {
            "evidence_id": row["evidence_id"],
            "checklist_id": row["checklist_id"],
            "version": row["version"],
            "excerpt": row["excerpt"],
            "excerpt_is_substring_before_mask": row["excerpt_is_substring_before_mask"],
            "raw_excerpt_stored": False,
            "content_digest": row["content_digest"],
            "evidence_sha256": None,
            "values_copied": False,
        },
        "mask": row["mask"],
    }

