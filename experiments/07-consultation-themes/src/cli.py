"""Command line for intake status and theme analysis.

Run from the experiment directory:

    python -m src.cli intake --input eval/synthetic_dataset.json --as-of 2026-10-24
    python -m src.cli analyse --input eval/synthetic_dataset.json --as-of 2026-10-24
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.pipeline import analyse, intake_status


def _load(path: Path) -> tuple[dict, dict | None, dict | None]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "batch" in payload and "responses" not in payload:
        return payload["batch"], payload.get("framework"), payload.get("approval")
    return payload, None, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consultation theme analysis (Experiment 07)")
    parser.add_argument("command", choices=("intake", "analyse"))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--framework", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--as-of", default="2026-10-24")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    batch, framework, approval = _load(args.input)
    if args.framework is not None:
        framework = json.loads(args.framework.read_text(encoding="utf-8"))
    if args.approval is not None:
        approval = json.loads(args.approval.read_text(encoding="utf-8"))

    if args.command == "intake":
        result = intake_status(batch, as_of=args.as_of)
    else:
        if framework is None:
            print("analyse needs a framework, in the dataset or via --framework", file=sys.stderr)
            return 2
        result = analyse(batch, framework, approval, as_of=args.as_of)

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
