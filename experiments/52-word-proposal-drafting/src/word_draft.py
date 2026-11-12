"""Build a .docx from a draft the author has not yet accepted.

The file is Office Open XML written with the standard library. It does not
call the Word JavaScript API and it does not call Microsoft Graph.
"""

from __future__ import annotations

import zipfile
from io import BytesIO
from xml.sax.saxutils import escape


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def _paragraph(text: str) -> str:
    safe = escape(text)
    return f"<w:p><w:r><w:t xml:space=\"preserve\">{safe}</w:t></w:r></w:p>"


def document_xml(paragraphs: list[str]) -> str:
    body = "".join(_paragraph(line) for line in paragraphs)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{body}<w:sectPr/></w:body></w:document>"
    )


def paragraphs_from_draft(draft: dict) -> list[str]:
    """Text the Word file shows. Requirement text is not copied."""
    lines = [
        str(draft.get("label") or ""),
        "Autonomy A1. The author accepts the complete draft before it is used anywhere. This file is not a submission.",
        f"Proposal {draft.get('proposal_id') or 'not recorded'}. As of {draft.get('as_of') or ''}.",
        str(draft.get("organisation") or ""),
        str(draft.get("buyer") or ""),
        "Compliance matrix. A row is met only when an approved source is quoted and the groundedness check supports that quote.",
    ]
    for row in draft.get("compliance_matrix") or []:
        met = "met" if row.get("requirement_met") is True else "not met"
        sources = ", ".join(row.get("source_ids") or []) or "no source"
        lines.append(
            f"{row.get('requirement_id')}: {row.get('status')}; {met}; sources {sources}."
        )
        answer = str(row.get("draft_answer") or "")
        if answer:
            lines.append(answer)
    lines.append("Gaps. A gap is not an answer and it is not met.")
    if draft.get("gaps"):
        lines.append("Gap requirement ids: " + ", ".join(draft["gaps"]) + ".")
    else:
        lines.append("No gap ids on this draft.")
    lines.append("Author checks. The author confirms every price, commitment, accreditation, statistic, case study, and anything else that was not marked met.")
    checks = draft.get("author_checks") or []
    if checks:
        for item in checks:
            lines.append(
                f"Check {item.get('requirement_id')}: {item.get('kind')}."
            )
    else:
        lines.append("No separate author-check row. The author still accepts the complete draft.")
    approval = draft.get("human_approval")
    if approval is None:
        lines.append("Human approval is empty.")
    else:
        lines.append("The author has accepted this draft for their own later use. The agent has not submitted it.")
    lines.append("A person can take this file outside the agent. The agent does not submit, send, or upload it.")
    return lines


def render_docx(draft: dict) -> bytes:
    paragraphs = paragraphs_from_draft(draft)
    xml = document_xml(paragraphs)
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", CONTENT_TYPES)
        package.writestr("_rels/.rels", RELS)
        package.writestr("word/document.xml", xml)
    return buffer.getvalue()


def write_docx(draft: dict, path) -> None:
    path.write_bytes(render_docx(draft))
