import json
from pathlib import Path

from model import ROOT, fingerprint, sample_confirmation, sample_pack

AS_OF = "2026-11-13"


def pack():
    return sample_pack()


def confirmation(cells=None, ranges=None):
    return sample_confirmation(cells, ranges)


def reviewed(cells=None, ranges=None, as_of=AS_OF, confirm=True):
    from review import review_workbook

    body = sample_pack(cells)
    gate = confirmation(body["cells"], ranges) if confirm else None
    return review_workbook(body, gate, as_of)


def load_report_blob(report) -> str:
    return json.dumps(report)


def xlsx_sha() -> str:
    import hashlib

    return hashlib.sha256((ROOT / "fixtures" / "northmere_grants.xlsx").read_bytes()).hexdigest()
