"""No digest until the requesting user confirms the channels and the period."""

import json

from digest import run
from support import bundle, message, review


def test_preview_does_not_digest_or_copy_message_text():
    export = bundle([message("SYN-MSG-1", "We decided to keep Saturday library hours.")])
    preview = run(export, "2026-11-12")
    assert preview["outcome"] == "scope_only"
    assert preview["digest_produced"] is False
    assert preview["digest"] is None
    assert preview["human_approval"] is None
    assert preview["scope_confirmed"] is False
    assert preview["graph_called"] is False
    assert preview["network_called"] is False
    blob = json.dumps(preview)
    assert "Saturday library hours" not in blob
    assert preview["channels"][0]["message_count_in_period"] == 1
    assert preview["channels"][0]["status"] == "ready"


def test_inaccessible_channel_is_not_read():
    channels = [
        {
            "channel_id": "SYN-CH-CABINET",
            "display_name": "Cabinet forward plan",
            "available": True,
            "messages": [message("SYN-MSG-1", "We decided to keep the hours.")],
        },
        {
            "channel_id": "SYN-CH-FINANCE",
            "display_name": "Finance SMT",
            "available": True,
            "messages": [message("SYN-MSG-X", "CANARY-LOCK-CHANNEL-51")],
        },
    ]
    export = bundle(
        channels=channels,
        requested=["SYN-CH-CABINET", "SYN-CH-FINANCE"],
        accessible=["SYN-CH-CABINET"],
    )
    preview = run(export, "2026-11-12")
    finance = preview["channels"][1]
    assert finance["status"] == "not_accessible"
    assert finance["message_count_in_period"] is None
    assert "CANARY-LOCK-CHANNEL-51" not in json.dumps(preview)
    refused = run(export, "2026-11-12", review(["SYN-CH-CABINET", "SYN-CH-FINANCE"], not_accessible_seen=True))
    assert refused["digest_produced"] is False
    assert refused["scope_confirmation"]["reason"] == "channel_not_readable"
    assert "CANARY-LOCK-CHANNEL-51" not in json.dumps(refused)


def test_unavailable_source_is_stated_and_not_invented():
    channels = [
        {
            "channel_id": "SYN-CH-ARCHIVE",
            "display_name": "Closed archive",
            "available": False,
            "messages": [message("SYN-MSG-Y", "CANARY-DARK-CHANNEL-51")],
        }
    ]
    export = bundle(channels=channels, accessible=["SYN-CH-ARCHIVE"])
    preview = run(export, "2026-11-12")
    row = preview["channels"][0]
    assert row["status"] == "source_unavailable"
    assert row["message_count_in_period"] is None
    assert "unavailable" in row["statement"].lower()
    assert "CANARY-DARK-CHANNEL-51" not in json.dumps(preview)


def test_empty_period_is_stated():
    export = bundle([])
    preview = run(export, "2026-11-12")
    assert preview["channels"][0]["status"] == "no_messages_in_period"
    assert preview["channels"][0]["statement"] == "No messages in this period."
    refused = run(export, "2026-11-12", review())
    assert refused["digest_produced"] is False
    assert refused["scope_confirmation"]["reason"] == "empty_period_not_acknowledged"
    produced = run(export, "2026-11-12", review(empty_period_seen=True))
    assert produced["digest_produced"] is True
    assert produced["digest"]["decisions"] == []
    assert produced["digest"]["channels"][0]["statement"] == "No messages in this period."


def test_message_outside_the_period_is_not_copied():
    export = bundle(
        [
            message("SYN-MSG-OLD", "We decided to paint the CANARY-OLD-PERIOD-51 hall.", "2026-10-01"),
            message("SYN-MSG-1", "We decided to keep Saturday library hours."),
        ]
    )
    produced = run(export, "2026-11-12", review())
    texts = [row["text"] for row in produced["digest"]["decisions"]]
    assert texts == ["We decided to keep Saturday library hours."]
    assert "CANARY-OLD-PERIOD-51" not in json.dumps(produced)


def test_not_synthetic_is_refused_without_the_text():
    export = bundle([message("SYN-MSG-1", "CANARY-REAL-51")], synthetic=False)
    refused = run(export, "2026-11-12", review())
    assert refused["outcome"] == "refused"
    assert refused["refusal"]["reason"] == "not_synthetic"
    assert refused["digest_produced"] is False
    assert "CANARY-REAL-51" not in json.dumps(refused)
    assert refused["human_route"]["offered"] is True
