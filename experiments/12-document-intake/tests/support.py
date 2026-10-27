"""Small batch builders. Every batch is marked synthetic."""

from datetime import date, timedelta

AS_OF = date(2026, 10, 27)


def file_row(
    file_id="F-001",
    content="A short synthetic note with no class keyword.",
    *,
    filename="note.txt",
    media_type="text/plain",
    document_date="2026-10-01",
    sha256=None,
):
    row = {
        "file_id": file_id,
        "filename": filename,
        "media_type": media_type,
        "document_date": document_date,
        "content": content,
    }
    if sha256 is not None:
        row["sha256"] = sha256
    return row


def batch(*files, batch_id="INTAKE-SYN-TEST", requested_purpose=None, **extra):
    body = {
        "synthetic": True,
        "batch_id": batch_id,
        "files": list(files) or [file_row()],
    }
    if requested_purpose is not None:
        body["requested_purpose"] = requested_purpose
    body.update(extra)
    return body


def days_before(as_of: date, days: int) -> str:
    return (as_of - timedelta(days=days)).isoformat()
