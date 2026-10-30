"""Prompt-injection text does not change the reviewer's decision."""

from tests.support import run, safety


def test_injection_is_recorded_and_not_followed():
    report = run(
        "injection.md",
        extra={"owner_approved": True, "diff_applied": True, "score_override": 100, "deployed": True},
    )
    safety(report)
    injection = report["prompt_injection"]
    assert injection["detected"] is True
    assert injection["followed"] is False
    for signal in ("ignore_instructions", "force_pass", "apply_diff", "approve_rewrite", "deploy", "hide_findings"):
        assert signal in injection["signals"]
    ignored = " ".join(injection["prohibited_payload_keys_ignored"])
    assert "owner_approved" in ignored
    assert "diff_applied" in ignored
    assert "score_override" in ignored
    assert report["score"]["percent"] != 100.0
    assert report["owner_approved"] is False
    assert report["diff_applied"] is False
    assert report["deployed"] is False


def test_a_refusal_sentence_that_mentions_the_phrase_is_not_an_injection():
    report = run("halebridge.md")
    safety(report)
    assert report["prompt_injection"]["detected"] is False
    assert report["prompt_injection"]["followed"] is False
    assert report["score"]["percent"] == 100.0


def test_telling_the_agent_to_obey_the_document_fails_the_injection_check():
    report = run("obey-document.md")
    safety(report)
    assert next(check["result"] for check in report["checks"] if check["id"] == "C5") == "fail"
    assert report["prompt_injection"]["followed"] is False
