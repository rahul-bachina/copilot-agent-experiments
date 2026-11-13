---
name: explain-a-ranked-hit
description: Use when the requesting user asks why a file in an existing find result ranked where it did, or whether it is stale, superseded, or a likely duplicate.
---

# Explain a ranked hit

This skill is for the Copilot Studio harness that the overview opened on 13 November 2026 calls the Microsoft Copilot harness. It is not a second search.

Use this skill when a find result is already in the conversation and the user asks about one rank. Read that JSON. Do not open a location that was not confirmed. Do not invent a reason that is not on the hit.

This starter does not assign a weight to a skill.

## Tool contract

There is no extra tool. The explanation is the `reasons` array, the `score`, and the flags already on the hit.

## What you may do

1. Point at the rank, the matched terms, and the flags.
2. Say the 365-day window is configuration, not a statutory period.
3. Say a later version that is not in the view was not named.

## What you must not do

- Add a file that is not in `matches`.
- Quote a snippet that the JSON left null.
- Suggest moving, deleting, sharing, or changing permissions.

## Approval gates

Explaining a hit does not set `human_approval`. A file change is not available from this skill.
