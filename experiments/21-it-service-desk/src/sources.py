"""Pages opened for this starter. The desk does not download them."""

from __future__ import annotations

from datetime import date

SOURCES: tuple[dict, ...] = (
    {
        "id": "ncsc-phishing",
        "title": "Phishing attacks: defending your organisation",
        "url": "https://www.ncsc.gov.uk/guidance/phishing",
        "last_verified": "2026-10-29",
        "note": (
            "Opened 29 October 2026. The page says attackers can exploit ways of "
            "working to trick users into handing over information, including "
            "passwords, and that important requests should be verified using a "
            "second type of communication. It also says to limit privileged access "
            "and to use multi-factor authentication. No publication date was "
            "printed on the page that was read."
        ),
    },
    {
        "id": "ncsc-end-user-devices",
        "title": "Advice for End Users",
        "url": "https://www.ncsc.gov.uk/guidance/end-user-devices-advice-end-users",
        "last_verified": "2026-10-29",
        "note": (
            "Published 24 September 2016. The page's own Reviewed line also says "
            "24 September 2016. The page says a person must never disclose a "
            "password to anyone, including IT support, and that the helpdesk "
            "confirms identity before a password reset."
        ),
    },
    {
        "id": "ncsc-retailers",
        "title": "Incidents impacting retailers – recommendations from the NCSC",
        "url": "https://www.ncsc.gov.uk/blog-post/incidents-impacting-retailers",
        "last_verified": "2026-10-29",
        "note": (
            "Published 4 May 2025. The post says there has been discussion about "
            "whether social engineering had been used by threat actors targeting "
            "IT helpdesks to perform password and MFA resets. It encourages "
            "organisations to review how the helpdesk authenticates staff before "
            "resetting passwords, especially accounts with escalated privileges. "
            "This starter does not treat press speculation named in the post as "
            "a finding about any real incident."
        ),
    },
    {
        "id": "uk-gdpr-article-6",
        "title": "UK GDPR Article 6",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/6",
        "last_verified": "2026-10-29",
        "note": (
            "Read 29 October 2026. Points (ea) and (f) of Article 6(1) do not "
            "apply to processing carried out by public authorities in the "
            "performance of their tasks. Article 6(11)(c) lists security of "
            "network and information systems as an example of a legitimate "
            "interest. This starter does not assert a lawful basis."
        ),
    },
    {
        "id": "uk-gdpr-article-32",
        "title": "UK GDPR Article 32",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/32",
        "last_verified": "2026-10-29",
        "note": (
            "Read 29 October 2026. Article 32(1) requires appropriate technical "
            "and organisational measures, including the ability to ensure "
            "confidentiality, integrity, availability, and resilience. Article "
            "32(4) says a person acting under the controller's authority does "
            "not process personal data except on instructions from the "
            "controller, unless domestic law requires it. This starter is not "
            "a finding that a controller complies."
        ),
    },
    {
        "id": "copilot-harnesses",
        "title": "Harnesses in Copilot Studio",
        "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview",
        "last_verified": "2026-10-29",
        "note": (
            "Opened 29 October 2026. The standard harness is described as a fit "
            "for an internal help-desk experience that answers common questions "
            "and routes simple requests. The GitHub Copilot harness is a "
            "Copilot Studio framework, not the GitHub Copilot service. The page "
            "says customer data is not sent to that service when agents run in "
            "Copilot Studio."
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
