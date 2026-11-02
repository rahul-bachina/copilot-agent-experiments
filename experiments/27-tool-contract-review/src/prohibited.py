"""Actions this reviewer does not take.

Calling one of these functions is a mistake. Each one raises. None of them
writes a file, publishes a policy, or records an approval.
"""

from __future__ import annotations


class ProhibitedAction(RuntimeError):
    """The reviewer was asked to approve, apply, publish, or deploy."""


def record_owner_approval(*_args, **_kwargs) -> None:
    raise ProhibitedAction(
        "The security/API owner approves the contract. This reviewer cannot record that approval."
    )


def apply_contract_diff(*_args, **_kwargs) -> None:
    raise ProhibitedAction("The reviewer cannot apply a contract diff.")


def publish_policy(*_args, **_kwargs) -> None:
    raise ProhibitedAction("The reviewer cannot publish an API Management policy.")


def deploy_contract(*_args, **_kwargs) -> None:
    raise ProhibitedAction("The reviewer cannot deploy a contract.")
