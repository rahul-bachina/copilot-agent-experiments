"""Build a .pptx from an outline the presenter has already approved.

The file is Office Open XML written with the standard library. It does not
call the PowerPoint JavaScript API and it does not call Microsoft Graph.
The caller must already have refused to build the file when approval is missing.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


def _slide_xml(text: str) -> str:
    lines = escape(text).split("\n")
    paragraphs = "".join(f"<a:p><a:r><a:t>{line}</a:t></a:r></a:p>" for line in lines)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        "<p:cSld><p:spTree>"
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        "<p:grpSpPr/>"
        "<p:sp><p:nvSpPr><p:cNvPr id=\"2\" name=\"Text\"/>"
        "<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/>"
        f"<p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs}</p:txBody>"
        "</p:sp></p:spTree></p:cSld>"
        "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"
    )


def _content_types(count: int) -> str:
    overrides = "".join(
        f'<Override PartName="/ppt/slides/slide{index}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for index in range(1, count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        f"{overrides}</Types>"
    )


def _presentation(count: int) -> str:
    slide_ids = "".join(
        f'<p:sldId id="{256 + index}" r:id="rId{index}"/>'
        for index in range(1, count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        f"<p:sldIdLst>{slide_ids}</p:sldIdLst></p:presentation>"
    )


def _rels(count: int) -> str:
    rows = "".join(
        f'<Relationship Id="rId{index}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
        f'Target="slides/slide{index}.xml"/>'
        for index in range(1, count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{rows}</Relationships>"
    )


def write_pptx(notes: list[str], path: Path, markings: dict) -> None:
    """Write speaker notes as slide text. Markings are already on each note."""
    del markings  # the note text already carries the marking; this argument documents that
    count = max(len(notes), 1)
    pages = list(notes) or ["MARKING NOT SUPPLIED. No sourced slide. Not shared."]
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types(count if notes else 1))
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="ppt/presentation.xml"/>'
            "</Relationships>",
        )
        archive.writestr("ppt/presentation.xml", _presentation(len(pages)))
        archive.writestr("ppt/_rels/presentation.xml.rels", _rels(len(pages)))
        for index, note in enumerate(pages, start=1):
            archive.writestr(f"ppt/slides/slide{index}.xml", _slide_xml(note))
