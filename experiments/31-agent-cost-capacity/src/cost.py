"""Price agents from a caller-supplied rate card. No built-in prices.

The period total is the sum of the kept agent rows. A rollup is not added.
Token quantities on a Copilot Studio row are not priced again unless the
rate line says additive. Foundry token fields are used once.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

try:
    from .money import InexactNumber, money, parse_decimal, quantity, unit
except ImportError:  # python src/report.py puts this directory on sys.path
    from money import InexactNumber, money, parse_decimal, quantity, unit

# There is no built-in rate table. Tests fail if this stops being None.
BUILTIN_RATES = None

STUDIO = (
    "copilot_studio_standard",
    "copilot_studio_github_copilot_harness",
)
FOUNDRY = "microsoft_foundry"
KNOWN_PLATFORMS = STUDIO + (FOUNDRY,)
CREDIT = "copilot_credits"
TOKEN_METERS = ("input_tokens", "output_tokens")
USAGE_METERS = ("tool_calls", "conversations")
KNOWN_METERS = (CREDIT,) + TOKEN_METERS + USAGE_METERS
_TOKEN_SIDE = {"input_tokens": "input", "output_tokens": "output"}


def _anomaly(anomaly_id: str, severity: str, **detail: Any) -> dict:
    row = {"id": anomaly_id, "severity": severity}
    row.update(detail)
    return row


def _parse_rate_card(rate_card: dict) -> tuple[list[dict], list[dict], str | None]:
    anomalies: list[dict] = []
    currency = rate_card.get("currency")
    if not isinstance(currency, str) or len(currency) != 3 or not currency.isalpha():
        anomalies.append(_anomaly("currency_missing", "blocker"))
        currency = None
    else:
        currency = currency.upper()
    parsed: list[dict] = []
    seen_ids: set[str] = set()
    for raw in rate_card.get("rates") or []:
        if not isinstance(raw, dict):
            anomalies.append(_anomaly("rate_line_ignored", "warning"))
            continue
        rate_id = str(raw.get("rate_id") or "")
        meter = raw.get("meter")
        if meter not in KNOWN_METERS:
            anomalies.append(_anomaly("unrecognised_meter", "warning", rate_id=rate_id, meter=str(meter)))
            continue
        if rate_id and rate_id in seen_ids:
            anomalies.append(_anomaly("duplicate_rate_id", "warning", rate_id=rate_id))
            continue
        if rate_id:
            seen_ids.add(rate_id)
        line_currency = raw.get("currency")
        if isinstance(line_currency, str) and currency and line_currency.upper() != currency:
            anomalies.append(_anomaly("mixed_currency", "blocker", rate_id=rate_id))
            continue
        try:
            price = parse_decimal(raw.get("price_per_unit"))
        except InexactNumber:
            anomalies.append(_anomaly("non_exact_number", "blocker", rate_id=rate_id, field="price_per_unit"))
            continue
        if price < 0:
            anomalies.append(_anomaly("negative_rate", "blocker", rate_id=rate_id))
            continue
        unit_name = raw.get("unit")
        if unit_name not in {"credit", "token", "1000_tokens", "call", "conversation", "case"}:
            anomalies.append(_anomaly("unrecognised_unit", "warning", rate_id=rate_id))
            continue
        if price == 0:
            anomalies.append(_anomaly("zero_rate", "info", rate_id=rate_id))
        parsed.append(
            {
                "rate_id": rate_id,
                "meter": meter,
                "platform": raw.get("platform") or "*",
                "unit": unit_name,
                "price": price,
                "additive": raw.get("additive") is True,
                "model_deployment": raw.get("model_deployment") or None,
            }
        )
    return parsed, anomalies, currency


def _matches(rate: dict, platform: str, meter: str, model: str | None) -> bool:
    if rate["meter"] != meter:
        return False
    if meter == CREDIT and platform == FOUNDRY:
        return False
    if rate["platform"] != "*" and rate["platform"] != platform:
        return False
    named = rate["model_deployment"]
    if named and named != model:
        return False
    return True


def _amount(qty: Decimal, rate: dict) -> Decimal:
    if rate["unit"] == "1000_tokens":
        return (qty / Decimal(1000)) * rate["price"]
    return qty * rate["price"]


def _token_quantity(agent: dict, meter: str) -> tuple[Decimal | None, str | None]:
    side = _TOKEN_SIDE[meter]
    tokens = agent.get("tokens") if isinstance(agent.get("tokens"), dict) else {}
    foundry = agent.get("foundry_usage") if isinstance(agent.get("foundry_usage"), dict) else {}
    top = tokens.get(side) if side in tokens else None
    other_key = f"{side}_tokens"
    other = foundry.get(other_key) if other_key in foundry else None
    present = [value for value in (top, other) if value is not None]
    if not present:
        return Decimal(0), None
    try:
        parsed = [parse_decimal(value) for value in present]
    except InexactNumber:
        return None, "non_exact_number"
    if any(value < 0 for value in parsed):
        return None, "negative_quantity"
    if len(parsed) == 2 and parsed[0] != parsed[1]:
        return None, "token_fields_disagree"
    return parsed[0], None


def _simple_quantity(agent: dict, field: str) -> tuple[Decimal | None, str | None]:
    if field not in agent or agent.get(field) is None:
        return None, "quantity_missing"
    try:
        parsed = parse_decimal(agent.get(field))
    except InexactNumber:
        return None, "non_exact_number"
    if parsed < 0:
        return None, "negative_quantity"
    return parsed, None


def _usage(agent: dict, meter: str) -> tuple[Decimal | None, str | None]:
    if meter in TOKEN_METERS:
        return _token_quantity(agent, meter)
    if meter == CREDIT:
        return _simple_quantity(agent, "copilot_credits")
    if meter == "tool_calls":
        if "tool_calls" not in agent or agent.get("tool_calls") is None:
            return Decimal(0), None
        return _simple_quantity(agent, "tool_calls")
    if meter == "conversations":
        if "conversations" not in agent or agent.get("conversations") is None:
            return Decimal(0), None
        return _simple_quantity(agent, "conversations")
    return None, "unrecognised_meter"


def _billable(platform: str, meter: str, rate: dict | None) -> bool:
    if platform in STUDIO and meter == CREDIT:
        return True
    if platform == FOUNDRY and meter in TOKEN_METERS:
        return True
    return bool(rate and rate["additive"])


def price_agents(agents: list[dict], rates: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return priced rows and anomalies. Does not read a rollup."""
    anomalies: list[dict] = []
    priced: list[dict] = []
    for agent in agents:
        platform = agent.get("platform")
        agent_id = str(agent.get("agent_id") or "")
        model = None
        foundry = agent.get("foundry_usage") if isinstance(agent.get("foundry_usage"), dict) else {}
        model = foundry.get("model_deployment") or agent.get("model_deployment")
        if platform not in KNOWN_PLATFORMS:
            anomalies.append(_anomaly("unknown_platform", "blocker", agent_id=agent_id))
            priced.append(_empty_agent(agent, incomplete=True))
            continue
        components: list[dict] = []
        applied_sum = Decimal(0)
        incomplete = False
        credits_value, credits_problem = _usage(agent, CREDIT)
        if platform == FOUNDRY and credits_value is not None and credits_value > 0:
            anomalies.append(_anomaly("credits_on_foundry_ignored", "warning", agent_id=agent_id))
        meters = [CREDIT, *TOKEN_METERS, *USAGE_METERS]
        for meter in meters:
            quantity_value, problem = _usage(agent, meter)
            if problem == "quantity_missing" and not (platform in STUDIO and meter == CREDIT):
                quantity_value = Decimal(0)
                problem = None
            if problem == "token_fields_disagree":
                anomalies.append(_anomaly("token_fields_disagree", "blocker", agent_id=agent_id, meter=meter))
                incomplete = True
                components.append(
                    {"meter": meter, "applied": False, "reason": "token_fields_disagree", "quantity": None}
                )
                continue
            if problem in {"non_exact_number", "negative_quantity"}:
                anomalies.append(_anomaly(problem, "blocker", agent_id=agent_id, meter=meter))
                incomplete = True
                components.append({"meter": meter, "applied": False, "reason": problem, "quantity": None})
                continue
            if problem == "quantity_missing":
                anomalies.append(_anomaly("rate_missing", "blocker", agent_id=agent_id, meter=meter))
                incomplete = True
                components.append({"meter": meter, "applied": False, "reason": "quantity_missing", "quantity": None})
                continue
            assert quantity_value is not None
            matching = [rate for rate in rates if _matches(rate, platform, meter, model)]
            billable_without_rate = (platform in STUDIO and meter == CREDIT) or (
                platform == FOUNDRY and meter in TOKEN_METERS
            )
            if billable_without_rate and quantity_value > 0 and not matching:
                anomalies.append(_anomaly("rate_missing", "blocker", agent_id=agent_id, meter=meter))
                incomplete = True
                components.append(
                    {
                        "meter": meter,
                        "applied": False,
                        "reason": "rate_missing",
                        "quantity": quantity(quantity_value),
                    }
                )
                continue
            if billable_without_rate and len(matching) > 1 and quantity_value > 0:
                anomalies.append(_anomaly("ambiguous_rate", "blocker", agent_id=agent_id, meter=meter))
                incomplete = True
                components.append(
                    {
                        "meter": meter,
                        "applied": False,
                        "reason": "ambiguous_rate",
                        "quantity": quantity(quantity_value),
                        "rate_ids": [rate["rate_id"] for rate in matching],
                    }
                )
                continue
            chosen = matching[0] if len(matching) == 1 else None
            if chosen is None or not _billable(platform, meter, chosen):
                reason = "not_the_billed_meter"
                if platform == FOUNDRY and meter == CREDIT:
                    reason = "foundry_not_priced_in_copilot_credits"
                components.append(
                    {
                        "meter": meter,
                        "applied": False,
                        "reason": reason,
                        "quantity": quantity(quantity_value),
                        "rate_ids_not_applied": [rate["rate_id"] for rate in matching],
                    }
                )
                continue
            if chosen["additive"] and not billable_without_rate:
                anomalies.append(
                    _anomaly("additive_line_applied", "warning", agent_id=agent_id, meter=meter, rate_id=chosen["rate_id"])
                )
            amount = parse_decimal(money(_amount(quantity_value, chosen)))
            applied_sum += amount
            components.append(
                {
                    "meter": meter,
                    "applied": True,
                    "reason": "additive" if chosen["additive"] and not billable_without_rate else "billed_meter",
                    "quantity": quantity(quantity_value),
                    "rate_id": chosen["rate_id"],
                    "price_per_unit": money(chosen["price"]),
                    "amount": money(amount),
                }
            )
        if "cases" not in agent or agent.get("cases") is None:
            cases, cases_problem = None, "quantity_missing"
        else:
            cases, cases_problem = _simple_quantity(agent, "cases")
        if cases_problem in {"non_exact_number", "negative_quantity"}:
            anomalies.append(_anomaly(cases_problem, "blocker", agent_id=agent_id, meter="cases"))
            incomplete = True
            cases = None
        elif cases_problem == "quantity_missing":
            cases = None
        cost = None if incomplete else money(applied_sum)
        unit_cost = None
        if cost is not None and cases is not None and cases > 0:
            unit_cost = unit(applied_sum / cases)
        elif cost is not None and (cases is None or cases == 0):
            anomalies.append(_anomaly("zero_cases", "info", agent_id=agent_id))
        row = _empty_agent(agent, incomplete=incomplete)
        row["cost"] = cost
        row["cost_complete"] = not incomplete
        row["cases"] = quantity(cases) if cases is not None else None
        row["unit_cost_per_case"] = unit_cost
        row["components"] = components
        row["model_deployment"] = model
        priced.append(row)
    return priced, anomalies


def _empty_agent(agent: dict, incomplete: bool) -> dict:
    return {
        "agent_id": str(agent.get("agent_id") or ""),
        "name": agent.get("name") if isinstance(agent.get("name"), str) else "",
        "platform": agent.get("platform"),
        "cost": None,
        "cost_complete": not incomplete,
        "cases": None,
        "unit_cost_per_case": None,
        "components": [],
        "model_deployment": None,
    }


def dedupe_agents(agents: list[dict]) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    seen: set[str] = set()
    anomalies: list[dict] = []
    for index, agent in enumerate(agents):
        if not isinstance(agent, dict):
            anomalies.append(_anomaly("agent_row_ignored", "warning", index=index))
            continue
        agent_id = str(agent.get("agent_id") or "")
        if not agent_id:
            anomalies.append(_anomaly("missing_agent_id", "warning", index=index))
            continue
        if agent_id in seen:
            anomalies.append(_anomaly("duplicate_agent_id", "warning", agent_id=agent_id, index=index))
            continue
        seen.add(agent_id)
        kept.append(agent)
    return kept, anomalies


def totals_from(priced: list[dict]) -> dict:
    complete = [row for row in priced if row["cost_complete"] and row["cost"] is not None]
    partial = sum((parse_decimal(row["cost"]) for row in complete), Decimal(0))
    all_complete = len(complete) == len(priced) and len(priced) > 0
    cases = Decimal(0)
    cases_ok = True
    credits = Decimal(0)
    token_amounts_on_studio = Decimal(0)
    for row in priced:
        if row["cases"] is not None:
            cases += parse_decimal(row["cases"])
        elif row["cost_complete"]:
            cases_ok = False
        for component in row["components"]:
            if not component.get("applied"):
                continue
            if row["platform"] in STUDIO and component["meter"] in TOKEN_METERS:
                token_amounts_on_studio += parse_decimal(component["amount"])
            if component["meter"] == CREDIT and row["platform"] in STUDIO:
                credits += parse_decimal(component["quantity"])
    cost = money(partial) if all_complete else None
    unit_cost = None
    if cost is not None and cases_ok and cases > 0:
        unit_cost = unit(partial / cases)
    return {
        "cost": cost,
        "cost_complete": all_complete,
        "partial_cost": money(partial),
        "partial_cost_is_not_the_total": not all_complete,
        "cases": quantity(cases),
        "unit_cost_per_case": unit_cost,
        "copilot_credits": quantity(credits),
        "agent_rows_used": len(priced),
        "priced_tokens_on_credit_agents": money(token_amounts_on_studio),
        "added_rollup": False,
    }


def compare_rollup(bundle: dict, priced: list[dict], total_cost: str | None, credit_total: str) -> list[dict]:
    rollup = bundle.get("period_rollup")
    if not isinstance(rollup, dict) or not rollup:
        return []
    anomalies: list[dict] = []
    if "copilot_credits" in rollup:
        try:
            stated = parse_decimal(rollup.get("copilot_credits"))
        except InexactNumber:
            anomalies.append(_anomaly("rollup_disagrees", "warning", meter=CREDIT, reason="non_exact_number"))
        else:
            if stated != parse_decimal(credit_total):
                anomalies.append(_anomaly("rollup_disagrees", "warning", meter=CREDIT))
    if "cost" in rollup and total_cost is not None:
        try:
            stated_cost = parse_decimal(rollup.get("cost"))
        except InexactNumber:
            anomalies.append(_anomaly("rollup_disagrees", "warning", meter="cost", reason="non_exact_number"))
        else:
            if stated_cost != parse_decimal(total_cost):
                anomalies.append(_anomaly("rollup_disagrees", "warning", meter="cost"))
    return anomalies


def usage_for_quota(agent_row: dict, source_agent: dict, meter: str) -> Decimal:
    """Quantity once. source_agent is the deduped input row."""
    if meter == CREDIT:
        if agent_row["platform"] not in STUDIO:
            return Decimal(0)
        value, problem = _usage(source_agent, CREDIT)
        if problem or value is None:
            return Decimal(0)
        return value
    value, problem = _usage(source_agent, meter)
    if problem or value is None:
        return Decimal(0)
    return value
