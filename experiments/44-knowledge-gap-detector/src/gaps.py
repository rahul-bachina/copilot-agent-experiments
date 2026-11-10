#!/usr/bin/env python3
"""Flag knowledge gaps in one synthetic review pack.

The same pack and the same as-of date produce the same JSON. Nothing is
published, nothing is edited, and a gap is not confirmed until a knowledge
manager records that confirmation on a separate object.

Customer and case text is not copied out. Experiment 08 counts identifiers.
Experiment 21 and Experiment 40 are consulted only as related catalogues.
Their article bodies are not copied.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from injection import PATTERNS, content_for_matching  # noqa: E402
    from knowledge import (  # noqa: E402
        ORGANISATION,
        OUTLINE_SECTIONS,
        article_matches,
        citation_block,
        conflicts_among,
        hint_topics,
        load_articles,
        screen_wording,
        title_for,
    )
    from sources import NOT_OPENED, PINNED_ON, SOURCE_WINDOW_DAYS, SOURCES  # noqa: E402
else:
    from .injection import PATTERNS, content_for_matching
    from .knowledge import (
        ORGANISATION,
        OUTLINE_SECTIONS,
        article_matches,
        citation_block,
        conflicts_among,
        hint_topics,
        load_articles,
        screen_wording,
        title_for,
    )
    from .sources import NOT_OPENED, PINNED_ON, SOURCE_WINDOW_DAYS, SOURCES

LABEL = "DRAFT FOR KNOWLEDGE MANAGER REVIEW"
CALLER = "exp-44-knowledge-gap-detector"
CATALOGUE_ID = "C005"
MAX_ITEMS = 20
MAX_TEXT = 4000

PACK_ID = re.compile(r"^SYN-PACK-\d{4}$")
QUERY_ID = re.compile(r"^SYN-QRY-\d{4}$")
NOTE_ID = re.compile(r"^SYN-NOTE-\d{4}$")
MISS_ID = re.compile(r"^SYN-MISS-\d{4}$")
MANAGER_ID = re.compile(r"^SYN-KM-\d{3}$")

SECTORS = frozenset(
    {
        "public_service",
        "financial_services",
        "it_service",
        "energy_retail",
        "telecoms",
    }
)
EXP40_SECTORS = frozenset(
    {"public_service", "financial_services", "energy_retail", "telecoms"}
)

PROHIBITED_KEYS = frozenset(
    {
        "human_approval",
        "executed",
        "actions_taken",
        "published",
        "articles_edited",
        "article_published",
        "article_edited",
        "article_deleted",
        "gap_confirmed",
        "knowledge_base_written",
        "message_sent",
    }
)

CONFIRM_DECISIONS = frozenset({"confirm_gap", "reject_gap", "defer"})
PROHIBITED_DECISIONS = frozenset(
    {
        "publish_article",
        "edit_article",
        "delete_article",
        "send_message",
        "confirm_as_published",
    }
)

_propose = None
_desk = None
_service = None


class GapForbidden(RuntimeError):
    """Raised when a caller asks the agent to publish, edit, delete, or send."""


def publish_article(*_args, **_kwargs) -> None:
    raise GapForbidden("the agent does not publish a knowledge article")


def edit_article(*_args, **_kwargs) -> None:
    raise GapForbidden("the agent does not edit a knowledge article")


def delete_article(*_args, **_kwargs) -> None:
    raise GapForbidden("the agent does not delete a knowledge article")


def send_message(*_args, **_kwargs) -> None:
    raise GapForbidden("the agent does not send a message")


def _load_module(path: Path, name: str):
    if not path.is_file():
        raise RuntimeError(f"Required file is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_propose():
    gateway_src = Path(__file__).resolve().parents[2] / "08-uk-pii-redaction-gateway" / "src"
    if not gateway_src.is_dir():
        raise RuntimeError(
            "Experiment 08 is required at experiments/08-uk-pii-redaction-gateway. "
            "This starter does not carry its own copy."
        )
    inserted = str(gateway_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    from gateway import propose

    return propose


def _gateway():
    global _propose
    if _propose is None:
        _propose = _load_propose()
    return _propose


def _desk_catalogue():
    global _desk
    if _desk is None:
        path = (
            Path(__file__).resolve().parents[2]
            / "21-it-service-desk"
            / "src"
            / "catalogue.py"
        )
        if not path.is_file():
            raise RuntimeError(
                "Experiment 21 is required at experiments/21-it-service-desk. "
                "This starter does not carry its own copy."
            )
        _desk = _load_module(path, "exp21_catalogue_for_exp44")
    return _desk


def _service_catalogue():
    global _service
    if _service is None:
        path = (
            Path(__file__).resolve().parents[2]
            / "40-customer-self-service"
            / "src"
            / "catalogue.py"
        )
        if not path.is_file():
            raise RuntimeError(
                "Experiment 40 is required at experiments/40-customer-self-service. "
                "This starter does not carry its own copy."
            )
        _service = _load_module(path, "exp40_catalogue_for_exp44")
    return _service


def _parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of must be YYYY-MM-DD") from exc


def _rules_current(as_of: date) -> bool:
    return (as_of - PINNED_ON).days <= SOURCE_WINDOW_DAYS


def _flags() -> dict:
    return {
        "article_published": False,
        "article_edited": False,
        "article_deleted": False,
        "message_sent": False,
        "knowledge_base_written": False,
        "consumer_duty_outcome_met": False,
        "equality_duty_met": False,
        "data_minimisation_met": False,
    }


def _human_route() -> dict:
    return {
        "offered": True,
        "approver": "Knowledge manager",
        "agent_publishes": False,
        "agent_edits": False,
        "sentence": (
            "A knowledge manager reviews this draft. "
            "This agent does not publish an article and does not edit one."
        ),
    }


def _regulatory(sector: str, rules_current: bool) -> dict:
    duty = sector == "financial_services"
    show = duty and rules_current
    return {
        "consumer_duty": {
            "applied": show,
            "withheld_because_sources_stale": duty and not rules_current,
            "provisions_read": ["PRIN 2A.5.3", "PRIN 2A.5.7", "PRIN 2A.5.10"] if show else [],
            "cross_references_seen": ["PRIN 2A.5.3R", "PRIN 2A.5.10R"] if show else [],
            "status_letter_on_2a_5_7": "not cleanly labelled in the PDF extraction",
            "outcome_met": False,
            "screen_is_the_test_in_2a_5_10": False,
        },
        "equality_act": {
            "section_read": "20(6)",
            "duty_met": False,
            "section_29_opened": False,
            "schedule_2_opened": False,
        },
        "uk_gdpr": {
            "article_read": "5(1)(c)",
            "data_minimisation_met": False,
            "source_text_copied": False,
            "article_6_opened": False,
        },
    }


def _source_rows(as_of: date) -> list[dict]:
    current = _rules_current(as_of)
    rows = []
    for source in SOURCES:
        rows.append(
            {
                "id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "opened_on": source["opened_on"],
                "outside_window": not current,
            }
        )
    return rows


def _base(pack_id: str, sector: str, as_of: str, rules_current: bool) -> dict:
    return {
        "label": LABEL,
        "catalogue_id": CATALOGUE_ID,
        "experiment": "44-knowledge-gap-detector",
        "agent_id": CALLER,
        "autonomy": "A0",
        "organisation": ORGANISATION,
        "pack_id": pack_id,
        "sector": sector,
        "as_of": as_of,
        "outcome": "review_ready",
        "human_approval": None,
        "actions_taken": [],
        "executed": False,
        "model_called": False,
        "network_called": False,
        "source_text_echoed": False,
        "published": False,
        "articles_edited": False,
        "gap_confirmed": False,
        "flags": _flags(),
        "human_route": _human_route(),
        "prompt_injection": {
            "detected": False,
            "signals": [],
            "followed": False,
            "hints_dropped": [],
        },
        "stale": {
            "rules_current": rules_current,
            "pinned_on": PINNED_ON.isoformat(),
            "window_days": SOURCE_WINDOW_DAYS,
            "boundary": "more than 180 days after the pin is outside; 180 days is inside",
        },
        "pii_gateway": {
            "called": False,
            "finding_count": 0,
            "entity_types": [],
            "items": [],
            "output_is_anonymised": False,
            "agent_may_release": False,
            "redacted_text_copied": False,
        },
        "related_catalogues": {
            "experiment_21": {"called": False, "current_ids": [], "stale_ids": []},
            "experiment_40": {"called": False, "current_ids": [], "stale_ids": []},
        },
        "items": [],
        "findings": [],
        "gaps": [],
        "outlines": [],
        "counts": {},
        "regulatory": _regulatory(sector, rules_current),
        "sources": _source_rows(_parse_as_of(as_of)) if _looks_like_date(as_of) else [],
        "not_opened": list(NOT_OPENED),
        "limitations_note": (
            "Keyword hints miss wording that is not on the list. "
            "The 25-word cap is not PRIN 2A.5.7 and not the test in PRIN 2A.5.10. "
            "Confirming a gap does not publish an article."
        ),
    }


def _looks_like_date(value: str) -> bool:
    try:
        _parse_as_of(value)
    except ValueError:
        return False
    return True


def _refusal(pack_id: str, sector: str, as_of: str, reason: str) -> dict:
    rules = False
    if _looks_like_date(as_of):
        rules = _rules_current(_parse_as_of(as_of))
    report = _base(pack_id, sector, as_of, rules)
    report["outcome"] = "refused"
    report["refusal_reason"] = reason
    report["counts"] = _counts([], [], [])
    _assert_safe(report)
    return report


def _counts(gaps: list[dict], findings: list[dict], outlines: list[dict]) -> dict:
    gap_topics = [gap["topic"] for gap in gaps]
    if len(gap_topics) != len(set(gap_topics)):
        raise RuntimeError("content gaps were counted more than once")
    evidence_rows = sum(len(gap["evidence_links"]) for gap in gaps)
    return {
        "content_gaps": len(gaps),
        "evidence_rows_on_gaps": evidence_rows,
        "findings": len(findings),
        "outlines": len(outlines),
        "content_gaps_equal_unique_topics": True,
    }


def _strip_pack(pack: dict) -> tuple[dict, list[str]]:
    clean = {}
    signals = []
    for key, value in pack.items():
        if key in PROHIBITED_KEYS:
            signals.append("prohibited_key")
            continue
        clean[key] = value
    return clean, signals


def _items_of(pack: dict) -> tuple[list[dict], str | None]:
    rows = []
    seen = set()
    specs = (
        ("queries", "query", "text", QUERY_ID),
        ("case_notes", "case_note", "text", NOTE_ID),
        ("search_misses", "search_miss", "query", MISS_ID),
    )
    for field, kind, text_key, pattern in specs:
        entries = pack.get(field) or []
        if not isinstance(entries, list):
            return [], "not_a_pack"
        for entry in entries:
            if not isinstance(entry, dict):
                return [], "not_a_pack"
            item_id = entry.get("id")
            if not isinstance(item_id, str) or not pattern.match(item_id):
                return [], "item_id"
            if item_id in seen:
                return [], "duplicate_id"
            seen.add(item_id)
            text = entry.get(text_key)
            if not isinstance(text, str):
                return [], "not_a_pack"
            if len(text) > MAX_TEXT:
                return [], "text_too_long"
            result_count = None
            if kind == "search_miss":
                result_count = entry.get("result_count")
                if not isinstance(result_count, int) or isinstance(result_count, bool) or result_count < 0:
                    return [], "miss_count"
            rows.append(
                {
                    "id": item_id,
                    "kind": kind,
                    "text": text,
                    "result_count": result_count,
                }
            )
    if len(rows) > MAX_ITEMS:
        return [], "too_many_items"
    return rows, None


def _redact(text: str) -> dict:
    proposal = _gateway()(text, caller=CALLER, reversible=False)
    findings = [
        finding
        for finding in proposal["audit_log"]["findings"]
        if finding.get("applied")
    ]
    types = sorted({finding["entity_type"] for finding in findings})
    return {
        "finding_count": len(findings),
        "entity_types": types,
        "input_sha256": proposal["audit_log"]["input_sha256"],
        "output_is_anonymised": proposal["anonymisation"]["output_is_anonymised"],
        "agent_may_release": proposal["release"]["agent_may_release"],
    }


def _related(text: str, sector: str, as_of: date) -> dict:
    result = {
        "experiment_21": {"called": False, "current_ids": [], "stale_ids": []},
        "experiment_40": {"called": False, "current_ids": [], "stale_ids": []},
    }
    if not text:
        return result
    if sector == "it_service":
        catalogue = _desk_catalogue()
        result["experiment_21"]["called"] = True
        for article in catalogue.match_articles(text):
            bucket = "stale_ids" if catalogue.is_stale(article["last_reviewed"], as_of) else "current_ids"
            result["experiment_21"][bucket].append(article["id"])
    elif sector in EXP40_SECTORS:
        catalogue = _service_catalogue()
        result["experiment_40"]["called"] = True
        for article in catalogue.match_articles(text, sector):
            bucket = "stale_ids" if catalogue.is_stale(article["last_reviewed"], as_of) else "current_ids"
            result["experiment_40"][bucket].append(article["id"])
    for side in result.values():
        side["current_ids"] = sorted(set(side["current_ids"]))
        side["stale_ids"] = sorted(set(side["stale_ids"]))
    return result


def _merge_related(into: dict, item: dict) -> None:
    for name in ("experiment_21", "experiment_40"):
        side = item[name]
        dest = into[name]
        if side["called"]:
            dest["called"] = True
        dest["current_ids"] = sorted(set(dest["current_ids"]) | set(side["current_ids"]))
        dest["stale_ids"] = sorted(set(dest["stale_ids"]) | set(side["stale_ids"]))


def _classify_item(item: dict, cleaned: str, articles: list[dict], sector: str, as_of: date, is_stale) -> dict:
    if not cleaned:
        return {
            "outcomes": ["instruction_only"],
            "topics": [],
            "pairs": [],
            "citable_ids": [],
            "not_citable": [],
        }
    hay = cleaned.lower()
    citable = []
    not_citable = []
    for article in articles:
        if not article_matches(article, hay, sector):
            continue
        ok, reason = citation_block(article, as_of, is_stale)
        if ok:
            citable.append(article)
        else:
            not_citable.append({"id": article["id"], "topic": article["topic"], "reason": reason})
    conflict_topics = {row["topic"] for row in conflicts_among(citable)}
    pairs: list[tuple[str, str]] = []
    seen_topics = set()
    by_topic: dict[str, list[dict]] = {}
    for article in citable:
        by_topic.setdefault(article["topic"], []).append(article)
    for topic in sorted(by_topic):
        seen_topics.add(topic)
        outcome = "conflict" if topic in conflict_topics else "covered"
        pairs.append((outcome, topic))
    for row in not_citable:
        if row["topic"] in seen_topics:
            continue
        seen_topics.add(row["topic"])
        pairs.append(("stale_coverage", row["topic"]))
    for topic in hint_topics(cleaned):
        if topic in seen_topics:
            continue
        seen_topics.add(topic)
        pairs.append(("content_gap", topic))
    if not pairs:
        pairs.append(("content_gap", f"unmatched-{item['id']}"))
    if item["kind"] == "search_miss" and item["result_count"] == 0:
        pairs = [
            ("retrieval_miss", topic) if outcome == "covered" else (outcome, topic)
            for outcome, topic in pairs
        ]
    return {
        "outcomes": sorted({outcome for outcome, _topic in pairs}),
        "topics": [topic for _outcome, topic in pairs],
        "pairs": pairs,
        "citable_ids": sorted(article["id"] for article in citable),
        "not_citable": sorted(not_citable, key=lambda row: row["id"]),
    }


def _evidence(kind: str, item_id: str) -> dict:
    return {"kind": kind, "id": item_id}


def _scan_articles(articles: list[dict], sector: str, as_of: date, is_stale) -> dict:
    in_sector = [article for article in articles if article["sector"] in {sector, "any"}]
    citable = []
    blocked = []
    for article in in_sector:
        ok, reason = citation_block(article, as_of, is_stale)
        if ok:
            citable.append(article)
        else:
            blocked.append({"id": article["id"], "topic": article["topic"], "title": article["title"], "reason": reason})
    wording = []
    access = []
    for article in citable:
        screen = screen_wording(article["body"])
        if not screen["passed"]:
            wording.append(
                {
                    "id": article["id"],
                    "topic": article["topic"],
                    "title": article["title"],
                    "long_sentence_word_counts": screen["long_sentence_word_counts"],
                    "jargon": screen["jargon"],
                    "is_the_prin_test": False,
                }
            )
        if not screen["accessible_format_mentioned"]:
            access.append(
                {
                    "id": article["id"],
                    "topic": article["topic"],
                    "title": article["title"],
                    "duty_met": False,
                }
            )
    blocked.sort(key=lambda row: row["id"])
    wording.sort(key=lambda row: row["id"])
    access.sort(key=lambda row: row["id"])
    return {
        "citable": citable,
        "blocked": blocked,
        "conflicts": conflicts_among(citable),
        "plain_english": wording,
        "accessibility": access,
    }


def _outline(kind: str, topic: str, article_id: str | None, evidence: list[dict]) -> dict:
    return {
        "kind": kind,
        "topic": topic,
        "article_id": article_id,
        "proposed_title": title_for(topic),
        "sections": list(OUTLINE_SECTIONS),
        "evidence_links": evidence,
        "published": False,
        "edited": False,
    }


def _assert_safe(report: dict) -> None:
    if report["published"] or report["articles_edited"] or report["executed"]:
        raise GapForbidden("a draft recorded a prohibited effect")
    if report["actions_taken"]:
        raise GapForbidden("a draft recorded an action")
    flags = report["flags"]
    for key in (
        "article_published",
        "article_edited",
        "article_deleted",
        "message_sent",
        "knowledge_base_written",
    ):
        if flags[key]:
            raise GapForbidden("a draft recorded a prohibited flag")
    if report["flags"]["consumer_duty_outcome_met"] or report["flags"]["equality_duty_met"]:
        raise GapForbidden("a draft recorded a duty as met")
    if report["flags"]["data_minimisation_met"]:
        raise GapForbidden("a draft recorded data minimisation as met")
    for outline in report["outlines"]:
        if outline["published"] or outline["edited"]:
            raise GapForbidden("an outline was marked published")


def detect_gaps(pack: dict, as_of: str, library: list[dict] | None = None) -> dict:
    if not isinstance(pack, dict):
        return _refusal("", "", as_of, "not_a_pack")
    clean, prohibited = _strip_pack(pack)
    as_of_text = as_of if isinstance(as_of, str) else ""
    try:
        as_of_date = _parse_as_of(as_of_text)
    except ValueError:
        return _refusal(str(clean.get("pack_id") or ""), str(clean.get("sector") or ""), as_of_text, "as_of")
    pack_id = clean.get("pack_id") if isinstance(clean.get("pack_id"), str) else ""
    sector = clean.get("sector") if isinstance(clean.get("sector"), str) else ""
    rules_current = _rules_current(as_of_date)
    if clean.get("synthetic") is not True:
        return _refusal(pack_id, sector, as_of_text, "not_synthetic")
    if not PACK_ID.match(pack_id):
        return _refusal(pack_id, sector, as_of_text, "pack_id")
    if sector not in SECTORS:
        return _refusal(pack_id, sector, as_of_text, "sector")
    rows, problem = _items_of(clean)
    if problem:
        return _refusal(pack_id, sector, as_of_text, problem)

    try:
        articles = load_articles(library)
    except ValueError:
        return _refusal(pack_id, sector, as_of_text, "library")

    is_stale = _desk_catalogue().is_stale
    report = _base(pack_id, sector, as_of_text, rules_current)
    if prohibited:
        report["prompt_injection"]["detected"] = True
        report["prompt_injection"]["signals"] = ["prohibited_key"]

    scan = _scan_articles(articles, sector, as_of_date, is_stale)
    signals: list[str] = list(report["prompt_injection"]["signals"])
    hints_dropped: list[str] = []
    entity_types: set[str] = set()
    finding_count = 0
    gateway_items = []
    gap_evidence: dict[str, list[dict]] = {}
    gap_related: dict[str, dict[str, list[str]]] = {}
    retrieval_evidence: dict[str, list[dict]] = {}
    stale_evidence: dict[str, list[dict]] = {}

    for row in rows:
        original = row["text"]
        item_signals, cleaned = content_for_matching(original)
        dropped = [topic for topic in hint_topics(original) if topic not in hint_topics(cleaned)]
        hints_dropped.extend(dropped)
        signals.extend(item_signals)
        gateway = _redact(original)
        finding_count += gateway["finding_count"]
        entity_types.update(gateway["entity_types"])
        gateway_items.append(
            {
                "id": row["id"],
                "finding_count": gateway["finding_count"],
                "entity_types": gateway["entity_types"],
                "input_sha256": gateway["input_sha256"],
            }
        )
        if gateway["output_is_anonymised"] or gateway["agent_may_release"]:
            raise GapForbidden("Experiment 08 returned an unexpected release flag")
        related = _related(cleaned, sector, as_of_date)
        _merge_related(report["related_catalogues"], related)
        classified = _classify_item(row, cleaned, articles, sector, as_of_date, is_stale)
        link = _evidence(row["kind"], row["id"])
        for outcome, topic in classified["pairs"]:
            if outcome == "content_gap":
                gap_evidence.setdefault(topic, []).append(link)
                gap_related.setdefault(topic, {"current_ids": [], "stale_ids": []})
                for side in ("experiment_21", "experiment_40"):
                    gap_related[topic]["current_ids"].extend(related[side]["current_ids"])
                    gap_related[topic]["stale_ids"].extend(related[side]["stale_ids"])
            elif outcome == "retrieval_miss":
                retrieval_evidence.setdefault(topic, []).append(link)
            elif outcome == "stale_coverage":
                stale_evidence.setdefault(topic, []).append(link)
        report["items"].append(
            {
                "id": row["id"],
                "kind": row["kind"],
                "outcomes": classified["outcomes"],
                "topics": classified["topics"],
                "citable_ids": classified["citable_ids"],
                "not_citable": classified["not_citable"],
                "injection_signals": item_signals,
                "legitimate_content_kept": not dropped,
                "related_current_ids": sorted(
                    set(related["experiment_21"]["current_ids"]) | set(related["experiment_40"]["current_ids"])
                ),
                "related_stale_ids": sorted(
                    set(related["experiment_21"]["stale_ids"]) | set(related["experiment_40"]["stale_ids"])
                ),
            }
        )

    ordered_signals = []
    for name, _pattern in PATTERNS:
        if name in signals and name not in ordered_signals:
            ordered_signals.append(name)
    if "prohibited_key" in signals:
        ordered_signals.append("prohibited_key")
    report["prompt_injection"]["signals"] = ordered_signals
    report["prompt_injection"]["detected"] = bool(ordered_signals)
    report["prompt_injection"]["followed"] = False
    report["prompt_injection"]["hints_dropped"] = sorted(set(hints_dropped))

    report["pii_gateway"] = {
        "called": True,
        "finding_count": finding_count,
        "entity_types": sorted(entity_types),
        "items": gateway_items,
        "output_is_anonymised": False,
        "agent_may_release": False,
        "redacted_text_copied": False,
    }

    findings = []
    gaps = []
    for topic in sorted(gap_evidence):
        related_ids = gap_related[topic]
        gap = {
            "gap_id": "GAP-" + topic.upper(),
            "topic": topic,
            "evidence_links": _unique_links(gap_evidence[topic]),
            "related_current_ids": sorted(set(related_ids["current_ids"])),
            "related_stale_ids": sorted(set(related_ids["stale_ids"])),
            "confirmed": False,
            "published": False,
        }
        gaps.append(gap)
        findings.append(
            {
                "kind": "content_gap",
                "topic": topic,
                "article_ids": [],
                "evidence_links": gap["evidence_links"],
                "detail": "No current approved article matched this topic.",
            }
        )
    for topic in sorted(retrieval_evidence):
        findings.append(
            {
                "kind": "retrieval_miss",
                "topic": topic,
                "article_ids": _article_ids_for_topic(scan["citable"], topic),
                "evidence_links": _unique_links(retrieval_evidence[topic]),
                "detail": "A current article exists. The search log recorded zero results.",
            }
        )
    for conflict in scan["conflicts"]:
        findings.append(
            {
                "kind": "conflict",
                "topic": conflict["topic"],
                "article_ids": conflict["article_ids"],
                "claim": conflict["claim"],
                "evidence_links": [{"kind": "article", "id": article_id} for article_id in conflict["article_ids"]],
                "winner_chosen": False,
                "detail": "Two current articles take opposite positions. This starter does not choose one.",
            }
        )
    for blocked in scan["blocked"]:
        extra = stale_evidence.get(blocked["topic"], [])
        links = [{"kind": "article", "id": blocked["id"]}] + extra
        findings.append(
            {
                "kind": blocked["reason"] if blocked["reason"] in {"withdrawn", "draft", "not_yet_in_force"} else "stale_article",
                "topic": blocked["topic"],
                "article_ids": [blocked["id"]],
                "reason": blocked["reason"],
                "evidence_links": _unique_links(links),
                "detail": "The article is not treated as current coverage. Its body is not copied.",
            }
        )
    for row in scan["plain_english"]:
        findings.append(
            {
                "kind": "plain_english",
                "topic": row["topic"],
                "article_ids": [row["id"]],
                "evidence_links": [{"kind": "article", "id": row["id"]}],
                "long_sentence_word_counts": row["long_sentence_word_counts"],
                "jargon": row["jargon"],
                "is_the_prin_test": False,
                "detail": "A current article failed the starter screen. The screen is not PRIN 2A.5.10.",
            }
        )
    for row in scan["accessibility"]:
        findings.append(
            {
                "kind": "accessibility",
                "topic": row["topic"],
                "article_ids": [row["id"]],
                "evidence_links": [{"kind": "article", "id": row["id"]}],
                "duty_met": False,
                "detail": "The article does not mention another format. Section 20(6) was read. The duty is not treated as met.",
            }
        )

    outlines = []
    for gap in gaps:
        outlines.append(_outline("new_article", gap["topic"], None, gap["evidence_links"]))
    for blocked in scan["blocked"]:
        kind = {
            "withdrawn": "withdrawn_article",
            "draft": "draft_article",
            "not_yet_in_force": "not_yet_in_force",
        }.get(blocked["reason"], "refresh_article")
        links = [{"kind": "article", "id": blocked["id"]}] + stale_evidence.get(blocked["topic"], [])
        outlines.append(_outline(kind, blocked["topic"], blocked["id"], _unique_links(links)))
    for row in scan["plain_english"]:
        outlines.append(
            _outline(
                "revise_wording",
                row["topic"],
                row["id"],
                [{"kind": "article", "id": row["id"]}],
            )
        )
    for row in scan["accessibility"]:
        if any(outline["article_id"] == row["id"] and outline["kind"] == "revise_wording" for outline in outlines):
            continue
        outlines.append(
            _outline(
                "revise_wording",
                row["topic"],
                row["id"],
                [{"kind": "article", "id": row["id"]}],
            )
        )

    outlines.sort(key=lambda outline: (outline["kind"], outline["topic"], outline["article_id"] or ""))
    for index, outline in enumerate(outlines, start=1):
        outline["outline_id"] = f"OUT-{index:03d}"
    findings.sort(key=lambda finding: (finding["kind"], finding["topic"], ",".join(finding["article_ids"])))
    for index, finding in enumerate(findings, start=1):
        finding["finding_id"] = f"F-{index:03d}"

    report["findings"] = findings
    report["gaps"] = gaps
    report["outlines"] = outlines
    report["counts"] = _counts(gaps, findings, outlines)
    if not rules_current:
        report["outcome"] = "stale_sources"
        report["outlines"] = []
        report["counts"] = _counts(gaps, findings, [])
        for outline_gap in report["gaps"]:
            outline_gap["published"] = False
    _assert_safe(report)
    return report


def _article_ids_for_topic(citable: list[dict], topic: str) -> list[str]:
    return sorted(article["id"] for article in citable if article["topic"] == topic)


def _unique_links(links: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for link in links:
        key = (link["kind"], link["id"])
        if key in seen:
            continue
        seen.add(key)
        unique.append({"kind": link["kind"], "id": link["id"]})
    unique.sort(key=lambda link: (link["kind"], link["id"]))
    return unique


def _review_refused(report: dict, decision: str, reason: str) -> dict:
    updated = deepcopy(report)
    updated["review"] = {
        "decision": decision,
        "accepted": False,
        "refused": True,
        "reason": reason,
        "executed": False,
        "published": False,
        "articles_edited": False,
    }
    updated["human_approval"] = None
    updated["gap_confirmed"] = False
    updated["published"] = False
    updated["articles_edited"] = False
    updated["executed"] = False
    _assert_safe(updated)
    return updated


def record_confirmation(report: dict, review: dict) -> dict:
    if not isinstance(report, dict) or not isinstance(review, dict):
        raise ValueError("report and review must be objects")
    decision = review.get("decision")
    if decision not in CONFIRM_DECISIONS:
        return _review_refused(report, str(decision), "prohibited_decision")
    if review.get("actor") != "knowledge_manager" or not isinstance(review.get("actor_id"), str):
        return _review_refused(report, str(decision), "actor")
    if not MANAGER_ID.match(review["actor_id"]):
        return _review_refused(report, str(decision), "actor")
    if report.get("outcome") == "refused":
        return _review_refused(report, str(decision), "report_refused")
    known = {gap["gap_id"] for gap in report.get("gaps") or []}
    requested = review.get("gap_ids")
    if decision == "confirm_gap":
        if not isinstance(requested, list) or not requested:
            return _review_refused(report, decision, "gap_ids")
        if any(not isinstance(gap_id, str) or gap_id not in known for gap_id in requested):
            return _review_refused(report, decision, "unknown_gap")
        if not report.get("stale", {}).get("rules_current", False):
            return _review_refused(report, decision, "stale_sources")
        if report.get("prompt_injection", {}).get("hints_dropped"):
            return _review_refused(report, decision, "content_dropped")
        updated = deepcopy(report)
        chosen = set(requested)
        for gap in updated["gaps"]:
            gap["confirmed"] = gap["gap_id"] in chosen
            gap["published"] = False
        updated["gap_confirmed"] = True
        updated["human_approval"] = {
            "approver": "Knowledge manager",
            "actor_id": review["actor_id"],
            "decision": "confirm_gap",
            "gap_ids": sorted(chosen),
            "executed": False,
            "published": False,
            "articles_edited": False,
        }
        updated["review"] = {
            "decision": "confirm_gap",
            "accepted": True,
            "refused": False,
            "reason": "recorded",
            "executed": False,
            "published": False,
            "articles_edited": False,
        }
        updated["published"] = False
        updated["articles_edited"] = False
        updated["executed"] = False
        updated["actions_taken"] = []
        _assert_safe(updated)
        return updated

    if requested is not None:
        if not isinstance(requested, list) or any(not isinstance(gap_id, str) or gap_id not in known for gap_id in requested):
            return _review_refused(report, str(decision), "unknown_gap")
    updated = deepcopy(report)
    updated["review"] = {
        "decision": decision,
        "accepted": True,
        "refused": False,
        "reason": "recorded_without_confirmation",
        "executed": False,
        "published": False,
        "articles_edited": False,
    }
    updated["human_approval"] = None
    updated["gap_confirmed"] = False
    updated["published"] = False
    _assert_safe(updated)
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft a knowledge-gap review. Does not publish.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2
    if not isinstance(pack, dict):
        return 2
    try:
        report = detect_gaps(pack, args.as_of)
    except ValueError:
        return 2
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
