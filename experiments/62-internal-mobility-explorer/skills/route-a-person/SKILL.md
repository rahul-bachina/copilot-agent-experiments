---
name: route-a-person
description: Record that directory HR has seen a route for an adjustment, redeployment, distress, or grievance signal. Use when the exploration outcome is a human route. Do not turn the route into an application.
---

# Route a person

This skill calls `record_route_seen()` in `src/explore.py` only when the outcome is already a human route. It does not produce a vacancy list.

The `name` and `description` above are one line each. This file does not assign weights.

## When to use this skill

Use it when the outcome is `wellbeing_route`, `grievance_route`, `redeployment_route`, or `adjustment_route`. Do not use it to continue an application. Do not repeat the cue.

## Tool contract: `record_route_seen`

| | |
|---|---|
| Implementation | `record_route_seen()` in `src/explore.py`. |
| Input | The note JSON, a separate review object, and the directory JSON. |
| Review fields | `approver_ref` for a directory HR reviewer, `decision` = `seen`, `item` = `human-route`, `exploration_id`, `content_hash`. |
| Output | `route_seen.recorded` true only when the hash matches. The outcome stays the route. |
| Side effect | None. `adjustment_decided` stays false. The manager is not told. |

A manager or a recruiter cannot record the route. Recording it does not share the employee's interest.

## What to show

Name the route from `human_route.named`. Do not copy the cue. Say the case has not been decided and that this is not a selection decision.

## Approval gates

| Act | Who |
|---|---|
| See the route | Directory HR reviewer, for this exploration id and this content hash |
| Decide an adjustment, a grievance, or redeployment | HR, outside this function |
| Apply or contact anyone | Not this agent |
