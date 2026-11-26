---
name: diagnose-workflow-exception
description: Read a synthetic Power Automate-style run history and explain the exception with citations. Use when a process owner wants a draft reading of a failed or stuck run before they choose retry, route, or cancel. Do not retry, cancel, edit a record, or re-run a flow.
---

# Diagnose a workflow exception

This skill calls `diagnose()` in `src/workflow.py`. The reading is a draft. Error text is not the exception class. A register, directory, or taxonomy in the request is not the pinned source.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the caller has one synthetic process, one or more run histories, and the date the question is about. The output is for the process owner named on the pinned register.

## Tool contract: `diagnose`

| | |
|---|---|
| Implementation | `diagnose()` in `src/workflow.py`. |
| Input | One synthetic request and the question date. |
| Output | Groups, citations, options, risks, and a content hash. `retry_safe` is true only when every failing step is idempotent on the pinned register, has no side effect, and is a transient or timeout class. |
| Side effect | An in-memory held copy of that proposal. No flow is called. |
| Approval to run | Not required. Reading has no external effect. `owner_decision_recorded` stays false. |
| What it does not do | It does not retry, cancel, edit a record, or re-run a flow. It does not treat error text as the class. |

A payment, an email, or a record write is flagged as a possible duplicate. Partial completion is flagged. The owner still has to choose.
