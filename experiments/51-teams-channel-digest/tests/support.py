"""Synthetic bundles for the tests. Northmere Borough Council is invented."""

from __future__ import annotations


def message(message_id: str, body: str, sent_on: str = "2026-11-03", **extra) -> dict:
    row = {
        "message_id": message_id,
        "sent_on": sent_on,
        "author_display_name": "Alex Wren",
        "body": body,
    }
    row.update(extra)
    return row


def bundle(
    messages: list[dict] | None = None,
    *,
    channels: list[dict] | None = None,
    requested: list[str] | None = None,
    accessible: list[str] | None = None,
    period: tuple[str, str] = ("2026-11-01", "2026-11-12"),
    retrieved_on: str = "2026-11-10",
    synthetic: bool = True,
    display_name: str = "Rowan Hale",
    sector: str = "public_body",
    export_id: str = "SYN-EXP-051",
) -> dict:
    if channels is None:
        channels = [
            {
                "channel_id": "SYN-CH-CABINET",
                "display_name": "Cabinet forward plan",
                "available": True,
                "messages": messages or [],
            }
        ]
    if accessible is None:
        accessible = [row["channel_id"] for row in channels if row.get("available") is True]
    if requested is None:
        requested = [row["channel_id"] for row in channels]
    return {
        "synthetic": synthetic,
        "organisation": "Northmere Borough Council",
        "sector": sector,
        "export_id": export_id,
        "retrieved_on": retrieved_on,
        "requesting_user": {
            "user_id": "SYN-USER-051",
            "display_name": display_name,
            "accessible_channel_ids": accessible,
        },
        "request": {
            "channel_ids": requested,
            "period_start": period[0],
            "period_end": period[1],
        },
        "channels": channels,
    }


def review(channel_ids: list[str] | None = None, **flags) -> dict:
    row = {
        "decision": "confirm_channels_and_period",
        "actor_role": "Requesting user",
        "actor_id": "SYN-USER-051",
        "export_id": "SYN-EXP-051",
        "channel_ids": channel_ids or ["SYN-CH-CABINET"],
        "period_start": "2026-11-01",
        "period_end": "2026-11-12",
    }
    row.update(flags)
    return row
