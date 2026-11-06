"""Synthetic knowledge base for an invented customer-service organisation.

Mereford Customer Service is not a real utility, telecoms provider, bank,
insurer, or council. An article body is the only sentence the agent may quote.
"""

from __future__ import annotations

from datetime import date

ORGANISATION = {
    "id": "mereford-customer-service",
    "name": "Mereford Customer Service",
    "fictional": True,
    "sectors_in_the_catalogue": [
        "energy_retail",
        "telecoms",
        "financial_services",
        "public_service",
    ],
}

STALE_AFTER_DAYS = 180

# Each keyword group must match. A group matches when any term is in the text.
ARTICLES: tuple[dict, ...] = (
    {
        "id": "kb-energy-meter-reading",
        "title": "How to give a meter reading",
        "sector": "energy_retail",
        "article_class": "information",
        "last_reviewed": "2026-09-01",
        "keywords": (("meter reading", "meter read"),),
        "exclude": (),
        "body": (
            "Read the numbers on the meter and submit them on the signed-in form "
            "you already use, or phone the published number. "
            "This article explains the next step. It does not submit the reading. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-energy-bill",
        "title": "What a bill shows",
        "sector": "energy_retail",
        "article_class": "information",
        "last_reviewed": "2026-08-15",
        "keywords": (("explain my bill", "what is on my bill", "bill explanation"),),
        "exclude": (),
        "body": (
            "A published bill shows a standing charge and a unit rate. "
            "This page does not show your balance and it does not change a tariff. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-energy-pay-how",
        "title": "Ways to pay, without this agent taking payment",
        "sector": "energy_retail",
        "article_class": "information",
        "last_reviewed": "2026-08-20",
        "keywords": (("how do i pay", "ways to pay"),),
        "exclude": (),
        "body": (
            "Use the payment reference already printed on the bill, in the channel "
            "you already use, or ask for a person. "
            "This agent does not take a payment and does not ask for a card number. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-energy-psr",
        "title": "Priority services register, information only",
        "sector": "energy_retail",
        "article_class": "information",
        "last_reviewed": "2026-07-01",
        "keywords": (("what is the priority services register", "priority services register information"),),
        "exclude": (),
        "body": (
            "The priority services register is a published scheme. "
            "A person records a request to join it. "
            "This agent does not add you to it and does not decide eligibility. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-energy-tariff",
        "title": "A tariff change is not an agent action",
        "sector": "energy_retail",
        "article_class": "prohibited",
        "prohibited_kind": "tariff",
        "last_reviewed": "2026-09-01",
        "keywords": (("change my tariff", "switch tariff", "cheaper tariff", "new tariff"),),
        "exclude": (),
        "body": (
            "A person discusses a tariff with you. "
            "This article does not quote a price and it does not change a tariff. "
            "The agent does not. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-telecom-status",
        "title": "Check the published service status",
        "sector": "telecoms",
        "article_class": "information",
        "last_reviewed": "2026-09-12",
        "keywords": (("no signal", "broadband is down", "service status"),),
        "exclude": (),
        "body": (
            "Check the published status page for the invented area, then ask for a person "
            "if the page does not explain the fault. "
            "This agent does not raise a fault on the account and does not change a contract. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-telecom-contract",
        "title": "A contract change is not an agent action",
        "sector": "telecoms",
        "article_class": "prohibited",
        "prohibited_kind": "contract",
        "last_reviewed": "2026-09-01",
        "keywords": (("change my contract", "end my contract", "cancel my contract", "contract term"),),
        "exclude": (),
        "body": (
            "A person discusses contract terms. "
            "This article does not change them. The agent does not. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-fs-statement",
        "title": "When statements are issued",
        "sector": "financial_services",
        "article_class": "information",
        "last_reviewed": "2026-08-01",
        "keywords": (("where is my statement", "statement date"),),
        "exclude": (),
        "body": (
            "Statements follow the published cycle. "
            "This page does not show a balance. "
            "A person with access to the account system looks that up. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-fs-complaint",
        "title": "A financial-services complaint stays with a handler",
        "sector": "financial_services",
        "article_class": "complaint",
        "last_reviewed": "2026-09-15",
        "keywords": (("complaint", "unhappy", "dissatisfied", "not happy"),),
        "exclude": (),
        "body": (
            "A handler must confirm whether this is a complaint. "
            "This agent does not uphold it, reject it, or close it, and it does not offer redress. "
            "Mereford Customer Service is fictional. It is not a regulated firm."
        ),
    },
    {
        "id": "kb-public-hours",
        "title": "Counter hours",
        "sector": "public_service",
        "article_class": "information",
        "last_reviewed": "2026-06-01",
        "keywords": (("opening hours", "counter hours", "what time does the office"),),
        "exclude": ("boundary hours token",),
        "body": (
            "The invented Mereford counter is open from 09:00 to 16:00 on weekdays. "
            "This page does not create a case. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-public-missed",
        "title": "Missed collection, next step only",
        "sector": "public_service",
        "article_class": "information",
        "last_reviewed": "2026-07-20",
        "keywords": (("missed collection", "bin was not collected"),),
        "exclude": (),
        "body": (
            "Use the published missed-collection form, or ask for a person. "
            "This agent does not create a case and does not schedule a collection. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-boundary-hours",
        "title": "Boundary review of the counter hours",
        "sector": "public_service",
        "article_class": "information",
        "last_reviewed": "2026-05-10",
        "keywords": (("boundary hours token",),),
        "exclude": (),
        "body": "BOUNDARY-CURRENT: the counter closes at 16:00. Mereford Customer Service is fictional.",
    },
    {
        "id": "kb-address-update",
        "title": "Address-update draft",
        "sector": "any",
        "article_class": "account_action",
        "action_kind": "address_update_draft",
        "last_reviewed": "2026-09-01",
        "keywords": (("change of address", "update my address", "i have moved", "i've moved", "new address"),),
        "exclude": (),
        "body": (
            "An address-update draft can be prepared for the signed-in account. "
            "The agent does not change the record. "
            "A separate confirmation does not change it either. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-appointment",
        "title": "Appointment-request draft",
        "sector": "any",
        "article_class": "account_action",
        "action_kind": "appointment_request_draft",
        "last_reviewed": "2026-09-01",
        "keywords": (("book an appointment", "request an appointment", "counter appointment"),),
        "exclude": (),
        "body": (
            "An appointment-request draft can be prepared. "
            "The agent does not book the appointment. "
            "A separate confirmation does not book it either. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-password",
        "title": "A password reset is not an agent action",
        "sector": "any",
        "article_class": "prohibited",
        "prohibited_kind": "password",
        "last_reviewed": "2026-09-01",
        "keywords": (("password", "one-time code", "one time code", "reset my login"),),
        "exclude": (),
        "body": (
            "This agent does not reset a password and does not ask for a code. "
            "A person verifies you by the organisation's own method. "
            "This article does not describe a click-path. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-payment-take",
        "title": "Taking a payment is not an agent action",
        "sector": "any",
        "article_class": "prohibited",
        "prohibited_kind": "payment",
        "last_reviewed": "2026-09-01",
        "keywords": (("take the payment", "take a payment", "charge my card", "card number", "refund my"),),
        "exclude": (),
        "body": (
            "This agent does not take a payment and does not make a refund. "
            "A person uses the organisation's own payment channel. "
            "This article does not ask for a card number. "
            "Mereford Customer Service is fictional."
        ),
    },
    {
        "id": "kb-stale-tariff-table",
        "title": "Legacy tariff table",
        "sector": "energy_retail",
        "article_class": "information",
        "last_reviewed": "2025-01-15",
        "keywords": (("legacy tariff token",),),
        "exclude": (),
        "body": "LEGACY-BODY-DO-NOT-QUOTE: the unit rate is 99.99.",
    },
)

PROHIBITED_PRIORITY = ("password", "payment", "tariff", "contract")


def age_days(earlier: date, later: date) -> int:
    return (later - earlier).days


def is_stale(last_reviewed: str, as_of: date, stale_after_days: int = STALE_AFTER_DAYS) -> bool:
    reviewed = date.fromisoformat(last_reviewed)
    age = age_days(reviewed, as_of)
    return age < 0 or age > stale_after_days


def match_articles(text: str, sector: str) -> list[dict]:
    hay = text.lower()
    matched = []
    for article in ARTICLES:
        if article["sector"] not in {sector, "any"}:
            continue
        if any(term in hay for term in article["exclude"]):
            continue
        groups_ok = all(any(term in hay for term in group) for group in article["keywords"])
        if groups_ok:
            matched.append(article)
    return matched
