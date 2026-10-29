"""Synthetic knowledge-base articles for an invented internal desk.

Aldermere District Council is not a real authority. Aldermere Shared ICT is
not a real desk. Nothing here is a member of staff's ticket. An article body
is the only sentence the desk may quote.
"""

from __future__ import annotations

from datetime import date

ORGANISATION = {
    "id": "aldermere-district-council",
    "name": "Aldermere District Council",
    "desk": "Aldermere Shared ICT",
    "fictional": True,
}

STALE_AFTER_DAYS = 180

# Each keyword group must match. A group matches when any term is in the text.
# exclude drops the article when any of those terms is present.
ARTICLES: tuple[dict, ...] = (
    {
        "id": "kb-vpn-809",
        "title": "VPN client error 809",
        "article_class": "standard_fix",
        "last_reviewed": "2026-08-01",
        "keywords": (("vpn",), ("809",)),
        "exclude": ("legacy", "2019"),
        "required_diagnostics": ("error_code", "network_connected"),
        "would_change_device": False,
        "would_change_account": False,
        "privileged": False,
        "body": (
            "Check the laptop is on the corporate network or a known home connection. "
            "Quit the VPN client and open it again. "
            "If error 809 is still shown, stop. A service desk analyst looks at the concentrator. "
            "This article does not change the device and does not change the account. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-wifi-guest",
        "title": "Corporate wireless, not the guest network",
        "article_class": "standard_fix",
        "last_reviewed": "2026-09-20",
        "keywords": (("wi-fi", "wifi", "wireless"),),
        "exclude": (),
        "required_diagnostics": ("network_connected",),
        "would_change_device": False,
        "would_change_account": False,
        "privileged": False,
        "body": (
            "Use the corporate wireless network named in the device build. "
            "The guest network is not for a corporate laptop. "
            "This article does not change the device. "
            "If the corporate network is not listed, stop and hand the ticket to an analyst. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-outlook-cache",
        "title": "Outlook will not open",
        "article_class": "device_change",
        "last_reviewed": "2026-07-15",
        "keywords": (("outlook",), ("will not open", "won't open", "wont open", "not opening")),
        "exclude": (),
        "required_diagnostics": ("os", "asset_tag"),
        "would_change_device": True,
        "would_change_account": False,
        "privileged": False,
        "body": (
            "Quit Outlook. Rename the local Outlook cache folder only after the signed-in "
            "member of staff has confirmed this device change. "
            "The agent does not rename the folder. "
            "If Outlook still does not open, stop and hand the ticket to an analyst. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-printer-map",
        "title": "Map the corporate printer",
        "article_class": "device_change",
        "last_reviewed": "2026-09-01",
        "keywords": (("printer",),),
        "exclude": (),
        "required_diagnostics": ("asset_tag",),
        "would_change_device": True,
        "would_change_account": False,
        "privileged": False,
        "body": (
            "The signed-in member of staff can confirm mapping the corporate printer queue SYN-PRINT. "
            "The agent does not map the printer. "
            "An asset tag is required before that confirmation is recorded. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-service-hours",
        "title": "Service desk hours",
        "article_class": "information",
        "last_reviewed": "2026-06-01",
        "keywords": (("service desk hours", "opening hours", "what time does the desk"),),
        "exclude": ("boundary hours token",),
        "required_diagnostics": (),
        "would_change_device": False,
        "would_change_account": False,
        "privileged": False,
        "body": (
            "Aldermere Shared ICT is open from 08:30 to 17:00 on weekdays. "
            "This page is information only. It does not change a device or an account. "
            "Aldermere District Council is fictional."
        ),
    },
    {
        "id": "kb-boundary-hours",
        "title": "Boundary review of the desk hours",
        "article_class": "information",
        "last_reviewed": "2026-05-02",
        "keywords": (("boundary hours token",),),
        "exclude": (),
        "required_diagnostics": (),
        "would_change_device": False,
        "would_change_account": False,
        "privileged": False,
        "body": "BOUNDARY-CURRENT: the desk closes at 17:00. Aldermere Shared ICT is fictional.",
    },
    {
        "id": "kb-password-reset",
        "title": "Password reset is an analyst action",
        "article_class": "privileged",
        "last_reviewed": "2026-09-01",
        "keywords": (("password", "locked out", "account locked"),),
        "exclude": (),
        "required_diagnostics": (),
        "would_change_device": False,
        "would_change_account": True,
        "privileged": True,
        "body": (
            "A service desk analyst resets the password in the identity system after they "
            "have verified the person by the organisation's own method. "
            "This article does not describe the click-path. "
            "The agent does not reset the password. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-mfa-change",
        "title": "MFA change is an analyst action",
        "article_class": "privileged",
        "last_reviewed": "2026-09-01",
        "keywords": (("mfa", "multi-factor", "authenticator app"),),
        "exclude": (),
        "required_diagnostics": (),
        "would_change_device": False,
        "would_change_account": True,
        "privileged": True,
        "body": (
            "A service desk analyst changes multi-factor authentication in the identity "
            "system after they have verified the person. "
            "This article does not describe the click-path. "
            "The agent does not change MFA and does not ask for a code. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-access-grant",
        "title": "Access grant is an analyst action",
        "article_class": "privileged",
        "last_reviewed": "2026-09-12",
        "keywords": (
            (
                "sharepoint access",
                "mailbox access",
                "admin rights",
                "global admin",
                "grant access",
                "access to the",
            ),
        ),
        "exclude": (),
        "required_diagnostics": (),
        "would_change_device": False,
        "would_change_account": True,
        "privileged": True,
        "body": (
            "A service desk analyst grants or refuses access in the identity system after "
            "they have verified the person and the owner of the resource has agreed. "
            "This article does not grant access. The agent does not. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-remote-wipe",
        "title": "Remote wipe is an analyst action",
        "article_class": "privileged",
        "last_reviewed": "2026-08-20",
        "keywords": (("remote wipe", "wipe the laptop", "wipe my laptop"),),
        "exclude": (),
        "required_diagnostics": (),
        "would_change_device": True,
        "would_change_account": False,
        "privileged": True,
        "body": (
            "A service desk analyst decides whether a lost device is wiped, after the "
            "member of staff has reported it and identity has been verified. "
            "This article does not wipe a device. The agent does not. "
            "Aldermere Shared ICT is fictional."
        ),
    },
    {
        "id": "kb-stale-vpn-legacy",
        "title": "Legacy VPN client 2019",
        "article_class": "standard_fix",
        "last_reviewed": "2025-01-15",
        "keywords": (("legacy vpn", "vpn client 2019"),),
        "exclude": (),
        "required_diagnostics": (),
        "would_change_device": False,
        "would_change_account": False,
        "privileged": False,
        "body": "LEGACY-BODY-DO-NOT-QUOTE: uninstall the 2019 client with the old key.",
    },
)


def age_days(earlier: date, later: date) -> int:
    return (later - earlier).days


def is_stale(last_reviewed: str, as_of: date, stale_after_days: int = STALE_AFTER_DAYS) -> bool:
    reviewed = date.fromisoformat(last_reviewed)
    age = age_days(reviewed, as_of)
    return age < 0 or age > stale_after_days


def match_articles(text: str) -> list[dict]:
    hay = text.lower()
    matched = []
    for article in ARTICLES:
        if any(term in hay for term in article["exclude"]):
            continue
        groups_ok = all(any(term in hay for term in group) for group in article["keywords"])
        if groups_ok:
            matched.append(article)
    return matched
