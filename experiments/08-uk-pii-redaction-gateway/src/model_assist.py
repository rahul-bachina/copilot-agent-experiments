"""Optional model assistance. The default adapter finds nothing.

A suggestion is not a deterministic hit. The gateway will not apply it
unless the caller opts in, and a suggestion cannot cancel a checksum hit
or release the text. No adapter in this file calls a network.
"""

from __future__ import annotations


class NullModel:
    """Used when the caller does not pass an adapter."""

    name = "off"

    def suggest(self, text: str) -> list[dict]:
        return []


class MockModel:
    """Smoke-test stand-in. It returns only the spans it was given.

    It is not a model, and it is not a measure of model accuracy.
    """

    name = "mock"

    def __init__(self, spans: list[dict] | None = None) -> None:
        self.spans = list(spans or [])

    def suggest(self, text: str) -> list[dict]:
        return list(self.spans)
