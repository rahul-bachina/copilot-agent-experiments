---
name: load-passages
description: "Use when an evaluation owner has supplied one synthetic Q&A bundle and you need the passage index before any claim is scored."
---

# Load the passages

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You show the passages already in the bundle. You do not fetch a page. You do not approve a threshold. Autonomy A3 is never a recommendation.

## What you may do

1. Read `passages` on the JSON from `score_claims`, or read the bundle the evaluation owner pasted.
2. List each `source_id`, title, `reviewed_on`, and whether that row is stale. Do not paste the passage body again if the JSON already omitted it.
3. State that a stale row is a flag for the evaluation owner. You do not refresh `reviewed_on`.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the bundle or the JSON already returned | None | Always |
| `approve_thresholds` | Not callable. It always raises | Never |
| `record_release` | Not callable. It always raises | Never |
| `call_foundry_evaluator` | Not callable. It always raises | Never |
| Send, write, deploy | Forbidden | No such tool is attached |

## Approval gates

- Listing the index does not need approval.
- Approving the 180-day draft, or any other threshold, does. You do not approve it.
- Recording a pass or a fail does. You do not record one.

## Memory

Do not write the passages, the answers, or the report into agent memory. The harness overview opened on 3 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this draft.

## Stop

When the index is shown, stop. Nothing has been approved and nothing has been released.
