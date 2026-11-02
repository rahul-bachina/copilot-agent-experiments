"""Ask Experiment 25 to score instruction text. Do not apply its diff.

The call is a local subprocess so this experiment's modules are not replaced
by Experiment 25's modules of the same name. It does not use the network.
The instruction score is not the contract score.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

EXP25_REVIEW = (
    Path(__file__).resolve().parents[2] / "25-instruction-quality-reviewer" / "src" / "review.py"
)


def cross_check(
    text: str | None,
    manifest: dict[str, Any] | None,
    as_of: str,
    bundle_id: str,
) -> dict[str, Any]:
    if not text or not str(text).strip():
        return {
            "called": False,
            "experiment": "25",
            "reason": "No instruction text was supplied. Experiment 25 was not called.",
            "owner_approved": False,
            "diff_applied": False,
            "a3_recommended": False,
            "followed": False,
            "deployed": False,
            "score_percent": None,
            "c8_result": None,
            "injection_detected": False,
            "do_not_rely": False,
            "error": None,
        }
    payload: dict[str, Any] = {
        "bundle_id": bundle_id or "contract-instructions",
        "title": bundle_id or "contract instructions",
        "documents": [
            {
                "path": "instructions.md",
                "kind": "system_prompt",
                "reviewed_on": as_of,
                "text": text,
            }
        ],
    }
    if isinstance(manifest, dict):
        payload["manifest"] = manifest
    path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(payload, handle)
            path = handle.name
        completed = subprocess.run(
            [sys.executable, str(EXP25_REVIEW), "--bundle", path, "--as-of", as_of],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _failed(str(exc))
    finally:
        if path:
            Path(path).unlink(missing_ok=True)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "Experiment 25 exited").strip()
        return _failed(detail[:500])
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return _failed(f"Experiment 25 did not return JSON ({exc}).")
    checks = {item.get("id"): item.get("result") for item in report.get("checks") or []}
    injection = report.get("prompt_injection") if isinstance(report.get("prompt_injection"), dict) else {}
    return {
        "called": True,
        "experiment": "25",
        "reason": "Experiment 25 scored the instruction text. Its diff was not applied. Its score is not the contract score.",
        "catalogue_id": report.get("catalogue_id"),
        "owner_approved": False,
        "diff_applied": False,
        "a3_recommended": False,
        "followed": False,
        "deployed": False,
        "score_percent": (report.get("score") or {}).get("percent"),
        "band": (report.get("score") or {}).get("band"),
        "c8_result": checks.get("C8"),
        "injection_detected": bool(injection.get("detected")),
        "do_not_rely": bool(report.get("do_not_rely")),
        "error": None,
    }


def _failed(detail: str) -> dict[str, Any]:
    return {
        "called": True,
        "experiment": "25",
        "reason": "Experiment 25 was called and did not return a draft.",
        "owner_approved": False,
        "diff_applied": False,
        "a3_recommended": False,
        "followed": False,
        "deployed": False,
        "score_percent": None,
        "c8_result": None,
        "injection_detected": False,
        "do_not_rely": True,
        "error": detail,
    }
