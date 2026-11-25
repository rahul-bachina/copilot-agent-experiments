"""Material differences between two clause texts.

A difference is a flag for a person. It is not a view on which text is better,
and it is not legal advice. Reformatting that does not change these checks is
not a material difference. A real difference that sits inside similar wording
is still a material difference.

"It is not true that the clause includes an exception" does not count as an
exception. An unreadable figure is flagged and is not turned into 0.
"""

from __future__ import annotations

import re

if __package__ in {None, ""}:
    from cues import carve_out_affirmed
    from dates import parse_date, with_question_date
    from mask import people_count_spans
    from negate import denied_at, sentences
    from siblings import neighbours
else:
    from .cues import carve_out_affirmed
    from .dates import parse_date, with_question_date
    from .mask import people_count_spans
    from .negate import denied_at, sentences
    from .siblings import neighbours

CHECKS = (
    "obligation_strength",
    "negation",
    "numbers",
    "amounts",
    "percentages",
    "dates",
    "periods",
    "notice_windows",
    "parties",
    "definitions",
    "carve_outs",
    "duplicates",
    "hidden_or_tracked",
    "alignment_confidence",
)

_OBLIGATIONS: tuple[tuple[int, re.Pattern[str]], ...] = (
    (3, re.compile(r"\b(?:shall|must|has to|is required to|is obliged to|is obligated to)\b", re.I)),
    (2, re.compile(r"\b(?:should|ought to|is expected to)\b", re.I)),
    (1, re.compile(r"\b(?:may|can|is permitted to|is allowed to)\b", re.I)),
)
_NEGATION = re.compile(r"\b(?:not|no|never|without|neither|nor)\b|n't", re.I)
_META = re.compile(r"\bnot\s+(?:true|the case|correct)\s+that\b", re.I)
_AMOUNT = re.compile(r"(?:£|GBP)\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b", re.I)
_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|per cent)\b", re.I)
_PERIOD = re.compile(
    r"\b(\d+)\s+(day|days|week|weeks|month|months|year|years)\b",
    re.I,
)
_NOTICE = re.compile(
    r"\b(\d+)\s+(day|days|week|weeks|month|months|year|years)(?:['’]s|['’])?\s+notice\b|"
    r"\bnotice\s+of\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)\b",
    re.I,
)
_PARTY = re.compile(
    r"\b([A-Z][A-Za-z&]+(?:\s+[A-Z][A-Za-z&]+){0,4})\s+\((?:the\s+)?(Buyer|Supplier|Customer|Contractor|Authority|Council)\)"
)
_DEFINITION = re.compile(r"^([A-Za-z][^.]{0,48}?)\s+means\s+(.+)$", re.I)
_LOCAL_DATE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{4}|"
    r"\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})\b"
)
_HIDDEN = (
    re.compile(r"<!--.*?-->", re.S),
    re.compile(r"<w:del\b.*?</w:del>", re.S | re.I),
    re.compile(r"<w:ins\b.*?</w:ins>", re.S | re.I),
    re.compile(r"\[deleted:.*?\]", re.S | re.I),
    re.compile(r"\[inserted:.*?\]", re.S | re.I),
    re.compile(r"~~.*?~~", re.S),
    re.compile(r"<span[^>]*display\s*:\s*none[^>]*>.*?</span>", re.S | re.I),
)
_ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
_THOUSANDS = re.compile(r"(\d),(\d{3})")


def hidden_or_tracked(text: str) -> bool:
    if not text:
        return False
    if _ZERO_WIDTH.search(text):
        return True
    return any(pattern.search(text) for pattern in _HIDDEN)


def visible_text(text: str) -> str:
    """Keep tracked words. Drop only the markup, so a tracked figure is not lost."""

    if not text:
        return ""
    cleaned = text
    cleaned = re.sub(r"<!--", " ", cleaned)
    cleaned = re.sub(r"-->", " ", cleaned)
    cleaned = re.sub(r"</?w:(?:del|ins)[^>]*>", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\[(deleted|inserted):\s*", " ", cleaned, flags=re.I)
    cleaned = cleaned.replace("]", " ")
    cleaned = cleaned.replace("~~", " ")
    cleaned = re.sub(r"</?span[^>]*>", " ", cleaned, flags=re.I)
    cleaned = _ZERO_WIDTH.sub("", cleaned)
    return cleaned


def obligation_ranks(text: str) -> list[int]:
    ranks: list[int] = []
    for sentence in sentences(visible_text(text)):
        for rank, pattern in _OBLIGATIONS:
            for match in pattern.finditer(sentence):
                if _may_is_not_modal(sentence, match):
                    continue
                if _modal_denied(sentence, match):
                    continue
                ranks.append(rank)
    return ranks


def _modal_denied(sentence: str, match: re.Match[str]) -> bool:
    """Only a negation immediately before the modal cancels it.

    'shall not' keeps the modal. 'without consent, and the buyer shall'
    does not cancel the later modal. A wider window is still used when
    deciding whether a carve-out or an instruction is affirmed.
    """

    before = sentence[: match.start()]
    return bool(re.search(r"\b(?:not|never|no)\s*$", before, re.I))


def _may_is_not_modal(sentence: str, match: re.Match[str]) -> bool:
    if match.group(0).casefold() not in {"may", "can"}:
        return False
    before = sentence[: match.start()]
    after = sentence[match.end() :]
    if re.search(r"\d\s*$", before):
        return True
    if re.match(r"\s+\d{4}\b", after):
        return True
    if match.group(0).casefold() == "may" and re.match(r"\s+tree\b", after, re.I):
        return True
    return False


def negation_count(text: str) -> int:
    """Count negation words, including a denial such as 'not true that'."""

    count = 0
    for sentence in sentences(visible_text(text)):
        count += len(list(_NEGATION.finditer(sentence)))
    return count


def _fold_numbers(text: str) -> str:
    folded = visible_text(text)
    while True:
        updated = _THOUSANDS.sub(r"\1\2", folded)
        if updated == folded:
            return folded
        folded = updated


def numbers_in(text: str) -> list[str]:
    raw = neighbours()["extract_numbers"](_fold_numbers(text))
    suppressed = set()
    for _start, _end, count in people_count_spans(visible_text(text)):
        if count is not None and count < 5:
            suppressed.add(str(count))
    published = []
    for number in raw:
        if number in suppressed:
            continue
        published.append(number)
    return published


def amounts_in(text: str) -> list[str]:
    found = []
    for match in _AMOUNT.finditer(_fold_numbers(text)):
        token = re.sub(r"\s+", "", match.group(0).upper().replace("GBP", "£"))
        if token not in found:
            found.append(token)
    return found


def percentages_in(text: str) -> list[str]:
    if people_count_spans(visible_text(text)):
        return []
    found = []
    for match in _PERCENT.finditer(visible_text(text)):
        token = re.sub(r"\s+", "", match.group(0).casefold()).replace("percent", "%")
        if token not in found:
            found.append(token)
    return found


def periods_in(text: str) -> list[str]:
    found = []
    for match in _PERIOD.finditer(visible_text(text)):
        unit = match.group(2).casefold().rstrip("s")
        token = f"{int(match.group(1))} {unit}"
        if token not in found:
            found.append(token)
    return found


def notice_windows(text: str) -> list[str]:
    found = []
    for match in _NOTICE.finditer(visible_text(text)):
        number = match.group(1) or match.group(3)
        unit = match.group(2) or match.group(4)
        token = f"{int(number)} {unit.casefold().rstrip('s')}"
        if token not in found:
            found.append(token)
    return found


def dates_in(text: str, *, question) -> tuple[list[str], list[dict]]:
    found: list[str] = []
    problems: list[dict] = []
    seen: set[str] = set()
    extracted = list(neighbours()["extract_dates"](visible_text(text)))
    for match in _LOCAL_DATE.finditer(visible_text(text)):
        if match.group(0) not in extracted:
            extracted.append(match.group(0))
    for token in extracted:
        if token in seen:
            continue
        seen.add(token)
        reading = with_question_date(parse_date(token), question)
        if reading.get("unparseable") or reading.get("ambiguous") or reading.get("future"):
            problems.append({"token": token, "reason": reading.get("reason"), "coerced": False})
            continue
        if reading.get("iso") and reading["iso"] not in found:
            found.append(reading["iso"])
    return found, problems


def parties_in(text: str) -> list[str]:
    found = []
    for match in _PARTY.finditer(text or ""):
        label = f"{match.group(1)} ({match.group(2).casefold()})"
        if label not in found:
            found.append(label)
    return found


def definitions_in(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for sentence in sentences(visible_text(text)):
        match = _DEFINITION.match(sentence.strip())
        if not match:
            continue
        if denied_at(sentence, "means", sentence.casefold().find("means")):
            continue
        term = re.sub(r"\s+", " ", match.group(1)).strip(" \"'").casefold()
        meaning = re.sub(r"\s+", " ", match.group(2)).strip()
        if term and term not in found:
            found[term] = meaning
    return found


def compare_texts(left: str, right: str, *, question) -> dict:
    """Compare two clause bodies. Nothing unreadable becomes zero."""

    flags: list[str] = []
    incomplete: list[str] = []
    left_ranks = obligation_ranks(left)
    right_ranks = obligation_ranks(right)
    if sorted(left_ranks) != sorted(right_ranks):
        flags.append("obligation_strength")
    if negation_count(left) != negation_count(right):
        flags.append("negation")
    left_numbers = numbers_in(left)
    right_numbers = numbers_in(right)
    if left_numbers != right_numbers:
        flags.append("numbers")
    if amounts_in(left) != amounts_in(right):
        flags.append("amounts")
    if percentages_in(left) != percentages_in(right):
        flags.append("percentages")
    left_dates, left_problems = dates_in(left, question=question)
    right_dates, right_problems = dates_in(right, question=question)
    if left_problems or right_problems:
        incomplete.append("dates")
        flags.append("dates")
    elif left_dates != right_dates:
        flags.append("dates")
    if periods_in(left) != periods_in(right):
        flags.append("periods")
    if notice_windows(left) != notice_windows(right):
        flags.append("notice_windows")
    if parties_in(left) != parties_in(right):
        flags.append("parties")
    if definitions_in(left) != definitions_in(right):
        flags.append("definitions")
    left_carve = carve_out_affirmed(left)
    right_carve = carve_out_affirmed(right)
    if left_carve != right_carve:
        flags.append("carve_outs")
    if hidden_or_tracked(left) or hidden_or_tracked(right):
        flags.append("hidden_or_tracked")
    if people_count_spans(visible_text(left)) or people_count_spans(visible_text(right)):
        flags.append("people_count_withheld")
    return {
        "flags": flags,
        "incomplete": incomplete,
        "left_carve_out": left_carve,
        "right_carve_out": right_carve,
        "removed_carve_out": left_carve and not right_carve,
        "obligation_ranks": {"baseline": left_ranks, "other": right_ranks},
        "coerced": False,
        "meta_negation_counted": bool(_META.search(left or "") or _META.search(right or "")),
    }
