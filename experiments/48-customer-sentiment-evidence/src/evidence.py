#!/usr/bin/env python3
"""Draft a customer sentiment evidence pack. Do not publish it.

The same batch and the same as-of date produce the same JSON. Free text is
passed through a local suppression of a few direct-identifier patterns and
then through Experiment 08. Duplicate texts are clustered with Experiment 07,
and the Wilson interval comes from the same experiment. A financial-services
complaint is classified with Experiment 20. The pack is not a board report,
not a finding that an outcome was met, and not anonymised.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import excise, signals_in
    from lexicon import SENTIMENTS, THEMES, sentiment_of, themes_of
    from reuse import classify_financial, cluster_responses, redact, round6, wilson_interval
    from sources import (
        LABEL_DRAFT,
        LABEL_READY,
        LABEL_REFUSED,
        SMALL_N,
        SOURCES,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
    )
else:
    from .injection import excise, signals_in
    from .lexicon import SENTIMENTS, THEMES, sentiment_of, themes_of
    from .reuse import classify_financial, cluster_responses, redact, round6, wilson_interval
    from .sources import (
        LABEL_DRAFT,
        LABEL_READY,
        LABEL_REFUSED,
        SMALL_N,
        SOURCES,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
    )

CATALOGUE_ID = "C010"
EXPERIMENT = "48-customer-sentiment-evidence"
MAX_TEXT = 20000
EXCERPT_CHARS = 240
CHANNELS = ("complaint", "survey", "contact_note", "review")
SECTORS = ("financial_services", "public_service")
METHODS = ("census", "random", "convenience", "not_stated")
TOKEN = re.compile(r"^SYN-[A-Za-z0-9-]{1,36}$")
PROHIBITED_DECISIONS = (
    "publish",
    "publish_pack",
    "contact_customer",
    "conclude_about_individual",
    "approve_board_report",
    "submit_return",
    "write_production_record",
)
CONTROL_KEYS = {
    "ready",
    "published",
    "human_approval",
    "status",
    "actions_taken",
    "contacted_customer",
    "individual_conclusion",
    "board_report_approved",
    "duty_met",
    "outcome_tested",
}
IGNORED_RECORD_KEYS = {
    "customer_name",
    "name",
    "email",
    "phone",
    "address",
    "customer_id",
    "supplied_sentiment",
    "sentiment",
    "ready",
    "published",
}

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(r"\b(?:\+44\s?7\d{3}|07\d{3})[\s-]?\d{3}[\s-]?\d{3}\b")
# Case-sensitive on the given name so "I am really unhappy" is kept.
_NAME = re.compile(r"\bmy name is\s+[A-Za-z]+(?:\s+[A-Za-z]+)?\b", re.IGNORECASE)
_I_AM = re.compile(r"\bI am\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b")


class SentimentForbidden(RuntimeError):
    """A direct call tried to publish, contact, conclude, or file."""


def publish_pack(*_args, **_kwargs) -> None:
    raise SentimentForbidden("publish")


def contact_customer(*_args, **_kwargs) -> None:
    raise SentimentForbidden("contact")


def conclude_about_individual(*_args, **_kwargs) -> None:
    raise SentimentForbidden("individual_conclusion")


def approve_board_report(*_args, **_kwargs) -> None:
    raise SentimentForbidden("board_report")


def submit_return(*_args, **_kwargs) -> None:
    raise SentimentForbidden("submit")


def write_production_record(*_args, **_kwargs) -> None:
    raise SentimentForbidden("write")


def _moment(as_of: date) -> datetime:
    return datetime(as_of.year, as_of.month, as_of.day, 12, 0, tzinfo=timezone.utc)


def _parse_day(value: object, *, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(field)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(field) from exc


def _suppress(text: str) -> tuple[str, list[str]]:
    """Replace a few direct-identifier shapes. This is not Article 4(1)(5)."""

    kinds: list[str] = []

    def _sub(pattern: re.Pattern[str], token: str, kind: str, value: str) -> str:
        if pattern.search(value):
            kinds.append(kind)
            return pattern.sub(token, value)
        return value

    cleaned = _sub(_EMAIL, "[EMAIL]", "email", text)
    cleaned = _sub(_PHONE, "[PHONE]", "phone", cleaned)
    cleaned = _sub(_NAME, "[NAME]", "name_introduction", cleaned)
    cleaned = _sub(_I_AM, "[NAME]", "name_introduction", cleaned)
    return cleaned, kinds


def _flags() -> dict:
    return {
        "published": False,
        "contacted_customer": False,
        "individual_conclusion": False,
        "board_report_approved": False,
        "regulatory_return_submitted": False,
        "production_record_written": False,
        "duty_met": False,
        "outcome_tested": False,
        "quotes_meet_article_4_1_5": False,
        "output_is_anonymised": False,
        "reversible_map_kept": False,
        "statistical_purpose_asserted": False,
    }


def _base(as_of: date, *, status: str, outcome: str, label: str) -> dict:
    return {
        "label": label,
        "catalogue_id": CATALOGUE_ID,
        "experiment": EXPERIMENT,
        "autonomy": "A0",
        "status": status,
        "outcome": outcome,
        "ready": False,
        "as_of": as_of.isoformat(),
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "text_echoed": False,
        "flags": _flags(),
        "human_route": {
            "offered": True,
            "agent_publishes": False,
            "agent_contacts": False,
            "how": "The analyst can stop and produce the pack in the organisation's own process.",
        },
    }


def _strings(value: object, prefix: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((prefix or "text", value))
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(_strings(item, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_strings(item, f"{prefix}[{index}]"))
    return found


def _checksum(payload: dict) -> str:
    body = {key: value for key, value in payload.items() if key != "draft_checksum"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _empty_counts() -> dict[str, int]:
    return {name: 0 for name in SENTIMENTS}


def _proportion_cell(counts: dict[str, int]) -> dict:
    total = sum(counts.values())
    negative = counts["negative"]
    positive = counts["positive"]
    low_n, high_n = wilson_interval()(negative, total)
    low_p, high_p = wilson_interval()(positive, total)
    return {
        "denominator": "unique_voices",
        "n": total,
        "counts": counts,
        "counts_sum_to_n": sum(counts.values()) == total,
        "negative_proportion": round6(negative / total) if total else 0.0,
        "positive_proportion": round6(positive / total) if total else 0.0,
        "negative_wilson_95": {"low": round6(low_n), "high": round6(high_n)},
        "positive_wilson_95": {"low": round6(low_p), "high": round6(high_p)},
        "interval_defined": total > 0,
        "intervals_are_not_a_partition": True,
        "wilson_source": "experiments/07-consultation-themes/src/stats.py",
        "caveat": (
            "The Wilson interval is the sampling uncertainty of one proportion "
            "in this sample, from Experiment 07. It assumes a simple random "
            "sample and independent texts. It is not a model confidence score. "
            "It does not include coding error or bias from a convenience sample. "
            "The negative interval and the positive interval are separate. "
            "Mixed and unclear texts sit in the denominator and in neither numerator. "
            "A narrow interval is not a finding that an outcome was met."
        ),
    }


def _sources_for(sector: str, *, current: bool) -> list[dict]:
    rows = []
    for source in SOURCES:
        is_prin = source["id"].startswith("prin_")
        # A public-service pack does not quote PRIN. The pages were opened for
        # the financial-services path. Quoting them here would read as a duty.
        withheld_for_sector = is_prin and sector != "financial_services"
        show = current and not withheld_for_sector
        rows.append(
            {
                "id": source["id"],
                "provision": source["provision"],
                "url": source["url"],
                "opened_on": SOURCES_PINNED_ON.isoformat(),
                "number_verified": source["number_verified"],
                "number_basis": source["number_basis"],
                "applied_to_this_pack": is_prin and sector == "financial_services",
                "taken": source["text"] if show else None,
                "text_withheld": not show,
                "withheld_reason": (
                    "prin_not_applied_to_public_service_pack" if withheld_for_sector else None
                ),
            }
        )
    return rows


def _limitations(context: dict) -> list[dict]:
    method = context["method"]
    exclusions = context["exclusions"]
    sampling_applies = method not in {"census", "random"} or bool(exclusions)
    rows = [
        {
            "id": "sampling_bias",
            "applies": sampling_applies,
            "text": (
                "A convenience sample, an unstated method, or a list of exclusions "
                "can miss the people who did not write in. A census of the file "
                "the analyst supplied is not a census of every customer. "
                "The interval does not correct for that."
            ),
        },
        {
            "id": "small_numbers",
            "applies": context["unique_voices"] < SMALL_N,
            "threshold": SMALL_N,
            "threshold_basis": "starter_default_not_a_statute",
            "text": (
                f"Fewer than {SMALL_N} unique voices is marked as small numbers. "
                "The threshold is a starter default. It is not a rule in PRIN 2A. "
                "A small sample can move a proportion a long way when one text is recoded."
            ),
        },
        {
            "id": "model_error",
            "applies": True,
            "text": (
                "No model was called. The codes are a keyword list. A keyword list "
                "misses paraphrase and can false-match. A later model would add "
                "model error. This pack does not measure that error."
            ),
        },
        {
            "id": "residual_identification",
            "applies": True,
            "text": (
                "Experiment 08 replaces detected UK identifiers and does not claim "
                "anonymisation. This starter also replaces an email, a mobile-shaped "
                "number, and a 'my name is' introduction. Those patterns are not "
                "Article 4(1)(5). Residual text can still identify a person. "
                "quotes_meet_article_4_1_5 is false. No reversible map is kept."
            ),
        },
        {
            "id": "not_statistical_purpose",
            "applies": True,
            "text": (
                "UK GDPR Article 4(5), the paragraph on statistical purposes, "
                "requires the resulting information to be aggregate data that is "
                "not personal data. Representative quotes may still be personal data. "
                "This pack does not assert that paragraph. It also does not use a "
                "quote in support of a decision about a particular person."
            ),
        },
        {
            "id": "not_individual_conclusions",
            "applies": True,
            "text": (
                "A sentiment code and a theme are codes on one text, for the "
                "aggregate. They are not a conclusion about the person who wrote it. "
                "individual_conclusion stays false."
            ),
        },
        {
            "id": "themes_overlap",
            "applies": True,
            "text": (
                "A text can sit in more than one theme. Theme counts must not be "
                "added up and called a population. The population is the unique-voice "
                "denominator on the distribution."
            ),
        },
        {
            "id": "wilson_assumptions",
            "applies": True,
            "text": (
                "The Wilson interval assumes a simple random sample. Campaign copies "
                "are clustered first, by Experiment 07, so an exact duplicate is not "
                "a second voice. Near-duplicate clustering can still join texts that "
                "are not the same sentiment. The counted sentiment is the "
                "representative's, which is the lowest record id in the cluster."
            ),
        },
    ]
    if context["sector"] == "financial_services":
        rows.append(
            {
                "id": "not_a_board_report",
                "applies": True,
                "text": (
                    "This pack is not the report a governing body approves under "
                    "PRIN 2A.8.4R(1), and it is not the monitoring in PRIN 2A.9. "
                    "duty_met and outcome_tested stay false. Where a provision "
                    "number was not reprinted on the 11 November 2026 rendering, "
                    "number_verified is false."
                ),
            }
        )
        rows.append(
            {
                "id": "lexicons_may_disagree",
                "applies": context["complaints_called"],
                "text": (
                    "Experiment 20, which calls Experiment 02, can name a different "
                    "root cause from the theme list in this folder. The pack does "
                    "not pick a winner and does not call that difference a breach."
                ),
            }
        )
    else:
        rows.append(
            {
                "id": "public_service_no_statute",
                "applies": True,
                "text": (
                    "No public-sector service-feedback statute was opened for this "
                    "starter. PRIN 2A is not applied to this pack. That is not a "
                    "finding that a public body is outside the Duty. It is a limit "
                    "of what was read."
                ),
            }
        )
    if context["rules_current"] is False:
        rows.append(
            {
                "id": "stale_sources",
                "applies": True,
                "text": (
                    "The as-of date is more than 180 days after 11 November 2026. "
                    "Legal quotations are withheld. The keyword codes are still produced. "
                    "The 180-day window is a starter default, not a review duty in PRIN 2A."
                ),
            }
        )
    if context["period_open"]:
        rows.append(
            {
                "id": "period_not_closed",
                "applies": True,
                "text": (
                    "The period end is after the as-of date. Later texts are not in "
                    "this file. The analyst has to acknowledge that before the pack can be marked ready."
                ),
            }
        )
    return rows


def _refused(as_of: date, outcome: str) -> dict:
    pack = _base(as_of, status="refused", outcome=outcome, label=LABEL_REFUSED)
    pack["sample_frame"] = None
    pack["distribution"] = None
    pack["themes"] = []
    pack["limitations"] = []
    pack["sources"] = []
    pack["prompt_injection"] = {"detected": False, "followed": False, "signals": []}
    pack["draft_checksum"] = _checksum(pack)
    return pack


def prepare_pack(batch: dict, as_of: str | date) -> dict:
    """Return one evidence pack. ``human_approval`` is null. ``ready`` is false."""

    if isinstance(as_of, str):
        as_of_day = _parse_day(as_of, field="as_of")
    elif isinstance(as_of, date):
        as_of_day = as_of
    else:
        raise ValueError("as_of")
    if not isinstance(batch, dict):
        raise ValueError("batch")

    if batch.get("synthetic") is not True:
        return _refused(as_of_day, "refused_not_synthetic")

    sector = batch.get("sector")
    if sector not in SECTORS:
        return _refused(as_of_day, "refused_sector")

    batch_id = batch.get("batch_id")
    if not isinstance(batch_id, str) or not TOKEN.match(batch_id):
        return _refused(as_of_day, "refused_batch_id")

    period_raw = batch.get("period") if isinstance(batch.get("period"), dict) else {}
    try:
        period_start = _parse_day(period_raw.get("start"), field="period.start")
        period_end = _parse_day(period_raw.get("end"), field="period.end")
    except ValueError:
        return _refused(as_of_day, "refused_period")
    if period_end < period_start:
        return _refused(as_of_day, "refused_period")

    frame = batch.get("sample_frame") if isinstance(batch.get("sample_frame"), dict) else None
    frame_gaps = []
    method = None
    channels_in_frame: list[str] = []
    exclusions: list[str] = []
    population = None
    if frame is None:
        frame_gaps.append("sample_frame_missing")
    else:
        population = frame.get("population_description")
        if not isinstance(population, str) or not population.strip():
            frame_gaps.append("population_description_missing")
            population = None
        elif len(population) > 400:
            frame_gaps.append("population_description_too_long")
            population = population[:400]
        method = frame.get("sampling_method")
        if method not in METHODS:
            frame_gaps.append("sampling_method_missing")
            method = None
        raw_channels = frame.get("channels_in_frame")
        if not isinstance(raw_channels, list) or not raw_channels:
            frame_gaps.append("channels_in_frame_missing")
        else:
            channels_in_frame = [item for item in raw_channels if item in CHANNELS]
            if len(channels_in_frame) != len(raw_channels):
                frame_gaps.append("channels_in_frame_not_closed")
            if not channels_in_frame:
                frame_gaps.append("channels_in_frame_missing")
        raw_exclusions = frame.get("known_exclusions")
        if not isinstance(raw_exclusions, list):
            frame_gaps.append("known_exclusions_missing")
        else:
            exclusions = [item for item in raw_exclusions if isinstance(item, str)][:12]

    records = batch.get("records")
    if not isinstance(records, list):
        return _refused(as_of_day, "refused_records")

    control_signals = []
    for key in CONTROL_KEYS:
        if key in batch:
            control_signals.append(
                {"signal": "prohibited_key", "hidden_in": "body", "key": key, "followed": False}
            )

    moment = _moment(as_of_day)
    rules_current = as_of_day <= SOURCES_PINNED_ON + timedelta(days=STALE_AFTER_DAYS)
    period_open = period_end > as_of_day

    injection_signals: list[dict] = []
    seen_signals: set[tuple[str, str]] = set()
    for field, text in _strings(batch):
        for signal in signals_in(text):
            marker = (signal["signal"], signal["hidden_in"])
            if marker in seen_signals:
                continue
            seen_signals.add(marker)
            injection_signals.append(signal)
    injection_signals.extend(control_signals)

    prepared: list[dict] = []
    excluded: dict[str, list[str]] = defaultdict(list)
    identifier_types: set[str] = set()
    local_kinds: set[str] = set()
    finding_counts = 0
    texts_not_scanned = 0
    ignored_fields = False

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            excluded["not_an_object"].append(f"index-{index}")
            continue
        if any(key in record for key in IGNORED_RECORD_KEYS):
            ignored_fields = True
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not TOKEN.match(record_id):
            excluded["record_id_not_synthetic_pattern"].append(
                record_id if isinstance(record_id, str) and TOKEN.match(record_id) else f"index-{index}"
            )
            continue
        channel = record.get("channel")
        if channel not in CHANNELS:
            excluded["channel_unknown"].append(record_id)
            continue
        if channels_in_frame and channel not in channels_in_frame:
            excluded["channel_not_in_frame"].append(record_id)
            continue
        try:
            received = _parse_day(record.get("received_on"), field="received_on")
        except ValueError:
            excluded["bad_date"].append(record_id)
            continue
        if received < period_start or received > period_end:
            excluded["out_of_period"].append(record_id)
            continue
        raw_text = record.get("text")
        if not isinstance(raw_text, str):
            excluded["text_missing"].append(record_id)
            continue
        if len(raw_text) > MAX_TEXT:
            texts_not_scanned += 1
            excluded["text_not_scanned_too_long"].append(record_id)
            continue
        cleaned = excise(raw_text)
        suppressed, kinds = _suppress(cleaned)
        local_kinds.update(kinds)
        redaction = redact(suppressed, now=moment)
        identifier_types.update(redaction["entity_types"])
        finding_counts += redaction["finding_count"]
        coded = redaction["text"]
        prepared.append(
            {
                "record_id": record_id,
                "channel": channel,
                "received_on": received.isoformat(),
                "period": received.strftime("%Y-%m"),
                "text": coded,
                "sentiment": sentiment_of(coded),
                "theme_ids": themes_of(coded),
            }
        )

    # Stable order so clustering does not depend on input order beyond ids.
    prepared.sort(key=lambda row: row["record_id"])
    duplicate_ids = [row["record_id"] for row in prepared]
    if len(duplicate_ids) != len(set(duplicate_ids)):
        seen: set[str] = set()
        kept = []
        for row in prepared:
            if row["record_id"] in seen:
                excluded["duplicate_record_id"].append(row["record_id"])
                continue
            seen.add(row["record_id"])
            kept.append(row)
        prepared = kept

    cluster_map = {}
    if prepared:
        cluster_map = cluster_responses()(
            [{"response_id": row["record_id"], "text": row["text"]} for row in prepared]
        )

    voices = []
    not_extra = []
    for row in prepared:
        cluster = cluster_map.get(row["record_id"], {})
        entry = {
            "record_id": row["record_id"],
            "cluster_id": cluster.get("cluster_id"),
            "cluster_size": cluster.get("cluster_size", 1),
            "channel": row["channel"],
            "period": row["period"],
            "sentiment": row["sentiment"],
            "theme_ids": row["theme_ids"],
            "text_code_not_a_customer_conclusion": True,
        }
        if cluster.get("is_representative", True):
            voices.append(entry)
        else:
            not_extra.append(
                {
                    "record_id": row["record_id"],
                    "cluster_id": cluster.get("cluster_id"),
                    "counted_in_denominator": False,
                }
            )

    overall_counts = _empty_counts()
    by_channel: dict[str, dict[str, int]] = defaultdict(_empty_counts)
    by_period: dict[str, dict[str, int]] = defaultdict(_empty_counts)
    for voice in voices:
        overall_counts[voice["sentiment"]] += 1
        by_channel[voice["channel"]][voice["sentiment"]] += 1
        by_period[voice["period"]][voice["sentiment"]] += 1

    themes = []
    for theme_id, family, _phrases in THEMES:
        members = [row for row in prepared if theme_id in row["theme_ids"]]
        if not members:
            continue
        cluster_ids = []
        for row in members:
            cluster_id = cluster_map.get(row["record_id"], {}).get("cluster_id", row["record_id"])
            if cluster_id not in cluster_ids:
                cluster_ids.append(cluster_id)
        quotes = []
        quoted_clusters: set[str] = set()
        for row in members:
            cluster_id = cluster_map.get(row["record_id"], {}).get("cluster_id", row["record_id"])
            if cluster_id in quoted_clusters:
                continue
            excerpt = row["text"].strip()
            if len(excerpt) > EXCERPT_CHARS:
                excerpt = excerpt[:EXCERPT_CHARS].rstrip() + "…"
            if not excerpt:
                continue
            quotes.append(
                {
                    "record_id": row["record_id"],
                    "channel": row["channel"],
                    "excerpt": excerpt,
                    "excerpt_is_redacted": True,
                }
            )
            quoted_clusters.add(cluster_id)
            if len(quotes) == 2:
                break
        themes.append(
            {
                "theme_id": theme_id,
                "family": family,
                "outcome_relevance": family if sector == "financial_services" else "not_applied",
                "record_ids": [row["record_id"] for row in members],
                "unique_voice_count": len(cluster_ids),
                "quotes": quotes,
                "do_not_sum_with_other_themes": True,
            }
        )

    complaints_rows = []
    complaints_called = False
    if sector == "financial_services":
        for row in prepared:
            if row["channel"] != "complaint":
                continue
            complaints_called = True
            coded = classify_financial(row["text"])
            complaints_rows.append(
                {
                    "record_id": row["record_id"],
                    "theme": coded.get("theme"),
                    "product": coded.get("product"),
                    "duty_outcome_touched": coded.get("duty_outcome_touched"),
                    "source": coded.get("source"),
                    "breach_found": False,
                    "customer_labelled_vulnerable": False,
                    "text_code_not_a_customer_conclusion": True,
                }
            )
    complaints = {
        "called": complaints_called,
        "experiment": "20-complaints-root-cause-mi" if complaints_called else None,
        "method": "classify" if complaints_called else None,
        "not_a_regulatory_return": True,
        "reason": None
        if complaints_called or sector == "financial_services"
        else "public_service_pack_does_not_use_the_complaints_mi_lexicon",
        "rows": complaints_rows,
    }
    if sector == "financial_services" and not complaints_called:
        complaints["reason"] = "no_in_frame_complaint"

    understanding_ids = [
        theme["theme_id"] for theme in themes if theme["family"] == "consumer_understanding"
    ]
    support_ids = [
        theme["theme_id"] for theme in themes if theme["family"] == "consumer_support"
    ]

    def _ids_for(theme_ids: list[str]) -> list[str]:
        found = []
        for theme in themes:
            if theme["theme_id"] in theme_ids:
                for record_id in theme["record_ids"]:
                    if record_id not in found:
                        found.append(record_id)
        return found

    if sector == "financial_services":
        outcome_testing = {
            "applied": True,
            "is_the_prin_2a_8_report": False,
            "monitoring_carried_out": False,
            "finding": None,
            "understanding": {
                "rules": ["PRIN 2A.5.3R(1)", "PRIN 2A.5.3R(2)", "PRIN 2A.5.10R(1)"],
                "monitoring_point": "PRIN 2A.9.9R(3)",
                "relevant_theme_ids": understanding_ids,
                "record_ids": _ids_for(understanding_ids),
                "finding": None,
            },
            "support": {
                "rules": ["PRIN 2A.6.2R"],
                "monitoring_point": "PRIN 2A.9.9R(4)",
                "relevant_theme_ids": support_ids,
                "record_ids": _ids_for(support_ids),
                "finding": None,
            },
            "root_cause_processes": {
                "rule": "PRIN 2A.9.11R",
                "number_verified": False,
                "note": (
                    "Experiment 20 assigns one root-cause code per in-frame complaint. "
                    "That is not the process PRIN 2A.9.11R requires a firm to have."
                ),
            },
            "board_report": {
                "rules": ["PRIN 2A.8.3R", "PRIN 2A.8.4R", "PRIN 2A.8.5R"],
                "this_pack_is_that_report": False,
                "prin_2a_8_5_number_verified": False,
            },
        }
    else:
        outcome_testing = {
            "applied": False,
            "reason": "public_service_feedback_prin_not_applied",
            "statute_opened": False,
            "is_the_prin_2a_8_report": False,
            "monitoring_carried_out": False,
            "finding": None,
        }

    distribution = {
        "denominator": "unique_voices",
        "themes_must_not_be_summed": True,
        "overall": _proportion_cell(overall_counts),
        "by_channel": [
            {"channel": channel, **_proportion_cell(by_channel[channel])}
            for channel in sorted(by_channel)
        ],
        "by_period": [
            {"period": period, **_proportion_cell(by_period[period])}
            for period in sorted(by_period)
        ],
    }
    channel_n = sum(cell["n"] for cell in distribution["by_channel"])
    period_n = sum(cell["n"] for cell in distribution["by_period"])
    distribution["channel_n_equals_overall"] = channel_n == distribution["overall"]["n"]
    distribution["period_n_equals_overall"] = period_n == distribution["overall"]["n"]

    unique_voices = len(voices)
    if frame_gaps:
        outcome = "sample_frame_incomplete"
    elif not prepared:
        outcome = "no_in_frame_records"
    elif not rules_current:
        outcome = "stale_sources"
    else:
        outcome = "draft_pending_analyst"

    organisation = batch.get("organisation")
    if not isinstance(organisation, str) or len(organisation) > 80:
        organisation = None

    pack = _base(as_of_day, status="draft", outcome=outcome, label=LABEL_DRAFT)
    pack.update(
        {
            "batch_id": batch_id,
            "sector": sector,
            "organisation": organisation,
            "organisation_is_fictional_in_the_samples": True,
            "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
            "period_open": period_open,
            "sample_frame": {
                "population_description": population,
                "sampling_method": method,
                "channels_in_frame": channels_in_frame,
                "known_exclusions": exclusions,
                "gaps": frame_gaps,
                "complete": not frame_gaps,
            },
            "counts": {
                "records_supplied": len(records),
                "in_frame_records": len(prepared),
                "unique_voices": unique_voices,
                "not_counted_as_extra_voices": len(not_extra),
                "excluded": {key: sorted(set(value)) for key, value in sorted(excluded.items())},
                "texts_not_scanned_too_long": texts_not_scanned,
                "direct_identifier_fields_ignored": ignored_fields,
            },
            "distribution": distribution,
            "voices": voices,
            "not_counted_as_extra_voices": not_extra,
            "themes": themes,
            "complaints_root_cause": complaints,
            "outcome_testing": outcome_testing,
            "limitations": _limitations(
                {
                    "method": method,
                    "exclusions": exclusions,
                    "unique_voices": unique_voices,
                    "sector": sector,
                    "complaints_called": complaints_called,
                    "rules_current": rules_current,
                    "period_open": period_open,
                }
            ),
            "sources": _sources_for(sector, current=rules_current),
            "stale": {
                "rules_current": rules_current,
                "pinned_on": SOURCES_PINNED_ON.isoformat(),
                "stale_after_days": STALE_AFTER_DAYS,
            },
            "prompt_injection": {
                "detected": bool(injection_signals),
                "followed": False,
                "signals": injection_signals,
            },
            "reuse": {
                "experiment_08": {
                    "called": True,
                    "finding_count": finding_counts,
                    "entity_types": sorted(identifier_types),
                    "output_is_anonymised": False,
                    "reversible_map_kept": False,
                    "model_suggestions_applied": False,
                },
                "experiment_07": {
                    "called": bool(prepared),
                    "cluster": True,
                    "wilson": True,
                },
                "experiment_20": {
                    "called": complaints_called,
                    "experiment_02_called_by_experiment_20": complaints_called,
                },
                "local_suppression": sorted(local_kinds),
            },
            "raw_text_kept": False,
        }
    )
    pack["draft_checksum"] = _checksum(pack)
    _force_safe(pack)
    return pack


def _force_safe(pack: dict) -> None:
    pack["actions_taken"] = []
    pack["executed"] = False
    pack["model_called"] = False
    pack["network_called"] = False
    pack["text_echoed"] = False
    flags = pack["flags"]
    for key in (
        "published",
        "contacted_customer",
        "individual_conclusion",
        "board_report_approved",
        "regulatory_return_submitted",
        "production_record_written",
        "duty_met",
        "outcome_tested",
        "quotes_meet_article_4_1_5",
        "output_is_anonymised",
        "reversible_map_kept",
        "statistical_purpose_asserted",
    ):
        flags[key] = False
    pack["human_route"]["agent_publishes"] = False
    pack["human_route"]["agent_contacts"] = False
    if pack.get("prompt_injection"):
        pack["prompt_injection"]["followed"] = False
        for signal in pack["prompt_injection"]["signals"]:
            signal["followed"] = False
    testing = pack.get("outcome_testing") or {}
    testing["is_the_prin_2a_8_report"] = False
    testing["monitoring_carried_out"] = False
    testing["finding"] = None
    for name in ("understanding", "support"):
        if isinstance(testing.get(name), dict):
            testing[name]["finding"] = None
    complaints = pack.get("complaints_root_cause") or {}
    complaints["not_a_regulatory_return"] = True
    for row in complaints.get("rows") or []:
        row["breach_found"] = False
        row["customer_labelled_vulnerable"] = False


def record_review(pack: dict, review: dict) -> dict:
    """Record an analyst confirmation or a rejection. Nothing is published."""

    updated = deepcopy(pack)
    decision = review.get("decision") if isinstance(review, dict) else None
    base_review = {
        "decision": decision if isinstance(decision, str) else None,
        "accepted": False,
        "refused": True,
        "executed": False,
        "published": False,
        "contacted_customer": False,
    }
    if not isinstance(review, dict):
        base_review["reason"] = "review_not_an_object"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if decision in PROHIBITED_DECISIONS:
        base_review["reason"] = "prohibited_decision"
        updated["review"] = base_review
        updated["ready"] = False
        updated["human_approval"] = None
        _force_safe(updated)
        return updated
    if decision not in {"confirm_sample_frame_and_limitations", "reject_pack"}:
        base_review["reason"] = "unknown_decision"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if review.get("actor_role") != "Analyst":
        base_review["reason"] = "analyst_role_required"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    actor_id = review.get("actor_id")
    if not isinstance(actor_id, str) or not TOKEN.match(actor_id):
        base_review["reason"] = "actor_id"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if updated.get("status") == "refused":
        base_review["reason"] = "pack_refused"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if review.get("batch_id") != updated.get("batch_id"):
        base_review["reason"] = "batch_id_mismatch"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if review.get("draft_checksum") != updated.get("draft_checksum"):
        base_review["reason"] = "checksum_mismatch"
        updated["review"] = base_review
        _force_safe(updated)
        return updated

    if decision == "reject_pack":
        updated["status"] = "draft"
        updated["ready"] = False
        updated["label"] = LABEL_DRAFT
        updated["human_approval"] = {
            "decision": "reject_pack",
            "actor_role": "Analyst",
            "actor_id": actor_id,
            "ready": False,
        }
        updated["review"] = {
            **base_review,
            "accepted": True,
            "refused": False,
            "reason": "rejected",
        }
        _force_safe(updated)
        return updated

    frame = updated.get("sample_frame") or {}
    if not frame.get("complete"):
        base_review["reason"] = "sample_frame_incomplete"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if review.get("sample_frame_confirmed") is not True:
        base_review["reason"] = "sample_frame_not_confirmed"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if review.get("limitations_read") is not True:
        base_review["reason"] = "limitations_not_read"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if updated.get("stale", {}).get("rules_current") is False and review.get("sources_acknowledged") is not True:
        base_review["reason"] = "stale_sources_not_acknowledged"
        updated["review"] = base_review
        _force_safe(updated)
        return updated
    if updated.get("period_open") is True and review.get("open_period_acknowledged") is not True:
        base_review["reason"] = "open_period_not_acknowledged"
        updated["review"] = base_review
        _force_safe(updated)
        return updated

    updated["status"] = "ready"
    updated["ready"] = True
    updated["outcome"] = "ready"
    updated["label"] = LABEL_READY
    updated["human_approval"] = {
        "decision": "confirm_sample_frame_and_limitations",
        "actor_role": "Analyst",
        "actor_id": actor_id,
        "sample_frame_confirmed": True,
        "limitations_read": True,
        "ready": True,
        "published": False,
    }
    updated["review"] = {
        **base_review,
        "accepted": True,
        "refused": False,
        "reason": "sample_frame_and_limitations_confirmed",
    }
    _force_safe(updated)
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a customer sentiment evidence pack.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--review")
    args = parser.parse_args(argv)
    try:
        batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
        pack = prepare_pack(batch, args.as_of)
        if args.review:
            review = json.loads(Path(args.review).read_text(encoding="utf-8"))
            pack = record_review(pack, review)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return 2
    json.dump(pack, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
