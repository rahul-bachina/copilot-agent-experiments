"""HTML tag balance for the MkDocs source pages.

A stray closing tag in a raw HTML block closes the Material content
wrapper early. The home page then lays out as narrow side-by-side
slivers. Every Markdown file under docs-site/docs must keep div,
article, and section tags balanced, and the running depth of each
tag must stay non-negative.
"""

import re
from pathlib import Path

import pytest

DOCS_ROOT = Path(__file__).resolve().parents[1] / "docs-site" / "docs"
TAGS = ("div", "article", "section")

TOKEN = re.compile(
    r"</(?P<close>div|article|section)\s*>"
    r"|<(?P<open>div|article|section)\b(?P<attrs>[^>]*)>",
    re.IGNORECASE,
)
FENCE = re.compile(r"```.*?```", re.DOTALL)


def _markdown_files():
    return sorted(DOCS_ROOT.rglob("*.md"))


def _fence_spans(text):
    return [match.span() for match in FENCE.finditer(text)]


def _inside(spans, position):
    return any(start <= position < end for start, end in spans)


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(DOCS_ROOT.parent.parent))
    except ValueError:
        return str(path)


def balance_errors(path: Path) -> list[str]:
    """Return tag-balance problems in one Markdown file."""
    text = path.read_text(encoding="utf-8")
    fences = _fence_spans(text)
    depth = {tag: 0 for tag in TAGS}
    opens = {tag: 0 for tag in TAGS}
    closes = {tag: 0 for tag in TAGS}
    errors = []

    for match in TOKEN.finditer(text):
        if _inside(fences, match.start()):
            continue
        line = text.count("\n", 0, match.start()) + 1
        if match.group("close"):
            tag = match.group("close").lower()
            closes[tag] += 1
            depth[tag] -= 1
            if depth[tag] < 0:
                errors.append(
                    f"{_display(path)}:{line}: </{tag}> makes {tag} depth negative"
                )
            continue
        attrs = match.group("attrs") or ""
        if attrs.rstrip().endswith("/"):
            continue
        tag = match.group("open").lower()
        opens[tag] += 1
        depth[tag] += 1

    for tag in TAGS:
        if opens[tag] != closes[tag]:
            errors.append(
                f"{_display(path)}: <{tag}> count {opens[tag]} != </{tag}> count {closes[tag]}"
            )
    return errors


@pytest.mark.parametrize(
    "path",
    _markdown_files(),
    ids=lambda path: str(path.relative_to(DOCS_ROOT)),
)
def test_docs_html_tags_are_balanced(path):
    """Opening and closing counts match, and depth never goes negative."""
    errors = balance_errors(path)
    assert not errors, "\n".join(errors)


def test_stray_close_makes_depth_negative(tmp_path):
    """A closing tag with nothing open is the home-page failure mode."""
    page = tmp_path / "page.md"
    page.write_text("<article>\n</article>\n</article>\n</div>\n", encoding="utf-8")
    errors = balance_errors(page)
    assert any("article depth negative" in error for error in errors)
    assert any("div depth negative" in error for error in errors)
    assert any("<div> count 0 != </div> count 1" in error for error in errors)
