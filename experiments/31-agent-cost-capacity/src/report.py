#!/usr/bin/env python3
"""Draft a cost and capacity report from telemetry and a rate card.

The same files and the same as-of date produce the same JSON. Rates come
only from the rate card argument. Nothing is validated and nothing is changed.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from capacity import headroom, spikes
    from cost import (
        BUILTIN_RATES,
        _empty_agent,
        _parse_rate_card,
        compare_rollup,
        dedupe_agents,
        price_agents,
        totals_from,
    )
    from forecast import build_forecast
    from injection import hostile, inspect
    from prohibited import PROHIBITED_FLAGS, ProhibitedAction
    from sources import (
        ASSUMPTIONS,
        DEFAULT_HEADROOM_TIGHT_BELOW,
        DEFAULT_SPIKE_MULTIPLE,
        DEFAULT_STALE_AFTER_DAYS,
        SOURCES,
    )
else:
    from .capacity import headroom, spikes
    from .cost import (
        BUILTIN_RATES,
        _empty_agent,
        _parse_rate_card,
        compare_rollup,
        dedupe_agents,
        price_agents,
        totals_from,
    )
    from .forecast import build_forecast
    from .injection import hostile, inspect
    from .prohibited import PROHIBITED_FLAGS, ProhibitedAction
    from .sources import (
        ASSUMPTIONS,
        DEFAULT_HEADROOM_TIGHT_BELOW,
        DEFAULT_SPIKE_MULTIPLE,
        DEFAULT_STALE_AFTER_DAYS,
        SOURCES,
    )

LABEL = "DRAFT FOR FINOPS REVIEW"


def _anomaly(anomaly_id: str, severity: str, **detail: object) -> dict:
    row: dict = {"id": anomaly_id, "severity": severity}
    row.update(detail)
    return row


def _sources(as_of: date, stale_after_days: int) -> list[dict]:
    rows = []
    for source in SOURCES:
        row = dict(source)
        if source["stale_applicable"]:
            verified = date.fromisoformat(source["last_verified"])
            age = (as_of - verified).days
            row["age_days"] = age
            row["stale"] = age > stale_after_days
        else:
            row["age_days"] = None
            row["stale"] = False
        rows.append(row)
    return rows


def _shell(bundle: dict, as_of: str, stale_after_days: int) -> dict:
    try:
        as_of_date = date.fromisoformat(as_of)
        sources = _sources(as_of_date, stale_after_days)
    except ValueError:
        sources = []
    return {
        "label": LABEL,
        "catalogue_id": "G009",
        "experiment": "31",
        "autonomy": "A0",
        "bundle_id": bundle.get("bundle_id"),
        "organisation": bundle.get("organisation") if isinstance(bundle.get("organisation"), str) else "",
        "synthetic": bundle.get("synthetic") is True,
        "as_of": as_of,
        "currency": None,
        "currency_source": "rate_card",
        "rates_validated": False,
        "forecast_validated": False,
        "quota_changed": False,
        "budget_changed": False,
        "subscription_changed": False,
        "actions_taken": [],
        "model_called": False,
        "network_called": False,
        "a3_recommended": False,
        "builtin_rates_used": BUILTIN_RATES is not None,
        "microsoft_prices_used": False,
        "added_rollup": False,
        "priced_tokens_on_credit_agents": "0.0000",
        "do_not_rely": True,
        "refused": False,
        "refusal_reasons": [],
        "agents": [],
        "totals": {
            "cost": None,
            "cost_complete": False,
            "partial_cost": None,
            "partial_cost_is_not_the_total": True,
            "cases": None,
            "unit_cost_per_case": None,
            "copilot_credits": None,
            "agent_rows_used": 0,
            "agent_rows_dropped_as_duplicates": 0,
            "priced_tokens_on_credit_agents": "0.0000",
            "added_rollup": False,
        },
        "forecast": {"validated": False, "do_not_rely": True, "statistical_interval": False, "microsoft_estimate": False},
        "capacity": [],
        "anomalies": [],
        "assumptions": ASSUMPTIONS,
        "prompt_injection": {"detected": False, "followed": False, "patterns": [], "note_withheld": False},
        "prohibited_actions": {"requested": False, "taken": False},
        "sources": sources,
        "rate_card": None,
    }


def _period(bundle: dict) -> tuple[int | None, date | None, dict | None]:
    period = bundle.get("period")
    if not isinstance(period, dict):
        return None, None, _anomaly("invalid_period", "blocker")
    try:
        start = date.fromisoformat(str(period.get("start")))
        end = date.fromisoformat(str(period.get("end")))
    except ValueError:
        return None, None, _anomaly("invalid_period", "blocker")
    if end < start:
        return None, None, _anomaly("invalid_period", "blocker")
    return (end - start).days + 1, end, None


def evaluate(
    bundle: dict,
    rate_card: dict | None,
    *,
    as_of: str,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> dict:
    if BUILTIN_RATES is not None:
        raise RuntimeError("builtin rates are forbidden")
    bundle = copy.deepcopy(bundle)
    rate_card = copy.deepcopy(rate_card) if rate_card is not None else None
    try:
        as_of_date = date.fromisoformat(as_of)
    except ValueError as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc

    inspection = inspect(bundle, rate_card)
    report = _shell(bundle, as_of, stale_after_days)
    report["prompt_injection"] = {
        "detected": inspection["detected"],
        "followed": False,
        "patterns": inspection["patterns"],
        "note_withheld": inspection["note_withheld"],
    }
    report["prohibited_actions"] = {
        "requested": inspection["prohibited_requested"],
        "taken": False,
    }
    anomalies: list[dict] = []
    if inspection["detected"]:
        anomalies.append(_anomaly("prompt_injection", "warning"))
    if inspection["prohibited_requested"]:
        anomalies.append(_anomaly("prohibited_request", "warning"))

    if "rate_card" in bundle:
        anomalies.append(_anomaly("embedded_rate_card_ignored", "warning"))
        del bundle["rate_card"]

    reasons: list[str] = []
    if bundle.get("synthetic") is not True:
        reasons.append("bundle_not_synthetic")
    if rate_card is None:
        reasons.append("rate_card_missing")
    elif rate_card.get("synthetic") is not True:
        reasons.append("rate_card_not_synthetic")
    if reasons:
        report["refused"] = True
        report["refusal_reasons"] = reasons
        report["do_not_rely"] = True
        report["anomalies"] = anomalies + [_anomaly(reason, "blocker") for reason in reasons]
        return report

    assert rate_card is not None
    rates, rate_anomalies, currency = _parse_rate_card(rate_card)
    anomalies.extend(rate_anomalies)
    report["currency"] = currency
    try:
        effective = date.fromisoformat(str(rate_card.get("effective_date")))
    except ValueError:
        report["refused"] = True
        report["refusal_reasons"] = ["rate_card_effective_date_invalid"]
        report["anomalies"] = anomalies + [_anomaly("rate_card_effective_date_invalid", "blocker")]
        return report
    age = (as_of_date - effective).days
    validity = rate_card.get("validity_days")
    validity_days = validity if isinstance(validity, int) and not isinstance(validity, bool) else None
    stale = age > stale_after_days
    future = effective > as_of_date
    report["rate_card"] = {
        "id": rate_card.get("rate_card_id"),
        "effective_date": effective.isoformat(),
        "age_days": age,
        "stale": stale,
        "not_yet_effective": future,
        "validity_days": validity_days,
        "currency": currency,
        "source": "user_supplied_file",
    }
    if stale:
        anomalies.append(_anomaly("rate_card_stale", "warning", age_days=age))
    if future:
        anomalies.append(_anomaly("rate_card_not_yet_effective", "blocker"))
        rates = []

    observed_days, period_end, period_anomaly = _period(bundle)
    if period_anomaly:
        anomalies.append(period_anomaly)

    kept, dedupe_anomalies = dedupe_agents(bundle.get("agents") or [])
    anomalies.extend(dedupe_anomalies)
    dropped = sum(1 for row in dedupe_anomalies if row["id"] == "duplicate_agent_id")

    if future or currency is None:
        priced = []
        for agent in kept:
            row = _empty_agent(agent, incomplete=True)
            row["name"] = agent.get("name") if isinstance(agent.get("name"), str) else ""
            priced.append(row)
        totals = totals_from([])
        totals["agent_rows_used"] = len(priced)
        totals["cost_complete"] = False
        totals["cost"] = None
        totals["partial_cost"] = None
        totals["cases"] = None
        totals["copilot_credits"] = None
        totals["unit_cost_per_case"] = None
    else:
        priced, price_anomalies = price_agents(kept, rates)
        anomalies.extend(price_anomalies)
        totals = totals_from(priced)
        anomalies.extend(compare_rollup(bundle, priced, totals["cost"], totals["copilot_credits"] or "0"))
    for row in priced:
        name = row.get("name")
        if not isinstance(name, str) or hostile(name):
            row["name"] = "[withheld]"
    organisation = report["organisation"]
    if not isinstance(organisation, str) or hostile(organisation):
        report["organisation"] = "[withheld]"
    totals["agent_rows_dropped_as_duplicates"] = dropped

    capacity_block = bundle.get("capacity") if isinstance(bundle.get("capacity"), dict) else {}
    tight = capacity_block.get("headroom_tight_below", DEFAULT_HEADROOM_TIGHT_BELOW)
    if not isinstance(tight, str):
        tight = DEFAULT_HEADROOM_TIGHT_BELOW
    multiple = capacity_block.get("spike_multiple", DEFAULT_SPIKE_MULTIPLE)
    if not isinstance(multiple, str):
        multiple = DEFAULT_SPIKE_MULTIPLE
    quotas = bundle.get("quotas") if isinstance(bundle.get("quotas"), list) else []
    if not future and currency is not None:
        capacity_rows, capacity_anomalies = headroom(quotas, priced, kept, str(tight))
        anomalies.extend(capacity_anomalies)
        anomalies.extend(spikes(priced, str(multiple)))
    else:
        capacity_rows = []

    forecast = build_forecast(
        bundle=bundle,
        cost=totals["cost"],
        cases=totals["cases"],
        period_end=period_end,
        observed_days=observed_days,
        effective=effective,
        validity_days=validity_days,
        cost_complete=bool(totals["cost_complete"]) and not future,
    )
    if stale or future:
        forecast["do_not_rely"] = True

    source_stale = any(row["stale"] for row in report["sources"])
    report["agents"] = priced
    report["totals"] = totals
    report["priced_tokens_on_credit_agents"] = totals["priced_tokens_on_credit_agents"]
    report["added_rollup"] = False
    report["forecast"] = forecast
    report["capacity"] = capacity_rows
    report["anomalies"] = anomalies
    report["do_not_rely"] = bool(
        stale
        or future
        or source_stale
        or forecast["do_not_rely"]
        or not totals["cost_complete"]
        or inspection["detected"]
        or inspection["prohibited_requested"]
    )
    report["rates_validated"] = False
    report["forecast_validated"] = False
    report["quota_changed"] = False
    report["budget_changed"] = False
    report["subscription_changed"] = False
    report["prohibited_actions"]["taken"] = False
    report["prompt_injection"]["followed"] = False
    return report


def _refuse_flag(argv: list[str]) -> int | None:
    for flag, function in PROHIBITED_FLAGS.items():
        if flag in argv:
            try:
                function()
            except ProhibitedAction as exc:
                print(str(exc), file=sys.stderr)
                return 2
    return None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    refused = _refuse_flag(argv)
    if refused is not None:
        return refused
    parser = argparse.ArgumentParser(description="Draft an agent cost and capacity report.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--rate-card", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    rate_card = json.loads(Path(args.rate_card).read_text(encoding="utf-8"))
    try:
        report = evaluate(
            bundle,
            rate_card,
            as_of=args.as_of,
            stale_after_days=args.stale_after_days,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
