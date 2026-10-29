"""Synthetic chain tokens only.

A live-looking address or hash is omitted. The raw value is not returned.
"""

from __future__ import annotations

import re

SYNTH_ADDR = re.compile(r"^SYNTH-ADDR-[A-Z0-9-]{4,48}$")
SYNTH_TX = re.compile(r"^SYNTH-TX-[A-Z0-9-]{4,48}$")

# Shapes this starter will not copy, even inside a case marked synthetic.
_REALISH = re.compile(
    r"^(?:0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{11,}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[a-km-zA-HJ-NP-Z1-9]{33})$"
)


def classify_token(value: str, kind: str) -> str:
    """Return synthetic, omitted, or empty. Never return the raw value."""

    if not isinstance(value, str):
        return "omitted"
    token = value.strip()
    if not token:
        return "empty"
    if _REALISH.match(token):
        return "omitted"
    if kind == "address" and SYNTH_ADDR.match(token):
        return "synthetic"
    if kind == "tx" and SYNTH_TX.match(token):
        return "synthetic"
    return "omitted"


def accept_token(value, kind: str) -> str | None:
    """Return the token when it is a synthetic id. Otherwise None."""

    if classify_token(value if isinstance(value, str) else "", kind) != "synthetic":
        return None
    return value.strip()
