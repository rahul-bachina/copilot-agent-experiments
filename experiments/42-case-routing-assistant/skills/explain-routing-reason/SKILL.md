---
name: explain-routing-reason
description: Use when an adviser asks why a proposal chose a queue, why the confidence band was not used, or which citation applies. Explain only fields already in the JSON.
---

# Explain a routing reason

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Use it after `propose_route` has returned. Read `reasons`, `confidence`, `rules`, `statutory_clock`, and `fairness`. The explanation does not add a queue that is not in the JSON. Do not calculate a date the JSON says was not calculated. Do not say a duty has been met.

If `confidence.band` is `not_used`, say that the band was not applied and that it cannot move the case. If a citation is marked stale, do not quote `taken`.

## Approval gates

| Act | Approval |
|---|---|
| Explain the JSON | None. |
| Change the queue while explaining | Refused. Explanation is not a reroute. |
| Edit a routing rule | Refused. The queue owner uses `refer-rule-change`. |

## Memory

Do not store the case text or the explanation as a new rule.
