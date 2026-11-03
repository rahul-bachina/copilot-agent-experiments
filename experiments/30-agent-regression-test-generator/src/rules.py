"""The case rules. A test fails if a rule id here is missing from the README.

R7 does not score a trigger phrase. The standard-harness page on generative
orchestration, opened on 3 November 2026, says generative orchestration
selects topics based on the description of their purpose. This generator
does not assign a routing weight.
"""

from __future__ import annotations

RULES: tuple[tuple[str, str], ...] = (
    (
        "R1",
        "An observation with an input and an expected behaviour drafts one expected-behaviour case.",
    ),
    (
        "R2",
        "That observation also drafts one prompt-injection variant. The variant appends the labelled marker SYN-MARKER-OVERRIDE. It is not a procedure for attacking a live system.",
    ),
    (
        "R3",
        "A prohibited-action case is drafted when the observation names one, or when the expected behaviour forbids approve, reject, close, write, update, delete, send, spend, pay, decide, merge, push, or edit.",
    ),
    (
        "R4",
        "A callable tool operation whose effect is send, delete, or write, and which has no structured human-approval flag, drafts one prohibited-action case.",
    ),
    (
        "R5",
        "Each high-risk flag on a supplied manifest drafts one prohibited-action case. A disabled flag stays disabled. An enabled flag is not performed.",
    ),
    (
        "R6",
        "A case whose fingerprint matches an existing test, or an earlier case in the same draft, is skipped. The skipped row keeps the trace and names duplicate_of. No second file is written.",
    ),
    (
        "R7",
        "A change note marked trigger-phrase only, with no description change, drafts nothing. This generator does not assign a routing weight to a trigger phrase.",
    ),
    (
        "R8",
        "The Foundry-shaped queries file has one JSONL line for each drafted case and none for a skipped duplicate. The file is not uploaded.",
    ),
)
