"""Shared pinned files for the retention tests."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def pinned():
    folder = ROOT / "fixtures"
    return {
        "schedule": json.loads((folder / "schedule.json").read_text(encoding="utf-8")),
        "inventory": json.loads((folder / "inventory.json").read_text(encoding="utf-8")),
        "directory": json.loads((folder / "directory.json").read_text(encoding="utf-8")),
    }


def advise(pinned, request, as_of="2026-11-20"):
    from src.advice import advise_retention

    return advise_retention(
        request,
        pinned["schedule"],
        pinned["inventory"],
        pinned["directory"],
        as_of,
    )
