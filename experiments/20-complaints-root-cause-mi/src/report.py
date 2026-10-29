#!/usr/bin/env python3
"""Draft complaints management information. Do not submit it.

The same batch and the same as-of date produce the same JSON. Free text is
passed through Experiment 08 before it is classified or copied. A
financial-services narrative is then passed to Experiment 02 analyse().
The draft is not a regulatory return, not anonymised, and not sent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from classify import classify
    from figures import (
        assert_sentences,
        count_figure,
        parse_date,
        sum_pence_figure,
        supplied_integer,
        to_pence,
    )
    from injection import neutralise, scan_fields
    from narratives import (
        common_sentences,
        consumer_duty_sentences,
        energy_sentences,
        housing_sentences,
    )
    from reuse import CALLER, redact
    from sources import (
        CHR_REG_11,
        CHR_REG_11_URL,
        CHR_REG_2_URL,
        CHR_RESOLVED,
        CHR_WORKING_DAY,
        CODE_1_2_BODY,
        CODE_8_1,
        CODE_9_4,
        CODE_9_7,
        CODE_PDF_URL,
        CODE_SUBMISSIONS_URL,
        LABEL,
        NOT_A_RETURN,
        OFGEM_B23,
        OFGEM_GUIDANCE_URL,
        OFGEM_RATE,
        OFGEM_SEND,
        PRIN_2A_8_3,
        PRIN_2A_8_4,
        PRIN_2A_8_5,
        PRIN_2A_8_URL,
        PRIN_2A_9_11,
        PRIN_2A_9_URL,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
    )
else:
    from .classify import classify
    from .figures import (
        assert_sentences,
        count_figure,
        parse_date,
        sum_pence_figure,
        supplied_integer,
        to_pence,
    )
    from .injection import neutralise, scan_fields
    from .narratives import (
        common_sentences,
        consumer_duty_sentences,
        energy_sentences,
        housing_sentences,
    )
    from .reuse import CALLER, redact
    from .sources import (
        CHR_REG_11,
        CHR_REG_11_URL,
        CHR_REG_2_URL,
        CHR_RESOLVED,
        CHR_WORKING_DAY,
        CODE_1_2_BODY,
        CODE_8_1,
        CODE_9_4,
        CODE_9_7,
        CODE_PDF_URL,
        CODE_SUBMISSIONS_URL,
        LABEL,
        NOT_A_RETURN,
        OFGEM_B23,
        OFGEM_GUIDANCE_URL,
        OFGEM_RATE,
        OFGEM_SEND,
        PRIN_2A_8_3,
        PRIN_2A_8_4,
        PRIN_2A_8_5,
        PRIN_2A_8_URL,
        PRIN_2A_9_11,
        PRIN_2A_9_URL,
        SOURCES_PINNED_ON,
        STALE_AFTER_DAYS,
    )

CATALOGUE_ID = "UK04"
TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
SECTOR_REPORT = {
    "financial_services": "consumer_duty_board",
    "social_housing": "housing_ombudsman_code",
    "energy": "ofgem_complaints",
}
OUTCOMES = ("upheld", "not_upheld", "open", "withdrawn", "refused", "unknown")
CHANNELS = (
    "telephone",
    "letter",
    "email",
    "webform",
    "webchat",
    "social_media",
    "in_person",
    "other",
)
CHANNEL_GROUP = {
    "telephone": "telephone",
    "letter": "letter",
    "email": "electronic",
    "webform": "electronic",
    "webchat": "electronic",
    "social_media": "electronic",
    "in_person": "not_in_ofgem_channel_list",
    "other": "not_in_ofgem_channel_list",
}
ENERGY_CATEGORIES = (
    "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14",
    "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22",
)
OMBUDSMAN_KINDS = (
    "code_non_compliance_finding",
    "annual_performance_report",
    "other_publication",
)
STRIPPED_KEYS = (
    "approved",
    "submitted",
    "published",
    "sent",
    "is_final_regulatory_return",
    "clusters_validated",
    "narrative_validated",
    "complying_with_consumer_duty",
    "code_compliant",
    "ofgem_return_complete",
    "actions_taken",
    "output_is_anonymised",
    "agent_may_release",
    "as_of",
)
DECISIONS_NOT_TAKEN = (
    "validate_clusters",
    "validate_narrative",
    "final_regulatory_return",
    "consumer_duty_compliance",
    "code_compliance",
    "ofgem_return",
    "submit",
    "publish",
    "send",
    "production_write",
    "redress_offer",
    "vulnerability_label",
    "working_day_calculation",
)


class NotSynthetic(ValueError):
    """The refusal does not echo the batch."""

    def __init__(self) -> None:
        super().__init__("refused: the batch is not marked synthetic")


class ReportForbidden(RuntimeError):
    """The generator has no validate, submit, publish, or send path."""


def approve_clusters(*_args, **_kwargs) -> None:
    raise ReportForbidden("the agent does not validate clusters")


def approve_narrative(*_args, **_kwargs) -> None:
    raise ReportForbidden("the agent does not validate the narrative")


def submit_regulatory_return(*_args, **_kwargs) -> None:
    raise ReportForbidden("the agent does not submit a regulatory return")


def publish_report(*_args, **_kwargs) -> None:
    raise ReportForbidden("the agent does not publish a report")


def send_report(*_args, **_kwargs) -> None:
    raise ReportForbidden("the agent does not send a report")


def write_production_record(*_args, **_kwargs) -> None:
    raise ReportForbidden("the agent does not write a production record")


def _strip(value: object) -> tuple[object, list[str]]:
    removed: list[str] = []

    def walk(item: object) -> object:
        if isinstance(item, dict):
            cleaned = {}
            for key, child in item.items():
                if key in STRIPPED_KEYS:
                    removed.append(str(key))
                    continue
                cleaned[key] = walk(child)
            return cleaned
        if isinstance(item, list):
            return [walk(child) for child in item]
        return item

    return walk(value), removed


def _strings(value: object, prefix: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((prefix or "batch", value))
    elif isinstance(value, dict):
        for key, child in value.items():
            found.extend(_strings(child, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_strings(child, f"{prefix}[{index}]"))
    return found


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or TOKEN.fullmatch(value) is None:
        raise ValueError(f"{field} must be a short token")
    return value


def _closed(value: object, allowed: tuple[str, ...]) -> str:
    if value is None or value == "":
        return "not_recorded"
    if isinstance(value, str) and value in allowed:
        return value
    return "not_in_closed_list"


def _optional_bool(value: object) -> str:
    if value is None:
        return "not_recorded"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return "not_recorded"


def _normalise(text: str) -> str:
    return " ".join(text.lower().split())


def _moment(as_of: date) -> datetime:
    return datetime(as_of.year, as_of.month, as_of.day, tzinfo=timezone.utc)


def _prior_state(prior: object) -> tuple[str, list[str]]:
    if prior is None:
        return "not_supplied", []
    if not isinstance(prior, dict) or not isinstance(prior.get("figures"), list):
        return "not_reconciled", []
    chosen: list[str] | None = None
    for figure in prior["figures"]:
        if not isinstance(figure, dict):
            return "not_reconciled", []
        record_ids = figure.get("record_ids")
        value = figure.get("value")
        if (
            not isinstance(record_ids, list)
            or not all(isinstance(item, str) and TOKEN.fullmatch(item) for item in record_ids)
            or isinstance(value, bool)
            or not isinstance(value, int)
            or value != len(record_ids)
            or len(record_ids) != len(set(record_ids))
        ):
            return "not_reconciled", []
        if figure.get("name") == "in_period_total":
            chosen = list(record_ids)
    if chosen is None:
        return "not_reconciled", []
    return "reconciled", sorted(chosen)


def _accounts(batch: dict) -> tuple[int, int] | None:
    raw = batch.get("customer_accounts")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("customer_accounts must be an object or omitted")
    electricity = raw.get("electricity")
    gas = raw.get("gas")
    if (
        isinstance(electricity, bool)
        or isinstance(gas, bool)
        or not isinstance(electricity, int)
        or not isinstance(gas, int)
        or electricity < 0
        or gas < 0
    ):
        raise ValueError("customer accounts must be non-negative integers or omitted")
    return electricity, gas


def _prepare_record(record: dict, *, sector: str, period: tuple[date, date], moment: datetime) -> dict:
    record_id = _token(record.get("record_id"), "record_id")
    received = parse_date(record.get("received_on"), field="received_on")
    narrative = record.get("narrative", "")
    if not isinstance(narrative, str):
        raise ValueError("narrative must be a string")
    redaction = redact(narrative, now=moment)
    cleaned = neutralise(redaction["text"])
    assigned = classify(sector, cleaned, record)
    start, end = period
    quality: list[str] = []
    closed_raw = record.get("closed_on")
    closed = None
    if closed_raw not in (None, ""):
        closed = parse_date(closed_raw, field="closed_on")
        if closed < received:
            quality.append("closed_before_received")
    redress = to_pence(record.get("redress_gbp")) if "redress_gbp" in record else None
    if "redress_gbp" not in record or record.get("redress_gbp") in (None, ""):
        redress = None
    outcome = _closed(record.get("outcome"), OUTCOMES)
    if outcome == "not_in_closed_list":
        quality.append("outcome_not_in_closed_list")
    channel = _closed(record.get("channel"), CHANNELS)
    if channel == "not_in_closed_list":
        quality.append("channel_not_in_closed_list")
    resolved = _optional_bool(record.get("resolved_by_end_of_first_working_day"))
    if "resolved_by_end_of_first_working_day" in record and resolved == "not_recorded":
        quality.append("resolved_flag_not_a_boolean")
    repeat = _optional_bool(record.get("repeat_complaint"))
    if "repeat_complaint" in record and repeat == "not_recorded":
        quality.append("repeat_flag_not_a_boolean")
    refused = record.get("refused") is True
    refusal_type = "not_refused"
    if refused:
        raw_type = record.get("refusal_type")
        if isinstance(raw_type, str) and TOKEN.fullmatch(raw_type):
            refusal_type = raw_type
        else:
            refusal_type = "type_not_recorded"
    row = {
        "record_id": record_id,
        "received_on": received.isoformat(),
        "in_period": start <= received <= end,
        "theme": assigned["theme"],
        "assignment_reason": assigned["assignment_reason"],
        "theme_source": assigned["source"],
        "matched_phrase": assigned["matched_phrase"],
        "meter_context": assigned.get("meter_context"),
        "meter_context_source": assigned.get("meter_context_source"),
        "outcome": outcome,
        "channel": channel,
        "channel_group": CHANNEL_GROUP.get(channel, channel if channel in {"not_recorded", "not_in_closed_list"} else "not_recorded"),
        "redress_pence": redress,
        "resolved_by_end_of_first_working_day": resolved,
        "repeat_complaint": repeat,
        "refused": refused,
        "refusal_type": refusal_type,
        "working_day_resolution_calculated": False,
        "redaction": redaction,
        "data_quality": quality,
        "normalised": _normalise(cleaned),
    }
    if sector == "financial_services":
        row["experiment_02"] = {
            "cause_suggested": assigned["cause_suggested_by_experiment_02"],
            "intake_cause": assigned["intake_cause"],
            "product_suggested": assigned["product"],
            "duty_outcome_touched": assigned["duty_outcome_touched"],
            "vulnerability_drivers": assigned["vulnerability_drivers"],
            "customer_labelled_vulnerable": False,
            "breach_found": False,
        }
    if assigned.get("intake_ignored"):
        row["data_quality"].append("intake_ignored_wrong_sector")
    return row


def _clusters(rows: list[dict], *, sector: str) -> list[dict]:
    grouped: dict[str, list[str]] = defaultdict(list)
    phrases: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["theme"]].append(row["record_id"])
        if row["matched_phrase"]:
            phrases[row["theme"]].append(
                {"record_id": row["record_id"], "matched_phrase": row["matched_phrase"]}
            )
    themes = list(ENERGY_CATEGORIES) + ["unassigned"] if sector == "energy" else sorted(grouped)
    if sector == "energy":
        # Keep a stable order: B5-B22, then any other theme such as unassigned.
        extras = sorted(set(grouped) - set(themes))
        themes = list(ENERGY_CATEGORIES) + extras
        if "unassigned" not in themes:
            themes.append("unassigned")
    clusters = []
    for theme in themes:
        record_ids = sorted(set(grouped.get(theme, [])))
        if sector != "energy" and not record_ids:
            continue
        clusters.append(
            {
                "theme": theme,
                "figure_id": f"cluster_{theme}",
                "record_ids": record_ids,
                "count": len(record_ids),
                "validated": False,
                "evidence": sorted(phrases.get(theme, []), key=lambda item: item["record_id"]),
            }
        )
    return clusters


def _duplicate_ids(rows: list[dict]) -> list[str]:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if not row["normalised"]:
            continue
        groups[row["normalised"]].append(row["record_id"])
    chosen: list[str] = []
    for record_ids in groups.values():
        if len(record_ids) >= 2:
            chosen.extend(record_ids)
    return sorted(set(chosen))


def _service_improvements(records: list[dict], rows_by_id: dict[str, dict], moment: datetime) -> list[dict]:
    found = []
    for record in records:
        text = record.get("service_improvement")
        if not isinstance(text, str) or not text.strip():
            continue
        if not rows_by_id[record["record_id"]]["in_period"]:
            continue
        redaction = redact(text, now=moment)
        cleaned = neutralise(redaction["text"]).strip()
        if not cleaned:
            continue
        found.append(
            {
                "record_id": record["record_id"],
                "text": cleaned[:500],
                "truncated": len(cleaned) > 500,
                "redaction_finding_count": redaction["finding_count"],
            }
        )
    return found


def _ombudsman(batch: dict, moment: datetime) -> list[dict]:
    raw = batch.get("ombudsman_materials")
    if not isinstance(raw, list):
        return []
    materials = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        material_id = item.get("material_id")
        if not isinstance(material_id, str) or TOKEN.fullmatch(material_id) is None:
            material_id = f"material-{index + 1}"
        kind = item.get("kind") if item.get("kind") in OMBUDSMAN_KINDS else "kind_not_in_closed_list"
        title = item.get("title") if isinstance(item.get("title"), str) else ""
        redaction = redact(title, now=moment)
        materials.append(
            {
                "material_id": material_id,
                "kind": kind,
                "title": neutralise(redaction["text"]).strip()[:300],
                "supplied": True,
            }
        )
    return materials


def _citations(sector: str) -> list[dict]:
    shared_note = "Pinned on 29 October 2026. Not re-fetched at runtime."
    if sector == "financial_services":
        return [
            {"id": "PRIN 2A.8.3R", "url": PRIN_2A_8_URL, "verbatim": True, "text": PRIN_2A_8_3, "note": shared_note},
            {"id": "PRIN 2A.8.4R", "url": PRIN_2A_8_URL, "verbatim": True, "text": PRIN_2A_8_4, "note": "Dated 26 June 2026 on the page."},
            {"id": "PRIN 2A.8.5R", "url": PRIN_2A_8_URL, "verbatim": True, "text": PRIN_2A_8_5, "note": "Dated 26 June 2026 on the page."},
            {"id": "PRIN 2A.9.11R", "url": PRIN_2A_9_URL, "verbatim": True, "text": PRIN_2A_9_11, "note": "Dated 31 July 2023 on the page."},
        ]
    if sector == "social_housing":
        return [
            {"id": "Code 1.2", "url": CODE_PDF_URL, "verbatim": True, "text": CODE_1_2_BODY, "note": "Body of the Code PDF, last revised 17 April 2024."},
            {"id": "Code 8.1", "url": CODE_PDF_URL, "verbatim": False, "text": CODE_8_1, "note": "Summary of the lettered list in section 8.1. Not a substitute for the PDF."},
            {"id": "Code 9.4", "url": CODE_PDF_URL, "verbatim": True, "text": CODE_9_4, "note": shared_note},
            {"id": "Code 9.7", "url": CODE_PDF_URL, "verbatim": False, "text": CODE_9_7, "note": "Summary of section 9.7. Not a substitute for the PDF."},
            {
                "id": "Annual submissions",
                "url": CODE_SUBMISSIONS_URL,
                "verbatim": False,
                "text": (
                    "The annual-submissions page says member landlords demonstrate "
                    "compliance through a dedicated electronic form. Landlords with "
                    "1,000 homes or more submit by 30 September. Landlords with fewer "
                    "than 1,000 properties submit six months after financial year-end. "
                    "This agent does not submit."
                ),
                "note": "The page also displayed a service notice on 29 October 2026.",
            },
        ]
    return [
        {"id": "CHR regulation 2 resolved complaint", "url": CHR_REG_2_URL, "verbatim": True, "text": CHR_RESOLVED, "note": shared_note},
        {"id": "CHR regulation 2 working day", "url": CHR_REG_2_URL, "verbatim": True, "text": CHR_WORKING_DAY, "note": "This draft does not apply the definition to dates."},
        {"id": "CHR regulation 11", "url": CHR_REG_11_URL, "verbatim": True, "text": CHR_REG_11, "note": shared_note},
        {"id": "Ofgem guidance B23", "url": OFGEM_GUIDANCE_URL, "verbatim": False, "text": OFGEM_B23, "note": "Paragraph 4.9 of the guidance published 4 November 2025."},
        {"id": "Ofgem guidance rates", "url": OFGEM_GUIDANCE_URL, "verbatim": False, "text": OFGEM_RATE, "note": "Paragraph 5.15. This draft does not state either rate."},
        {"id": "Ofgem guidance send", "url": OFGEM_GUIDANCE_URL, "verbatim": False, "text": OFGEM_SEND, "note": "The address in the guidance is not a tool."},
    ]


def _housing_prompts() -> list[dict]:
    return [
        {"provision": "1.2", "comply": None, "note": "The Code definition is in the citations. This draft does not decide that a record meets it."},
        {"provision": "8.1", "comply": None, "note": "Counts are the figures. The self-assessment is not completed."},
        {"provision": "8.2", "comply": None, "note": "Nothing is published and nothing is sent to a governing body."},
        {"provision": "9.4", "comply": None, "note": "Themes are suggestions. The senior lead assesses them."},
        {"provision": "9.7", "comply": None, "note": "Volume, categories, and outcomes are draft figures. Ombudsman orders are not tracked unless the batch supplies a material."},
    ]


def _tracker(clusters: list[dict]) -> list[dict]:
    rows = []
    for cluster in clusters:
        if cluster["count"] == 0:
            continue
        rows.append(
            {
                "tracker_id": f"T-{cluster['theme']}",
                "theme": cluster["theme"],
                "record_ids": list(cluster["record_ids"]),
                "question": "The complaints owner has not agreed an action for this cluster.",
                "status": "not_agreed",
                "agreed_by_agent": False,
            }
        )
    return rows


def _force_safe(draft: dict) -> None:
    draft["label"] = LABEL
    draft["not_a_regulatory_return"] = NOT_A_RETURN
    draft["document_status"] = "draft"
    draft["is_final_regulatory_return"] = False
    draft["submitted"] = False
    draft["published"] = False
    draft["sent"] = False
    draft["clusters_validated"] = False
    draft["narrative_validated"] = False
    draft["complying_with_consumer_duty"] = None
    draft["code_compliant"] = None
    draft["ofgem_return_complete"] = None
    draft["actions_taken"] = []
    draft["output_is_anonymised"] = False
    draft["agent_may_release"] = False
    draft["model_called"] = False
    draft["network_called"] = False
    draft["working_day_resolution_calculated"] = False
    draft["decisions_not_taken"] = list(DECISIONS_NOT_TAKEN)
    draft["prompt_injection"]["followed"] = False
    for cluster in draft["clusters"]:
        cluster["validated"] = False
        cluster["count"] = len(cluster["record_ids"])


def draft_checksum(draft: dict) -> str:
    copy = deepcopy(draft)
    copy.pop("checksum", None)
    copy.pop("external_attestation", None)
    payload = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def draft_report(batch: dict, *, as_of: date) -> dict:
    """Return one draft. Raises NotSynthetic without echoing the narratives."""

    if not isinstance(batch, dict):
        raise TypeError("batch must be an object")
    if batch.get("synthetic") is not True:
        raise NotSynthetic()
    records = batch.get("records")
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    for record in records:
        if isinstance(record, dict) and record.get("synthetic") is False:
            raise NotSynthetic()

    cleaned, removed_keys = _strip(batch)
    assert isinstance(cleaned, dict)
    records = cleaned["records"]
    sector = cleaned.get("sector")
    if sector not in SECTOR_REPORT:
        raise ValueError("sector must be financial_services, social_housing, or energy")
    requested = cleaned.get("report_type") or SECTOR_REPORT[sector]
    if requested not in SECTOR_REPORT.values():
        raise ValueError("report_type is not supported")
    report_blocked = requested != SECTOR_REPORT[sector]
    period_raw = cleaned.get("period")
    if not isinstance(period_raw, dict):
        raise ValueError("period must be an object")
    period_start = parse_date(period_raw.get("start"), field="period.start")
    period_end = parse_date(period_raw.get("end"), field="period.end")
    if period_end < period_start:
        raise ValueError("period end is before period start")
    batch_id = _token(cleaned.get("batch_id"), "batch_id")
    seen_ids: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each record must be an object")
        seen_ids.append(_token(record.get("record_id"), "record_id"))
    if len(seen_ids) != len(set(seen_ids)):
        raise ValueError("duplicate record_id")

    injection = scan_fields(_strings(cleaned))
    moment = _moment(as_of)
    prepared = [
        _prepare_record(record, sector=sector, period=(period_start, period_end), moment=moment)
        for record in records
    ]
    in_period = [row for row in prepared if row["in_period"]]
    outside = [row for row in prepared if not row["in_period"]]
    clusters = _clusters(in_period, sector=sector)
    in_ids = [row["record_id"] for row in in_period]
    membership = [record_id for cluster in clusters for record_id in cluster["record_ids"]]
    if sorted(membership) != sorted(in_ids) or len(membership) != len(set(membership)):
        raise RuntimeError("clusters do not partition the in-period records")

    figures: dict[str, dict] = {
        "in_period_total": count_figure("in_period_total", in_ids),
        "outside_period": count_figure("outside_period", [row["record_id"] for row in outside]),
    }
    for cluster in clusters:
        figures[cluster["figure_id"]] = count_figure(cluster["figure_id"], cluster["record_ids"])
    redress_pairs = [
        (row["record_id"], row["redress_pence"])
        for row in in_period
        if row["redress_pence"] is not None
    ]
    figures["redress_pence"] = sum_pence_figure("redress_pence", redress_pairs)
    figures["redress_records"] = count_figure("redress_records", [record_id for record_id, _pence in redress_pairs])
    figures["redress_missing"] = count_figure(
        "redress_missing",
        [row["record_id"] for row in in_period if row["redress_pence"] is None],
    )
    outcome_ids = []
    for outcome in (*OUTCOMES, "not_recorded", "not_in_closed_list"):
        figure_id = f"outcome_{outcome}"
        outcome_ids.append(figure_id)
        figures[figure_id] = count_figure(
            figure_id,
            [row["record_id"] for row in in_period if row["outcome"] == outcome],
        )
    figures["duplicate_text_records"] = count_figure("duplicate_text_records", _duplicate_ids(in_period))
    prior_state, prior_ids = _prior_state(cleaned.get("prior_period"))
    if prior_state == "reconciled":
        figures["prior_in_period_total"] = count_figure("prior_in_period_total", prior_ids)

    duty_ids: list[str] = []
    refusal_ids: list[str] = []
    channel_ids: list[str] = []
    accounts_supplied = False
    service_improvements: list[dict] = []
    ombudsman: list[dict] = []
    prompts: list[dict] = []

    if sector == "financial_services":
        flagged = [
            row["record_id"]
            for row in in_period
            if row.get("experiment_02", {}).get("vulnerability_drivers")
        ]
        figures["vulnerability_flags_for_review"] = count_figure("vulnerability_flags_for_review", flagged)
        duty_names = (
            "price_and_value",
            "consumer_support",
            "products_and_services",
            "consumer_understanding",
            "not_mapped",
        )
        for name in duty_names:
            figure_id = f"duty_{name}"
            duty_ids.append(figure_id)
            if name == "not_mapped":
                ids = [
                    row["record_id"]
                    for row in in_period
                    if row["theme"] == "needs_owner" or not row["experiment_02"]["duty_outcome_touched"]
                ]
            else:
                ids = [
                    row["record_id"]
                    for row in in_period
                    if row["theme"] != "needs_owner" and row["experiment_02"]["duty_outcome_touched"] == name
                ]
            figures[figure_id] = count_figure(figure_id, ids)
    elif sector == "social_housing":
        refused_ids = [row["record_id"] for row in in_period if row["refused"]]
        figures["refused_total"] = count_figure("refused_total", refused_ids)
        by_type: dict[str, list[str]] = defaultdict(list)
        for row in in_period:
            if row["refused"]:
                by_type[row["refusal_type"]].append(row["record_id"])
        for refusal_type in sorted(by_type):
            figure_id = f"refused_{refusal_type}"
            refusal_ids.append(figure_id)
            figures[figure_id] = count_figure(figure_id, by_type[refusal_type])
        by_id = {row["record_id"]: row for row in prepared}
        service_improvements = _service_improvements(records, by_id, moment)
        figures["service_improvements"] = count_figure(
            "service_improvements",
            [item["record_id"] for item in service_improvements],
        )
        ombudsman = _ombudsman(cleaned, moment)
        figures["ombudsman_materials"] = supplied_integer(
            "ombudsman_materials",
            len(ombudsman),
            "count of materials supplied on the batch",
        )
        if not report_blocked:
            prompts = _housing_prompts()
    else:
        empty = 0
        for category in ENERGY_CATEGORIES:
            figure = figures[f"cluster_{category}"]
            if figure["value"] == 0:
                empty += 1
        figures["empty_table_1_categories"] = supplied_integer(
            "empty_table_1_categories",
            empty,
            "count of B5 to B22 categories with no records",
        )
        for flag, figure_id in (
            ("yes", "resolved_d1_yes"),
            ("no", "resolved_d1_no"),
            ("not_recorded", "resolved_d1_not_recorded"),
        ):
            figures[figure_id] = count_figure(
                figure_id,
                [row["record_id"] for row in in_period if row["resolved_by_end_of_first_working_day"] == flag],
            )
        figures["repeat_true"] = count_figure(
            "repeat_true",
            [row["record_id"] for row in in_period if row["repeat_complaint"] == "yes"],
        )
        figures["repeat_not_recorded"] = count_figure(
            "repeat_not_recorded",
            [row["record_id"] for row in in_period if row["repeat_complaint"] == "not_recorded"],
        )
        groups = ("telephone", "letter", "electronic", "not_in_ofgem_channel_list", "not_recorded", "not_in_closed_list")
        for group in groups:
            figure_id = f"channel_{group}"
            channel_ids.append(figure_id)
            figures[figure_id] = count_figure(
                figure_id,
                [row["record_id"] for row in in_period if row["channel_group"] == group],
            )
        accounts = _accounts(cleaned)
        if accounts is not None:
            accounts_supplied = True
            electricity, gas = accounts
            figures["electricity_accounts"] = supplied_integer(
                "electricity_accounts", electricity, "supplied on the batch"
            )
            figures["gas_accounts"] = supplied_integer("gas_accounts", gas, "supplied on the batch")
            figures["account_total"] = supplied_integer(
                "account_total", electricity + gas, "sum of the two supplied account figures"
            )

    organisation = cleaned.get("organisation_name")
    if isinstance(organisation, str) and organisation.strip():
        organisation_out = neutralise(redact(organisation, now=moment)["text"]).strip()
    else:
        organisation_out = "not supplied"

    sources_stale = (as_of - SOURCES_PINNED_ON).days > STALE_AFTER_DAYS
    context = {
        "figures": figures,
        "clusters": clusters,
        "period_start": period_start,
        "period_end": period_end,
        "as_of": as_of,
        "prior_state": prior_state,
        "sources_stale": sources_stale,
        "report_blocked": report_blocked,
        "outcome_ids": outcome_ids,
        "duty_ids": duty_ids,
        "refusal_ids": refusal_ids,
        "channel_ids": channel_ids,
        "accounts_supplied": accounts_supplied,
    }
    narrative = common_sentences(context)
    if not report_blocked and sector == "financial_services":
        narrative.extend(consumer_duty_sentences(context))
    elif not report_blocked and sector == "social_housing":
        narrative.extend(housing_sentences(context))
    elif not report_blocked and sector == "energy":
        narrative.extend(energy_sentences(context))
    assert_sentences(narrative, figures, [as_of, period_start, period_end])

    public_records = []
    for row in prepared:
        copied = {key: value for key, value in row.items() if key != "normalised"}
        public_records.append(copied)

    draft = {
        "catalogue_id": CATALOGUE_ID,
        "agent_id": CALLER,
        "autonomy": "A0",
        "batch_id": batch_id,
        "organisation_name": organisation_out,
        "sector": sector,
        "report_type_requested": requested,
        "report_type_for_sector": SECTOR_REPORT[sector],
        "report_blocked": report_blocked,
        "as_of": as_of.isoformat(),
        "as_of_in_batch_ignored": "as_of" in removed_keys,
        "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
        "sources_pinned_on": SOURCES_PINNED_ON.isoformat(),
        "sources_stale": sources_stale,
        "stale_after_days": STALE_AFTER_DAYS,
        "stripped_keys": sorted(set(removed_keys)),
        "prompt_injection": injection,
        "records": public_records,
        "clusters": clusters,
        "figures": figures,
        "narrative": narrative,
        "action_tracker": _tracker(clusters),
        "service_improvements": service_improvements,
        "ombudsman_materials": ombudsman,
        "code_prompts": prompts,
        "citations": _citations(sector),
        "prior_period_state": prior_state,
        "category_arithmetic_complete": (
            figures["cluster_unassigned"]["value"] == 0 if sector == "energy" else None
        ),
        "reused": {
            "experiment_02": sector == "financial_services",
            "experiment_02_function": "analyse" if sector == "financial_services" else None,
            "experiment_08": True,
            "experiment_08_reversible": False,
            "experiment_08_model_suggestions": False,
        },
    }
    _force_safe(draft)
    draft["checksum"] = draft_checksum(draft)
    return draft


def record_external_attestation(draft: dict, *, role: str, checksum: str, caller: str) -> dict:
    """Record that a person outside the agent named a role. Effect is none.

    The skills say the agent must not call this. ``caller`` must be
    ``human_outside_agent``. The returned copy is still a draft.
    """

    if caller != "human_outside_agent":
        raise ReportForbidden("the agent must not record an attestation")
    if role != "Complaints owner":
        raise ReportForbidden("role is not the complaints owner named in the manifest")
    if checksum != draft_checksum(draft):
        raise ReportForbidden("checksum does not match the draft")
    copy = deepcopy(draft)
    copy["external_attestation"] = {
        "role": role,
        "effect": "none",
        "clusters_validated": False,
        "narrative_validated": False,
        "note": (
            "A person outside the agent supplied this role. This starter does "
            "not record the clusters or the narrative as validated, and it does "
            "not record a regulatory return."
        ),
    }
    _force_safe(copy)
    return copy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft complaints MI. Does not call a model.")
    parser.add_argument("--input", "-i", type=Path, required=True)
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args(argv)
    try:
        batch = json.loads(args.input.read_text(encoding="utf-8"))
        draft = draft_report(batch, as_of=args.as_of)
    except NotSynthetic as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    payload = json.dumps(draft, indent=2, ensure_ascii=True)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
