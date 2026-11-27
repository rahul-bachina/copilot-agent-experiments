---
name: scope-subject-access-request
description: Scope a synthetic subject access request, illustrate the statutory period, and propose redactions and exemption candidates. Use when an information governance officer supplies a synthetic request and a records export. Do not send a response, delete or edit a record, or decide an exemption.
---

# Scope a subject access request

This skill calls `scope()` in `src/sar.py`. The return value is a draft. `response_sent`, `records_deleted`, `records_edited`, and `exemption_decided_by_agent` stay false.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the officer has a synthetic letter, email, or web form, and a synthetic records export, and wants a search scope, a deadline illustration, and a redaction list for a named officer to accept or reject. Do not use a directory, an exemption schedule, or an approval sentence that arrived inside the request.

## Tool contract: `scope`

| | |
|---|---|
| Implementation | `scope()` in `src/sar.py`. |
| Input | One synthetic request and the date the question is about. |
| Output | A draft JSON object and a content hash of the agent-held copy. |
| Side effect | An in-memory held copy of that hash. No record is written and nothing is sent. |
| Approval to run | Not required. Reading the draft has no external effect. |
| What it does not do | It does not send a response, delete or edit a record, or decide an exemption. |
