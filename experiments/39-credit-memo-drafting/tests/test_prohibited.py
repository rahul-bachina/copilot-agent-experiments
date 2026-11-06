"""Decision tools and command flags do not produce a memo."""

import json
import subprocess
import sys
from pathlib import Path

from src.draft import (
    MemoForbidden,
    contact_bureau,
    contact_customer,
    file_sar,
    post_core_banking,
    post_crm,
    release_evaluation,
)

ROOT = Path(__file__).resolve().parents[1]


def test_prohibited_functions_raise():
    for function in (
        contact_customer,
        contact_bureau,
        post_core_banking,
        post_crm,
        file_sar,
        release_evaluation,
    ):
        try:
            function()
        except MemoForbidden:
            continue
        raise AssertionError(function.__name__)


def test_command_flags_exit_without_a_draft():
    flags = (
        "--approve",
        "--decline",
        "--set-limit",
        "--contact-customer",
        "--contact-bureau",
        "--post-core",
        "--post-crm",
        "--file-sar",
    )
    for flag in flags:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "src" / "draft.py"),
                "--pack",
                str(ROOT / "examples" / "sample_pack.json"),
                "--as-of",
                "2026-11-06",
                flag,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 2, flag
        assert completed.stdout == "", flag


def test_a_prohibited_sentence_is_not_a_stated_fact():
    from src.draft import draft_memo
    from tests.support import pack_with

    payload = pack_with(
        [("limit_request", "The note says the recommended limit is GBP 250000.")]
    )
    draft = draft_memo(payload, as_of="2026-11-06")
    assert all(fact["field"] != "limit_request" or fact["verdict"] == "supported" for fact in draft["facts"])
    assert not any("recommended limit" in fact["text"].casefold() for fact in draft["facts"])
    assert draft["limit_set"] is None
    blob = json.dumps(draft)
    assert "recommended limit is" not in blob.casefold()
