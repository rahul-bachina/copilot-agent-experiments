"""Pages opened on 19 November 2026. The checker does not download them again.

A pin is confirmed for a question date only when that date is on or before a
stamp the page actually showed. Article 28 and Unfair Contract Terms Act 1977
sections 2 and 11 did not show an "up to date on or before" date. Their
currency is unverified. Today is not used.
"""

from __future__ import annotations

from datetime import date

OPENED_ON = "2026-11-19"

PINS: tuple[dict, ...] = (
    {
        "id": "uk-gdpr-art-28",
        "title": "UK GDPR Article 28",
        "url": "https://www.legislation.gov.uk/eur/2016/679/article/28",
        "extent": "United Kingdom",
        "up_to_date_on_or_before": None,
        "currency_stamp_seen": False,
        "currency": "unverified",
        "quote": (
            "Processing by a processor shall be governed by a contract or other "
            "legal act under domestic law, that is binding on the processor with "
            "regard to the controller and that sets out the subject-matter and "
            "duration of the processing, the nature and purpose of the processing, "
            "the type of personal data and categories of data subjects and the "
            "obligations and rights of the controller."
        ),
        "use": (
            "Article 28(3), including points (a) to (h), as a presence checklist. "
            "The page said there are currently no known outstanding effects. It did "
            "not show an up-to-date date, and it said revised legislation may not "
            "be fully up to date. Currency is unverified. Phrase presence is not "
            "compliance. Article 28(8)'s substituted word was not readable. That "
            "paragraph is not relied on."
        ),
    },
    {
        "id": "ucta-s2",
        "title": "Unfair Contract Terms Act 1977, section 2",
        "url": "https://www.legislation.gov.uk/ukpga/1977/50/section/2",
        "extent": "E+W+N.I.",
        "up_to_date_on_or_before": None,
        "currency_stamp_seen": False,
        "currency": "unverified",
        "quote": (
            "A person cannot by reference to any contract term or to a notice "
            "given to persons generally or to particular persons exclude or "
            "restrict his liability for death or personal injury resulting from "
            "negligence."
        ),
        "use": (
            "Section 2(1) is context where the audience is business and the stated "
            "law is not Scotland. Section 2(4): this section does not apply to a "
            "term in a consumer contract or a consumer notice, and points to "
            "sections 62 and 65 of the Consumer Rights Act 2015. Part II was not "
            "opened. This starter does not decide that a term is void. Currency "
            "is unverified."
        ),
    },
    {
        "id": "ucta-s11",
        "title": "Unfair Contract Terms Act 1977, section 11",
        "url": "https://www.legislation.gov.uk/ukpga/1977/50/section/11",
        "extent": "E+W+N.I.",
        "up_to_date_on_or_before": None,
        "currency_stamp_seen": False,
        "currency": "unverified",
        "quote": (
            "It is for those claiming that a contract term or notice satisfies "
            "the requirement of reasonableness to show that it does."
        ),
        "use": (
            "Section 11(5), with section 11(1) and section 11(4) as context. The "
            "reasonableness test is not applied. Currency is unverified."
        ),
    },
    {
        "id": "cra-part-2",
        "title": "Consumer Rights Act 2015, Part 2",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/part/2",
        "extent": "U.K.",
        "up_to_date_on_or_before": "2026-11-18",
        "currency_stamp_seen": True,
        "currency": "stamped",
        "quote": "PART 2 Unfair terms",
        "use": (
            "Part 2 is context for a consumer contract. Schedule 2 was not opened. "
            "Fairness is not decided."
        ),
    },
    {
        "id": "cra-s61",
        "title": "Consumer Rights Act 2015, section 61",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/61",
        "extent": "U.K.",
        "up_to_date_on_or_before": "2026-11-19",
        "currency_stamp_seen": True,
        "currency": "stamped",
        "quote": "This Part applies to a contract between a trader and a consumer.",
        "use": "Section 61(1). This starter does not decide that the contract is a consumer contract.",
    },
    {
        "id": "cra-s62",
        "title": "Consumer Rights Act 2015, section 62",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/62",
        "extent": "U.K.",
        "up_to_date_on_or_before": "2026-11-19",
        "currency_stamp_seen": True,
        "currency": "stamped",
        "quote": "An unfair term of a consumer contract is not binding on the consumer.",
        "use": (
            "Section 62(1). Section 62(4) defines unfairness by good faith and a "
            "significant imbalance. This starter does not apply that test."
        ),
    },
    {
        "id": "cra-s65",
        "title": "Consumer Rights Act 2015, section 65",
        "url": "https://www.legislation.gov.uk/ukpga/2015/15/section/65",
        "extent": "U.K.",
        "up_to_date_on_or_before": "2026-11-18",
        "currency_stamp_seen": True,
        "currency": "stamped",
        "quote": (
            "A trader cannot by a term of a consumer contract or by a consumer "
            "notice exclude or restrict liability for death or personal injury "
            "resulting from negligence."
        ),
        "use": (
            "Section 65(1) is context where the audience is consumer. Section 66 "
            "was read on the Part 2 page and is not applied. This starter does not "
            "decide that a term is void."
        ),
    },
)


def pin_rows(as_of: date) -> list[dict]:
    rows = []
    for pin in PINS:
        stamp = pin["up_to_date_on_or_before"]
        if stamp is None:
            confirmed = False
        else:
            confirmed = as_of.isoformat() <= stamp
        rows.append(
            {
                "id": pin["id"],
                "title": pin["title"],
                "url": pin["url"],
                "extent": pin["extent"],
                "quote": pin["quote"],
                "use": pin["use"],
                "up_to_date_on_or_before": stamp,
                "currency_stamp_seen": pin["currency_stamp_seen"],
                "currency": pin["currency"],
                "confirmed_for_question_date": confirmed,
                "opened_on": OPENED_ON,
            }
        )
    return rows


def statutory_note(as_of: date, audience: str, jurisdictions: list[str]) -> dict:
    rows = pin_rows(as_of)
    scots = any(place == "Scotland" for place in jurisdictions)
    england_or_ni = any(
        place in {"England and Wales", "England", "Northern Ireland"} for place in jurisdictions
    )
    return {
        "opened_on": OPENED_ON,
        "question_date": as_of.isoformat(),
        "today_not_used": True,
        "pins": rows,
        "any_unconfirmed": any(not row["confirmed_for_question_date"] for row in rows),
        "audience_context": audience,
        "jurisdictions_seen": jurisdictions,
        "ucta_part_ii_opened": False,
        "scots_law_unverified": scots,
        "section_2_extent_note": (
            "Section 2 and section 11 are marked E+W+N.I. Part II was not opened."
            if scots or not england_or_ni
            else "Section 2 and section 11 are marked E+W+N.I."
        ),
        "reasonableness_decided": False,
        "fairness_decided": False,
        "voidness_decided": False,
        "article_28_complied": False,
        "legal_advice": False,
    }
