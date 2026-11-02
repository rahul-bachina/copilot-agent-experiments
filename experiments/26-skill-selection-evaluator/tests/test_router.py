"""Routing on the synthetic Northfen catalogue."""

from tests.support import run, safety


def _by_id(report):
    return {row["id"]: row for row in report["utterances"]}


def test_sample_agreement_and_safety():
    report = run()
    safety(report)
    assert report["agreement"]["percent"] == 100.0
    assert report["agreement"]["labelled"] == 19
    assert report["do_not_rely"] is False
    assert report["bundle_id"] == "northfen-desk"


def test_trigger_description_tie_and_topic():
    rows = _by_id(run())
    assert rows["bulk"]["predicted"] == "skill:book-bulk-collection"
    assert rows["bulk"]["reason"] == "trigger"
    assert rows["drip"]["predicted"] == "skill:housing-repair"
    assert rows["socket"]["predicted"] == "skill:housing-repair-urgent"
    assert rows["tie"]["predicted"] == "human"
    assert rows["tie"]["reason"] == "ambiguous_tie"
    assert rows["parking"]["predicted"] == "none"
    assert rows["library"]["predicted"] == "skill:library-hours"
    library = next(skill for skill in run()["skills"] if skill["id"] == "library-hours")
    assert library["kind"] == "topic"


def test_confusable_pair_and_vague_description():
    report = run()
    pairs = report["confusable_pairs"]
    assert len(pairs) == 1
    assert pairs[0]["skills"] == ["housing-repair", "housing-repair-urgent"]
    assert "shared_trigger" in pairs[0]["reasons"]
    assert "description_overlap" in pairs[0]["reasons"]
    assert "housing repair" in pairs[0]["shared_triggers"]
    vague = next(row for row in report["description_findings"] if row["skill_id"] == "vague-helper")
    assert vague["missing"] is True
    assert vague["ambiguous"] is True
    assert vague["needs_rewrite"] is True
    ids = [item["skill_id"] for item in report["proposed_diff"]["files"]]
    assert "vague-helper" in ids
    assert "housing-repair" in ids
    assert report["proposed_diff"]["applied"] is False
    assert "Not applied" in report["proposed_diff"]["diff"]
    assert "SKILL.md" not in report["actions_taken"]


def test_per_class_counts_match_the_labels():
    report = run()
    by_class = {row["class"]: row for row in report["per_class"]}
    bulky = by_class["book-bulk-collection"]
    assert bulky["true_positive"] == 3
    assert bulky["false_positive"] == 0
    assert bulky["false_negative"] == 0
    assert bulky["precision"] == 100.0
    assert bulky["recall"] == 100.0
    assert by_class["human"]["support"] == 7
    assert by_class["none"]["support"] == 1
    assert by_class["vague-helper"]["support"] == 0
    assert by_class["vague-helper"]["precision"] is None
    assert by_class["vague-helper"]["recall"] is None


def test_same_inputs_produce_the_same_json():
    left = run()
    right = run()
    assert left == right


def test_readme_names_the_routing_rules():
    from pathlib import Path

    readme = Path(__file__).resolve().parents[1].joinpath("README.md").read_text(encoding="utf-8")
    for phrase in (
        "trigger phrase",
        "ambiguous",
        "none",
        "human",
        "precision",
        "recall",
        "The maintainer validates routing tests",
        "diff_applied",
        "Microsoft Foundry",
    ):
        assert phrase in readme
    assert "Azure AI " + "Foundry" not in readme
