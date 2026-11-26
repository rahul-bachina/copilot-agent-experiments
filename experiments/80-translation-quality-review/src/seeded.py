"""Seeded translation errors and paraphrase sets.

These are authored fixtures. Precision and recall here are not a live
quality-estimation score and are not added to the smoke-test case total.
"""

from __future__ import annotations

from datetime import date

if __package__ in {None, ""}:
    from checks import analyse
    from risk import RISK_STEMS, SENSITIVE_STEMS, risk_categories, sensitive_categories
    from siblings import neighbours
else:
    from .checks import analyse
    from .risk import RISK_STEMS, SENSITIVE_STEMS, risk_categories, sensitive_categories
    from .siblings import neighbours

QUESTION = date(2026, 11, 26)
WORDS = (
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango",
)
INFORMAL = (
    ("en", "gonna"),
    ("en", "wanna"),
    ("en", "hiya"),
    ("en", "cheers mate"),
    ("en", "you guys"),
    ("en", "kiddos"),
    ("cy", "shwmae"),
    ("cy", "hwyl fawr"),
    ("pl", "siema"),
    ("pl", "nara"),
)


def _one(source: str, target: str, *, language: str = "en", kind: str = "public_information") -> dict:
    return {
        "source_segments": [{"segment_id": "s1", "number": "1", "text": source}],
        "target_segments": [{"segment_id": "s1", "number": "1", "text": target}],
        "target_language": language,
        "document_kind": kind,
    }


def _flags(case: dict) -> set[str]:
    result = analyse(
        case["source_segments"],
        case["target_segments"],
        target_language=case["target_language"],
        document_kind=case["document_kind"],
        question=QUESTION,
    )
    return {row["type"] for row in result["flags"]}


def _cases(builder) -> list[dict]:
    rows = []
    for index, word in enumerate(WORDS):
        positive, negative = builder(index, word)
        positive["expect"] = True
        negative["expect"] = False
        rows.append(positive)
        rows.append(negative)
    return rows


def _omitted(index: int, word: str) -> tuple[dict, dict]:
    kept = f"The office opens at nine. Marker {word}."
    missing = f"Bring a spare pen to the counter. Marker {word}."
    positive = {
        "source_segments": [
            {"segment_id": "s1", "number": "1", "text": kept},
            {"segment_id": "s2", "number": "2", "text": missing},
        ],
        "target_segments": [{"segment_id": "s1", "number": "1", "text": kept}],
        "target_language": "en",
        "document_kind": "guidance",
    }
    negative = {
        "source_segments": [
            {"segment_id": "s1", "number": "1", "text": kept},
            {"segment_id": "s2", "number": "2", "text": missing},
        ],
        "target_segments": [
            {"segment_id": "s1", "number": "1", "text": kept},
            {"segment_id": "s2", "number": "2", "text": missing},
        ],
        "target_language": "en",
        "document_kind": "guidance",
    }
    return positive, negative


def _added(index: int, word: str) -> tuple[dict, dict]:
    kept = f"The office opens at nine. Marker {word}."
    extra = f"A poster is on the wall. Marker {word}."
    positive = {
        "source_segments": [{"segment_id": "s1", "number": "1", "text": kept}],
        "target_segments": [
            {"segment_id": "s1", "number": "1", "text": kept},
            {"segment_id": "s2", "number": "2", "text": extra},
        ],
        "target_language": "en",
        "document_kind": "guidance",
    }
    negative = _one(kept, kept, kind="guidance")
    return positive, negative


def _changed_number(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"The reference code is {100 + index} for {word}.",
        f"The reference code is {400 + index} for {word}.",
        kind="guidance",
    )
    negative = _one(
        f"The reference code is {100 + index} for {word}.",
        f"The reference code is {100 + index} for {word}.",
        kind="guidance",
    )
    return positive, negative


def _changed_amount(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"The fee for {word} is £{200 + index}.",
        f"The fee for {word} is £{20 + index}.",
        kind="guidance",
    )
    negative = _one(
        f"The fee for {word} is £{200 + index}.",
        f"The fee for {word} is {200 + index} pounds.",
        kind="guidance",
    )
    return positive, negative


def _changed_date(index: int, word: str) -> tuple[dict, dict]:
    day = index + 1
    positive = _one(
        f"The day for {word} is {day} March 2024.",
        f"The day for {word} is {day} April 2024.",
        kind="guidance",
    )
    negative = _one(
        f"The day for {word} is {day} March 2024.",
        f"The day for {word} is {day} March 2024.",
        kind="guidance",
    )
    return positive, negative


def _changed_deadline(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"Apply within {10 + index} working days for {word}.",
        f"Apply within {40 + index} working days for {word}.",
        kind="guidance",
    )
    if index % 2 == 0:
        negative = _one(
            f"Apply within {10 + index} working days for {word}.",
            f"Apply within {10 + index} working days for {word}.",
            kind="guidance",
        )
    else:
        negative = _one(
            f"Apply within {10 + index} working days for {word}.",
            f"Gwnewch gais o fewn {10 + index} diwrnod gwaith am {word}.",
            language="cy",
            kind="guidance",
        )
    return positive, negative


def _changed_phone(index: int, word: str) -> tuple[dict, dict]:
    source = f"07700900{index:03d}"
    other = f"07700910{index:03d}"
    positive = _one(f"Call {source} about {word} today.", f"Call {other} about {word} today.", kind="guidance")
    spaced = source[:5] + " " + source[5:]
    negative = _one(f"Call {source} about {word} today.", f"Call {spaced} about {word} today.", kind="guidance")
    return positive, negative


def _changed_url(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"See https://example.test/{word}{index} today.",
        f"See https://example.test/other{index} today.",
        kind="guidance",
    )
    negative = _one(
        f"See https://example.test/{word}{index} today.",
        f"See https://example.test/{word}{index} today.",
        kind="guidance",
    )
    return positive, negative


def _reversed_negation(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(f"You must apply for {word}.", f"You must not apply for {word}.", kind="guidance")
    negative = _one(f"You must apply for {word}.", f"You must apply for {word}.", kind="guidance")
    return positive, negative


def _dropped_negation(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(f"You must not apply for {word}.", f"You must apply for {word}.", kind="guidance")
    negative = _one(f"You must not apply for {word}.", f"You must not apply for {word}.", kind="guidance")
    return positive, negative


def _softened(index: int, word: str) -> tuple[dict, dict]:
    if index % 2 == 0:
        positive = _one(f"You must send the {word} form.", f"You may send the {word} form.", kind="guidance")
    else:
        positive = _one(
            f"You are required to send the {word} form.",
            f"You are permitted to send the {word} form.",
            kind="guidance",
        )
    if index % 2 == 0:
        negative = _one(f"You must send the {word} form.", f"Rhaid i chi anfon y ffurflen {word}.", language="cy", kind="guidance")
    else:
        negative = _one(f"You must send the {word} form.", f"You must send the {word} form.", kind="guidance")
    return positive, negative


def _strengthened(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(f"You may send the {word} form.", f"You must send the {word} form.", kind="guidance")
    if index % 2 == 0:
        negative = _one(f"You may send the {word} form.", f"Gallwch chi anfon y ffurflen {word}.", language="cy", kind="guidance")
    else:
        negative = _one(f"You may send the {word} form.", f"You may send the {word} form.", kind="guidance")
    return positive, negative


def _mistranslated(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"Please read the complaint about {word}.",
        f"Darllenwch y problem am {word}.",
        language="cy",
    )
    negative = _one(
        f"Please read the complaint about {word}.",
        f"Darllenwch y cwyn am {word}.",
        language="cy",
    )
    return positive, negative


def _untranslated(index: int, word: str) -> tuple[dict, dict]:
    sentence = f"Please bring a pen to the counter today for {word}."
    positive = _one(sentence, sentence, language="cy", kind="guidance")
    negative = _one(sentence, f"Dewch â beiro i'r cownter heddiw os gwelwch yn dda {word}.", language="cy", kind="guidance")
    return positive, negative


def _inconsistent(index: int, word: str) -> tuple[dict, dict]:
    positive = {
        "source_segments": [
            {"segment_id": "s1", "number": "1", "text": f"Send the complaint about {word}."},
            {"segment_id": "s2", "number": "2", "text": f"Send the complaint about {word} again."},
        ],
        "target_segments": [
            {"segment_id": "s1", "number": "1", "text": f"Anfonwch y cwyn am {word}."},
            {"segment_id": "s2", "number": "2", "text": f"Anfonwch y problem am {word}."},
        ],
        "target_language": "cy",
        "document_kind": "public_information",
    }
    negative = {
        "source_segments": [
            {"segment_id": "s1", "number": "1", "text": f"Send the complaint about {word}."},
            {"segment_id": "s2", "number": "2", "text": f"Send the complaint about {word} again."},
        ],
        "target_segments": [
            {"segment_id": "s1", "number": "1", "text": f"Anfonwch y cwyn am {word}."},
            {"segment_id": "s2", "number": "2", "text": f"Anfonwch y cwyn am {word} eto."},
        ],
        "target_language": "cy",
        "document_kind": "public_information",
    }
    return positive, negative


def _register(index: int, word: str) -> tuple[dict, dict]:
    language, stem = INFORMAL[index % len(INFORMAL)]
    positive = _one(
        f"The counter is open for {word}.",
        f"{stem}, the counter is open for {word}.",
        language=language,
    )
    negative = _one(
        f"The counter is open for {word}.",
        f"The counter is open for {word}.",
        language=language,
        kind="public_information",
    )
    return positive, negative


def _added_exception(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"You must appeal the {word} notice.",
        f"You must appeal the {word} notice unless the case is closed.",
        kind="guidance",
    )
    negative = _one(
        f"You must appeal the {word} notice unless the case is closed.",
        f"You must appeal the {word} notice unless the case is closed.",
        kind="guidance",
    )
    return positive, negative


def _dropped_exception(index: int, word: str) -> tuple[dict, dict]:
    positive = _one(
        f"You must appeal the {word} notice unless the case is closed.",
        f"You must appeal the {word} notice.",
        kind="guidance",
    )
    negative = _one(
        f"You must appeal the {word} notice.",
        f"You must appeal the {word} notice.",
        kind="guidance",
    )
    return positive, negative


def _meaning_shift(index: int, word: str) -> tuple[dict, dict]:
    pairs = (
        (f"You must send the {word} form.", f"You may send the {word} form."),
        (f"You are required to send the {word} form.", f"You are permitted to send the {word} form."),
        (f"The resident is not eligible for the {word} service.", f"The resident is eligible for the {word} service."),
        (f"Do not use the {word} side door.", f"Use the {word} side door."),
        (f"The fee for {word} is £250.", f"The fee for {word} is £25."),
        (f"Apply within 10 working days for {word}.", f"Apply within 20 working days for {word}."),
        (f"The day for {word} is 12 March 2024.", f"The day for {word} is 12 April 2024."),
        (f"You must appeal the {word} notice.", f"You must appeal the {word} notice unless the case is closed."),
        (f"You must appeal the {word} notice unless the case is closed.", f"You must appeal the {word} notice."),
        (f"The council shall write about {word}.", f"The council may write about {word}."),
    )
    source, target = pairs[index % len(pairs)]
    positive = _one(source, target, kind="guidance")
    if index < 10:
        negative = _one(f"The office opens at nine for {word}.", f"The office opens at nine for {word}.", kind="guidance")
    elif index < 15:
        negative = _one(f"The office opens at nine for {word}.", f"The canteen opens at nine for {word}.", kind="guidance")
    else:
        sentence = f"It is not true that the {word} notice includes an exception."
        negative = _one(sentence, sentence, kind="guidance")
    return positive, negative


BUILDERS = {
    "omitted_content": _omitted,
    "added_content": _added,
    "changed_number": _changed_number,
    "changed_amount": _changed_amount,
    "changed_date": _changed_date,
    "changed_deadline": _changed_deadline,
    "changed_phone": _changed_phone,
    "changed_url": _changed_url,
    "reversed_negation": _reversed_negation,
    "dropped_negation": _dropped_negation,
    "softened_obligation": _softened,
    "strengthened_obligation": _strengthened,
    "mistranslated_term": _mistranslated,
    "untranslated_segment": _untranslated,
    "inconsistent_terminology": _inconsistent,
    "register": _register,
    "added_exception": _added_exception,
    "dropped_exception": _dropped_exception,
    "meaning_shift": _meaning_shift,
}


def seeded_report() -> dict:
    categories = {}
    for name, builder in BUILDERS.items():
        cases = _cases(builder)
        true_positive = false_positive = false_negative = 0
        for case in cases:
            found = name in _flags(case)
            if case["expect"] and found:
                true_positive += 1
            elif case["expect"] and not found:
                false_negative += 1
            elif not case["expect"] and found:
                false_positive += 1
        positives = sum(1 for case in cases if case["expect"])
        negatives = sum(1 for case in cases if not case["expect"])
        precision_den = true_positive + false_positive
        recall_den = true_positive + false_negative
        categories[name] = {
            "positives": positives,
            "negatives": negatives,
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "precision": round(true_positive / precision_den, 4) if precision_den else None,
            "recall": round(true_positive / recall_den, 4) if recall_den else None,
        }
    return {
        "not_added_to_case_total": True,
        "not_a_model_evaluation": True,
        "authored_fixtures": True,
        "categories": categories,
    }


def paraphrase_report() -> dict:
    categories = {}
    for name, stems in RISK_STEMS.items():
        hits = 0
        false_inclusions = 0
        for stem in stems:
            if name in risk_categories(f"Please note that {stem} before you reply."):
                hits += 1
            if name in risk_categories(f"It is not true that {stem}."):
                false_inclusions += 1
        unrelated = 1 if name in risk_categories("The library opens on Tuesday and the desks are free.") else 0
        false_inclusions += unrelated
        categories[name] = {
            "sentences": len(stems),
            "hits": hits,
            "false_inclusions": false_inclusions,
            "recall": round(hits / len(stems), 4) if stems else None,
            "expect_match": True,
        }
    sensitive = {}
    for name, stems in SENSITIVE_STEMS.items():
        hits = 0
        denied_hits = 0
        for stem in stems:
            if name in sensitive_categories(f"Please help. {stem}."):
                hits += 1
            if name in sensitive_categories(f"I am not saying that {stem}."):
                denied_hits += 1
        title = sensitive_categories("Please read the safeguarding policy.")
        sensitive[name] = {
            "sentences": len(stems),
            "hits": hits,
            "denied_hits": denied_hits,
            "recall": round(hits / len(stems), 4) if stems else None,
            "denied_recall": round(denied_hits / len(stems), 4) if stems else None,
            "title_is_not_a_cue": name not in title,
        }
    return {
        "not_added_to_case_total": True,
        "not_a_model_evaluation": True,
        "authored_fixtures": True,
        "risk": categories,
        "sensitive": sensitive,
    }


def alignment_report() -> dict:
    flat = []
    for word in WORDS:
        flat.append({
            "left": f"The office opens at nine for {word}.",
            "right": f"The office opens at nine for {word}.",
            "expect_aligned": True,
        })
    for word in WORDS:
        flat.append({
            "left": f"The office opens at nine for {word}.",
            "right": "Bring a spare pen for the drawer.",
            "expect_aligned": False,
        })
    scored = neighbours()["score_pairs"](flat)
    scored["not_added_to_case_total"] = True
    scored["reused"] = "experiments/79-document-comparison/src/align.py score_pairs"
    return scored
