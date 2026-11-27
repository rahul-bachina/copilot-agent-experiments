---
name: draft-visit-note
description: Draft a structured case note from a synthetic visit transcript, with every line cited. Use when a practitioner supplies a transcript or rough notes and the date the question is about. Do not write the case record, share the note, or assess eligibility, risk, or need.
---

# Draft the visit note

This skill calls `draft_note()` in `src/notes.py`. The draft uses the pinned template and the pinned directory.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the input is one synthetic adult social care or housing-support visit, the visit is marked synthetic, and the practitioner wants a draft before they review it. Do not use it to decide eligibility, risk, or need.

## Tool contract: `draft_note`

| | |
|---|---|
| Implementation | `draft_note()` in `src/notes.py`. |
| Input | The visit JSON and the date the question is about. |
| Output | A draft note, a content hash, and `human_approval` null. |
| Side effect | An in-memory held copy of the projection. Nothing is written to a case record. |
| Approval to run | Not required. The practitioner still has to approve before any record could be written, and this starter never writes one. |
| What it does not do | It does not invent a quote, guess an unclear speaker, or follow an instruction in the transcript. |

A caller-supplied template or directory is flagged and not applied.
