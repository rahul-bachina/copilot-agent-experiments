---
name: explain-cost-report
description: Use when the cost report JSON already exists and the FinOps owner wants the assumptions, approval points, and flags explained.
---

# Explain the cost report

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

Use only the JSON the report-agent-cost skill already returned. Do not add a citation, a price, or a recommendation to buy credits. Do not change a quota. Autonomy A3 is never a recommendation.

## What you may do

1. List the assumption ids already in the JSON, in particular B1, B3, B6, and B8. Do not soften B1. The standard-harness double-count guard is this starter's rule.
2. Say the forecast is not a statistical interval and not a Microsoft estimate, using the flags already on `forecast`.
3. List the human approval points: the FinOps owner validates the rates, the FinOps owner validates the forecast, a stale card or a stale page is re-opened before anyone relies on it, and a quota, budget, or subscription change happens outside this agent.
4. Keep every control flag false. If `a3_recommended` is true, stop and do not show the draft.
5. Stop. Do not offer to apply the report to a subscription.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the JSON already returned | None | Once |
| Web search | Forbidden | Do not refresh a citation |
| Validate, change a quota, change a budget, change a subscription, send, spend | Forbidden | No such tool is attached |

## Approval gates

- Explaining the JSON does not need approval.
- Relying on a figure does. The FinOps owner validates rates and the forecast.
- You do not record either validation.

## Memory

The harness overview says this harness supports memory. An administrator control to turn it off was not found on the page opened on 3 November 2026. Do not use it for the report.

## Stop

When the assumptions and the approval points have been shown, stop. Nothing has been validated and nothing has been changed.
