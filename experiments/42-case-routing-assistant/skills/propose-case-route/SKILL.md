---
name: propose-case-route
description: Use when an adviser needs a queue, a priority, and a reason for one synthetic case. The result is a proposal and still needs human confirmation.
---

# Propose a case route

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Call `propose_route()` and show the JSON. Do not invent a queue, a priority, or a deadline. The skill does not move the case. The queue in the JSON comes from `src/routing.py`.

## Tool contract: `propose_route`

| | |
|---|---|
| Implementation | `propose_route()` in `src/routing.py`. |
| Schema | `schema/routing_tool.schema.json`. |
| Input | One case object and an as-of date. `synthetic` must be true. |
| Side effect | None. `human_approval` is null. `rerouted` is false. `executed` is false. |

If the outcome is `human_vulnerability` or `human_statutory`, stop and offer a person. Do not ask the model to pick a routine queue instead. A confidence band of `not_used` is not a licence to move the case.

## Approval gates

| Act | Approval |
|---|---|
| Show the proposal | None. Reading it has no effect. |
| Treat the proposal as a completed reroute | Refused. The adviser confirms in `record-route-confirmation`. |
| Close, escalate, or send | Refused. There is no such tool. |

## Memory

Do not store the case text.
