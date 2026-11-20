---
name: route-to-compliance-owner
description: Stop a routine briefing when the notice shows distress, a grievance, or a disclosure. Use when draft_briefing returns human_route. Do not copy the cue text, decide applicability, or send.
---

# Route to the compliance owner

This skill reads `cue` on the briefing JSON. It does not re-detect the cue and it does not copy the cue sentence.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the outcome is `human_route`, or when `cue.distress` or `cue.grievance` is true. A paraphrase that the core flagged is still this route. Do not treat it as a routine briefing.

## What to show

Say that a person must see the route. Do not quote the cue. Do not decide that the change applies. Do not change a policy. Do not send.

The seen item for this route is `distress-seen` or `grievance-seen`, from a directory compliance owner. A later `briefing` seen step does not replace it.

If the core did not flag a cue, do not invent one.
