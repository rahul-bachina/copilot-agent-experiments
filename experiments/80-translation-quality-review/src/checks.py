"""Translation checks on aligned segments.

Alignment is Experiment 79 align(). Masking is not done here.
A lexical overlap score is not a quality score. A different language
with overlap below the Experiment 79 high threshold is low confidence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

if __package__ in {None, ""}:
    from risk import distress_sentences, injection_signals, risk_categories, sensitive_categories
    from siblings import neighbours
else:
    from .risk import distress_sentences, injection_signals, risk_categories, sensitive_categories
    from .siblings import neighbours

ROOT = Path(__file__).resolve().parents[1]
HIGH_OVERLAP = 0.84
MEANING_OVERLAP = 0.45

CHECKS = (
    "omitted_content",
    "added_content",
    "changed_number",
    "changed_amount",
    "changed_date",
    "changed_deadline",
    "changed_phone",
    "changed_url",
    "reversed_negation",
    "dropped_negation",
    "softened_obligation",
    "strengthened_obligation",
    "mistranslated_term",
    "untranslated_segment",
    "inconsistent_terminology",
    "register",
    "added_exception",
    "dropped_exception",
    "meaning_shift",
    "low_confidence_alignment",
    "high_risk_content",
    "duplicate_conflict",
    "conflicting_values",
)

MEANING_TYPES = frozenset({
    "changed_number",
    "changed_amount",
    "changed_date",
    "changed_deadline",
    "reversed_negation",
    "dropped_negation",
    "softened_obligation",
    "strengthened_obligation",
    "added_exception",
    "dropped_exception",
    "mistranslated_term",
})

_URL = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_PHONE = re.compile(
    r"(?:\+44[\s-]?\d(?:[\s-]?\d){9,12}|07\d{3}[\s-]?\d{6}|0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4})"
)
_AMOUNT = re.compile(
    r"£\s*\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\s*(?:GBP|pounds)\b",
    re.IGNORECASE,
)
_DATE = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b"
    r"|\b\d{4}/\d{2}/\d{2}\b"
    r"|\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b"
    r"|\b\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4}\b",
    re.IGNORECASE,
)
_DEADLINE_COUNT = re.compile(
    r"\bwithin\s+(\d+)\s+(?:working\s+)?days\b"
    r"|\b(\d+)\s+working\s+days\b"
    r"|\bo fewn\s+(\d+)\s+diwrnod"
    r"|\b(\d+)\s+diwrnod(?:au)?(?:\s+gwaith)?\b"
    r"|\bw ciągu\s+(\d+)\s+dni\b"
    r"|\b(\d+)\s+dni roboczych\b",
    re.IGNORECASE,
)
_DEADLINE_CUE = re.compile(
    r"\b(?:deadline|dyddiad cau|termin|no later than|the last day|time limit|erbyn)\b",
    re.IGNORECASE,
)
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")
_NOT_NEGATION = re.compile(r"\bno later than\b|\bno earlier than\b", re.IGNORECASE)
_NEGATION = re.compile(
    r"\b(?:must not|do not|does not|did not|cannot|can't|mustn't|don't|doesn't|didn't|"
    r"not|never|neither|without|ddim|nid|heb|byth|peidiwch|paid|beidio|"
    r"nie|nigdy)\b",
    re.IGNORECASE,
)
_STRONG = (
    "is required to",
    "are required to",
    "mae'n rhaid",
    "rhaid",
    "must",
    "shall",
    "musi",
    "należy",
    "jest zobowiązany",
)
_MEDIUM = ("ought to", "should", "dylai", "powinien", "powinna")
_WEAK = (
    "is permitted to",
    "are permitted to",
    "gallwch",
    "gellir",
    "cewch",
    "caiff",
    "gall",
    "may",
    "może",
    "can",
)
_EXCEPTION = re.compile(
    r"\b(?:unless|except|save where|on condition that|provided that|os nad|chyba że|z wyjątkiem)\b",
    re.IGNORECASE,
)
_INFORMAL = {
    "en": re.compile(
        r"\b(?:gonna|wanna|hiya|cheers mate|you guys|kiddos)\b",
        re.IGNORECASE,
    ),
    "cy": re.compile(r"\b(?:shwmae|hwyl fawr|be' di)\b", re.IGNORECASE),
    "pl": re.compile(r"\b(?:siema|nara)\b", re.IGNORECASE),
}


def pinned_glossary() -> dict:
    return json.loads((ROOT / "fixtures" / "glossary.json").read_text(encoding="utf-8"))


def read_date(value: object, question) -> dict:
    """Parse one date. Do not coerce. Do not read today's date."""

    tools = neighbours()
    reading = tools["with_question_date"](tools["parse_date"](value), question)
    reading["coerced"] = False
    return reading


def _blank(text: str, spans: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for index in range(max(0, start), min(len(chars), end)):
            chars[index] = " "
    return "".join(chars)


def _amount_key(raw: str) -> str:
    cleaned = re.sub(r"[£,\s]|GBP|pounds", "", raw, flags=re.IGNORECASE)
    if not cleaned:
        return raw.casefold()
    if "." in cleaned:
        whole, fraction = cleaned.split(".", 1)
        fraction = (fraction + "00")[:2]
        return f"{int(whole)}.{fraction}"
    return f"{int(cleaned)}.00"


def _dates_in(text: str, question) -> tuple[list[str], list[tuple[int, int]], list[dict]]:
    keys = []
    spans = []
    readings = []
    for match in _DATE.finditer(text or ""):
        spans.append((match.start(), match.end()))
        reading = read_date(match.group(0), question)
        readings.append({"text": match.group(0), **{k: reading.get(k) for k in ("iso", "unparseable", "ambiguous", "future", "reason", "coerced")}})
        if reading.get("iso") and not reading.get("ambiguous") and not reading.get("unparseable"):
            keys.append(reading["iso"])
        else:
            keys.append(f"unreadable:{match.group(0).casefold()}")
    return keys, spans, readings


def _counts(pattern: re.Pattern[str], text: str) -> tuple[list[str], list[tuple[int, int]]]:
    found = []
    spans = []
    for match in pattern.finditer(text or ""):
        spans.append((match.start(), match.end()))
        digits = next((group for group in match.groups() if group), None)
        if digits is None:
            digits = re.sub(r"\D", "", match.group(0))
        found.append(digits)
    return found, spans


def _strength(text: str) -> int | None:
    folded = (text or "").casefold()
    best = None
    for rank, phrases in ((3, _STRONG), (2, _MEDIUM), (1, _WEAK)):
        for phrase in phrases:
            if re.search(rf"\b{re.escape(phrase)}\b", folded):
                best = rank if best is None else max(best, rank)
    return best


def _has_negation(text: str) -> bool:
    cleaned = _NOT_NEGATION.sub(" ", text or "")
    return _NEGATION.search(cleaned) is not None


def _has_exception(text: str) -> bool:
    return _EXCEPTION.search(text or "") is not None


def _small_people(text: str) -> bool:
    return bool(neighbours()["people_count_spans"](text or ""))


def _empty_numbers() -> dict:
    return {
        "values_published": False,
        "published_count": None,
        "published_difference": None,
        "published_percentage": None,
        "headcount": None,
        "delta": None,
        "source_values": None,
        "target_values": None,
    }


def _flag(kind: str, segment_id: str | None, detail: str, *, publish: dict | None = None) -> dict:
    row = {
        "type": kind,
        "segment_id": segment_id,
        "detail": detail,
        **_empty_numbers(),
    }
    if publish:
        row.update(publish)
    return row


def _pair_flags(source: str, target: str, *, target_language: str, document_kind: str, glossary: dict, question, segment_id: str, overlap: float) -> list[dict]:
    flags = []
    url_s = [match.group(0).rstrip(".,);") for match in _URL.finditer(source)]
    url_t = [match.group(0).rstrip(".,);") for match in _URL.finditer(target)]
    url_spans_s = [(m.start(), m.end()) for m in _URL.finditer(source)]
    url_spans_t = [(m.start(), m.end()) for m in _URL.finditer(target)]
    if sorted(item.casefold() for item in url_s) != sorted(item.casefold() for item in url_t):
        flags.append(_flag(
            "changed_url",
            segment_id,
            "A URL differs.",
            publish={
                "values_published": True,
                "source_values": sorted(item.casefold() for item in url_s),
                "target_values": sorted(item.casefold() for item in url_t),
            },
        ))

    phone_s, phone_spans_s = _counts(_PHONE, source)
    phone_t, phone_spans_t = _counts(_PHONE, target)
    if sorted(phone_s) != sorted(phone_t):
        flags.append(_flag("changed_phone", segment_id, "A phone number differs. The digits are not copied."))

    amount_s = [_amount_key(match.group(0)) for match in _AMOUNT.finditer(source)]
    amount_t = [_amount_key(match.group(0)) for match in _AMOUNT.finditer(target)]
    amount_spans_s = [(m.start(), m.end()) for m in _AMOUNT.finditer(source)]
    amount_spans_t = [(m.start(), m.end()) for m in _AMOUNT.finditer(target)]
    if sorted(amount_s) != sorted(amount_t):
        flags.append(_flag(
            "changed_amount",
            segment_id,
            "An amount differs.",
            publish={
                "values_published": True,
                "source_values": sorted(amount_s),
                "target_values": sorted(amount_t),
                "published_difference": None,
                "published_percentage": None,
            },
        ))

    date_s, date_spans_s, _readings_s = _dates_in(source, question)
    date_t, date_spans_t, _readings_t = _dates_in(target, question)
    if sorted(date_s) != sorted(date_t):
        conflicting = len(set(date_s)) > 1 or len(set(date_t)) > 1
        if conflicting:
            flags.append(_flag("conflicting_values", segment_id, "More than one date is in a segment. Neither is chosen."))
        flags.append(_flag(
            "changed_date",
            segment_id,
            "A date differs or could not be read as the same day.",
            publish={
                "values_published": True,
                "source_values": date_s,
                "target_values": date_t,
            },
        ))
    elif any(key.startswith("unreadable:") for key in date_s + date_t):
        flags.append(_flag("conflicting_values", segment_id, "A date in the segment could not be read. It was not coerced."))

    count_s, count_spans_s = _counts(_DEADLINE_COUNT, source)
    count_t, count_spans_t = _counts(_DEADLINE_COUNT, target)
    cue_s = _DEADLINE_CUE.search(source) is not None
    cue_t = _DEADLINE_CUE.search(target) is not None
    if sorted(count_s) != sorted(count_t) or (sorted(date_s) != sorted(date_t) and (cue_s or cue_t)):
        flags.append(_flag("changed_deadline", segment_id, "A deadline count or a deadline date differs."))

    source_blank = _blank(source, url_spans_s + phone_spans_s + amount_spans_s + date_spans_s + count_spans_s)
    target_blank = _blank(target, url_spans_t + phone_spans_t + amount_spans_t + date_spans_t + count_spans_t)
    numbers_s = _NUMBER.findall(source_blank)
    numbers_t = _NUMBER.findall(target_blank)
    if sorted(numbers_s) != sorted(numbers_t):
        small = _small_people(source) or _small_people(target)
        publish = _empty_numbers()
        if not small:
            publish = {
                "values_published": True,
                "source_values": numbers_s,
                "target_values": numbers_t,
                "published_count": None,
                "published_difference": None,
                "published_percentage": None,
                "headcount": None,
                "delta": None,
            }
        flags.append(_flag(
            "changed_number",
            segment_id,
            "A number differs. A headcount below 5 is not published.",
            publish=publish,
        ))

    neg_s = _has_negation(source_blank)
    neg_t = _has_negation(target_blank)
    if neg_s and not neg_t:
        flags.append(_flag("dropped_negation", segment_id, "Negation is in the source and not in the target."))
    elif neg_t and not neg_s:
        flags.append(_flag("reversed_negation", segment_id, "Negation is in the target and not in the source."))

    strength_s = _strength(source_blank)
    strength_t = _strength(target_blank)
    both_prohibit = neg_s and neg_t
    if strength_s is not None and strength_t is not None and strength_s > strength_t:
        flags.append(_flag("softened_obligation", segment_id, "An obligation is weaker in the target."))
    elif strength_s is not None and strength_t is not None and strength_t > strength_s:
        flags.append(_flag("strengthened_obligation", segment_id, "An obligation is stronger in the target."))
    elif strength_s is not None and strength_t is None and not both_prohibit:
        flags.append(_flag("softened_obligation", segment_id, "An obligation in the source has no listed modal in the target."))
    elif strength_t is not None and strength_s is None and not both_prohibit:
        flags.append(_flag("strengthened_obligation", segment_id, "The target has a listed modal the source does not."))

    if _has_exception(target) and not _has_exception(source):
        flags.append(_flag("added_exception", segment_id, "The target adds an exception or a condition."))
    if _has_exception(source) and not _has_exception(target):
        flags.append(_flag("dropped_exception", segment_id, "The source exception or condition is not in the target."))

    if target_language != "en" and source.casefold().strip() == target.casefold().strip() and source.strip():
        flags.append(_flag("untranslated_segment", segment_id, "The target repeats the source. The languages differ."))
    elif (
        target_language != "en"
        and len(source.strip()) >= 40
        and source.casefold().strip() in target.casefold()
    ):
        flags.append(_flag("untranslated_segment", segment_id, "A long source sentence is still in the target."))

    if document_kind == "public_information":
        informal = _INFORMAL.get(target_language)
        if informal and informal.search(target):
            flags.append(_flag("register", segment_id, "An informal marker is in a public-information target."))

    affirmed = neighbours()["affirmed"]
    for term in glossary.get("terms") or []:
        if not isinstance(term, dict):
            continue
        source_term = term.get("en") if isinstance(term.get("en"), str) else ""
        if not source_term or not affirmed(source, source_term):
            continue
        expected = term.get(target_language) if isinstance(term.get(target_language), str) else ""
        if expected and expected.casefold() not in target.casefold():
            flags.append(_flag(
                "mistranslated_term",
                segment_id,
                f"The pinned term {term.get('id')} is not the pinned target wording.",
            ))

    kinds = {row["type"] for row in flags}
    if overlap >= MEANING_OVERLAP and kinds & MEANING_TYPES:
        flags.append(_flag("meaning_shift", segment_id, "Similar wording does not carry the same facts."))
    return flags


def _rendering(term: dict, target: str, language: str) -> str:
    expected = term.get(language) if isinstance(term.get(language), str) else ""
    alternatives = (term.get("alternatives") or {}).get(language) or []
    folded = target.casefold()
    if expected and expected.casefold() in folded:
        return expected.casefold()
    if isinstance(alternatives, list):
        for alternative in alternatives:
            if isinstance(alternative, str) and alternative.casefold() in folded:
                return alternative.casefold()
    return "absent"


def analyse(
    source_segments: list,
    target_segments: list,
    *,
    target_language: str,
    document_kind: str,
    glossary: dict | None = None,
    question,
) -> dict:
    """Align segments and return flags. Do not publish, send, or overwrite."""

    tools = neighbours()
    glossary = glossary if isinstance(glossary, dict) else pinned_glossary()
    flags: list[dict] = []
    unparseable: list[dict] = []
    rows = []

    def usable(segments: list, side: str) -> list[dict]:
        prepared = []
        seen: dict[str, set[str]] = {}
        clean = []
        for index, segment in enumerate(segments or []):
            if not isinstance(segment, dict):
                unparseable.append({"side": side, "reason": "segment_not_object", "coerced": False})
                continue
            segment_id = segment.get("segment_id")
            text = segment.get("text")
            if not isinstance(segment_id, str) or not segment_id:
                unparseable.append({"side": side, "reason": "segment_id_unreadable", "coerced": False})
                continue
            if not isinstance(text, str):
                unparseable.append({"side": side, "segment_id": segment_id, "reason": "text_not_a_string", "coerced": False})
                continue
            seen.setdefault(segment_id, set()).add(text)
            clean.append((index, segment_id, text, segment.get("number") if isinstance(segment.get("number"), str) else ""))
        duplicated = {key for key, bodies in seen.items() if len(bodies) > 1}
        for index, segment_id, text, number in clean:
            prepared.append({
                "index": index,
                "segment_id": segment_id,
                "text": text,
                "number": number,
                "duplicate": segment_id in duplicated,
            })
        for segment_id in sorted(duplicated):
            flags.append(_flag("duplicate_conflict", segment_id, "The same segment id has more than one wording. Neither is chosen."))
        return prepared

    source_rows = usable(source_segments, "source")
    target_rows = usable(target_segments, "target")
    source_map = {row["segment_id"]: row["text"] for row in source_rows if not row["duplicate"]}
    target_map = {row["segment_id"]: row["text"] for row in target_rows if not row["duplicate"]}
    # A duplicated id is withheld from ordinary pairing. Both wordings stay flagged.
    source_clauses = [
        {
            "clause_id": row["segment_id"],
            "number": row["number"],
            "heading": "",
            "text": row["text"],
            "duplicate_conflict": row["duplicate"],
            "citation": {"segment_id": row["segment_id"]},
        }
        for row in source_rows
    ]
    target_clauses = [
        {
            "clause_id": row["segment_id"],
            "number": row["number"],
            "heading": "",
            "text": row["text"],
            "duplicate_conflict": row["duplicate"],
            "citation": {"segment_id": row["segment_id"]},
        }
        for row in target_rows
    ]
    aligned = tools["align"](source_clauses, target_clauses) if source_clauses or target_clauses else []
    low = 0
    term_renderings: dict[str, set[str]] = {}
    affirmed = tools["affirmed"]
    for row in aligned:
        change = row.get("change_class")
        baseline = row.get("baseline") if isinstance(row.get("baseline"), dict) else None
        other = row.get("other") if isinstance(row.get("other"), dict) else None
        if change == "deleted" and baseline:
            flags.append(_flag("omitted_content", baseline.get("clause_id"), "A source segment has no target segment."))
            rows.append({"change_class": change, "segment_id": baseline.get("clause_id"), "low_confidence": False, "lexical_overlap": None})
            continue
        if change == "added" and other:
            flags.append(_flag("added_content", other.get("clause_id"), "A target segment has no source segment."))
            rows.append({"change_class": change, "segment_id": other.get("clause_id"), "low_confidence": False, "lexical_overlap": None})
            continue
        if change == "duplicate_conflict":
            rows.append({"change_class": change, "segment_id": None, "low_confidence": False, "lexical_overlap": None, "chosen_text": None})
            continue
        if not isinstance(baseline, dict) or not isinstance(other, dict):
            flags.append(_flag("low_confidence_alignment", None, "The alignment did not cite both sides."))
            low += 1
            continue
        segment_id = baseline.get("clause_id")
        source_text = source_map.get(segment_id, "")
        target_text = target_map.get(other.get("clause_id"), "")
        overlap = row.get("score")
        if not isinstance(overlap, (int, float)):
            overlap = tools["jaccard"](tools["tokens"](source_text), tools["tokens"](target_text))
        overlap = float(overlap)
        cross_language_uncertain = target_language != "en" and overlap < HIGH_OVERLAP
        row_low = bool(row.get("low_confidence")) or cross_language_uncertain or change in {"split", "merged"}
        if row_low:
            low += 1
            flags.append(_flag(
                "low_confidence_alignment",
                segment_id,
                "The alignment is not certain. Lexical overlap is not a translation score.",
            ))
        if source_text.strip() and not target_text.strip():
            flags.append(_flag("omitted_content", segment_id, "The target segment is empty."))
        pair = _pair_flags(
            source_text,
            target_text,
            target_language=target_language,
            document_kind=document_kind,
            glossary=glossary,
            question=question,
            segment_id=segment_id,
            overlap=overlap,
        )
        flags.extend(pair)
        for term in glossary.get("terms") or []:
            if not isinstance(term, dict):
                continue
            source_term = term.get("en") if isinstance(term.get("en"), str) else ""
            if source_term and affirmed(source_text, source_term):
                term_renderings.setdefault(str(term.get("id")), set()).add(
                    _rendering(term, target_text, target_language)
                )
        rows.append({
            "change_class": change,
            "segment_id": segment_id,
            "low_confidence": row_low,
            "lexical_overlap": round(overlap, 4),
            "quality_score": None,
        })

    for term_id, renderings in term_renderings.items():
        concrete = {item for item in renderings if item != "absent"}
        if len(concrete) > 1:
            flags.append(_flag(
                "inconsistent_terminology",
                None,
                f"The pinned term {term_id} is worded in more than one way. Neither wording is chosen.",
            ))

    return {
        "flags": flags,
        "rows": rows,
        "low_confidence_count": low,
        "unparseable": unparseable,
        "checks_performed": list(CHECKS),
        "alignment_reused": "exp-79-document-comparison align()",
        "experiment_38_compare_called": False,
        "quality_score": None,
    }


def joined_text(segments: list) -> str:
    parts = []
    for segment in segments or []:
        if isinstance(segment, dict) and isinstance(segment.get("text"), str):
            parts.append(segment["text"])
    return "\n".join(parts)


def content_risk(source_segments: list, target_segments: list) -> list[dict]:
    found = []
    for side, segments in (("source", source_segments), ("target", target_segments)):
        for segment in segments or []:
            if not isinstance(segment, dict) or not isinstance(segment.get("text"), str):
                continue
            categories = risk_categories(segment["text"])
            if categories:
                found.append({
                    "segment_id": segment.get("segment_id"),
                    "side": side,
                    "categories": categories,
                    "routed_regardless_of_score": True,
                    "cue_copied": False,
                })
    return found


def sensitive_report(source_segments: list, target_segments: list) -> dict:
    categories: list[str] = []
    for segments in (source_segments, target_segments):
        for segment in segments or []:
            if isinstance(segment, dict) and isinstance(segment.get("text"), str):
                for name in sensitive_categories(segment["text"]):
                    if name not in categories:
                        categories.append(name)
    return {
        "routed": bool(categories),
        "categories": categories,
        "cue_copied": False,
        "source_seen": False,
    }


def injection_report(*texts: str) -> dict:
    signals: list[str] = []
    for text in texts:
        for signal in injection_signals(text or ""):
            if signal not in signals:
                signals.append(signal)
    return {"signals": signals, "followed": False, "cue_copied": False}


def glossary_differences(caller: object, pinned: dict) -> dict:
    """Compare a caller glossary with the pinned one. Do not apply the caller glossary."""

    if caller is None:
        return {
            "present": False,
            "applied": False,
            "differences": [],
            "unparseable": False,
        }
    if not isinstance(caller, dict):
        return {
            "present": True,
            "applied": False,
            "differences": [],
            "unparseable": True,
        }
    terms = caller.get("terms")
    if terms is None:
        terms = []
    if not isinstance(terms, list):
        return {"present": True, "applied": False, "differences": [], "unparseable": True}
    pinned_terms = {row.get("id"): row for row in pinned.get("terms") or [] if isinstance(row, dict)}
    differences = []
    for term in terms:
        if not isinstance(term, dict):
            return {"present": True, "applied": False, "differences": [], "unparseable": True}
        term_id = term.get("id")
        pinned_row = pinned_terms.get(term_id)
        if pinned_row is None:
            differences.append({"id": term_id, "reason": "not_in_pinned_glossary", "applied": False})
            continue
        for language in ("en", "cy", "pl"):
            caller_value = term.get(language)
            pinned_value = pinned_row.get(language)
            if caller_value is None:
                continue
            if not isinstance(caller_value, str) or caller_value != pinned_value:
                differences.append({
                    "id": term_id,
                    "language": language,
                    "pinned": pinned_value,
                    "caller": caller_value if isinstance(caller_value, str) else None,
                    "applied": False,
                })
    return {
        "present": True,
        "applied": False,
        "differences": differences,
        "unparseable": False,
    }
