"""The gate blocks export. The prohibited calls do not write a file."""

import json
from pathlib import Path

from src.assemble import assemble, main
from src.prohibited import (
    ProhibitedAction,
    decide_needs,
    decide_outcomes,
    decide_placement,
    decide_provision,
    edit_final_plan,
    secure_provision,
    send_to_parents,
    send_to_school,
    write_to_la_system,
)
from tests.support import AS_OF, ROOT, bundle, signoff


def test_the_prohibited_functions_raise_and_do_not_return_a_plan():
    for function in (
        decide_needs,
        decide_provision,
        decide_placement,
        decide_outcomes,
        edit_final_plan,
        send_to_parents,
        send_to_school,
        write_to_la_system,
        secure_provision,
    ):
        try:
            function()
        except ProhibitedAction:
            continue
        raise AssertionError(function.__name__)


def test_export_without_signoff_stays_blocked():
    draft = assemble(bundle(), as_of=AS_OF)
    assert draft["export_blocked"] is True
    assert draft["export_block_reason"] == "no_caseworker_signoff"
    assert draft["exported"] is False
    assert draft["sent_to_parents"] is False


def test_a_string_true_does_not_open_the_gate():
    payload = signoff(authorises_export="true")
    draft = assemble(bundle(), as_of=AS_OF, signoff=payload)
    assert draft["export_blocked"] is True
    assert draft["export_block_reason"] == "authorises_export"
    assert draft["exported"] is False


def test_a_valid_signoff_includes_a_local_copy_and_still_does_not_send():
    payload = signoff()
    draft = assemble(bundle(), as_of=AS_OF, signoff=payload)
    assert draft["exported"] is True
    assert draft["export_blocked"] is False
    assert draft["export"]["label"] == "LOCAL COPY FOR THE CASEWORKER — NOT SENT"
    assert draft["export"]["sent_to_parents"] is False
    assert draft["export"]["sent_to_school"] is False
    assert draft["export"]["written_to_la_system"] is False
    assert draft["export"]["final_plan_included"] is False
    assert draft["sent_to_parents"] is False
    assert draft["final_plan_edited"] is False
    assert draft["needs_decided"] is False
    assert draft["signoff_stored"] is False
    assert draft["caseworker_confirmed_la_template"] is True
    assert draft["agent_checked_template"] is False
    blob = json.dumps(draft)
    assert "typed a final paragraph" not in blob
    assert draft["export"]["sections"]["I"]["lines"] == []


def test_a_signoff_on_the_wrong_date_is_blocked():
    draft = assemble(bundle(), as_of=AS_OF, signoff=signoff(signed_on="2026-11-03"))
    assert draft["export_blocked"] is True
    assert draft["export_block_reason"] == "signed_on"
    assert draft["exported"] is False


def test_cli_prohibited_flags_exit_without_writing(tmp_path: Path):
    out = tmp_path / "out.json"
    code = main(
        [
            "--bundle",
            str(ROOT / "examples" / "sample_bundle.json"),
            "--as-of",
            AS_OF,
            "--send-to-parents",
            "--output",
            str(out),
        ]
    )
    assert code == 2
    assert not out.exists()


def test_cli_export_without_signoff_writes_nothing(tmp_path: Path, capsys):
    out = tmp_path / "out.json"
    code = main(
        [
            "--bundle",
            str(ROOT / "examples" / "sample_bundle.json"),
            "--as-of",
            AS_OF,
            "--export",
            "--output",
            str(out),
        ]
    )
    assert code == 2
    assert not out.exists()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cli_export_with_signoff_does_not_include_the_final_text(tmp_path: Path, capsys):
    out = tmp_path / "out.json"
    code = main(
        [
            "--export",
            "--bundle",
            str(ROOT / "examples" / "sample_bundle.json"),
            "--as-of",
            AS_OF,
            "--signoff",
            str(ROOT / "examples" / "sample_signoff.json"),
            "--output",
            str(out),
        ]
    )
    assert code == 0
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["exported"] is True
    assert saved["sent_to_parents"] is False
    assert "typed a final paragraph" not in out.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert "typed a final paragraph" not in captured.out
