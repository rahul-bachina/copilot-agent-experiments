"""OWASP Top 10 for LLM Applications, 2025 titles.

Titles are the listing headings on https://genai.owasp.org/llm-top-10/
as fetched on 2 November 2026. The vulnerability essays were not opened.
Short text under each heading was truncated in that fetch and is not stored.
Do not add a title that was not on the listing.
"""

from __future__ import annotations

OWASP_LISTING_URL = "https://genai.owasp.org/llm-top-10/"
OWASP_VERIFIED_ON = "2026-11-02"

# Order and spelling follow the listing headings. The year suffix is part of the heading.
OWASP_2025: tuple[dict[str, str], ...] = (
    {"id": "LLM01:2025", "name": "Prompt Injection"},
    {"id": "LLM02:2025", "name": "Sensitive Information Disclosure"},
    {"id": "LLM03:2025", "name": "Supply Chain"},
    {"id": "LLM04:2025", "name": "Data and Model Poisoning"},
    {"id": "LLM05:2025", "name": "Improper Output Handling"},
    {"id": "LLM06:2025", "name": "Excessive Agency"},
    {"id": "LLM07:2025", "name": "System Prompt Leakage"},
    {"id": "LLM08:2025", "name": "Vector and Embedding Weaknesses"},
    {"id": "LLM09:2025", "name": "Misinformation"},
    {"id": "LLM10:2025", "name": "Unbounded Consumption"},
)

# This starter's reading of which suite class sits under which title.
# It is not an OWASP endorsement. Categories absent from this map are not exercised.
CLASS_TO_OWASP: dict[str, str] = {
    "instruction_override": "LLM01:2025",
    "encoding": "LLM01:2025",
    "data_exfiltration": "LLM02:2025",
    "tool_misuse": "LLM06:2025",
    "prohibited_action": "LLM06:2025",
    "system_prompt_disclosure": "LLM07:2025",
}

NOT_EXERCISED_NOTE = (
    "This suite version does not exercise this category. "
    "Absence of a finding is not a pass."
)


def by_id() -> dict[str, str]:
    return {row["id"]: row["name"] for row in OWASP_2025}


def title(owasp_id: str) -> str:
    names = by_id()
    if owasp_id not in names:
        raise KeyError(owasp_id)
    return f"{owasp_id} {names[owasp_id]}"
