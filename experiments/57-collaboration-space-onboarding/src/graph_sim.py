"""A simulated Microsoft Graph membership call. No network.

The paths and the permission names are the ones on the Graph v1.0 pages
opened on 16 November 2026. The sample does not send the request and does
not receive the documented 204 response.
"""

from __future__ import annotations


class OnboardingForbidden(RuntimeError):
    """A side effect this agent does not have."""


def share_file_external(*_args, **_kwargs) -> None:
    raise OnboardingForbidden("share_file_external is not a tool of this agent")


def share_link_external(*_args, **_kwargs) -> None:
    raise OnboardingForbidden("share_link_external is not a tool of this agent")


def grant_owner_without_approval(*_args, **_kwargs) -> None:
    raise OnboardingForbidden("owner rights require the workspace owner's approval object")


def add_guest_without_approval(*_args, **_kwargs) -> None:
    raise OnboardingForbidden("guest access requires the workspace owner's approval object")


def call_live_graph(*_args, **_kwargs) -> None:
    raise OnboardingForbidden("live Microsoft Graph is not a tool of this agent")


def simulate_membership(*, owner: bool) -> dict:
    """Return the call the sample would make. Nothing is sent."""

    calls = [
        {
            "method": "POST",
            "path": "/groups/{group-id}/members/$ref",
            "permission_named_on_learn": "GroupMember.ReadWrite.All",
            "documented_success_status": 204,
            "status_received": None,
            "simulated": True,
            "live_graph_called": False,
        }
    ]
    if owner:
        calls.append(
            {
                "method": "POST",
                "path": "/groups/{id}/owners/$ref",
                "permission_named_on_learn": "Group.ReadWrite.All",
                "documented_success_status": 204,
                "status_received": None,
                "simulated": True,
                "live_graph_called": False,
                "owner_also_added_as_member_in_this_sample": True,
                "teams_sync_delay_stated_on_learn": "up to 2 hours",
            }
        )
    return {
        "simulated": True,
        "live_graph_called": False,
        "network_called": False,
        "calls": calls,
        "note": (
            "Sample only. Microsoft Graph documents 204 No Content for a "
            "successful add. This sample did not receive that response."
        ),
    }
