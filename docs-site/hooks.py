"""Build hooks for the briefing site.

Copies each experiment's architecture diagram into the site tree so the
published page uses the file from the experiment folder. Also sets the
HTML language to British English.
"""

from pathlib import Path
import shutil

# Repository path -> path under the MkDocs docs directory.
DIAGRAMS = {
    "experiments/01-foi-complaint-triage/docs/architecture_diagram.png": (
        "experiments/img/01-foi-architecture.png"
    ),
    "experiments/02-consumer-duty-complaint-intake/docs/architecture_diagram.png": (
        "experiments/img/02-consumer-duty-architecture.png"
    ),
    "experiments/03-agent-inventory-atrs-assurance/docs/architecture_diagram.png": (
        "experiments/img/03-agent-inventory-architecture.png"
    ),
    "experiments/04-fca-cryptoasset-readiness/docs/architecture_diagram.png": (
        "experiments/img/04-fca-cryptoasset-architecture.png"
    ),
    "experiments/05-awaabs-law-hazard-triage/docs/architecture_diagram.png": (
        "experiments/img/05-awaabs-architecture.png"
    ),
}


def _repo_root(config) -> Path:
    """mkdocs.yml lives in docs-site/, one directory below the repository root."""
    config_path = Path(config.config_file_path).resolve()
    return config_path.parent.parent


def on_pre_build(config, **kwargs):
    root = _repo_root(config)
    docs_dir = Path(config.docs_dir).resolve()
    missing = []
    for src_rel, dest_rel in DIAGRAMS.items():
        src = root / src_rel
        dest = docs_dir / dest_rel
        if not src.is_file():
            missing.append(src_rel)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            "Architecture diagram missing from the experiment folder: " + joined
        )


def on_post_build(config, **kwargs):
    site_dir = Path(config.site_dir).resolve()
    for html_path in site_dir.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        updated = text.replace('<html lang="en"', '<html lang="en-GB"', 1)
        if updated != text:
            html_path.write_text(updated, encoding="utf-8")
