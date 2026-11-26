"""Choose the pinned matrix row, the amount, and the eligible approvers.

A caller-supplied matrix, directory, or delegation is compared and not applied.
An unreadable amount is not coerced to zero. Parts that disagree with the
headline are a conflict: neither figure is chosen. Parts that add up are
routed at the total, so a split does not stay under a threshold.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from cues import category_hit
else:
    from .cues import category_hit

_MONEY = re.compile(r"^\d+(\.\d{1,2})?$")
_OUT_OF_RANGE = 100_000_000_000


def version_key(value: object) -> tuple[int, ...] | None:
    """A version that is not dotted integers is unreadable. It is not zero."""

    if not isinstance(value, str) or not value.strip():
        return None
    parts = value.strip().split(".")
    numbers = []
    for part in parts:
        if not part.isdigit():
            return None
        numbers.append(int(part))
    return tuple(numbers)


def parse_pence(value: object) -> dict:
    """Whole pounds as an int, or a string of pounds and at most two decimals."""

    if value is None or value == "":
        return _money(None, True, "missing")
    if isinstance(value, bool) or isinstance(value, float):
        return _money(None, True, "not_a_decimal_string_or_int")
    if isinstance(value, int):
        if value < 0:
            return _money(None, True, "negative")
        if value > 1_000_000_000:
            return _money(None, True, "out_of_range")
        return _money(value * 100, False, None)
    if isinstance(value, str):
        text = value.strip().replace(",", "").replace("£", "")
        if not _MONEY.fullmatch(text):
            return _money(None, True, "unparseable")
        pounds, _, frac = text.partition(".")
        frac = (frac + "00")[:2]
        pence = int(pounds) * 100 + int(frac)
        if pence > _OUT_OF_RANGE:
            return _money(None, True, "out_of_range")
        return _money(pence, False, None)
    return _money(None, True, "not_a_decimal_string_or_int")


def _money(pence: int | None, unparseable: bool, reason: str | None) -> dict:
    return {
        "pence": pence,
        "gbp": None if pence is None else f"{pence // 100}.{pence % 100:02d}",
        "unparseable": unparseable,
        "reason": reason,
        "coerced": False,
    }


def people(directory: dict) -> list[dict]:
    rows = directory.get("people") if isinstance(directory, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def person(directory: dict, ref: object) -> dict | None:
    if not isinstance(ref, str):
        return None
    for row in people(directory):
        if row.get("employee_ref") == ref:
            return row
    return None


def _ids(rows: list, field: str) -> set[str]:
    found = set()
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get(field), str):
            found.add(row[field])
    return found


def id_diff(caller: object, pinned_ids: set[str], field: str) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": "not_object", "applied": False}]
    rows = caller.get("rules") or caller.get("people") or caller.get("limits") or []
    if not isinstance(rows, list):
        rows = []
    caller_ids = _ids(rows, field)
    diffs = []
    for item_id in sorted(caller_ids - pinned_ids):
        diffs.append({"id": item_id, "kind": "not_in_pinned", "applied": False})
    for item_id in sorted(pinned_ids - caller_ids):
        diffs.append({"id": item_id, "kind": "missing_from_caller", "applied": False})
    return diffs


def delegation_diff(caller: object, directory: dict) -> list[dict]:
    if caller is None:
        return []
    if not isinstance(caller, dict):
        return [{"kind": "not_object", "applied": False}]
    rows = caller.get("limits") if isinstance(caller.get("limits"), list) else []
    pinned = {
        row.get("employee_ref"): row.get("delegation_limit_gbp")
        for row in people(directory)
        if isinstance(row.get("employee_ref"), str)
    }
    diffs = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("employee_ref"), str):
            diffs.append({"kind": "unreadable_row", "applied": False})
            continue
        ref = row["employee_ref"]
        seen.add(ref)
        if ref not in pinned:
            diffs.append({"id": ref, "kind": "not_in_pinned", "applied": False})
        elif row.get("delegation_limit_gbp") != pinned[ref]:
            diffs.append({"id": ref, "kind": "limit_differs", "applied": False})
    for ref in sorted(set(pinned) - seen):
        diffs.append({"id": ref, "kind": "missing_from_caller", "applied": False})
    return diffs


def _rules(matrix: dict) -> list[dict]:
    rows = matrix.get("rules") if isinstance(matrix, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def matching_rules(matrix: dict, request_type: object, pence: int | None, severity: object, change_class: object) -> list[dict]:
    found = []
    for rule in _rules(matrix):
        if rule.get("request_type") != request_type:
            continue
        if request_type == "spend":
            minimum = rule.get("min_pence")
            maximum = rule.get("max_pence")
            if type(minimum) is not int or pence is None or pence < minimum:
                continue
            if maximum is not None and (type(maximum) is not int or pence >= maximum):
                continue
            found.append(rule)
        elif request_type == "policy_exception" and rule.get("severity") == severity:
            found.append(rule)
        elif request_type == "change" and rule.get("change_class") == change_class:
            found.append(rule)
    return found


def band_rank(rule: dict | None) -> int | None:
    if not isinstance(rule, dict) or type(rule.get("min_pence")) is not int:
        if isinstance(rule, dict) and rule.get("request_type") != "spend":
            return 0
        return None
    return rule["min_pence"]


def combine_amounts(request: dict, matrix: dict, text: str) -> dict:
    headline_present = isinstance(request, dict) and "amount_gbp" in request
    headline = parse_pence(request.get("amount_gbp")) if headline_present else _money(None, False, "absent")
    parts_in = request.get("parts") if isinstance(request, dict) else None
    related_in = request.get("related_requests") if isinstance(request, dict) else None
    parts = []
    part_bad = False
    if isinstance(parts_in, list) and parts_in:
        for part in parts_in:
            amount = part.get("amount_gbp") if isinstance(part, dict) else part
            reading = parse_pence(amount)
            parts.append(reading)
            if reading["unparseable"]:
                part_bad = True
    related = []
    related_bad = False
    if isinstance(related_in, list) and related_in:
        for part in related_in:
            amount = part.get("amount_gbp") if isinstance(part, dict) else part
            reading = parse_pence(amount)
            related.append(reading)
            if reading["unparseable"]:
                related_bad = True
    cue = category_hit(text, "split_cue")
    result = {
        "headline": headline,
        "parts": parts,
        "related": related,
        "routing_pence": None,
        "routing_gbp": None,
        "conflicting": False,
        "unreadable": False,
        "split_to_dodge_threshold": False,
        "split_cue": cue,
        "coerced": False,
        "chosen_when_conflict": None,
    }
    if part_bad or related_bad or (headline_present and headline["unparseable"]):
        result["unreadable"] = True
        return result
    part_total = sum(item["pence"] for item in parts) if parts else None
    if parts and headline_present and headline["pence"] != part_total:
        result["conflicting"] = True
        return result
    base = part_total if parts else (headline["pence"] if headline_present else None)
    if related:
        if base is None:
            result["unreadable"] = True
            return result
        base = base + sum(item["pence"] for item in related)
    if base is None and request.get("request_type") == "spend":
        result["unreadable"] = True
        return result
    result["routing_pence"] = base
    if base is not None:
        result["routing_gbp"] = f"{base // 100}.{base % 100:02d}"
    if request.get("request_type") == "spend" and base is not None:
        total_rules = matching_rules(matrix, "spend", base, None, None)
        total_rank = band_rank(total_rules[0]) if len(total_rules) == 1 else None
        piece_ranks = []
        for reading in parts or ([headline] if headline_present else []):
            if reading["pence"] is None:
                continue
            piece = matching_rules(matrix, "spend", reading["pence"], None, None)
            if len(piece) == 1:
                piece_ranks.append(band_rank(piece[0]))
        if total_rank is not None and piece_ranks and any(rank is not None and rank < total_rank for rank in piece_ranks):
            result["split_to_dodge_threshold"] = True
        if related and headline_present and headline["pence"] is not None:
            alone = matching_rules(matrix, "spend", headline["pence"], None, None)
            if len(alone) == 1 and total_rank is not None and band_rank(alone[0]) is not None and band_rank(alone[0]) < total_rank:
                result["split_to_dodge_threshold"] = True
    return result


def eligible_refs(directory: dict, role: str, requester: object, request_type: object, pence: int | None) -> list[str]:
    refs = []
    for row in people(directory):
        if row.get("role") != role or row.get("active") is not True or row.get("guest") is True:
            continue
        if row.get("employee_ref") == requester or not isinstance(row.get("employee_ref"), str):
            continue
        if request_type == "spend":
            limit = row.get("delegation_limit_gbp")
            if type(limit) is not int or pence is None or pence > limit * 100:
                continue
        refs.append(row["employee_ref"])
    return refs


def approver_problem(row: dict | None, requester: object, roles: list[str], request_type: object, pence: int | None) -> str | None:
    if row is None:
        return "approver_not_in_directory"
    if row.get("active") is not True:
        return "approver_inactive"
    if row.get("guest") is True:
        return "guest_cannot_approve"
    if row.get("employee_ref") == requester:
        return "requester_cannot_approve"
    if row.get("role") not in roles:
        return "not_a_required_approver"
    if request_type == "spend":
        limit = row.get("delegation_limit_gbp")
        if type(limit) is not int:
            return "delegation_limit_unreadable"
        if pence is None:
            return "amount_unreadable"
        if pence > limit * 100:
            return "above_delegation_limit"
    return None
