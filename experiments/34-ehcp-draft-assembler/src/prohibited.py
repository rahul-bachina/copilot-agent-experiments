"""Actions this starter cannot take. Calling one raises. Nothing is written."""

from __future__ import annotations


class ProhibitedAction(Exception):
    """The caller asked for a decision or a send this tool does not have."""


def decide_needs(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The caseworker decides needs. This tool does not.")


def decide_provision(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The caseworker decides provision. This tool does not.")


def decide_placement(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The caseworker decides placement. This tool does not.")


def decide_outcomes(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The caseworker decides outcomes. This tool does not.")


def edit_final_plan(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("The caseworker authors the final plan. This tool does not edit it.")


def send_to_parents(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("This tool does not send anything to parents.")


def send_to_school(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("This tool does not send anything to a school.")


def write_to_la_system(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("This tool does not write to a local authority system.")


def secure_provision(*_args: object, **_kwargs: object) -> None:
    raise ProhibitedAction("Section 42 is the local authority's duty. This tool does not secure provision.")


PROHIBITED_FLAGS = {
    "--decide-needs": decide_needs,
    "--decide-provision": decide_provision,
    "--decide-placement": decide_placement,
    "--decide-outcomes": decide_outcomes,
    "--edit-final-plan": edit_final_plan,
    "--send-to-parents": send_to_parents,
    "--send-to-school": send_to_school,
    "--write-la-system": write_to_la_system,
    "--secure-provision": secure_provision,
}
