"""Duplicate and campaign clustering."""

from src.clusters import cluster_responses
from src.safeguards import redact


def _row(response_id: str, text: str) -> dict[str, str]:
    redacted, _types, _special = redact(text)
    return {"response_id": response_id, "text": redacted}


def test_blank_answers_are_not_a_campaign():
    clustered = cluster_responses(
        [
            {"response_id": "A", "text": ""},
            {"response_id": "B", "text": "   "},
        ]
    )
    assert clustered["A"]["cluster_id"] != clustered["B"]["cluster_id"]
    assert clustered["A"]["campaign_cluster"] is False
    assert clustered["A"]["duplicate"] is False


def test_campaign_survives_different_identifiers():
    template = (
        "I write as a member of the Friends of Northmere Library. "
        "Keep the current hours. Do not cut Sunday opening."
    )
    clustered = cluster_responses(
        [
            _row("R-14", template + " You can reach me at friend.one@example.com."),
            _row("R-15", template + " You can reach me at friend.two@example.com."),
            _row(
                "R-16",
                template + " National Insurance AB123456C. Postcode XM4 5HQ. Phone 07700 900123.",
            ),
            _row("R-17", template + " Thank you for considering this view."),
        ]
    )
    cluster_ids = {clustered[key]["cluster_id"] for key in ("R-14", "R-15", "R-16", "R-17")}
    assert len(cluster_ids) == 1
    assert clustered["R-14"]["campaign_cluster"] is True
    assert clustered["R-14"]["representative_id"] == "R-14"
    assert clustered["R-15"]["is_representative"] is False
    assert "exact" in clustered["R-14"]["cluster_reasons"]
    assert "repeated_sentence" in clustered["R-16"]["cluster_reasons"]
