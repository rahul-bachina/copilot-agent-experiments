"""permissions.yaml is the agent manifest, byte for byte."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_permissions_yaml_matches_the_manifest():
    assert (ROOT / "permissions.yaml").read_text(encoding="utf-8") == (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")
    text = (ROOT / "agent-manifest.yaml").read_text(encoding="utf-8")
    assert 'level: "A0"' in text
    assert "A3" in text
    assert "enabled: false" in text
    assert "Reviewer resolves every material discrepancy" in text
