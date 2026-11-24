"""Structured eligibility. A gap stays a gap.

Checks use the pinned charity profile and the pinned monitoring rows.
A sentence in the request cannot turn a gap into a met criterion.
"""

from __future__ import annotations

from datetime import date

if __package__ in {None, ""}:
    from dates import as_date, parse_date, subtract_months
else:
    from .dates import as_date, parse_date, subtract_months


def _row(criterion_id: str, status: str, *, source_ref: str | None, gap: bool, **extra) -> dict:
    payload = {
        "criterion_id": criterion_id,
        "status": status,
        "source_ref": source_ref,
        "gap": gap,
        "coerced": False,
        "papered_over": False,
    }
    payload.update(extra)
    return payload


def _registered(charity: dict) -> dict:
    registered = charity.get("registered_england_wales")
    jurisdiction = charity.get("jurisdiction")
    source = "charity.registered_england_wales"
    if registered is True and jurisdiction == "England and Wales":
        return _row("EL-REG", "met", source_ref=source, gap=False, jurisdiction=jurisdiction)
    if registered is False or (isinstance(jurisdiction, str) and jurisdiction != "England and Wales"):
        return _row("EL-REG", "not_met", source_ref=source, gap=True, jurisdiction=jurisdiction)
    return _row("EL-REG", "unreadable", source_ref=source, gap=True, jurisdiction=None)


def _income(charity: dict, brief: dict) -> dict:
    value = charity.get("income_gbp")
    threshold = brief.get("income_under_gbp")
    source = "charity.income_gbp"
    if type(value) is not int or type(threshold) is not int:
        return _row(
            "EL-INC",
            "unreadable",
            source_ref=source,
            gap=True,
            value=None,
            threshold_gbp=None,
        )
    met = value < threshold
    return _row(
        "EL-INC",
        "met" if met else "not_met",
        source_ref=source,
        gap=not met,
        value=value,
        threshold_gbp=threshold,
        income_year=charity.get("income_year") if isinstance(charity.get("income_year"), str) else None,
    )


def _area(charity: dict, brief: dict) -> dict:
    required = brief.get("required_area")
    areas = charity.get("area")
    source = "charity.area"
    if not isinstance(required, str) or not isinstance(areas, list):
        return _row("EL-AREA", "unreadable", source_ref=source, gap=True, area=None)
    names = [item for item in areas if isinstance(item, str)]
    if len(names) != len(areas):
        return _row("EL-AREA", "unreadable", source_ref=source, gap=True, area=None)
    met = required in names
    return _row(
        "EL-AREA",
        "met" if met else "not_met",
        source_ref=source,
        gap=not met,
        area=required if met else None,
    )


def _safeguarding(charity: dict, deadline: date | None) -> dict:
    source = "charity.safeguarding_policy_date"
    reading = parse_date(charity.get("safeguarding_policy_date"))
    policy = as_date(reading)
    if deadline is None or policy is None:
        return _row(
            "EL-SAFE",
            "unreadable",
            source_ref=source,
            gap=True,
            policy_date=reading.get("iso"),
            ambiguous=reading.get("ambiguous") is True,
        )
    window = subtract_months(deadline, 12)
    start = date.fromisoformat(window["date"]) if window.get("date") else None
    if start is None:
        return _row("EL-SAFE", "unreadable", source_ref=source, gap=True, policy_date=None)
    met = start <= policy <= deadline
    return _row(
        "EL-SAFE",
        "met" if met else "not_met",
        source_ref=source,
        gap=not met,
        policy_date=policy.isoformat(),
        window_start=start.isoformat(),
        deadline=deadline.isoformat(),
        months=12,
        note="Twelve months is the window written in the pinned brief. It is not a statutory period.",
    )


def _match(charity: dict, brief: dict) -> dict:
    source = "charity.match_funding_available"
    flag = charity.get("match_funding_available")
    percent = charity.get("match_funding_percent")
    minimum = brief.get("match_funding_minimum_percent")
    if flag is False:
        return _row("EL-MATCH", "not_met", source_ref=source, gap=True, percent=None)
    if flag is not True or type(minimum) is not int:
        return _row("EL-MATCH", "unreadable", source_ref=source, gap=True, percent=None)
    if type(percent) is not int:
        return _row("EL-MATCH", "unreadable", source_ref=source, gap=True, percent=None)
    met = percent >= minimum
    return _row(
        "EL-MATCH",
        "met" if met else "not_met",
        source_ref=source,
        gap=not met,
        percent=percent,
        minimum_percent=minimum,
    )


def _outcomes(rows: list[dict]) -> dict:
    evidenced = []
    for row in rows:
        if row.get("kind") == "outcome" and type(row.get("value")) is int and isinstance(row.get("row_id"), str):
            evidenced.append(row["row_id"])
    if evidenced:
        return _row("EL-OUT", "met", source_ref=evidenced[0], gap=False, source_refs=evidenced)
    return _row("EL-OUT", "not_met", source_ref=None, gap=True, source_refs=[])


def _not_party(charity: dict) -> dict:
    source = "charity.political_party"
    flag = charity.get("political_party")
    kind = charity.get("organisation_type")
    if flag is False and kind == "charity":
        return _row("EL-NOT-PARTY", "met", source_ref=source, gap=False)
    if flag is True:
        return _row("EL-NOT-PARTY", "not_met", source_ref=source, gap=True)
    return _row("EL-NOT-PARTY", "unreadable", source_ref=source, gap=True)


def assess(charity: dict, brief: dict, rows: list[dict], deadline: date | None) -> list[dict]:
    return [
        _registered(charity),
        _income(charity, brief),
        _area(charity, brief),
        _safeguarding(charity, deadline),
        _match(charity, brief),
        _outcomes(rows),
        _not_party(charity),
    ]
