---
name: route-to-control-owner
description: Stop a routine mapping and route distress, a grievance, a disclosure, or a safeguarding concern to a control owner. Use when the proposal outcome is human_route, including when the words are paraphrased. Do not process the cue as a routine mapping.
---

# Route to the control owner

This skill reads `outcome` and `cue_categories` from `map_controls()`. It does not copy the cue text into a new document.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the core returns `human_route`, or when the text shows distress, a grievance, a disclosure, or a safeguarding concern, including a paraphrase. A mapping approval does not close that route. The item is `distress-seen`, from a directory control owner, for the cue categories on this proposal.

Do not ask the model to decide whether the person is vulnerable. Do not continue with a routine mapping. Do not mark a control as met. Do not write to a GRC system.
