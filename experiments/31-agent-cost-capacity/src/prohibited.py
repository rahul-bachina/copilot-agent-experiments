"""Actions this starter cannot take. Calling one raises. Nothing is written."""

from __future__ import annotations


class ProhibitedAction(Exception):
    """The caller asked for a control this tool does not have."""


def validate_rates(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The FinOps owner validates rates. This tool does not.")


def validate_forecast(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The FinOps owner validates the forecast. This tool does not.")


def change_quota(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("This tool does not change a quota.")


def change_budget(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("This tool does not change a budget.")


def change_subscription(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("This tool does not change a subscription.")


PROHIBITED_FLAGS = {
    "--validate-rates": validate_rates,
    "--validate-forecast": validate_forecast,
    "--change-quota": change_quota,
    "--change-budget": change_budget,
    "--change-subscription": change_subscription,
}
