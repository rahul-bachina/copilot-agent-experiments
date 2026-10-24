#!/usr/bin/env python3
"""Write a draft agent-manifest.yaml. Refuses --approve."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from inventory import load_json
from lifecycle import ProhibitedAction
from manifest_generator import generate_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft a permissions manifest from an inventory record. Never approves it."
    )
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Refused. Present so a caller cannot pass it quietly.",
    )
    args = parser.parse_args(argv)
    record = load_json(args.inventory)
    try:
        result = generate_manifest(record, args.as_of, approve=args.approve)
    except ProhibitedAction as exc:
        json.dump(
            {
                "document_status": "draft",
                "approved": False,
                "approved_by": None,
                "validation_passed": False,
                "errors": [str(exc)],
                "actions_taken": [],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 2
    if args.output and result["validation_passed"]:
        args.output.write_text(result["yaml"], encoding="utf-8")
        result["wrote"] = str(args.output)
    elif args.output:
        result["wrote"] = None
    public = {
        "document_status": result["document_status"],
        "approved": result["approved"],
        "approved_by": result["approved_by"],
        "may_be_relied_on": result["may_be_relied_on"],
        "validation_passed": result["validation_passed"],
        "errors": result["errors"],
        "actions_taken": result["actions_taken"],
        "wrote": result.get("wrote"),
        "manifest": result["manifest"],
    }
    json.dump(public, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
