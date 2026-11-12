"""A stale export is not digested until the user has seen that it is stale.

The 14-day window is a starter default. It is not a Microsoft or ICO period.
A stale legal pin is not quoted. The pin date is 12 November 2026.
"""

from digest import run
from support import bundle, message, review


def test_stale_export_blocks_the_digest_until_it_is_acknowledged():
    export = bundle(
        [message("SYN-MSG-1", "We decided to keep the hours.")],
        retrieved_on="2026-10-01",
    )
    preview = run(export, "2026-11-12")
    assert preview["stale_export"]["stale"] is True
    assert preview["digest_produced"] is False
    refused = run(export, "2026-11-12", review())
    assert refused["digest_produced"] is False
    assert refused["scope_confirmation"]["reason"] == "stale_export_not_acknowledged"
    produced = run(export, "2026-11-12", review(stale_export_seen=True))
    assert produced["digest_produced"] is True
    assert produced["stale_export"]["stale"] is True
    assert produced["digest"]["decisions"][0]["text"] == "We decided to keep the hours."


def test_stale_legal_pin_is_not_quoted():
    export = bundle(
        [message("SYN-MSG-1", "We decided to keep the hours.", "2027-05-20")],
        retrieved_on="2027-05-28",
        period=("2027-05-01", "2027-05-31"),
    )
    asked = review(period_start="2027-05-01", period_end="2027-05-31")
    produced = run(export, "2027-06-01", asked)
    assert produced["digest_produced"] is True
    assert produced["regulatory"]["sources_current"] is False
    assert produced["regulatory"]["quotes"] is None
    blob_sources = produced["sources"]
    assert all(row["taken"] is None for row in blob_sources)
    assert "adequate, relevant and limited" not in str(produced["regulatory"])
    assert produced["digest"]["decisions"][0]["message_ids"] == ["SYN-MSG-1"]
