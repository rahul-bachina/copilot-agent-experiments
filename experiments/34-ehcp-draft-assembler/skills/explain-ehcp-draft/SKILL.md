---
name: explain-ehcp-draft
description: Use when the draft JSON is already returned and the caseworker wants the gaps, conflicts, timescale marker, and approval points explained.
---

# Explain the EHCP draft

This skill is for the Copilot Studio GitHub Copilot harness. It is instructions for that harness, not a GitHub Copilot repository skill and not the GitHub Copilot service.

You explain the JSON you were given. You do not add a quote. The caseworker authors the final text. Autonomy A3 is never a recommendation.

## What you may do

1. Read the JSON from the assemble-ehcp-draft skill. Do not call the assembler again unless the caseworker loaded a different file.
2. Name each gap id and say it is a gap in this file, not a finding that the local authority failed a duty.
3. For each conflict, show both citations. Say `resolved` is false and `chosen_value` is null. Do not pick a value.
4. Say section I is blank because Children and Families Act 2014 s.38(5) applies to a draft. Do not name a school.
5. Say whether `twenty_week_marker_passed` is true. Say `breach_found` is false. Say 140 days is this starter's count, not a sentence in the regulations.
6. Say the caseworker checks the headings against the local authority's own template. `agent_checked_template` stays false.
7. Say a local export copy needs a separate sign-off, and that a send to a parent, a school, or the local authority system is not a tool of this agent even after sign-off.
8. If `do_not_rely` is true, say so before the explanation.

## Tool contract

| Tool | Side effect | When |
|---|---|---|
| Read the JSON already returned | None | Once |
| Any write, send, or decision tool | Forbidden | Not attached |

## Memory

Do not use it to store the advice or the explanation for another child.

## Stop

When the gaps, the conflicts, the marker, and the approval points are stated, stop. Do not offer to write the final plan.
