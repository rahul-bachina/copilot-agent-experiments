"""A straight-line forecast. The band is a caller fraction, not an interval."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

try:
    from .money import InexactNumber, money, parse_decimal, quantity
    from .sources import DEFAULT_FORECAST_BAND
except ImportError:  # python src/report.py puts this directory on sys.path
    from money import InexactNumber, money, parse_decimal, quantity
    from sources import DEFAULT_FORECAST_BAND


def _flag(anomaly_id: str, severity: str) -> dict:
    return {"id": anomaly_id, "severity": severity}


def build_forecast(
    *,
    bundle: dict,
    cost: str | None,
    cases: str | None,
    period_end: date | None,
    observed_days: int | None,
    effective: date | None,
    validity_days: int | None,
    cost_complete: bool,
) -> dict:
    raw = bundle.get("forecast") if isinstance(bundle.get("forecast"), dict) else {}
    band_source = "caller"
    band_raw = raw.get("band", DEFAULT_FORECAST_BAND)
    if "band" not in raw:
        band_source = "starter_default"
    flags: list[dict] = []
    try:
        band = parse_decimal(band_raw)
    except InexactNumber:
        band = None
    if band is None or band < 0 or band > 1:
        flags.append(_flag("forecast_band_invalid", "blocker"))
        band = None
    horizon = raw.get("horizon_days")
    horizon_days = horizon if isinstance(horizon, int) and not isinstance(horizon, bool) and horizon > 0 else None
    if horizon_days is None:
        flags.append(_flag("forecast_horizon_missing", "warning"))
    coverage_end = None
    horizon_end = None
    if effective is not None and isinstance(validity_days, int) and not isinstance(validity_days, bool) and validity_days > 0:
        coverage_end = effective + timedelta(days=validity_days)
    else:
        flags.append(_flag("forecast_validity_unspecified", "warning"))
    if period_end is not None and horizon_days is not None:
        horizon_end = period_end + timedelta(days=horizon_days)
    if coverage_end is not None and horizon_end is not None and horizon_end > coverage_end:
        flags.append(_flag("forecast_rate_uncovered", "warning"))
    point = low = high = cases_point = None
    if (
        cost is not None
        and cost_complete
        and band is not None
        and observed_days
        and horizon_days
        and cases is not None
    ):
        observed = Decimal(observed_days)
        horizon_dec = Decimal(horizon_days)
        point_dec = parse_decimal(cost) * horizon_dec / observed
        point = money(point_dec)
        low = money(point_dec * (Decimal(1) - band))
        high = money(point_dec * (Decimal(1) + band))
        cases_point = quantity(parse_decimal(cases) * horizon_dec / observed)
    else:
        flags.append(_flag("forecast_incomplete", "warning"))
    do_not_rely = any(
        row["id"] in {"forecast_rate_uncovered", "forecast_validity_unspecified", "forecast_incomplete", "forecast_band_invalid"}
        for row in flags
    )
    return {
        "point": point,
        "low": low,
        "high": high,
        "band": money(band) if band is not None else None,
        "band_source": band_source,
        "observed_days": observed_days,
        "horizon_days": horizon_days,
        "cases_point": cases_point,
        "do_not_rely": do_not_rely or not cost_complete,
        "statistical_interval": False,
        "microsoft_estimate": False,
        "coverage_end": coverage_end.isoformat() if coverage_end else None,
        "horizon_end": horizon_end.isoformat() if horizon_end else None,
        "flags": flags,
        "validated": False,
    }
