"""Pages opened for this starter. The front door does not download them."""

from __future__ import annotations

from datetime import date

SOURCES: tuple[dict, ...] = (
    {
        "id": "ai-playbook",
        "title": "AI Playbook for the UK Government",
        "url": (
            "https://www.gov.uk/government/publications/ai-playbook-for-the-uk-government/"
            "artificial-intelligence-playbook-for-the-uk-government-html"
        ),
        "last_verified": "2026-10-27",
        "note": (
            "Published 10 February 2025. Principle 4 is meaningful human control, "
            "including chatbots that cannot be reviewed in real time. Principle 7 "
            "asks for a clear line on an automated response, and encourages ATRS "
            "where it is not yet mandatory."
        ),
    },
    {
        "id": "atrs-scope",
        "title": "ATRS mandatory scope and exemptions policy",
        "url": (
            "https://www.gov.uk/government/publications/"
            "algorithmic-transparency-recording-standard-mandatory-scope-and-exemptions-policy/"
            "algorithmic-transparency-recording-standard-atrs-mandatory-scope-and-exemptions-policy"
        ),
        "last_verified": "2026-10-27",
        "note": (
            "Published 17 December 2024. Mandatory scope is central government. "
            "The standard is recommended for the broader public sector. This starter "
            "does not decide that a council is in the mandatory scope."
        ),
    },
    {
        "id": "copilot-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": "2026-10-27",
        "note": (
            "Standard harness, GitHub Copilot harness, and Customer Conversation "
            "harness. The GitHub Copilot harness is not the GitHub Copilot service."
        ),
    },
    {
        "id": "accessibility-regs",
        "title": "Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018",
        "url": "https://www.legislation.gov.uk/uksi/2018/952",
        "last_verified": "2026-10-27",
        "note": (
            "A public-sector website or mobile application must meet the "
            "accessibility requirement and publish an accessibility statement. "
            "This command-line starter is not that website."
        ),
    },
)


def source_rows(as_of: date, stale_after_days: int, age_days) -> list[dict]:
    """age_days(last_verified, as_of) -> int. The caller owns the stale rule."""
    rows = []
    for source in SOURCES:
        verified = date.fromisoformat(source["last_verified"])
        age = age_days(verified, as_of)
        stale = age < 0 or age > stale_after_days
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "last_verified": source["last_verified"],
                "stale": stale,
            }
        )
    return rows
