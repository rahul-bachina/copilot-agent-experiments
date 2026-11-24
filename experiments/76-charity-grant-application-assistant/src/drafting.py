"""Draft answers and an impact report from pinned rows only.

A figure, a beneficiary count, or a quotation is copied only when a row
or a profile field contains it. Small beneficiary counts are not published.
"""

from __future__ import annotations

if __package__ in {None, ""}:
    from dates import as_date, parse_date, shift_days
else:
    from .dates import as_date, parse_date, shift_days


def words(text: str) -> int:
    return len([part for part in text.split() if part])


def _int_or_none(value: object) -> int | None:
    if type(value) is int:
        return value
    return None


def _threshold(criteria: dict) -> tuple[int | None, bool]:
    value = criteria.get("small_number_threshold")
    if type(value) is int and value >= 1:
        return value, False
    return None, True


def figures(rows: list[dict], criteria: dict) -> tuple[list[dict], bool]:
    """Publish sourced figures. A count of people below the threshold is withheld."""

    threshold, bad_threshold = _threshold(criteria)
    published: list[dict] = []
    for row in rows:
        kind = row.get("kind")
        if kind not in {"outcome", "beneficiary_count"}:
            continue
        row_id = row.get("row_id") if isinstance(row.get("row_id"), str) else None
        metric = row.get("metric") if isinstance(row.get("metric"), str) else None
        unit = row.get("unit") if isinstance(row.get("unit"), str) else None
        value = row.get("value")
        if row_id is None or metric is None:
            published.append(
                {
                    "source_ref": row_id,
                    "metric": metric,
                    "value": None,
                    "unit": unit,
                    "suppressed": False,
                    "unparseable": True,
                    "coerced": False,
                }
            )
            continue
        number = _int_or_none(value)
        if number is None:
            published.append(
                {
                    "source_ref": row_id,
                    "metric": metric,
                    "value": None,
                    "unit": unit,
                    "suppressed": False,
                    "unparseable": True,
                    "coerced": False,
                }
            )
            continue
        suppress = kind == "beneficiary_count" and (bad_threshold or (threshold is not None and number < threshold))
        published.append(
            {
                "source_ref": row_id,
                "metric": metric,
                "value": None if suppress else number,
                "unit": unit,
                "suppressed": suppress,
                "unparseable": False,
                "coerced": False,
                "threshold": threshold,
                "value_copied": not suppress,
            }
        )
    return published, bad_threshold


def quotations(rows: list[dict], withheld_ids: set[str]) -> list[dict]:
    found = []
    for row in rows:
        if row.get("kind") != "quotation":
            continue
        row_id = row.get("row_id") if isinstance(row.get("row_id"), str) else None
        quote = row.get("quote") if isinstance(row.get("quote"), str) else None
        if row_id is None or not quote or row_id in withheld_ids:
            found.append(
                {
                    "source_ref": row_id,
                    "quote": None,
                    "copied_exactly": False,
                    "withheld": row_id in withheld_ids,
                }
            )
            continue
        found.append(
            {
                "source_ref": row_id,
                "quote": quote,
                "copied_exactly": True,
                "withheld": False,
            }
        )
    return found


def partners(charity: dict) -> list[dict]:
    rows = charity.get("partners")
    if not isinstance(rows, list):
        return []
    found = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        partner_id = row.get("partner_id")
        name = row.get("name")
        if isinstance(partner_id, str) and isinstance(name, str) and name.strip():
            found.append({"source_ref": f"profile.partners.{partner_id}", "name": name})
    return found


def _fit(text: str, limit: object, source_refs: list[str]) -> dict:
    if type(limit) is not int or limit < 1:
        return {
            "text": None,
            "word_count": None,
            "word_limit": None,
            "within_limit": False,
            "source_refs": source_refs,
            "unparseable_limit": True,
            "coerced": False,
            "omitted": True,
        }
    count = words(text)
    if count <= limit:
        return {
            "text": text,
            "word_count": count,
            "word_limit": limit,
            "within_limit": True,
            "source_refs": source_refs,
            "unparseable_limit": False,
            "coerced": False,
            "omitted": False,
        }
    return {
        "text": None,
        "word_count": count,
        "word_limit": limit,
        "within_limit": False,
        "source_refs": source_refs,
        "unparseable_limit": False,
        "coerced": False,
        "omitted": True,
        "reason": "over_word_limit_not_truncated",
    }


def _limit(questions: list[dict], question_id: str) -> object:
    for question in questions:
        if isinstance(question, dict) and question.get("question_id") == question_id:
            return question.get("word_limit")
    return None


def _prompt(questions: list[dict], question_id: str) -> str | None:
    for question in questions:
        if isinstance(question, dict) and question.get("question_id") == question_id:
            prompt = question.get("prompt")
            return prompt if isinstance(prompt, str) else None
    return None


def answers(
    questions: list[dict],
    figure_rows: list[dict],
    quote_rows: list[dict],
    partner_rows: list[dict],
    eligibility: list[dict],
) -> list[dict]:
    by_id = {row["source_ref"]: row for row in figure_rows if row.get("source_ref")}
    meals = by_id.get("ME-OUT-01")
    people = by_id.get("ME-BEN-01")
    small = by_id.get("ME-BEN-SMALL")
    quote = next((row for row in quote_rows if row.get("copied_exactly")), None)
    match = next((row for row in eligibility if row.get("criterion_id") == "EL-MATCH"), None)
    built = []

    if meals and meals.get("value_copied") and type(meals.get("value")) is int:
        text = f"Harbour Lane Community Kitchen served {meals['value']} meals. Source {meals['source_ref']}."
        refs = [meals["source_ref"]]
    else:
        text = "No sourced meal figure is on the monitoring rows."
        refs = []
    built.append({"question_id": "Q1", "prompt": _prompt(questions, "Q1"), **_fit(text, _limit(questions, "Q1"), refs)})

    parts = []
    refs = []
    if people and people.get("value_copied") and type(people.get("value")) is int:
        parts.append(f"The monitoring row records {people['value']} people. Source {people['source_ref']}.")
        refs.append(people["source_ref"])
    if small and small.get("suppressed"):
        parts.append(f"One beneficiary count is withheld because it is below the threshold. Source {small['source_ref']}.")
        refs.append(small["source_ref"])
    if not parts:
        parts.append("No sourced beneficiary count can be published.")
    built.append(
        {
            "question_id": "Q2",
            "prompt": _prompt(questions, "Q2"),
            **_fit(" ".join(parts), _limit(questions, "Q2"), refs),
        }
    )

    if quote and isinstance(quote.get("quote"), str):
        text = f"Recorded quotation: {quote['quote']} Source {quote['source_ref']}."
        refs = [quote["source_ref"]]
    else:
        text = "No quotation can be copied from the monitoring rows."
        refs = []
    built.append({"question_id": "Q3", "prompt": _prompt(questions, "Q3"), **_fit(text, _limit(questions, "Q3"), refs)})

    if partner_rows:
        named = partner_rows[0]
        text = f"The profile names {named['name']}. Source {named['source_ref']}."
        refs = [named["source_ref"]]
    else:
        text = "No partner is named on the charity profile."
        refs = []
    built.append({"question_id": "Q4", "prompt": _prompt(questions, "Q4"), **_fit(text, _limit(questions, "Q4"), refs)})

    if match and match.get("status") == "not_met":
        text = "Match funding is not on the profile. Criterion EL-MATCH is not met. Source charity.match_funding_available."
        refs = ["charity.match_funding_available"]
    elif match and match.get("status") == "met":
        text = f"Match funding is recorded at {match.get('percent')} percent. Source charity.match_funding_available."
        refs = ["charity.match_funding_available"]
    else:
        text = "Match funding on the profile cannot be read. Criterion EL-MATCH is not treated as met."
        refs = ["charity.match_funding_available"]
    built.append({"question_id": "Q5", "prompt": _prompt(questions, "Q5"), **_fit(text, _limit(questions, "Q5"), refs)})
    return built


def claims(proposed: object, figure_rows: list[dict], quote_rows: list[dict], partner_rows: list[dict], eligibility: list[dict]) -> list[dict]:
    """A caller claim is evidenced only by an exact pinned value. Otherwise it is flagged."""

    if proposed is None:
        return []
    if not isinstance(proposed, list):
        return [{"claim_id": None, "status": "unreadable", "coerced": False, "used_in_draft": False}]
    figures_by_metric: dict[str, list[dict]] = {}
    for row in figure_rows:
        metric = row.get("metric")
        if isinstance(metric, str):
            figures_by_metric.setdefault(metric, []).append(row)
    quotes = {row.get("quote"): row.get("source_ref") for row in quote_rows if row.get("copied_exactly")}
    partner_names = {row["name"].casefold(): row["source_ref"] for row in partner_rows}
    eligibility_by_id = {row["criterion_id"]: row for row in eligibility}
    found = []
    for claim in proposed:
        if not isinstance(claim, dict):
            found.append({"claim_id": None, "status": "unreadable", "coerced": False, "used_in_draft": False})
            continue
        claim_id = claim.get("claim_id") if isinstance(claim.get("claim_id"), str) else None
        kind = claim.get("kind")
        if kind == "figure":
            metric = claim.get("metric") if isinstance(claim.get("metric"), str) else None
            value = claim.get("value")
            rows = figures_by_metric.get(metric or "", [])
            matched = None
            for row in rows:
                if row.get("suppressed"):
                    continue
                if row.get("value") == value and row.get("value_copied") is True:
                    matched = row
                    break
            suppressed = any(row.get("suppressed") and row.get("metric") == metric for row in rows)
            if matched:
                found.append(
                    {
                        "claim_id": claim_id,
                        "status": "evidenced",
                        "source_ref": matched["source_ref"],
                        "coerced": False,
                        "used_in_draft": False,
                    }
                )
            elif suppressed and type(value) is int:
                found.append(
                    {
                        "claim_id": claim_id,
                        "status": "suppressed_small_number",
                        "source_ref": next(row["source_ref"] for row in rows if row.get("suppressed")),
                        "stated_value_copied": False,
                        "coerced": False,
                        "used_in_draft": False,
                    }
                )
            else:
                found.append(
                    {
                        "claim_id": claim_id,
                        "status": "unsupported",
                        "source_ref": None,
                        "stated_value_copied": False,
                        "coerced": False,
                        "used_in_draft": False,
                    }
                )
            continue
        if kind == "quotation":
            quote = claim.get("quote") if isinstance(claim.get("quote"), str) else None
            source = quotes.get(quote)
            found.append(
                {
                    "claim_id": claim_id,
                    "status": "evidenced" if source else "unsupported",
                    "source_ref": source,
                    "quote_copied": bool(source),
                    "coerced": False,
                    "used_in_draft": False,
                }
            )
            continue
        if kind == "partner":
            name = claim.get("name") if isinstance(claim.get("name"), str) else ""
            source = partner_names.get(name.casefold())
            found.append(
                {
                    "claim_id": claim_id,
                    "status": "evidenced" if source else "unsupported",
                    "source_ref": source,
                    "name_copied": bool(source),
                    "coerced": False,
                    "used_in_draft": False,
                }
            )
            continue
        if kind == "eligibility":
            criterion_id = claim.get("criterion_id") if isinstance(claim.get("criterion_id"), str) else None
            row = eligibility_by_id.get(criterion_id or "")
            if row is None:
                found.append(
                    {
                        "claim_id": claim_id,
                        "status": "unsupported",
                        "source_ref": None,
                        "coerced": False,
                        "used_in_draft": False,
                    }
                )
            elif row.get("status") == "met":
                found.append(
                    {
                        "claim_id": claim_id,
                        "status": "evidenced",
                        "source_ref": row.get("source_ref"),
                        "coerced": False,
                        "used_in_draft": False,
                    }
                )
            else:
                found.append(
                    {
                        "claim_id": claim_id,
                        "status": "gap_not_papered",
                        "source_ref": row.get("source_ref"),
                        "criterion_id": criterion_id,
                        "eligibility_status": row.get("status"),
                        "coerced": False,
                        "used_in_draft": False,
                    }
                )
            continue
        found.append({"claim_id": claim_id, "status": "unsupported", "source_ref": None, "coerced": False, "used_in_draft": False})
    return found


def attachments(brief: dict, charity: dict) -> list[dict]:
    required = brief.get("required_attachments")
    if not isinstance(required, list):
        return []
    found = []
    for item in required:
        if not isinstance(item, dict):
            continue
        attachment_id = item.get("attachment_id") if isinstance(item.get("attachment_id"), str) else None
        name = item.get("name") if isinstance(item.get("name"), str) else None
        field = item.get("profile_field")
        present = False
        source_ref = None
        if isinstance(field, str) and field:
            present = charity.get(field) not in (None, "", False)
            source_ref = f"charity.{field}" if present else None
        found.append(
            {
                "attachment_id": attachment_id,
                "name": name,
                "present": present,
                "gap": not present,
                "source_ref": source_ref,
                "satisfies_eligibility": False,
            }
        )
    return found


def deadline_plan(brief: dict, question: date | None) -> dict:
    reading = parse_date(brief.get("deadline"))
    deadline = as_date(reading)
    offsets = brief.get("plan_offsets_days")
    milestones = []
    unparseable_offset = False
    if isinstance(offsets, dict) and deadline is not None:
        for name in sorted(offsets):
            shifted = shift_days(deadline, offsets[name])
            if shifted["unparseable"]:
                unparseable_offset = True
            milestones.append({"name": name, **shifted, "statutory": False})
    elif offsets is not None:
        unparseable_offset = True
    past = bool(deadline and question and deadline < question)
    due = bool(deadline and question and deadline == question)
    return {
        "deadline": deadline.isoformat() if deadline else None,
        "unparseable": reading.get("unparseable") is True or reading.get("ambiguous") is True,
        "ambiguous": reading.get("ambiguous") is True,
        "reason": reading.get("reason"),
        "past": past,
        "due_on_question_date": due,
        "question_date": question.isoformat() if question else None,
        "coerced": False,
        "offsets_are_statutory": False,
        "unparseable_offset": unparseable_offset,
        "milestones": milestones,
    }


def priorities(brief: dict, figure_rows: list[dict]) -> list[dict]:
    rows = brief.get("priorities")
    if not isinstance(rows, list):
        return []
    known = {row.get("source_ref") for row in figure_rows if row.get("value_copied")}
    found = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        priority_id = item.get("priority_id") if isinstance(item.get("priority_id"), str) else None
        evidence = item.get("evidence_row_ids")
        refs = [ref for ref in evidence if isinstance(ref, str) and ref in known] if isinstance(evidence, list) else []
        found.append(
            {
                "priority_id": priority_id,
                "supported": bool(refs),
                "gap": not bool(refs),
                "source_refs": refs,
                "papered_over": False,
            }
        )
    return found
