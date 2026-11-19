"""Compare eight clause topics with a playbook. Quotes stay verbatim.

A topic that is not affirmed is not found. A sentence outside the playbook
positions is not reclassified. Nothing in this module is legal advice, and
nothing is marked safe.
"""

from __future__ import annotations

import re
from decimal import Decimal

if __package__ in {None, ""}:
    from cues import (
        AUTO_RENEW_RES,
        DISTRESS_RE,
        GRIEVANCE_RE,
        affirmed,
        ambiguous_sentence,
        any_pattern_affirmed,
        death_pi,
        pattern_affirmed_sentence,
        sentences,
        span_is_denied,
    )
else:
    from .cues import (
        AUTO_RENEW_RES,
        DISTRESS_RE,
        GRIEVANCE_RE,
        affirmed,
        ambiguous_sentence,
        any_pattern_affirmed,
        death_pi,
        pattern_affirmed_sentence,
        sentences,
        span_is_denied,
    )

TOPICS: tuple[str, ...] = (
    "limitation_of_liability",
    "indemnities",
    "data_protection",
    "termination",
    "governing_law",
    "intellectual_property",
    "confidentiality",
    "auto_renewal",
)

_HEADING = re.compile(
    r"^(?:clause\s+)?(\d+(?:\.\d+)*)\s*[.\-–—:)]\s*(.*?)\s*$",
    re.IGNORECASE,
)
_MONEY = re.compile(r"£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)")
_BAD_MONEY = re.compile(r"(?:£|GBP)\s*(?!\d)\S+", re.IGNORECASE)
_NOTICE = re.compile(r"\b(\d{1,3})\s+days?\b", re.IGNORECASE)
_BAD_NOTICE = re.compile(
    r"\b(?:reasonable|tbc|tba|soon|n/a)\s+notice\b|\bnotice\s+(?:tbc|tba|soon)\b",
    re.IGNORECASE,
)
_PLACES = (
    "England and Wales",
    "Northern Ireland",
    "Republic of Ireland",
    "New York",
    "Scotland",
    "England",
    "France",
    "Ireland",
)
_CUSTOMER_OWNS = re.compile(
    r"vests in the customer|customer owns|property of the customer",
    re.IGNORECASE,
)
_SUPPLIER_OWNS = re.compile(
    r"vests in the supplier|supplier owns|property of the supplier",
    re.IGNORECASE,
)
_PROCESSOR = re.compile(r"\b(?:is|as) (?:a |the )?processor\b", re.IGNORECASE)
_ROLE_CLAIM = re.compile(r"\bmy role is\b|\bi am the lawyer\b|\bi am a lawyer\b", re.IGNORECASE)
_CLEARANCE_CLAIM = re.compile(r"\bmy clearance is\b", re.IGNORECASE)

_HEADING_RES = {
    "limitation_of_liability": re.compile(r"limitation of liability|\bliability\b", re.I),
    "indemnities": re.compile(r"indemn", re.I),
    "data_protection": re.compile(r"data protection|personal data|processor", re.I),
    "termination": re.compile(r"termination", re.I),
    "governing_law": re.compile(r"governing law|jurisdiction", re.I),
    "intellectual_property": re.compile(r"intellectual property|\bip rights\b", re.I),
    "confidentiality": re.compile(r"confidential", re.I),
    "auto_renewal": re.compile(r"\brenewal\b", re.I),
}
_BODY_RES = {
    "limitation_of_liability": (
        re.compile(r"limitation of liability", re.I),
        re.compile(r"aggregate liability", re.I),
        re.compile(r"liability (?:is |shall be )?(?:capped|limited|unlimited)", re.I),
        re.compile(r"shall not exceed", re.I),
        re.compile(r"cap on liability", re.I),
    ),
    "indemnities": (re.compile(r"indemnif|hold harmless|\bindemnity\b", re.I),),
    "data_protection": (
        re.compile(r"data protection|personal data|\bprocessor\b|uk gdpr|article 28|data subject", re.I),
    ),
    "termination": (re.compile(r"terminat|notice to terminate", re.I),),
    "governing_law": (re.compile(r"governing law|laws of|this agreement is governed|\bjurisdiction\b", re.I),),
    "intellectual_property": (re.compile(r"intellectual property|\bip rights\b|\bcopyright\b|background ip", re.I),),
    "confidentiality": (re.compile(r"confidential", re.I),),
    "auto_renewal": AUTO_RENEW_RES,
}

ARTICLE_28: tuple[tuple[str, str, tuple[re.Pattern[str], ...]], ...] = (
    ("subject_matter_and_duration", "Article 28(3) subject-matter and duration",
     (re.compile(r"subject[- ]matter and duration", re.I), re.compile(r"subject[- ]matter of the processing", re.I))),
    ("nature_and_purpose", "Article 28(3) nature and purpose",
     (re.compile(r"nature and purpose", re.I),)),
    ("type_of_personal_data", "Article 28(3) type of personal data",
     (re.compile(r"type of personal data", re.I), re.compile(r"types of personal data", re.I))),
    ("categories_of_data_subjects", "Article 28(3) categories of data subjects",
     (re.compile(r"categories of data subjects", re.I),)),
    ("a_documented_instructions", "Article 28(3)(a)",
     (re.compile(r"documented instructions", re.I),)),
    ("b_confidentiality", "Article 28(3)(b)",
     (re.compile(r"duty of confidentiality|obligation of confidentiality|committed themselves to confidentiality", re.I),)),
    ("c_article_32", "Article 28(3)(c)",
     (re.compile(r"article 32", re.I), re.compile(r"security measures required", re.I))),
    ("d_another_processor", "Article 28(3)(d)",
     (re.compile(r"another processor|sub-processor|subprocessor", re.I),)),
    ("e_data_subject_rights", "Article 28(3)(e)",
     (re.compile(r"data subject(?:'s|s'|s)? rights|chapter iii", re.I),)),
    ("f_articles_32_to_36", "Article 28(3)(f)",
     (re.compile(r"articles 32 to 36", re.I), re.compile(r"personal data breach", re.I))),
    ("g_delete_or_return", "Article 28(3)(g)",
     (re.compile(r"delete or return|deletes or returns|return or delete", re.I),)),
    ("h_audits", "Article 28(3)(h)",
     (re.compile(r"\baudits?\b", re.I), re.compile(r"demonstrate compliance", re.I))),
)


def _strings(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    rows = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        rows.append(item.strip())
    return rows


def _blocks(text: str) -> list[dict]:
    current = {"reference": "not found", "heading": "", "lines": []}
    rows: list[dict] = []
    for line in (text or "").splitlines():
        match = _HEADING.match(line.strip())
        if match:
            if current["lines"] or current["reference"] != "not found":
                rows.append(current)
            current = {"reference": match.group(1), "heading": match.group(2).strip(), "lines": []}
        else:
            current["lines"].append(line)
    if current["lines"] or current["reference"] != "not found":
        rows.append(current)
    for row in rows:
        row["body"] = "\n".join(row["lines"]).strip()
    return rows


def _sensitive(sentence: str) -> bool:
    return bool(DISTRESS_RE.search(sentence or "") or GRIEVANCE_RE.search(sentence or ""))


def _heading_topics(heading: str) -> list[str]:
    found = []
    for topic, pattern in _HEADING_RES.items():
        match = pattern.search(heading or "")
        if match and not span_is_denied(heading, match.start()):
            found.append(topic)
    return found


def _sentence_topics(sentence: str) -> list[str]:
    found = []
    for topic, patterns in _BODY_RES.items():
        if any_pattern_affirmed(sentence, patterns):
            found.append(topic)
    if any_pattern_affirmed(sentence, tuple(ARTICLE_28[0][2])):
        if "data_protection" not in found:
            found.append("data_protection")
    if death_pi(sentence)["affirmed"] or death_pi(sentence)["denied"]:
        if "limitation_of_liability" not in found:
            found.append("limitation_of_liability")
    return found


def _gather(text: str) -> tuple[dict[str, list[dict]], list[dict]]:
    grouped = {topic: [] for topic in TOPICS}
    outside: list[dict] = []
    seen = {topic: set() for topic in TOPICS}
    for block in _blocks(text):
        heading_topics = _heading_topics(block["heading"])
        body_sentences = sentences(block["body"])
        if not body_sentences and block["heading"]:
            body_sentences = [block["heading"]]
        sentence_topics: set[str] = set(heading_topics)
        for sentence in body_sentences:
            sentence_topics.update(_sentence_topics(sentence))
        if block["reference"] != "not found" and not sentence_topics:
            quotes = [
                sentence
                for sentence in (body_sentences or ([block["heading"]] if block["heading"] else []))
                if not _sensitive(sentence)
            ]
            outside.append(
                {
                    "reference": block["reference"],
                    "heading": block["heading"],
                    "sentences": quotes,
                    "cue_withheld": len(quotes) < len(body_sentences or []),
                }
            )
            continue
        for topic in sentence_topics:
            for sentence in body_sentences:
                key = (block["reference"], sentence)
                if key in seen[topic]:
                    continue
                # A heading match keeps the block. A body match keeps the
                # sentence that affirmed the topic, and the rest of that block
                # when the heading itself named the topic.
                if _sensitive(sentence) or _ROLE_CLAIM.search(sentence) or _CLEARANCE_CLAIM.search(sentence):
                    continue
                if topic in heading_topics or topic in _sentence_topics(sentence):
                    seen[topic].add(key)
                    grouped[topic].append({"reference": block["reference"], "sentence": sentence})
    return grouped, outside


def _places(text: str) -> list[str]:
    found: list[str] = []
    for sentence in sentences(text):
        working = sentence
        for place in _PLACES:
            pattern = re.compile(re.escape(place), re.IGNORECASE)
            match = pattern.search(working)
            if not match:
                continue
            if not span_is_denied(sentence, match.start()):
                if place not in found:
                    found.append(place)
            working = pattern.sub(" ", working, count=1)
    return found


def _amounts(text: str) -> tuple[list[str], bool]:
    bad = _BAD_MONEY.search(text or "") is not None
    values = []
    for match in _MONEY.finditer(text or ""):
        if span_is_denied(text, match.start()):
            continue
        raw = match.group(1).replace(",", "")
        try:
            parsed = Decimal(raw)
        except Exception:
            bad = True
            continue
        rendered = format(parsed, "f")
        if rendered not in values:
            values.append(rendered)
    return values, bad


def _notice_days(text: str) -> tuple[list[int], bool]:
    bad = False
    for sentence in sentences(text):
        match = _BAD_NOTICE.search(sentence)
        if match and not span_is_denied(sentence, match.start()):
            bad = True
    numbers = []
    for sentence in sentences(text):
        for match in _NOTICE.finditer(sentence):
            if span_is_denied(sentence, match.start()):
                continue
            numbers.append(int(match.group(1)))
    unique = []
    for number in numbers:
        if number not in unique:
            unique.append(number)
    return unique, bad


def _hits(text: str, signals: list[str] | None) -> list[str]:
    if not signals:
        return []
    return [signal for signal in signals if affirmed(text, signal)]


def _position(playbook: dict, topic: str) -> tuple[dict | None, bool]:
    positions = playbook.get("positions") if isinstance(playbook, dict) else None
    if not isinstance(positions, dict) or topic not in positions:
        return None, False
    row = positions.get(topic)
    if not isinstance(row, dict):
        return None, True
    parsed = {
        "preferred_text": row.get("preferred_text") if isinstance(row.get("preferred_text"), str) else None,
        "fallback_text": row.get("fallback_text") if isinstance(row.get("fallback_text"), str) else None,
        "unacceptable_text": row.get("unacceptable_text") if isinstance(row.get("unacceptable_text"), str) else None,
        "preferred_signals": _strings(row.get("preferred_signals")),
        "fallback_signals": _strings(row.get("fallback_signals")),
        "unacceptable_signals": _strings(row.get("unacceptable_signals")),
        "requires_death_carve_out": row.get("requires_death_carve_out") is True,
        "minimum_notice_days": row.get("minimum_notice_days", None),
    }
    broken = any(
        parsed[key] is None
        for key in ("preferred_text", "fallback_text", "unacceptable_text", "preferred_signals", "fallback_signals", "unacceptable_signals")
    )
    if "minimum_notice_days" in row and type(row.get("minimum_notice_days")) is not int:
        broken = True
        parsed["minimum_unparseable"] = True
    else:
        parsed["minimum_unparseable"] = False
    return parsed, broken


def _refs(items: list[dict]) -> list[str]:
    refs = []
    for item in items:
        ref = item["reference"]
        if ref not in refs:
            refs.append(ref)
    return refs


def _ref_label(refs: list[str]) -> str:
    usable = [ref for ref in refs if ref and ref != "not found"]
    if not usable:
        return "not found"
    return "; ".join(usable)


def _base_row(topic: str, items: list[dict]) -> dict:
    quotes = [item["sentence"] for item in items]
    refs = _refs(items)
    return {
        "topic": topic,
        "status": "not_found",
        "result": "not_found",
        "clause_reference": _ref_label(refs) if items else "not found",
        "clause_references": refs if items else [],
        "quotes": quotes,
        "playbook_position": "not found",
        "playbook_text": "not found",
        "lawyer_route": False,
        "below_statutory_floor": False,
        "statutory_floor_source": None,
        "statutory_floor_unverified": False,
        "below_playbook_minimum": False,
        "marked_safe": False,
        "unparseable": False,
        "coerced": False,
        "positions_affirmed": [],
        "voidness_decided": False,
    }


def _set(row: dict, status: str, result: str, position: str, text: str, lawyer: bool) -> None:
    row["status"] = status
    row["result"] = result
    row["playbook_position"] = position
    row["playbook_text"] = text if isinstance(text, str) and text.strip() else "not found"
    row["lawyer_route"] = lawyer


def _floor_source(audience: str, places: list[str]) -> str:
    domestic = {"England and Wales", "England", "Northern Ireland"}
    home = [place for place in places if place in domestic]
    other = [place for place in places if place not in domestic]
    if home and other:
        return "not_chosen"
    if other:
        return "unverified"
    if audience == "consumer":
        return "cra-s65-1"
    if audience == "business":
        return "ucta-s2-1"
    return "not_chosen"


def _apply_floor(row: dict, audience: str, places: list[str]) -> None:
    source = _floor_source(audience, places)
    row["statutory_floor_source"] = source
    if source in {"ucta-s2-1", "cra-s65-1"}:
        row["below_statutory_floor"] = True
    else:
        row["below_statutory_floor"] = False
        row["statutory_floor_unverified"] = True
    row["marked_safe"] = False
    row["voidness_decided"] = False
    row["lawyer_route"] = True


def _article_sentence(text: str, patterns: tuple[re.Pattern[str], ...]) -> str | None:
    """A sentence that affirms the point. A bar on sub-processors is still that point."""

    for sentence in sentences(text):
        for pattern in patterns:
            match = pattern.search(sentence)
            if not match:
                continue
            before = sentence[: match.start()]
            if re.search(
                r"not true that|not the case that|not correct that|does not include|doesn't include",
                before,
                re.IGNORECASE,
            ):
                continue
            if not span_is_denied(sentence, match.start()):
                return sentence
            if re.search(r"\bnot engage another processor without\b", sentence, re.IGNORECASE):
                return sentence
    return None


def article_28_check(text: str, *, role: str, processor_affirmed: bool) -> dict:
    conflict = role == "controller_only" and processor_affirmed
    if role == "unparseable":
        applies = True
        reason = "role_unparseable"
    elif role == "processor" or processor_affirmed or conflict:
        applies = True
        reason = "processor"
    else:
        applies = False
        reason = "not_engaged"
    elements = []
    if applies:
        for point, label, patterns in ARTICLE_28:
            sentence = _article_sentence(text, patterns)
            elements.append(
                {
                    "point": point,
                    "label": label,
                    "status": "present" if sentence else "not_found",
                    "quoted_text": sentence if sentence else "not found",
                    "complies": False,
                }
            )
    not_found = [row["point"] for row in elements if row["status"] == "not_found"]
    return {
        "applies": applies,
        "reason": reason,
        "role_conflict": conflict,
        "elements": elements,
        "not_found": not_found,
        "complies": False,
        "marked_complete": False,
        "marked_safe": False,
    }


def compare(text: str, playbook: dict, audience: str, processing_role: str) -> dict:
    grouped, outside = _gather(text or "")
    processor_sentence = pattern_affirmed_sentence(text or "", _PROCESSOR)
    article = article_28_check(
        text or "",
        role=processing_role,
        processor_affirmed=processor_sentence is not None,
    )
    rows = []
    any_unparseable = False
    coerced = False
    for topic in TOPICS:
        items = grouped[topic]
        row = _base_row(topic, items)
        position, broken = _position(playbook, topic)
        blob = "\n".join(item["sentence"] for item in items)
        if position is None or broken or position["preferred_signals"] is None:
            row["unparseable"] = True
            any_unparseable = True
            _set(row, "unparseable", "lawyer_route", "not found", "not found", True)
            if not items:
                row["quotes"] = []
                row["clause_reference"] = "not found"
            rows.append(row)
            continue
        preferred = _hits(blob, position["preferred_signals"])
        fallback = _hits(blob, position["fallback_signals"])
        unacceptable = _hits(blob, position["unacceptable_signals"])
        row["_hit_signals"] = preferred + fallback + unacceptable
        row["positions_affirmed"] = [
            *(["preferred"] if preferred else []),
            *(["fallback"] if fallback else []),
            *(["unacceptable"] if unacceptable else []),
        ]
        ambiguous = ambiguous_sentence(blob)
        if not items:
            _set(row, "not_found", "not_found", "preferred", position["preferred_text"], False)
            row["quotes"] = []
            row["clause_reference"] = "not found"
            rows.append(row)
            continue
        if topic == "governing_law":
            places = _places(blob)
            row["jurisdictions"] = places
            if len(places) > 1:
                _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
                rows.append(row)
                continue
        if topic == "intellectual_property":
            customer = pattern_affirmed_sentence(blob, _CUSTOMER_OWNS)
            supplier = pattern_affirmed_sentence(blob, _SUPPLIER_OWNS)
            if customer and supplier:
                _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
                rows.append(row)
                continue
        if topic == "termination":
            numbers, bad_notice = _notice_days(blob)
            minimum = position["minimum_notice_days"]
            if position["minimum_unparseable"] or bad_notice:
                row["unparseable"] = True
                any_unparseable = True
                _set(row, "unparseable", "lawyer_route", "not found", "not found", True)
                row["notice_days"] = None
                rows.append(row)
                continue
            if len(numbers) > 1:
                _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
                row["notice_days"] = numbers
                rows.append(row)
                continue
            row["notice_days"] = numbers[0] if numbers else None
            if type(minimum) is int and len(numbers) == 1 and numbers[0] < minimum:
                row["below_playbook_minimum"] = True
                row["marked_safe"] = False
                _set(row, "below_playbook_minimum", "deviation", "preferred", position["preferred_text"], True)
                rows.append(row)
                continue
        if topic == "limitation_of_liability":
            amounts, bad_amount = _amounts(blob)
            if bad_amount:
                row["unparseable"] = True
                any_unparseable = True
                row["amounts"] = []
                _set(row, "unparseable", "lawyer_route", "not found", "not found", True)
                rows.append(row)
                continue
            if len(amounts) > 1:
                _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
                row["amounts"] = amounts
                rows.append(row)
                continue
            death = death_pi(blob)
            places = _places(blob) or _places(text or "")
            if death["affirmed"] and death["denied"]:
                _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
                _apply_floor(row, audience, places)
                rows.append(row)
                continue
            if death["affirmed"]:
                _set(row, "unacceptable", "deviation", "unacceptable", position["unacceptable_text"], True)
                _apply_floor(row, audience, places)
                rows.append(row)
                continue
            row["_needs_carve_out"] = bool(position["requires_death_carve_out"] and not death["denied"])
            row["_carve_out_seen"] = bool(death["denied"])
        if ambiguous:
            _set(row, "ambiguous", "lawyer_route", "not found", "not found", True)
            rows.append(row)
            continue
        if unacceptable and (preferred or fallback):
            _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
            rows.append(row)
            continue
        if unacceptable:
            _set(row, "unacceptable", "deviation", "unacceptable", position["unacceptable_text"], True)
            rows.append(row)
            continue
        if row.get("_needs_carve_out"):
            _set(row, "incomplete", "lawyer_route", "preferred", position["preferred_text"], True)
            row["death_or_personal_injury"] = "not found"
            rows.append(row)
            continue
        if preferred and not fallback:
            _set(row, "preferred", "in_playbook", "preferred", position["preferred_text"], False)
        elif fallback and not preferred:
            _set(row, "fallback", "in_playbook", "fallback", position["fallback_text"], False)
        elif preferred and fallback:
            _set(row, "ambiguous", "lawyer_route", "not found", "not found", True)
        else:
            _set(row, "outside_playbook", "lawyer_route", "not found", "not found", True)
        if topic == "data_protection" and article["applies"] and article["not_found"]:
            _set(row, "incomplete_processor_terms", "lawyer_route", "preferred", position["preferred_text"], True)
            row["marked_safe"] = False
        if topic == "data_protection" and article["role_conflict"]:
            _set(row, "conflicting", "lawyer_route", "not found", "not found", True)
        rows.append(row)
    outside_rows = []
    for item in outside:
        outside_rows.append(
            {
                "topic": "outside_playbook",
                "status": "outside_playbook",
                "result": "lawyer_route",
                "clause_reference": item["reference"],
                "clause_references": [item["reference"]],
                "quotes": list(item.get("sentences") or []),
                "cue_withheld": bool(item.get("cue_withheld")),
                "playbook_position": "not found",
                "playbook_text": "not found",
                "lawyer_route": True,
                "below_statutory_floor": False,
                "statutory_floor_source": None,
                "statutory_floor_unverified": False,
                "below_playbook_minimum": False,
                "marked_safe": False,
                "unparseable": False,
                "coerced": False,
                "positions_affirmed": [],
                "voidness_decided": False,
                "heading": item["heading"],
            }
        )
    for row in rows:
        signals = row.pop("_hit_signals", [])
        quotes = row.get("quotes") or []
        if signals and quotes:
            row["quotes"] = sorted(
                quotes,
                key=lambda sentence: 0 if any(affirmed(sentence, signal) for signal in signals) else 1,
            )
        for key in [key for key in row if str(key).startswith("_")]:
            row.pop(key, None)
    return {
        "rows": rows,
        "outside_rows": outside_rows,
        "article_28": article,
        "processor_affirmed": processor_sentence is not None,
        "jurisdictions": _places(text or ""),
        "unparseable": any_unparseable,
        "coerced": coerced,
    }
