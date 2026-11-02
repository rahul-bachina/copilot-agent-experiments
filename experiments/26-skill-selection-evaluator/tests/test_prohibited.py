"""Prohibited actions route to a person, and the command refuses to act."""

import json

from src.report import ProhibitedAction, evaluate, main

from tests.support import SAMPLE, run, safety


def test_prohibited_requests_route_to_human_and_a_negation_does_not():
    report = run()
    safety(report)
    by_id = {row["id"]: row for row in report["utterances"]}
    for utterance_id in ("send", "pay", "deploy", "delete", "grant"):
        assert by_id[utterance_id]["predicted"] == "human"
        assert by_id[utterance_id]["reason"] == "prohibited_action"
    assert by_id["negation"]["predicted"] == "skill:book-bulk-collection"
    assert by_id["negation"]["prohibited"] == []
    assert report["prohibited_actions"]["count"] == 5
    assert report["prohibited_actions"]["all_routed_to_human"] is True
    assert set(report["refusal"]) == {"send", "pay", "deploy", "delete", "grant"}


def test_cli_refuses_to_validate_apply_edit_or_deploy(tmp_path, capsys):
    code = main(["--bundle", str(SAMPLE), "--as-of", "2026-11-02", "--approve"])
    assert code == 2
    assert capsys.readouterr().out == ""
    for flag in ("--apply", "--edit-skills", "--deploy"):
        code = main(["--bundle", str(SAMPLE), "--as-of", "2026-11-02", flag])
        assert code == 2
    destination = tmp_path / "out.json"
    assert not destination.exists()


def test_function_refuses_the_same_flags():
    bundle = json.loads(SAMPLE.read_text(encoding="utf-8"))
    for kwargs in (
        {"approve": True},
        {"apply": True},
        {"edit_skills": True},
        {"deploy": True},
    ):
        try:
            evaluate(bundle, "2026-11-02", base_dir=SAMPLE.parent, **kwargs)
        except ProhibitedAction:
            continue
        raise AssertionError(kwargs)
