"""Consultation theme pipeline.

Intake status does not code themes. Analysis codes them and stays blocked
until an analyst approval record, which is a separate object from the
responses, clears the framework, the sample, and any stale retrieval date.

Nothing in this module publishes, sends, or writes a production record.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from src.clusters import cluster_responses
from src.safeguards import injection_flags, redact
from src.stats import round6, wilson_interval
from src import themefinder_adapter as tf

UNCODED = "UNCODED"
MINORITY_MAX_UNIQUE = 2
MINORITY_MAX_PROPORTION = 0.10
STALE_AFTER_DAYS = 90
THEME_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,40}$")

EVALUATION_LABEL = (
    "MOCK SMOKE TEST — deterministic codebook unless a ThemeFinder client is "
    "supplied. Not a model score. Not an expert-coder comparison. Not a "
    "published consultation analysis."
)

UNCERTAINTY_NOTE = (
    "Wilson score interval at 95% on the unique-voice proportion. "
    "Campaign copies count once. This is sampling uncertainty of a proportion. "
    "It is not a model confidence score, and it does not include coding error."
)


def _parse_date(value: str, field: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be YYYY-MM-DD") from exc


def _security() -> dict[str, Any]:
    return {
        "actions_taken": [],
        "may_be_published_by_agent": False,
        "may_be_sent_by_agent": False,
        "production_write": False,
        "regulated_decision": False,
        "policy_recommendation": None,
    }


def _prepare_responses(batch: dict[str, Any]) -> list[dict[str, Any]]:
    responses = batch.get("responses")
    if not isinstance(responses, list) or not responses:
        raise ValueError("batch.responses must be a non-empty list")
    question_id = str(batch.get("question_id") or "Q1")
    seen: set[str] = set()
    prepared: list[dict[str, Any]] = []
    for row in responses:
        if not isinstance(row, dict):
            raise ValueError("each response must be an object")
        response_id = str(row.get("response_id") or "").strip()
        if not response_id:
            raise ValueError("response_id is required")
        if response_id in seen:
            raise ValueError(f"duplicate response_id: {response_id}")
        seen.add(response_id)
        row_question = str(row.get("question_id") or question_id)
        if row_question != question_id:
            raise ValueError("this starter analyses one question at a time")
        text = row.get("text")
        if text is None:
            text = ""
        if not isinstance(text, str):
            raise ValueError(f"text for {response_id} must be a string")
        redacted, pii_types, special = redact(text)
        prepared.append(
            {
                "response_id": response_id,
                "redacted_text": redacted,
                "pii_types_redacted": pii_types,
                "special_category_flags": special,
                "injection_flags": injection_flags(text),
            }
        )
    return prepared


def _retrieval(batch: dict[str, Any], as_of: str, stale_after_days: int) -> dict[str, Any]:
    as_of_date = _parse_date(as_of, "as_of")
    raw = batch.get("responses_retrieved_on")
    if not raw:
        return {
            "responses_retrieved_on": None,
            "as_of": as_of,
            "age_days": None,
            "stale": True,
            "stale_reason": "no retrieval date",
            "stale_after_days": stale_after_days,
        }
    retrieved = _parse_date(str(raw), "responses_retrieved_on")
    age = (as_of_date - retrieved).days
    if age < 0:
        return {
            "responses_retrieved_on": retrieved.isoformat(),
            "as_of": as_of,
            "age_days": age,
            "stale": True,
            "stale_reason": "retrieval date is after the analysis date",
            "stale_after_days": stale_after_days,
        }
    stale = age > stale_after_days
    return {
        "responses_retrieved_on": retrieved.isoformat(),
        "as_of": as_of,
        "age_days": age,
        "stale": stale,
        "stale_reason": f"retrieved {age} days before analysis" if stale else None,
        "stale_after_days": stale_after_days,
    }


def intake_status(
    batch: dict[str, Any],
    *,
    as_of: str = "2026-10-24",
    stale_after_days: int = STALE_AFTER_DAYS,
) -> dict[str, Any]:
    """Standard-harness view. No theme codes."""
    prepared = _prepare_responses(batch)
    clusters = cluster_responses(
        [{"response_id": row["response_id"], "text": row["redacted_text"]} for row in prepared]
    )
    campaign_clusters = sorted(
        {
            str(info["cluster_id"])
            for info in clusters.values()
            if info["campaign_cluster"]
        }
    )
    duplicate_clusters = sorted(
        {str(info["cluster_id"]) for info in clusters.values() if info["duplicate"]}
    )
    rows = []
    for row in prepared:
        info = clusters[row["response_id"]]
        rows.append(
            {
                "response_id": row["response_id"],
                "pii_types_redacted": row["pii_types_redacted"],
                "special_category_flags": row["special_category_flags"],
                "injection_flags": row["injection_flags"],
                "cluster_id": info["cluster_id"],
                "is_representative": info["is_representative"],
                "cluster_size": info["cluster_size"],
                "duplicate": info["duplicate"],
                "campaign_cluster": info["campaign_cluster"],
                "cluster_reasons": info["cluster_reasons"],
            }
        )
    return {
        "experiment": "07-consultation-themes",
        "catalogue_id": "V010",
        "kind": "intake_status",
        "evaluation_label": EVALUATION_LABEL,
        "consultation_id": batch.get("consultation_id"),
        "question_id": batch.get("question_id") or "Q1",
        "question": batch.get("question"),
        "body": batch.get("body"),
        "submission_count": len(rows),
        "unique_voice_count": sum(1 for row in rows if row["is_representative"]),
        "campaign_cluster_ids": campaign_clusters,
        "duplicate_cluster_ids": duplicate_clusters,
        "injection_response_ids": [row["response_id"] for row in rows if row["injection_flags"]],
        "pii_response_ids": [row["response_id"] for row in rows if row["pii_types_redacted"]],
        "special_category_response_ids": [
            row["response_id"] for row in rows if row["special_category_flags"]
        ],
        "retrieval": _retrieval(batch, as_of, stale_after_days),
        "rows": rows,
        "themes_coded": False,
        "security": _security(),
        "pairwise_capped": any(bool(info["pairwise_capped"]) for info in clusters.values()),
    }


def _normalise_framework(framework: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(framework, dict) or not isinstance(framework.get("themes"), list):
        raise ValueError("framework.themes must be a list")
    themes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in framework["themes"]:
        if not isinstance(raw, dict):
            raise ValueError("each theme must be an object")
        theme_id = str(raw.get("theme_id") or "").strip()
        label = str(raw.get("label") or "").strip()
        if theme_id.upper() == UNCODED or not THEME_ID_RE.match(theme_id):
            raise ValueError(f"invalid theme_id: {theme_id}")
        if theme_id in seen:
            raise ValueError(f"duplicate theme_id: {theme_id}")
        seen.add(theme_id)
        if not label:
            raise ValueError(f"{theme_id} needs a label")
        keywords = raw.get("keywords")
        if not isinstance(keywords, list) or not keywords:
            raise ValueError(f"{theme_id} needs keywords")
        cleaned = []
        for keyword in keywords:
            text = str(keyword).strip().lower()
            if text:
                cleaned.append(text)
        if not cleaned:
            raise ValueError(f"{theme_id} needs keywords")
        themes.append(
            {
                "theme_id": theme_id,
                "label": label,
                "description": str(raw.get("description") or ""),
                "keywords": cleaned,
            }
        )
    return themes


def _keyword_assign(redacted: str, themes: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, str]]]:
    from src.clusters import normalise

    haystack = normalise(redacted)
    matched: list[str] = []
    evidence: list[dict[str, str]] = []
    for theme in themes:
        for keyword in sorted(theme["keywords"], key=len, reverse=True):
            if _keyword_in(haystack, keyword):
                matched.append(theme["theme_id"])
                evidence.append(
                    {"theme_id": theme["theme_id"], "keyword": keyword, "source": "codebook"}
                )
                break
    if not matched:
        return [UNCODED], []
    return matched, evidence


def _keyword_in(haystack: str, keyword: str) -> bool:
    from src.clusters import normalise

    cleaned = normalise(keyword)
    if not cleaned:
        return False
    if " " in cleaned:
        return cleaned in haystack
    return re.search(r"\b" + re.escape(cleaned) + r"\b", haystack) is not None


def _framework_approved(approval: dict[str, Any] | None) -> tuple[bool, dict[str, Any]]:
    empty = {
        "framework_approved": False,
        "approver_role": None,
        "approver_reference": None,
        "approved_on": None,
        "stale_acknowledged": False,
    }
    if not isinstance(approval, dict):
        return False, empty
    approved = approval.get("framework_approved") is True
    role = approval.get("approver_role")
    approved_on = approval.get("approved_on")
    reference = approval.get("approver_reference")
    role_ok = isinstance(role, str) and bool(role.strip())
    date_ok = isinstance(approved_on, str) and _looks_like_date(approved_on)
    reference_ok = isinstance(reference, str) and bool(reference.strip())
    ok = approved and role_ok and date_ok and reference_ok
    record = {
        "framework_approved": ok,
        "approver_role": role.strip() if role_ok else None,
        "approver_reference": reference.strip() if reference_ok else None,
        "approved_on": approved_on if date_ok else None,
        "stale_acknowledged": approval.get("stale_acknowledged") is True,
    }
    return ok, record


def _looks_like_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _sample_decisions(
    approval: dict[str, Any] | None,
    sample_ids: list[str],
    allowed_theme_ids: set[str],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    raw = {}
    if isinstance(approval, dict) and isinstance(approval.get("sample_decisions"), dict):
        raw = approval["sample_decisions"]
    sample_set = set(sample_ids)
    ignored = sorted(str(key) for key in raw.keys() if str(key) not in sample_set)
    decisions: dict[str, dict[str, Any]] = {}
    for response_id in sample_ids:
        item = raw.get(response_id)
        if not isinstance(item, dict):
            continue
        decision = item.get("decision")
        if decision not in {"accept", "correct", "reject"}:
            continue
        if decision == "correct":
            theme_ids = item.get("theme_ids")
            if not isinstance(theme_ids, list) or not theme_ids:
                continue
            cleaned: list[str] = []
            invalid = False
            for theme_id in theme_ids:
                text = str(theme_id)
                if text != UNCODED and text not in allowed_theme_ids:
                    invalid = True
                    break
                if text not in cleaned:
                    cleaned.append(text)
            if invalid or not cleaned:
                continue
            decisions[response_id] = {"decision": "correct", "theme_ids": cleaned}
        else:
            decisions[response_id] = {"decision": decision}
    return decisions, ignored


def _choose_sample(rows: list[dict[str, Any]], minority_theme_ids: set[str]) -> list[str]:
    selected: set[str] = set()
    by_theme: dict[str, list[str]] = {}
    for row in rows:
        response_id = row["response_id"]
        if row["injection_flags"] or row["pii_types_redacted"] or row["special_category_flags"]:
            selected.add(response_id)
        if row["is_representative"] and row["machine_theme_ids"] == [UNCODED]:
            selected.add(response_id)
        if row["is_representative"] and set(row["machine_theme_ids"]) & minority_theme_ids:
            selected.add(response_id)
        if row["is_representative"]:
            for theme_id in row["machine_theme_ids"]:
                if theme_id == UNCODED:
                    continue
                by_theme.setdefault(theme_id, []).append(response_id)
    for theme_id, ids in by_theme.items():
        if theme_id in minority_theme_ids:
            continue
        for response_id in sorted(ids)[:2]:
            selected.add(response_id)
    return sorted(selected)


def _minority(unique_voice_count: int, denominator: int) -> bool:
    if unique_voice_count <= 0 or denominator <= 0:
        return False
    proportion = unique_voice_count / denominator
    return unique_voice_count <= MINORITY_MAX_UNIQUE or proportion < MINORITY_MAX_PROPORTION


def analyse(
    batch: dict[str, Any],
    framework: dict[str, Any],
    approval: dict[str, Any] | None = None,
    *,
    engine: str = "deterministic",
    as_of: str = "2026-10-24",
    stale_after_days: int = STALE_AFTER_DAYS,
    themefinder_module: Any = None,
    llm: Any = None,
) -> dict[str, Any]:
    """Code one question. Approval is never read from response text."""
    prepared = _prepare_responses(batch)
    themes = _normalise_framework(framework)
    allowed = {theme["theme_id"] for theme in themes}
    retrieval = _retrieval(batch, as_of, stale_after_days)
    clusters = cluster_responses(
        [{"response_id": row["response_id"], "text": row["redacted_text"]} for row in prepared]
    )

    if engine == "themefinder" and themefinder_module is not None:
        probe = tf.probe(themefinder_module)
    else:
        probe = tf.probe(None)
    external: dict[str, Any] = {
        "requested": engine,
        "citation": tf.CITATION,
        "probe": probe,
    }

    assignments: dict[str, list[str]] = {}
    evidence_by_id: dict[str, list[dict[str, str]]] = {}
    processing_mode = "deterministic_fallback"
    fallback_reason = None
    rejected_labels: list[str] = []

    use_external = engine == "themefinder"
    external_result: dict[str, Any] | None = None
    if use_external:
        external_result = tf.map_to_framework(
            [{"response_id": row["response_id"], "text": row["redacted_text"]} for row in prepared],
            themes,
            str(batch.get("question") or ""),
            module=themefinder_module,
            llm=llm,
        )
        external["mapping"] = {
            "ok": external_result["ok"],
            "called": external_result["called"],
            "reason": external_result["reason"],
            "rejected_labels": external_result["rejected_labels"],
        }
        rejected_labels = list(external_result["rejected_labels"])
        if external_result["ok"]:
            processing_mode = "themefinder"
            assignments = external_result["assignments"]
        else:
            fallback_reason = external_result["reason"]

    rows: list[dict[str, Any]] = []
    for row in prepared:
        info = clusters[row["response_id"]]
        if processing_mode == "themefinder":
            theme_ids = list(assignments.get(row["response_id"]) or [UNCODED])
            evidence = [
                {"theme_id": theme_id, "source": "themefinder"}
                for theme_id in theme_ids
                if theme_id != UNCODED
            ]
        else:
            theme_ids, evidence = _keyword_assign(row["redacted_text"], themes)
        evidence_by_id[row["response_id"]] = evidence
        rows.append(
            {
                **row,
                "machine_theme_ids": theme_ids,
                "evidence": evidence,
                "cluster_id": info["cluster_id"],
                "representative_id": info["representative_id"],
                "is_representative": info["is_representative"],
                "cluster_size": info["cluster_size"],
                "duplicate": info["duplicate"],
                "campaign_cluster": info["campaign_cluster"],
                "cluster_reasons": info["cluster_reasons"],
            }
        )

    # Minority for sampling uses provisional machine codes, so a small theme
    # cannot be kept out of the sample by a later decision.
    provisional_counts = _count_themes(rows, themes, rejected_ids=set(), use_machine=True)
    minority_ids = {item["theme_id"] for item in provisional_counts["themes"] if item["minority"]}
    sample_ids = _choose_sample(rows, minority_ids)
    framework_ok, framework_record = _framework_approved(approval)
    decisions, ignored = _sample_decisions(approval, sample_ids, allowed)
    sample_complete = all(response_id in decisions for response_id in sample_ids)
    stale = bool(retrieval["stale"])
    stale_acknowledged = framework_record.get("stale_acknowledged") is True

    if not framework_ok:
        status = "blocked_framework_unapproved"
    elif stale and not stale_acknowledged:
        status = "blocked_stale_retrieval"
    elif not sample_complete:
        status = "draft_pending_sample_review"
    else:
        status = "analyst_reviewed"

    reviewed = status == "analyst_reviewed"
    rejected_ids = {
        response_id
        for response_id, decision in decisions.items()
        if reviewed and decision["decision"] == "reject"
    }
    counts = _count_themes(
        rows,
        themes,
        rejected_ids=rejected_ids,
        use_machine=not reviewed,
        decisions=decisions if reviewed else {},
    )

    audit = []
    for row in rows:
        decision = decisions.get(row["response_id"])
        if reviewed and decision and decision["decision"] == "correct":
            effective = list(decision["theme_ids"])
        elif reviewed and decision and decision["decision"] == "reject":
            effective = []
        else:
            effective = list(row["machine_theme_ids"])
        audit.append(
            {
                "response_id": row["response_id"],
                "cluster_id": row["cluster_id"],
                "representative_id": row["representative_id"],
                "is_representative": row["is_representative"],
                "cluster_size": row["cluster_size"],
                "duplicate": row["duplicate"],
                "campaign_cluster": row["campaign_cluster"],
                "cluster_reasons": row["cluster_reasons"],
                "injection_flags": row["injection_flags"],
                "pii_types_redacted": row["pii_types_redacted"],
                "special_category_flags": row["special_category_flags"],
                "redacted_text": row["redacted_text"],
                "machine_theme_ids": row["machine_theme_ids"],
                "theme_ids": effective,
                "evidence": row["evidence"],
                "in_sample": row["response_id"] in sample_ids,
                "sample_decision": decision["decision"] if decision else ("pending" if row["response_id"] in sample_ids else None),
            }
        )

    minority_views = []
    for theme in counts["themes"]:
        if not theme["minority"]:
            continue
        excerpts = []
        for response_id in theme["unique_voice_ids"]:
            match = next(item for item in audit if item["response_id"] == response_id)
            excerpts.append(
                {
                    "response_id": response_id,
                    "redacted_excerpt": match["redacted_text"][:240],
                }
            )
        minority_views.append({**theme, "excerpts": excerpts})

    return {
        "experiment": "07-consultation-themes",
        "catalogue_id": "V010",
        "kind": "theme_analysis",
        "evaluation_label": EVALUATION_LABEL,
        "autonomy": "A1",
        "processing_mode": processing_mode,
        "fallback_reason": fallback_reason,
        "analysis_status": status,
        "headline_counts_provisional": not reviewed,
        "unsampled_assignments_are_not_individually_approved": True,
        "consultation_id": batch.get("consultation_id"),
        "question_id": batch.get("question_id") or "Q1",
        "question": batch.get("question"),
        "body": batch.get("body"),
        "framework": {
            **framework_record,
            "theme_ids": [theme["theme_id"] for theme in themes],
        },
        "retrieval": {**retrieval, "stale_acknowledged": stale_acknowledged},
        "counts": {
            "submissions": len(rows),
            "unique_voices": counts["denominator"],
            "campaign_clusters": len(
                {row["cluster_id"] for row in rows if row["campaign_cluster"]}
            ),
            "proportion_basis": "unique_voices_after_duplicate_clustering",
            "uncertainty_method": UNCERTAINTY_NOTE,
        },
        "themes": counts["themes"],
        "minority_views": minority_views,
        "framework_themes_with_no_support": counts["no_support"],
        "uncoded_response_ids": counts["uncoded_response_ids"],
        "sample": [
            {
                "response_id": response_id,
                "decision": decisions.get(response_id, {}).get("decision", "pending"),
            }
            for response_id in sample_ids
        ],
        "ignored_decisions_outside_sample": ignored,
        "rejected_external_theme_ids": rejected_labels,
        "audit": audit,
        "external_engine": external,
        "security": _security(),
        "campaign_copies_not_dropped": True,
        "every_submission_is_in_the_audit": len(audit) == len(rows),
    }


def _effective_theme_ids(
    row: dict[str, Any],
    *,
    use_machine: bool,
    decisions: dict[str, dict[str, Any]],
) -> list[str] | None:
    """Return theme ids to count, or None when the row is held out."""
    if use_machine:
        return list(row["machine_theme_ids"])
    decision = decisions.get(row["response_id"])
    if decision and decision["decision"] == "reject":
        return None
    if decision and decision["decision"] == "correct":
        return list(decision["theme_ids"])
    return list(row["machine_theme_ids"])


def _count_themes(
    rows: list[dict[str, Any]],
    themes: list[dict[str, Any]],
    *,
    rejected_ids: set[str],
    use_machine: bool,
    decisions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    decisions = decisions or {}
    # Denominator: clusters with at least one row that is still counted.
    clusters: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        clusters.setdefault(str(row["cluster_id"]), []).append(row)
    alive_clusters = 0
    for members in clusters.values():
        if any(member["response_id"] not in rejected_ids for member in members):
            alive_clusters += 1

    theme_rows: list[dict[str, Any]] = []
    no_support: list[dict[str, Any]] = []
    for theme in themes:
        theme_id = theme["theme_id"]
        linked: list[str] = []
        counted: list[str] = []
        held: list[str] = []
        for row in rows:
            machine_hit = theme_id in row["machine_theme_ids"]
            decision = decisions.get(row["response_id"])
            corrected_hit = bool(
                decision
                and decision["decision"] == "correct"
                and theme_id in decision["theme_ids"]
            )
            if machine_hit or corrected_hit:
                linked.append(row["response_id"])
            effective = _effective_theme_ids(row, use_machine=use_machine, decisions=decisions)
            if effective is None:
                if machine_hit or corrected_hit:
                    held.append(row["response_id"])
                continue
            if theme_id in effective:
                counted.append(row["response_id"])

        unique_ids: list[str] = []
        for members in clusters.values():
            alive_hits = []
            for member in members:
                if member["response_id"] in rejected_ids:
                    continue
                effective = _effective_theme_ids(member, use_machine=use_machine, decisions=decisions)
                if effective and theme_id in effective:
                    alive_hits.append(member["response_id"])
            if alive_hits:
                unique_ids.append(sorted(alive_hits)[0])
        unique_ids = sorted(unique_ids)
        unique_count = len(unique_ids)
        low, high = wilson_interval(unique_count, alive_clusters)
        proportion = (unique_count / alive_clusters) if alive_clusters else 0.0
        record = {
            "theme_id": theme_id,
            "label": theme["label"],
            "submission_count": len(counted),
            "unique_voice_count": unique_count,
            "proportion_of_unique_voices": round6(proportion),
            "wilson_95": {"low": round6(low), "high": round6(high)},
            "uncertainty_note": UNCERTAINTY_NOTE,
            "minority": _minority(unique_count, alive_clusters),
            "response_ids": sorted(linked),
            "counted_response_ids": sorted(counted),
            "unique_voice_ids": unique_ids,
            "held_out_response_ids": sorted(held),
            "preserved": True,
        }
        theme_rows.append(record)
        if not linked:
            no_support.append(
                {
                    "theme_id": theme_id,
                    "label": theme["label"],
                    "response_ids": [],
                    "note": "In the framework. No submission was coded to it. Kept so an absent code is visible.",
                }
            )

    uncoded = []
    for row in rows:
        effective = _effective_theme_ids(row, use_machine=use_machine, decisions=decisions)
        if effective is None:
            continue
        if effective == [UNCODED]:
            uncoded.append(row["response_id"])

    return {
        "themes": theme_rows,
        "no_support": no_support,
        "uncoded_response_ids": sorted(uncoded),
        "denominator": alive_clusters,
    }


def propose_from_batch(
    batch: dict[str, Any],
    *,
    module: Any = None,
    llm: Any = None,
) -> dict[str, Any]:
    """Ask ThemeFinder for a proposal. Flagged rows are not sent. Never approved."""
    prepared = _prepare_responses(batch)
    excluded = [row["response_id"] for row in prepared if row["injection_flags"]]
    sendable = [
        {"response_id": row["response_id"], "text": row["redacted_text"]}
        for row in prepared
        if not row["injection_flags"]
    ]
    result = tf.propose_themes(
        sendable,
        str(batch.get("question") or ""),
        module=module,
        llm=llm,
    )
    result["approved"] = False
    result["excluded_response_ids"] = excluded
    result["security"] = _security()
    return result
