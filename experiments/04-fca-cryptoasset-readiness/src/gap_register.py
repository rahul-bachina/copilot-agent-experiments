"""Build a draft observation register from one policy pack.

Deterministic. No model. No network. The same pack and the same as-of date
always produce the same JSON. Readiness fields stay null.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    from .checklist import REQUIREMENTS
    from .currency import assess_catalogue, assess_document_date, parse_iso
    from .dates import date_observations
    from .injection import scan_document
    from .sources import (
        DEFAULT_DOCUMENT_STALE_AFTER_DAYS,
        DEFAULT_STALE_AFTER_DAYS,
        KEY_DATES,
        LAST_VERIFIED,
        SOURCES,
    )
except ImportError:  # python src/gap_register.py puts src/ on the path, not the package
    from checklist import REQUIREMENTS
    from currency import assess_catalogue, assess_document_date, parse_iso
    from dates import date_observations
    from injection import scan_document
    from sources import (
        DEFAULT_DOCUMENT_STALE_AFTER_DAYS,
        DEFAULT_STALE_AFTER_DAYS,
        KEY_DATES,
        LAST_VERIFIED,
        SOURCES,
    )

DISCLAIMER = (
    "DRAFT FOR HUMAN REVIEW. This output is not regulatory advice and it is not "
    "legal advice. It is not a conclusion on readiness for FCA authorisation or "
    "MLR registration. The Compliance Officer or the MLRO owns every gap "
    "conclusion. Each row records only whether expected wording was found in the "
    "text supplied. Consultation-stage and planned items are marked and are not "
    "scored as rules."
)

DECISIONS_NOT_TAKEN = [
    "Make a readiness finding on authorisation or registration",
    "Give regulatory advice",
    "Give legal advice",
    "Accept or reject a gap",
    "Submit or vary an application, or use Connect",
    "File a suspicious activity report",
    "Approve a financial promotion",
    "Treat a consultation or a plan to consult as a final rule",
    "Write a production record or send a message",
]

FORBIDDEN_CONCLUSION_PHRASES = (
    "the firm is ready",
    "the firm is not ready",
    "the firm is compliant",
    "the firm is non-compliant",
    "the firm isn't ready",
    "authorisation should be granted",
    "authorization should be granted",
    "application should be refused",
    "this firm is ready",
)

LABEL = "DRAFT FOR HUMAN REVIEW"

_CLASSIFIERS: dict[str, list[str]] = {
    "bwra": ["business-wide risk assessment", "bwra"],
    "cra": ["customer risk assessment"],
    "cdd_onboarding": ["customer due diligence", "onboarding"],
    "transaction_monitoring": ["transaction monitoring", "on-chain", "off-chain"],
    "travel_rule": ["travel rule"],
    "governance_smcr": ["sm&cr", "smcr", "nominated officer", "mlro"],
    "consumer_duty": ["consumer duty"],
    "financial_promotions": ["financial promotion"],
    "operational_resilience": ["operational resilience", "business continuity"],
    "safeguarding_custody": ["safeguarding", "private key", "custody"],
}

_STAGE_LABELS = {
    "in_force_expectation": (
        "Described on an FCA page opened on 24 October 2026 as material the FCA "
        "looks for now, or as a regime already in force on that page. Not a finding "
        "that a duty applies to this firm, and not a finding of breach."
    ),
    "final_not_yet_in_force": (
        "Named as final rules or finalised guidance in the June 2026 policy "
        "statements, or in PS26/18. The pinned pages put commencement on "
        "25 October 2027. The landing page says the regime is expected to come "
        "into force on that date. Not scored as a current MLR expectation. "
        "PDFs and Handbook sections named here were not opened unless the source row says otherwise."
    ),
    "consultation": (
        "The pinned FCA page calls this a consultation or a guidance consultation. "
        "It is not scored. Policy text cannot change this stage."
    ),
    "planned_consultation": (
        "The pinned FCA page says the FCA plans to consult. This starter did not "
        "verify that the consultation has since opened. It is not scored. "
        "Policy text cannot change this stage."
    ),
}


def classify_document(title: str, body: str) -> str:
    """Pick a document type from the title and the start of the body.

    Title matches count more than body matches. A tie, or no match, is unclassified.
    """
    title_l = title.lower()
    body_l = body.lower()[:800]
    scores: dict[str, int] = {}
    for doc_type, words in _CLASSIFIERS.items():
        score = 0
        for word in words:
            if word in title_l:
                score += 3
            if word in body_l:
                score += 1
        scores[doc_type] = score
    best = max(scores.values())
    if best <= 0:
        return "unclassified"
    winners = [name for name, score in scores.items() if score == best]
    if len(winners) != 1:
        return "unclassified"
    return winners[0]


def _phrase_in(haystack: str, phrase: str) -> bool:
    """Substring match. Tokens of four letters or fewer use word boundaries.

    That stops 'mlr' matching inside 'mlro'. Longer phrases and phrases with
    spaces or punctuation stay as substrings, so a stem such as 'verif' still
    matches 'verify'.
    """
    needle = phrase.lower()
    if re.fullmatch(r"[a-z0-9]+", needle) and len(needle) <= 4:
        return re.search(rf"\b{re.escape(needle)}\b", haystack) is not None
    return needle in haystack


def _groups_found(text: str, groups: list[list[str]]) -> tuple[bool, list[str], list[str]]:
    lowered = text.lower()
    matched: list[str] = []
    missing: list[str] = []
    for group in groups:
        hit = next((phrase for phrase in group if _phrase_in(lowered, phrase)), None)
        if hit:
            matched.append(hit)
        else:
            missing.append(group[0])
    return not missing, matched, missing


def _excerpt(text: str, phrase: str) -> str | None:
    if not phrase:
        return None
    lowered = text.lower()
    index = lowered.find(phrase.lower())
    if index < 0:
        return None
    start = max(0, index - 40)
    end = min(len(text), index + len(phrase) + 80)
    snippet = text[start:end].replace("\n", " ").strip()
    return snippet[:180]


def _prepare_documents(documents: list[dict]) -> list[dict]:
    prepared = []
    for index, document in enumerate(documents):
        text = document.get("text") or ""
        scan = scan_document(text)
        declared = document.get("doc_type")
        if declared:
            doc_type = declared
            doc_type_source = "declared"
        else:
            doc_type = classify_document(document.get("title") or "", scan["usable_text"] or text)
            doc_type_source = "classified"
        prepared.append(
            {
                "id": document.get("id") or f"document-{index + 1}",
                "title": document.get("title") or document.get("id") or f"Document {index + 1}",
                "doc_type": doc_type,
                "doc_type_source": doc_type_source,
                "document_date": document.get("document_date"),
                "character_count": len(text),
                "scan": scan,
                "usable_text": scan["usable_text"],
            }
        )
    return prepared


def _usable_blob(documents: list[dict], doc_types: list[str] | None = None) -> str:
    chosen = documents
    if doc_types is not None:
        chosen = [item for item in documents if item["doc_type"] in doc_types]
    return "\n".join(item["usable_text"] for item in chosen)


def _applicable(requirement: dict, documents: list[dict]) -> bool:
    rule = requirement.get("applicability")
    if not rule:
        return True
    if rule["search"] == "pack":
        haystack = _usable_blob(documents).lower()
    else:
        haystack = _usable_blob(documents, requirement["doc_types"]).lower()
    return any(_phrase_in(haystack, term) for term in rule["any_of"])


def _mentioned(requirement: dict, documents: list[dict]) -> bool:
    haystack = _usable_blob(documents).lower()
    return any(_phrase_in(haystack, alias) for alias in requirement.get("mention_aliases", []))


def _source_refs(source_ids: list[str], currency_by_id: dict[str, dict]) -> list[dict]:
    refs = []
    for source_id in source_ids:
        row = currency_by_id[source_id]
        refs.append(
            {
                "source_id": source_id,
                "title": row["title"],
                "url": row["url"],
                "last_verified": row["last_verified"],
                "currency": row["currency"],
            }
        )
    return refs


def _observation_shell(requirement: dict, currency_by_id: dict[str, dict]) -> dict:
    refs = _source_refs(requirement["source_ids"], currency_by_id)
    return {
        "requirement_id": requirement["id"],
        "control_area": requirement["control_area"],
        "title": requirement["title"],
        "rule_stage": requirement["rule_stage"],
        "rule_stage_label": _STAGE_LABELS[requirement["rule_stage"]],
        "page_says": requirement["page_says"],
        "handbook_names": list(requirement["handbook_names"]),
        "sources": refs,
        "do_not_rely_until_sources_reverified": any(item["currency"] == "stale" for item in refs),
        "accepted_as_gap": False,
        "for_human_review": True,
        "pack_cannot_change_rule_stage": True,
    }


def _score_requirement(requirement: dict, documents: list[dict], currency_by_id: dict[str, dict]) -> dict:
    row = _observation_shell(requirement, currency_by_id)
    stage = requirement["rule_stage"]

    if stage in {"consultation", "planned_consultation"}:
        row["text_observation"] = "not_scored_consultation_or_planned"
        row["mentioned_in_pack"] = _mentioned(requirement, documents)
        row["scored_as_current_expectation"] = False
        row["preparation_item"] = False
        return row

    if not _applicable(requirement, documents):
        row["text_observation"] = "not_indicated_in_the_text"
        row["scored_as_current_expectation"] = False
        row["preparation_item"] = False
        row["matched_phrases"] = []
        row["missing_phrase_groups"] = []
        return row

    scope = requirement.get("search_scope")
    if scope == "pack":
        relevant = [item for item in documents if not item["scan"]["quarantine_document"]]
        typed = documents
    else:
        typed = [item for item in documents if item["doc_type"] in requirement["doc_types"]]
        relevant = [item for item in typed if not item["scan"]["quarantine_document"]]

    quarantined = [item for item in typed if item["scan"]["quarantine_document"]]

    if scope != "pack" and not typed:
        row["text_observation"] = "document_not_supplied"
        row["matched_phrases"] = []
        row["missing_phrase_groups"] = [group[0] for group in requirement["signal_groups"]]
    elif quarantined and not relevant:
        row["text_observation"] = "document_quarantined_prompt_injection"
        row["matched_phrases"] = []
        row["missing_phrase_groups"] = [group[0] for group in requirement["signal_groups"]]
    else:
        combined = "\n".join(item["usable_text"] for item in relevant)
        found, matched, missing = _groups_found(combined, requirement["signal_groups"])
        row["text_observation"] = "signal_present" if found else "signal_not_found"
        row["matched_phrases"] = matched
        row["missing_phrase_groups"] = missing
        if matched:
            row["evidence_excerpt"] = _excerpt(combined, matched[0])

    if quarantined and relevant:
        row["quarantined_document_ids"] = [item["id"] for item in quarantined]

    row["scored_as_current_expectation"] = stage == "in_force_expectation"
    row["preparation_item"] = stage == "final_not_yet_in_force"
    return row


def _counts(observations: list[dict]) -> dict:
    def tally(status: str) -> int:
        return sum(1 for row in observations if row["text_observation"] == status)

    missing = {"signal_not_found", "document_not_supplied"}
    return {
        "rows": len(observations),
        "signal_present": tally("signal_present"),
        "signal_not_found": tally("signal_not_found"),
        "document_not_supplied": tally("document_not_supplied"),
        "document_quarantined_prompt_injection": tally("document_quarantined_prompt_injection"),
        "not_indicated_in_the_text": tally("not_indicated_in_the_text"),
        "not_scored_consultation_or_planned": tally("not_scored_consultation_or_planned"),
        "current_expectation_phrase_missing": sum(
            1
            for row in observations
            if row["scored_as_current_expectation"] and row["text_observation"] in missing
        ),
        "preparation_phrase_missing": sum(
            1
            for row in observations
            if row["preparation_item"] and row["text_observation"] in missing
        ),
    }


def _reject_conclusions(payload: dict) -> None:
    blob = json.dumps(payload, ensure_ascii=True).lower()
    found = [phrase for phrase in FORBIDDEN_CONCLUSION_PHRASES if phrase in blob]
    if found:
        joined = ", ".join(found)
        raise RuntimeError(f"Draft contained a forbidden conclusion phrase: {joined}")


def build_register(
    pack: dict,
    *,
    as_of: date | None = None,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
    document_stale_after_days: int = DEFAULT_DOCUMENT_STALE_AFTER_DAYS,
) -> dict:
    """Return the draft register for one pack."""
    as_of = as_of or date.fromisoformat(LAST_VERIFIED)
    documents = _prepare_documents(pack.get("documents") or [])
    currency_rows = assess_catalogue(SOURCES, as_of, stale_after_days)
    currency_by_id = {row["source_id"]: row for row in currency_rows}
    observations = [_score_requirement(item, documents, currency_by_id) for item in REQUIREMENTS]
    counts = _counts(observations)

    injection_documents = []
    for document in documents:
        scan = document["scan"]
        if not scan["detected"]:
            continue
        injection_documents.append(
            {
                "document_id": document["id"],
                "quarantined": scan["quarantine_document"],
                "findings": scan["findings"],
            }
        )

    document_rows = []
    for document in documents:
        document_rows.append(
            {
                "id": document["id"],
                "title": document["title"],
                "doc_type": document["doc_type"],
                "doc_type_source": document["doc_type_source"],
                "character_count": document["character_count"],
                "document_currency": assess_document_date(
                    document["document_date"],
                    as_of,
                    document_stale_after_days,
                ),
                "prompt_injection_detected": document["scan"]["detected"],
                "quarantined": document["scan"]["quarantine_document"],
            }
        )

    payload = {
        "label": LABEL,
        "catalogue_id": "UK02",
        "experiment": "04-fca-cryptoasset-readiness",
        "autonomy": "A0",
        "processing_mode": "deterministic",
        "evaluation_label": None,
        "model_called": False,
        "network_called": False,
        "disclaimer": DISCLAIMER,
        "owner_of_gap_conclusions": "Compliance Officer / MLRO",
        "readiness_conclusion": None,
        "firm_ready": None,
        "firm_not_ready": None,
        "regulatory_advice": None,
        "legal_advice": None,
        "actions_taken": [],
        "decisions_not_taken": list(DECISIONS_NOT_TAKEN),
        "as_of": as_of.isoformat(),
        "catalogue_last_verified": LAST_VERIFIED,
        "stale_after_days": stale_after_days,
        "document_stale_after_days": document_stale_after_days,
        "firm_name": pack.get("firm_name") or "Unnamed synthetic pack",
        "synthetic": bool(pack.get("synthetic", False)),
        "key_dates": KEY_DATES,
        "sources_and_currency": currency_rows,
        "any_source_stale": any(row["currency"] == "stale" for row in currency_rows),
        "documents": document_rows,
        "prompt_injection": {
            "detected": bool(injection_documents),
            "followed": False,
            "documents": injection_documents,
        },
        "date_observations": date_observations(documents),
        "observations": observations,
        "counts": counts,
        "summary_for_humans": (
            "Draft observations only. "
            f"{counts['current_expectation_phrase_missing']} current-expectation "
            f"rows and {counts['preparation_phrase_missing']} preparation rows did not "
            "find the expected wording or had no document of that type. "
            f"{counts['not_scored_consultation_or_planned']} rows are consultation or "
            "planned and are not scored. These numbers are not a readiness result."
        ),
        "human_review": {
            "required_before_anyone_relies_on_a_row": True,
            "approver": "Compliance Officer or MLRO",
            "agent_accepted_any_gap": False,
        },
    }
    _reject_conclusions(payload)
    return payload


def load_pack(path: Path) -> dict:
    """Load a pack from a JSON file or a directory containing pack.json."""
    if path.is_dir():
        manifest_path = path / "pack.json"
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        documents = []
        for document in raw.get("documents") or []:
            item = dict(document)
            if "file" in item and "text" not in item:
                item["text"] = (path / item["file"]).read_text(encoding="utf-8")
            documents.append(item)
        raw["documents"] = documents
        return raw
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw


def render_sources_table(as_of: date, stale_after_days: int) -> str:
    """Plain-text sources and currency table."""
    rows = assess_catalogue(SOURCES, as_of, stale_after_days)
    lines = [
        f"Sources and currency. As of {as_of.isoformat()}. Stale if last_verified is older than {stale_after_days} days.",
        "",
    ]
    for row in rows:
        lines.append(
            f"{row['source_id']}\t{row['currency']}\tlast_verified {row['last_verified']}\t"
            f"page_last_updated {row['page_last_updated']}\t{row['url']}"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Command line. Exit 0 when JSON is produced. A missing phrase is not a failed run."""
    parser = argparse.ArgumentParser(description="Draft FCA cryptoasset observation register")
    parser.add_argument("--pack", type=Path, help="Pack directory or JSON file")
    parser.add_argument("--sources", action="store_true", help="Print the sources and currency table")
    parser.add_argument("--as-of", default=LAST_VERIFIED, help="ISO date used for the stale-data check")
    parser.add_argument("--stale-after-days", type=int, default=DEFAULT_STALE_AFTER_DAYS)
    parser.add_argument(
        "--document-stale-after-days",
        type=int,
        default=DEFAULT_DOCUMENT_STALE_AFTER_DAYS,
    )
    args = parser.parse_args(argv)
    as_of = parse_iso(args.as_of)

    if args.sources and not args.pack:
        sys.stdout.write(render_sources_table(as_of, args.stale_after_days))
        return 0
    if not args.pack:
        parser.error("pass --pack, or --sources")

    pack = load_pack(args.pack)
    payload = build_register(
        pack,
        as_of=as_of,
        stale_after_days=args.stale_after_days,
        document_stale_after_days=args.document_stale_after_days,
    )
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
