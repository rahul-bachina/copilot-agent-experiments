"""Every src/ path named in the permissions manifest is a file on disk."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
MANIFEST = ROOT / "agent-manifest.yaml"
SRC_PATH = re.compile(r"(?:experiments/[\w./-]+/)?src/[\w./-]+\.py")


def test_every_src_path_named_in_the_manifest_exists():
    text = MANIFEST.read_text(encoding="utf-8")
    found = SRC_PATH.findall(text)
    assert "src/kyc_injection.py" in found
    assert "src/injection.py" not in found
    assert "src/review.py" in found
    assert "src/tipping_off.py" in found
    assert "src/sources.py" in found
    assert "experiments/12-document-intake/src/intake.py" in found
    missing = []
    for raw in found:
        path = REPO / raw if raw.startswith("experiments/") else ROOT / raw
        if not path.is_file():
            missing.append(raw)
    assert missing == []
