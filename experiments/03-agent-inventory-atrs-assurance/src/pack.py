"""Assemble one assurance pack. The pack is a draft and does nothing else."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from drafts import draft_atrs, draft_dpia, draft_fca, draft_playbook, screen_duaa
from evaluations import evaluate_groundedness, evaluate_injection, handle_untrusted
from inventory import load_json


def build_pack(record: dict[str, Any], as_of: str, untrusted_instruction: str = "") -> dict[str, Any]:
    atrs = draft_atrs(record)
    playbook = draft_playbook(record)
    dpia = draft_dpia(record)
    duaa = screen_duaa(record)
    fca = draft_fca(record)
    injection = evaluate_injection(record, extra_text=untrusted_instruction)
    groundedness = evaluate_groundedness(record, atrs, playbook, as_of)
    pack = {
        "catalogue_id": "G010",
        "evaluations_included": ["G006", "G007"],
        "inventory_id": record["inventory_id"],
        "document_status": "draft",
        "approved": False,
        "approved_by": None,
        "may_be_relied_on": False,
        "may_be_submitted": False,
        "may_be_sent": False,
        "stale": groundedness["stale"],
        "as_of": as_of,
        "actions_taken": [],
        "atrs": atrs,
        "playbook": playbook,
        "dpia": dpia,
        "duaa_screen": duaa,
        "fca_style_inventory": fca,
        "evaluations": {"G006": injection, "G007": groundedness},
    }
    if untrusted_instruction:
        pack["untrusted_instruction"] = handle_untrusted(record, untrusted_instruction, pack)
    return pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft an assurance pack. Nothing is approved.")
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--instruction", default="")
    args = parser.parse_args(argv)
    record = load_json(args.inventory)
    pack = build_pack(record, args.as_of, args.instruction)
    json.dump(pack, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
