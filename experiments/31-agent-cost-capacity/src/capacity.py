"""Quota headroom from the caller's limits. The limit is not changed."""

from __future__ import annotations

from decimal import Decimal

try:
    from .cost import CREDIT, STUDIO, usage_for_quota
    from .money import InexactNumber, parse_decimal, quantity, unit
    from .sources import DEFAULT_HEADROOM_TIGHT_BELOW, DEFAULT_SPIKE_MULTIPLE, MIN_AGENTS_FOR_SPIKE
except ImportError:  # python src/report.py puts this directory on sys.path
    from cost import CREDIT, STUDIO, usage_for_quota
    from money import InexactNumber, parse_decimal, quantity, unit
    from sources import DEFAULT_HEADROOM_TIGHT_BELOW, DEFAULT_SPIKE_MULTIPLE, MIN_AGENTS_FOR_SPIKE


def _anomaly(anomaly_id: str, severity: str, **detail: object) -> dict:
    row: dict = {"id": anomaly_id, "severity": severity}
    row.update(detail)
    return row


def headroom(
    quotas: list[dict],
    priced: list[dict],
    sources: list[dict],
    tight_below: str,
) -> tuple[list[dict], list[dict]]:
    try:
        threshold = parse_decimal(tight_below)
    except InexactNumber:
        threshold = parse_decimal(DEFAULT_HEADROOM_TIGHT_BELOW)
    rows: list[dict] = []
    anomalies: list[dict] = []
    by_id = {str(agent.get("agent_id")): agent for agent in sources}
    for quota in quotas:
        if not isinstance(quota, dict):
            continue
        meter = quota.get("meter")
        platform = quota.get("platform") or "*"
        quota_id = str(quota.get("quota_id") or meter or "")
        try:
            limit = parse_decimal(quota.get("limit"))
        except InexactNumber:
            anomalies.append(_anomaly("non_exact_number", "blocker", quota_id=quota_id, field="limit"))
            continue
        if limit < 0:
            anomalies.append(_anomaly("negative_quantity", "blocker", quota_id=quota_id))
            continue
        used = Decimal(0)
        for row in priced:
            source = by_id.get(row["agent_id"])
            if source is None or meter not in {CREDIT, "input_tokens", "output_tokens", "tool_calls", "conversations"}:
                continue
            if platform != "*" and row["platform"] != platform:
                continue
            if platform == "*" and meter == CREDIT and row["platform"] not in STUDIO:
                continue
            used += usage_for_quota(row, source, meter)
        remaining = limit - used
        ratio = None if limit == 0 else remaining / limit
        flags: list[str] = []
        if limit == 0:
            anomalies.append(_anomaly("zero_quota_limit", "warning", quota_id=quota_id))
            flags.append("zero_quota_limit")
        elif used > limit:
            anomalies.append(_anomaly("over_quota", "warning", quota_id=quota_id))
            flags.append("over_quota")
        elif ratio is not None and ratio < threshold:
            anomalies.append(_anomaly("tight_headroom", "info", quota_id=quota_id))
            flags.append("tight_headroom")
        rows.append(
            {
                "quota_id": quota_id,
                "meter": meter,
                "platform": platform,
                "limit": quantity(limit),
                "used": quantity(used),
                "headroom": quantity(remaining),
                "headroom_ratio": unit(ratio) if ratio is not None else None,
                "flags": flags,
                "changed": False,
                "added_rollup": False,
            }
        )
    return rows, anomalies


def spikes(priced: list[dict], multiple: str) -> list[dict]:
    try:
        factor = parse_decimal(multiple)
    except InexactNumber:
        factor = parse_decimal(DEFAULT_SPIKE_MULTIPLE)
    if factor <= 0:
        return []
    by_platform: dict[str, list[tuple[dict, Decimal]]] = {}
    for row in priced:
        if row.get("unit_cost_per_case") is None:
            continue
        by_platform.setdefault(row["platform"], []).append((row, parse_decimal(row["unit_cost_per_case"])))
    anomalies: list[dict] = []
    for platform, pairs in by_platform.items():
        if len(pairs) < MIN_AGENTS_FOR_SPIKE:
            continue
        values = sorted(value for _, value in pairs)
        mid = len(values) // 2
        if len(values) % 2 == 1:
            median = values[mid]
        else:
            median = (values[mid - 1] + values[mid]) / 2
        if median <= 0:
            continue
        for row, value in pairs:
            if value > median * factor:
                anomalies.append(
                    _anomaly(
                        "spike",
                        "warning",
                        agent_id=row["agent_id"],
                        platform=platform,
                        median_unit_cost=unit(median),
                    )
                )
    return anomalies
