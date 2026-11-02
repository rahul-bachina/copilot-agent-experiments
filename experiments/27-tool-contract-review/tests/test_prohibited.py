"""The reviewer has no approve, apply, publish, or deploy action."""

import pytest

from src.prohibited import (
    ProhibitedAction,
    apply_contract_diff,
    deploy_contract,
    publish_policy,
    record_owner_approval,
)
from src.review import review
from tests.support import bundle_for


def test_flags_raise_before_a_report_is_built():
    bundle = bundle_for("clean-openapi.json")
    for kwargs in (
        {"approve": True},
        {"apply": True},
        {"publish": True},
        {"deploy": True},
    ):
        with pytest.raises(ProhibitedAction):
            review(bundle, "2026-11-02", **kwargs)


@pytest.mark.parametrize(
    "function",
    [record_owner_approval, apply_contract_diff, publish_policy, deploy_contract],
)
def test_named_tools_always_raise(function):
    with pytest.raises(ProhibitedAction):
        function({"contract_approved": True})


def test_cli_refuses_the_flags_and_writes_nothing(tmp_path, capsys):
    from src.review import main

    bundle = tmp_path / "bundle.json"
    bundle.write_text(__import__("json").dumps(bundle_for("clean-openapi.json")), encoding="utf-8")
    for flag in ("--approve", "--apply", "--publish", "--deploy"):
        code = main(["--bundle", str(bundle), "--as-of", "2026-11-02", flag])
        captured = capsys.readouterr()
        assert code == 2
        assert captured.out == ""
        assert "security/API owner" in captured.err
