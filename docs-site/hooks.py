"""Build hooks for the briefing site.

Copies each experiment's architecture diagram into the site tree so the
published page uses the file from the experiment folder. Also sets the
HTML language to British English, gives header icons a fixed size, and
embeds the stylesheets in each page.
"""

from pathlib import Path
from urllib.parse import urlparse
import re
import shutil

STYLESHEET = re.compile(r'<link rel="stylesheet" href="([^"]+)">')
SVG_TAG = re.compile(r"<svg\b([^>]*)>", re.IGNORECASE)

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
    "experiments/06-nhs-policy-qa/docs/architecture_diagram.png": (
        "experiments/img/06-nhs-policy-architecture.png"
    ),
    "experiments/07-consultation-themes/docs/architecture_diagram.png": (
        "experiments/img/07-consultation-architecture.png"
    ),
    "experiments/08-uk-pii-redaction-gateway/docs/architecture_diagram.png": (
        "experiments/img/08-uk-pii-architecture.png"
    ),
    "experiments/09-casework-correspondence-draft/docs/architecture_diagram.png": (
        "experiments/img/09-casework-architecture.png"
    ),
    "experiments/10-travel-rule-exception-triage/docs/architecture_diagram.png": (
        "experiments/img/10-travel-rule-architecture.png"
    ),
    "experiments/11-era-2025-hr-assistant/docs/architecture_diagram.png": (
        "experiments/img/11-era-hr-architecture.png"
    ),
    "experiments/12-document-intake/docs/architecture_diagram.png": (
        "experiments/img/12-document-intake-architecture.png"
    ),
    "experiments/13-council-contact-front-door/docs/architecture_diagram.png": (
        "experiments/img/13-council-contact-architecture.png"
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


def _size_inline_svgs(html: str) -> str:
    """Icons ship without width or height. With no stylesheet they fill the window."""

    def repl(match: re.Match) -> str:
        attrs = match.group(1)
        if re.search(r"\bwidth\s*=", attrs, re.IGNORECASE):
            return match.group(0)
        return f"<svg{attrs} width=\"24\" height=\"24\">"

    return SVG_TAG.sub(repl, html)


def _stylesheet_path(href: str, html_path: Path, site_dir: Path, site_url: str) -> Path | None:
    """Resolve a stylesheet link to a file inside the built site."""
    if href.startswith(("http://", "https://", "//")):
        return None
    if href.startswith("/"):
        site_path = urlparse(site_url).path if site_url else ""
        prefix = site_path.rstrip("/")
        if prefix and (href == prefix or href.startswith(prefix + "/")):
            relative = href[len(prefix):].lstrip("/")
        else:
            relative = href.lstrip("/")
        css_path = (site_dir / relative).resolve()
    else:
        css_path = (html_path.parent / href).resolve()
    try:
        css_path.relative_to(site_dir)
    except ValueError:
        return None
    if not css_path.is_file():
        return None
    return css_path


def _embed_stylesheets(html: str, html_path: Path, site_dir: Path, site_url: str) -> str:
    """Keep the linked files, and repeat them in the page.

    A failed stylesheet request otherwise leaves the search icon at the
    size of the window. Relative addresses in these files are data URIs,
    so embedding them does not point images at the wrong folder. The 404
    page links stylesheets from the site root, so those are resolved there.
    """

    def repl(match: re.Match) -> str:
        css_path = _stylesheet_path(match.group(1), html_path, site_dir, site_url)
        if css_path is None:
            return match.group(0)
        css = css_path.read_text(encoding="utf-8")
        if "</style>" in css.lower():
            return match.group(0)
        return match.group(0) + "\n<style>\n" + css + "\n</style>"

    return STYLESHEET.sub(repl, html)


def on_post_build(config, **kwargs):
    site_dir = Path(config.site_dir).resolve()
    site_url = config.site_url or ""
    for html_path in site_dir.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        updated = text.replace('<html lang="en"', '<html lang="en-GB"', 1)
        updated = _size_inline_svgs(updated)
        updated = _embed_stylesheets(updated, html_path, site_dir, site_url)
        if updated != text:
            html_path.write_text(updated, encoding="utf-8")
