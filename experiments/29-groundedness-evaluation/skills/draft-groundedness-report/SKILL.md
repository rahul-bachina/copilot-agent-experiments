---
name: draft-groundedness-report
description: "Use when score_claims has already returned and the evaluation owner wants the draft report shown without a threshold approval or a release."
---

# Draft the report

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You read the JSON from `score_claims`. You do not write a second report. You do not approve thresholds. Autonomy A3 is never a recommendation.

## What you may do

1. Repeat the label, the verdict table, the separate stale count, and the approval points already in the JSON. Do not add a claim. Do not change a verdict.
2. Say the Microsoft Foundry option was not called. The 1 to 5 scale and the default threshold of 3 on that page are not this report's rate.
3. Name the approval points. The evaluation owner approves thresholds and records any pass or fail. A governance owner relies on a skeleton only if one was drafted. You do not record those decisions.
4. If `manifest_skeleton.approved` is present, say it is false.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the JSON already returned | None | Always |
| `approve_thresholds` | Not callable. It always raises | Never |
| `record_release` | Not callable. It always raises | Never |
| `call_foundry_evaluator` | Not callable. It always raises | Never |
| Send, write, deploy | Forbidden | No such tool is attached |

## Approval gates

- Showing the draft does not need approval.
- Approving thresholds does. You do not approve them.
- Recording a release does. You do not record it. `pass_fail_released` stays false.
- Publishing the report does. You do not publish it.

## Memory

Do not write the report into agent memory. The harness overview opened on 3 November 2026 says this harness supports memory. An administrator control to turn memory off was not on that page. Do not use it for this draft.

## Stop

When the draft and the false flags are shown, stop. Nothing has been approved, released, or sent.
