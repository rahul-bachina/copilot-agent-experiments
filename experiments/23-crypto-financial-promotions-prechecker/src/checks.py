"""Phrase checks against the pinned extracts. None of them is a finding."""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from sources import (
        PERSONALISED_RISK_CORE,
        RISK_LINK_TEXT,
        RISK_WARNING_CRYPTO,
        RISK_WARNING_CRYPTO_SHORT,
        RISK_WARNING_NRR,
    )
else:
    from .sources import (
        PERSONALISED_RISK_CORE,
        RISK_LINK_TEXT,
        RISK_WARNING_CRYPTO,
        RISK_WARNING_CRYPTO_SHORT,
        RISK_WARNING_NRR,
    )

_INCENTIVES: list[tuple[str, re.Pattern[str]]] = [
    ("refer_a_friend", re.compile(r"refer(?:ral)?[\s-]a[\s-]friend", re.I)),
    ("referral_bonus", re.compile(r"referral\s+bonus", re.I)),
    ("bonus", re.compile(r"\bbonus(?:es)?\b", re.I)),
    ("cashback", re.compile(r"\bcash\s*back\b", re.I)),
    ("free_crypto", re.compile(r"\bfree\s+(?:crypto(?:asset)?s?|bitcoins?|tokens?|eth|btc|coins?)\b", re.I)),
    ("extra_tokens", re.compile(r"\bextra\s+(?:coins?|tokens?|crypto)\b", re.I)),
    ("free_gift", re.compile(r"\bfree\s+gifts?\b", re.I)),
    ("volume_discount", re.compile(r"\bvolume\s+discount\b|\bfee\s+rebate\b", re.I)),
]

_FAIR_TERMS: list[tuple[str, re.Pattern[str]]] = [
    ("guaranteed", re.compile(r"\bguaranteed\b", re.I)),
    ("protected", re.compile(r"\bprotected\b", re.I)),
    ("secure", re.compile(r"\bsecure\b", re.I)),
    ("risk_free", re.compile(r"\brisk[\s-]free\b", re.I)),
    ("cannot_lose", re.compile(r"\bcan(?:not|'t)\s+lose\b", re.I)),
    ("no_risk", re.compile(r"\bno\s+risk\b", re.I)),
    ("fscs", re.compile(r"\bfscs\b", re.I)),
    ("fca_approved", re.compile(r"\bfca[\s-]approved\b|\bapproved\s+by\s+the\s+fca\b", re.I)),
]

_ROUTES: list[tuple[str, re.Pattern[str]]] = [
    ("authorised_person", re.compile(r"\bfca[\s-]authorised\b|\bauthorised\s+person\b|\bauthorized\s+person\b", re.I)),
    ("s21_approval", re.compile(r"\bsection\s+21\b|\bs\.?\s*21\b", re.I)),
    ("mlr_registered", re.compile(r"\barticle\s+73za\b|\bmlr[\s-]registered\b|\bmoney\s+laundering\b", re.I)),
    ("fpo_exemption", re.compile(r"\bfinancial\s+promotion\s+order\b|\bfpo\s+exemption\b", re.I)),
]

_OFFER = re.compile(
    r"\b(?:buy\s+now|invest\s+now|open\s+an\s+account|start\s+investing|deposit\s+and)\b",
    re.I,
)
_COOLING = re.compile(r"24[\s-]*hours?|cooling[\s-]off", re.I)
_CATEGORY = re.compile(
    r"restricted\s+investor|high\s+net\s+worth|sophisticated\s+investor|categoris",
    re.I,
)
_APPROPRIATENESS = re.compile(r"\bappropriateness\b", re.I)

ROUTE_IDS = ("authorised_person", "s21_approval", "mlr_registered", "fpo_exemption")


def normalise(text: str) -> str:
    """Fold apostrophes and whitespace so a Handbook quotation can be found."""
    folded = (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )
    return re.sub(r"\s+", " ", folded).strip().casefold()


def _row(
    row_id: str,
    area: str,
    status: str,
    title: str,
    citation_id: str,
    detail: str,
    *,
    excerpt: str | None = None,
) -> dict:
    return {
        "id": row_id,
        "area": area,
        "status": status,
        "title": title,
        "source_id": citation_id,
        "detail": detail,
        "excerpt_redacted": excerpt,
        "compliance_finding": False,
        "for_the_s21_approver": True,
    }


def _excerpt(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    start = max(0, match.start() - 40)
    end = min(len(text), match.end() + 40)
    return re.sub(r"\s+", " ", text[start:end]).strip()[:180]


def build_checklist(usable: str, promotion: dict) -> list[dict]:
    """Return checklist rows. Every row has compliance_finding false."""
    claimed_route = _claimed_route(promotion)
    text_routes = [name for name, pattern in _ROUTES if pattern.search(usable)]
    claims_crypto = promotion.get("caller_claims_qualifying_cryptoasset") is True
    rows = [
        _route_row(usable, claimed_route, text_routes),
        _approver_row(promotion, claimed_route, text_routes),
        _gateway_row(),
        _qualifying_row(claims_crypto),
        _risk_row(usable, promotion, claims_crypto),
        _link_row(usable, promotion, claims_crypto),
        _prominence_row(),
        _incentive_row(usable),
        _fair_row(usable),
        _direct_offer_row(usable, promotion),
        _offence_row(),
    ]
    return rows


def _claimed_route(promotion: dict) -> str | None:
    communicator = promotion.get("communicator")
    if not isinstance(communicator, dict):
        return None
    route = communicator.get("route_claimed")
    if route in ROUTE_IDS:
        return route
    return None


def _route_row(usable: str, claimed: str | None, text_routes: list[str]) -> dict:
    if claimed or text_routes:
        stated = claimed or text_routes[0]
        return _row(
            "FP-ROUTE",
            "communication_route",
            "phrase_present",
            "A communication route is stated on the draft",
            "fca-marketing",
            (
                f"The caller or the text states '{stated}'. The marketing page "
                "lists four routes. Stating one is not a finding that the route "
                "is available to this firm, and not a finding that section 21 "
                "is satisfied. Text also mentioned: "
                + (", ".join(text_routes) if text_routes else "nothing further")
                + "."
            ),
        )
    return _row(
        "FP-ROUTE",
        "communication_route",
        "phrase_not_found",
        "No communication route is stated on the draft",
        "fca-marketing",
        (
            "The marketing page lists four routes: an FCA authorised person; "
            "approval by an authorised person; an MLR-registered cryptoasset "
            "business; or an exemption in the Financial Promotion Order. None "
            "of those phrases, and no route_claimed value, was on this draft."
        ),
    )


def _approver_row(promotion: dict, claimed: str | None, text_routes: list[str]) -> dict:
    relevant = claimed == "s21_approval" or "s21_approval" in text_routes
    approver = promotion.get("s21_approver")
    name = ""
    if isinstance(approver, dict) and isinstance(approver.get("name"), str):
        name = approver["name"].strip()
    if not relevant:
        return _row(
            "FP-S21-NAME",
            "s21_approver",
            "not_applied",
            "Section 21 approver name is not required by a route the draft did not claim",
            "fsma-s21",
            (
                "Section 21(2)(b) is the approval route. This draft did not "
                "claim it. An empty approver field is not, by itself, a finding. "
                "The section 21 approver still signs off before any communication."
            ),
        )
    if not name:
        return _row(
            "FP-S21-NAME",
            "s21_approver",
            "phrase_not_found",
            "The draft claims section 21 approval and names no approver",
            "fsma-s21",
            (
                "Section 21(2)(b) requires the content to be approved by an "
                "authorised person. No name was on s21_approver. This is not a "
                "finding that approval is impossible, and not a finding that "
                "section 55NA permission is held. Section 55NA was not opened."
            ),
        )
    return _row(
        "FP-S21-NAME",
        "s21_approver",
        "phrase_present",
        "The draft names a section 21 approver",
        "fsma-s21",
        (
            f"The draft names '{name}'. That is not a finding that the person "
            "is an authorised person, and not a finding that section 55NA "
            "permission is held. Section 55NA was not opened. The agent has "
            "not recorded their sign-off."
        ),
    )


def _gateway_row() -> dict:
    return _row(
        "FP-GATEWAY",
        "s21_gateway",
        "recorded_not_applied",
        "The marketing page and section 21(2A) are both recorded",
        "fsma-s21",
        (
            "The marketing page, last updated 6 February 2026, still says "
            "legislation on a regulatory gateway for approvers was making its "
            "way through Parliament. Section 21(2A), on the text opened "
            "30 October 2026, says content may be approved only if permitted "
            "under section 55NA or within an exemption under section 55NB, "
            "with a commencement note of 7 February 2024 in so far as not "
            "already in force. This checker does not decide which sentence "
            "a firm should follow. Sections 55NA and 55NB were not opened."
        ),
    )


def _qualifying_row(claims_crypto: bool) -> dict:
    if claims_crypto:
        detail = (
            "The caller says the draft relates to a qualifying cryptoasset. "
            "Paragraph 26F, as displayed, defines that term and carries a "
            "substitution note (25 February 2026 for specified purposes, "
            "otherwise prospective). This checker does not apply the "
            "definition and does not decide that the product is inside it."
        )
    else:
        detail = (
            "The caller did not say the draft relates to a qualifying "
            "cryptoasset. COBS 4.12A.11R(1)(d) is not applied. The section 21 "
            "approver decides whether paragraph 26F applies. The substitution "
            "note on that paragraph was not resolved."
        )
    return _row(
        "FP-26F",
        "qualifying_cryptoasset",
        "recorded_not_applied",
        "Paragraph 26F is recorded and not applied",
        "fpo-26f",
        detail,
    )


def _risk_row(usable: str, promotion: dict, claims_crypto: bool) -> dict:
    if not claims_crypto:
        return _row(
            "FP-RISK",
            "risk_warning",
            "not_applied",
            "The qualifying-cryptoasset risk warning is not scored",
            "cobs-4-12a",
            (
                "COBS 4.12A.11R(1)(d) applies where the promotion relates to "
                "one or more qualifying cryptoassets. The caller did not say "
                "that it does. Warning text, if any, is not scored."
            ),
        )
    folded = normalise(usable)
    full = normalise(RISK_WARNING_CRYPTO)
    short = normalise(RISK_WARNING_CRYPTO_SHORT)
    nrr = normalise(RISK_WARNING_NRR)
    if full in folded:
        return _row(
            "FP-RISK",
            "risk_warning",
            "phrase_present",
            "The COBS 4.12A.11R(1)(d) risk warning is in the text",
            "cobs-4-12a",
            (
                "The words in COBS 4.12A.11R(1)(d) were found. Presence is not "
                "prominence. COBS 4.12A.36R and COBS 4.12A.38R were not opened. "
                "COBS 4.12A.11R(5) tells a firm, when its conditions are met, "
                "to omit words that do not appear in (1)(d). This checker does "
                "not apply that omission and does not decide the conditions."
            ),
        )
    if nrr in folded:
        return _row(
            "FP-RISK",
            "risk_warning",
            "flagged_for_review",
            "The text uses the non-readily realisable securities warning",
            "cobs-4-12a",
            (
                "The words match COBS 4.12A.11R(1)(a) ('you are unlikely to be "
                "protected'), not COBS 4.12A.11R(1)(d) ('you should not expect "
                "to be protected'). This is not a finding of a breach."
            ),
        )
    if short in folded:
        limited = promotion.get("character_limited") is True
        if limited:
            return _row(
                "FP-RISK",
                "risk_warning",
                "question_for_approver",
                "Only the short risk warning is in the text",
                "cobs-4-12a",
                (
                    "COBS 4.12A.11R(2)(a) permits the shorter warning where the "
                    "warning in (1) exceeds a third-party marketing provider's "
                    "character limit. The caller says a limit applies. This "
                    "checker cannot see the provider's limit."
                ),
            )
        return _row(
            "FP-RISK",
            "risk_warning",
            "flagged_for_review",
            "Only the short risk warning is in the text",
            "cobs-4-12a",
            (
                "The shorter warning in COBS 4.12A.11R(2)(a) was found, and "
                "the caller has not said a third-party character limit applies. "
                "This is not a finding that the short form is unavailable."
            ),
        )
    return _row(
        "FP-RISK",
        "risk_warning",
        "phrase_not_found",
        "The COBS 4.12A.11R(1)(d) risk warning was not found",
        "cobs-4-12a",
        (
            "Neither the warning in COBS 4.12A.11R(1)(d) nor the shorter "
            "warning in COBS 4.12A.11R(2)(a) was found in the text used as "
            "evidence. Absence is not a finding of a breach. A paraphrase "
            "would not match."
        ),
    )


def _link_row(usable: str, promotion: dict, claims_crypto: bool) -> dict:
    if not claims_crypto:
        return _row(
            "FP-RISK-LINK",
            "risk_summary_link",
            "not_applied",
            "The digital-medium link is not scored",
            "cobs-4-12a",
            "COBS 4.12A.11R(3) was not applied because the caller did not claim a qualifying cryptoasset.",
        )
    folded = normalise(usable)
    if normalise(RISK_WARNING_CRYPTO) not in folded and normalise(RISK_WARNING_CRYPTO_SHORT) not in folded:
        return _row(
            "FP-RISK-LINK",
            "risk_summary_link",
            "not_applied",
            "There is no scored warning text to attach a link to",
            "cobs-4-12a",
            "COBS 4.12A.11R(3) adds a link to the warning in (1) or (2). That warning was not found.",
        )
    channel = promotion.get("channel")
    digital = channel in {"web", "app", "social"}
    has_link = normalise(RISK_LINK_TEXT).rstrip(".") in folded
    if not digital:
        return _row(
            "FP-RISK-LINK",
            "risk_summary_link",
            "question_for_approver",
            "The channel is not one of web, app, or social",
            "cobs-4-12a",
            (
                "COBS 4.12A.11R(3) is for a website, mobile application, or "
                "other digital medium. COBS 4.12A.11R(4) is for other media "
                "and requires a risk summary from COBS 4 Annex 1R in a durable "
                "medium. Annex 1R was not opened. The approver decides which "
                "paragraph applies."
            ),
        )
    if has_link:
        return _row(
            "FP-RISK-LINK",
            "risk_summary_link",
            "phrase_present",
            "The words 'Take 2 mins to learn more' are in the text",
            "cobs-4-12a",
            (
                "COBS 4.12A.11R(3)(a) asks for a link in that form to a risk "
                "summary selected from COBS 4 Annex 1R. Annex 1R was not "
                "opened. The words are not a finding that the link works or "
                "that the summary is the right one."
            ),
        )
    return _row(
        "FP-RISK-LINK",
        "risk_summary_link",
        "question_for_approver",
        "The digital-medium link text was not found",
        "cobs-4-12a",
        (
            "COBS 4.12A.11R(3)(a) asks for 'Take 2 mins to learn more' on a "
            "website, mobile application, or other digital medium. "
            "COBS 4.12A.11R(3)(b) says that text need not be in that form if "
            "it would exceed a third-party character limit, and need not be "
            "provided if the medium does not allow a link. "
            f"character_limited is {promotion.get('character_limited') is True}. "
            "This checker cannot see the medium. Annex 1R was not opened."
        ),
    )


def _prominence_row() -> dict:
    return _row(
        "FP-PROMINENCE",
        "prominence",
        "not_applied",
        "Prominence is not checked",
        "cobs-4-12a",
        (
            "COBS 4.12A.11R(6) says the risk warning and the risk summary "
            "must comply with COBS 4.12A.36R and COBS 4.12A.38R. Those two "
            "rules were named and not opened. Font, position, and colour "
            "are not checked."
        ),
    )


def _incentive_row(usable: str) -> dict:
    hits = [(name, pattern) for name, pattern in _INCENTIVES if pattern.search(usable)]
    if not hits:
        return _row(
            "FP-INCENTIVE",
            "incentives",
            "phrase_not_found",
            "No incentive example from COBS 4.12A.8G was found",
            "cobs-4-12a",
            (
                "COBS 4.12A.7R prohibits a monetary or non-monetary incentive "
                "to a retail client, with conditions in (3) and (4). The "
                "examples in COBS 4.12A.8G were not found as phrases. Absence "
                "is not a finding that no incentive is offered. Paragraph (3) "
                "does not list qualifying cryptoassets. This checker does not "
                "decide that paragraph (4) applies."
            ),
        )
    names = [name for name, _pattern in hits]
    excerpt = _excerpt(usable, hits[0][1])
    return _row(
        "FP-INCENTIVE",
        "incentives",
        "flagged_for_review",
        "The text contains an incentive phrase from the COBS 4.12A.8G examples",
        "cobs-4-12a",
        (
            "Phrases matched: " + ", ".join(names) + ". COBS 4.12A.7R and the "
            "examples in COBS 4.12A.8G. This is not a finding that the rule "
            "is breached. COBS 4.12A.7R(3) does not list qualifying cryptoassets. "
            "COBS 4.12A.7R(4) is a transfer-only condition. Neither condition "
            "is applied. COBS 4.12A.9G says information and research tools, "
            "and lower fees not linked to volumes and made available to all "
            "retail clients, do not constitute an incentive. That guidance "
            "is not applied to clear a flag."
        ),
        excerpt=excerpt,
    )


def _without_prescribed(usable: str) -> str:
    """Drop Handbook sentences so words inside them are not flagged again."""
    scrubbed = usable
    for sentence in (
        RISK_WARNING_CRYPTO,
        RISK_WARNING_NRR,
        RISK_WARNING_CRYPTO_SHORT,
        PERSONALISED_RISK_CORE,
        RISK_LINK_TEXT,
    ):
        scrubbed = re.sub(re.escape(sentence), " ", scrubbed, flags=re.IGNORECASE)
        curly = sentence.replace("'", "\u2019")
        scrubbed = re.sub(re.escape(curly), " ", scrubbed, flags=re.IGNORECASE)
    return scrubbed


def _fair_row(usable: str) -> dict:
    hits = [(name, pattern) for name, pattern in _FAIR_TERMS if pattern.search(_without_prescribed(usable))]
    if not hits:
        return _row(
            "FP-FAIR",
            "fair_clear_not_misleading",
            "phrase_not_found",
            "None of the watched fair-clear-not-misleading words was found",
            "cobs-4-2",
            (
                "COBS 4.2.1R is the rule. COBS 4.2.5G names 'guaranteed', "
                "'protected' or 'secure', or a similar term. The watched list "
                "also includes risk-free, cannot lose, no risk, FSCS, and "
                "FCA-approved, as similar terms for a person to read. Absence "
                "is not a finding that the promotion is fair, clear and not "
                "misleading."
            ),
        )
    names = [name for name, _pattern in hits]
    excerpt = _excerpt(_without_prescribed(usable), hits[0][1])
    return _row(
        "FP-FAIR",
        "fair_clear_not_misleading",
        "flagged_for_review",
        "The text uses a word COBS 4.2.5G tells a firm to justify",
        "cobs-4-2",
        (
            "Phrases matched: " + ", ".join(names) + ". COBS 4.2.5G says the "
            "term should not be used unless it is capable of being fair, "
            "clear and not misleading and the necessary information is "
            "communicated with sufficient clarity and prominence. This checker "
            "does not decide that test. 'Risk-free', 'FSCS', and 'FCA-approved' "
            "are on the watched list as similar terms, not as words quoted "
            "from COBS 4.2.5G."
        ),
        excerpt=excerpt,
    )


def _journey_missing(usable: str) -> list[str]:
    missing = []
    if not _COOLING.search(usable):
        missing.append("COBS 4.12A.18R cooling-off period of at least 24 hours")
    if normalise(PERSONALISED_RISK_CORE) not in normalise(usable) and "personalised risk warning" not in normalise(usable):
        missing.append("COBS 4.12A.20R personalised risk warning")
    if not _CATEGORY.search(usable):
        missing.append("COBS 4.12A.21R categorisation")
    if not _APPROPRIATENESS.search(usable):
        missing.append("COBS 4.12A.28R appropriateness")
    return missing


def _direct_offer_row(usable: str, promotion: dict) -> dict:
    marked = promotion.get("caller_marks_direct_offer") is True
    offer = bool(_OFFER.search(usable))
    if not marked and not offer:
        return _row(
            "FP-DOFP",
            "direct_offer",
            "not_applied",
            "Direct-offer conditions are not scored",
            "cobs-4-12a",
            (
                "The caller did not mark the draft as a direct offer financial "
                "promotion, and the text did not contain buy-now, invest-now, "
                "open-an-account, start-investing, or deposit-and. The glossary "
                "definition was not opened. This checker does not decide that "
                "the draft is, or is not, a direct offer financial promotion."
            ),
        )
    missing = _journey_missing(usable)
    history = (
        "COBS 4.12A.17G says the cooling-off period and the personalised "
        "risk warning are only required the first time that person "
        "communicates a direct offer financial promotion for a restricted "
        "mass market investment to that retail client, and that "
        "appropriateness is only required the first time for that specific "
        "type. This checker cannot see the client's history and does not "
        "assume it is the first occasion. COBS 4.12A.28R(1)(d) names a "
        "person who will transact in a qualifying cryptoasset. COBS 10 and "
        "COBS 10A were not opened."
    )
    if marked and not missing:
        return _row(
            "FP-DOFP",
            "direct_offer",
            "phrase_present",
            "The draft mentions the four direct-offer conditions",
            "cobs-4-12a",
            (
                "The caller marked this as a direct offer. The text mentions "
                "a cooling-off period, a personalised risk warning, "
                "categorisation, and appropriateness. Mentioning them is not "
                "a finding that COBS 4.12A.15R is satisfied. " + history
            ),
        )
    if marked:
        return _row(
            "FP-DOFP",
            "direct_offer",
            "phrase_not_found",
            "The caller marked a direct offer and some condition words are absent",
            "cobs-4-12a",
            (
                "Not found: " + "; ".join(missing) + ". COBS 4.12A.15R names "
                "COBS 4.12A.18R, 4.12A.20R, 4.12A.21R, and 4.12A.28R. Absence "
                "of the words is not a finding that the condition will not "
                "be met in the journey. " + history
            ),
        )
    return _row(
        "FP-DOFP",
        "direct_offer",
        "question_for_approver",
        "The text invites a person to invest and was not marked as a direct offer",
        "cobs-4-12a",
        (
            "The glossary definition of a direct offer financial promotion "
            "was not opened. This checker does not decide that the draft is "
            "one. If the approver decides that it is, the words not found "
            "were: " + ("; ".join(missing) if missing else "none") + ". " + history
        ),
    )


def _offence_row() -> dict:
    return _row(
        "FP-OFFENCE",
        "section_25",
        "recorded_not_applied",
        "Section 25 is recorded and not applied",
        "fsma-s25",
        (
            "Section 25(1) makes contravention of section 21(1) an offence, "
            "with a maximum of two years' imprisonment on indictment, or a "
            "fine, or both. The marketing page states the same maximum. This "
            "checklist does not decide that section 21(1) applies, that an "
            "exemption applies, or that an offence would be committed. The "
            "defence in section 25(2) is not applied."
        ),
    )
