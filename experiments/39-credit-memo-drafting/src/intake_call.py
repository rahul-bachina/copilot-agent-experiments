"""Call Experiment 12. This module does not re-implement the inventory.

No purpose is requested, so nothing is routed. Credit files are not a KYC
purpose. Confirmation flags stay false. File content is not copied into the memo.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

INTAKE_EXPERIMENT_ID = "exp-12-document-intake"
INTAKE_CATALOGUE_ID = "O001"


class IntakeUnavailable(RuntimeError):
    """Experiment 12 is not beside this experiment. An inventory is not invented."""


def _load_intake():
    intake_src = Path(__file__).resolve().parents[2] / "12-document-intake" / "src"
    if not intake_src.is_dir():
        raise IntakeUnavailable(
            "Experiment 12 is not beside this experiment. The memo will not invent an inventory."
        )
    inserted = str(intake_src)
    if inserted not in sys.path:
        sys.path.insert(0, inserted)
    import intake as intake_module

    if getattr(intake_module, "EXPERIMENT_ID", None) != INTAKE_EXPERIMENT_ID:
        raise IntakeUnavailable("the intake module is not Experiment 12")
    return intake_module


def inventory(
    files: list[dict[str, Any]],
    *,
    batch_id: str,
    as_of: date,
    stale_after_days: int,
) -> dict[str, Any]:
    intake_module = _load_intake()
    draft = intake_module.intake(
        {"synthetic": True, "batch_id": batch_id, "files": files},
        as_of=as_of,
        stale_after_days=stale_after_days,
        rules_as_of=as_of,
    )
    if draft.get("experiment_id") != INTAKE_EXPERIMENT_ID:
        raise IntakeUnavailable("the intake result is not Experiment 12")
    rows = []
    for row in draft["files"]:
        pii = row["pii"]
        rows.append(
            {
                "file_id": row["file_id"],
                "read_status": row["read_status"],
                "date_status": row["date_status"],
                "suggested_class": row["suggested_class"],
                "finding_count": pii["finding_count"],
                "entity_types": list(pii["entity_types"]),
                "output_is_anonymised": False,
            }
        )
    flags = draft["flags"]
    return {
        "called": True,
        "experiment_id": INTAKE_EXPERIMENT_ID,
        "catalogue_id": draft["catalogue_id"],
        "autonomy_of_intake": draft["autonomy"],
        "files_confirmed": False,
        "purpose_confirmed": False,
        "handed_off": False,
        "accepted_into_queue": flags["accepted_into_queue"],
        "production_record_written": flags["production_record_written"],
        "external_sent": flags["external_sent"],
        "underlying_matter_approved": flags["underlying_matter_approved"],
        "underlying_matter_rejected": flags["underlying_matter_rejected"],
        "catalogue_stale": draft["catalogue_stale"],
        "any_document_not_current": draft["any_document_not_current"],
        "gateway_rules_stale": draft["gateway_rules_stale"],
        "prompt_injection_detected": draft["prompt_injection"]["detected"],
        "prompt_injection_followed": False,
        "purpose_requested": None,
        "files": rows,
    }
