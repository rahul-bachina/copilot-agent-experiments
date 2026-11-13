---
name: produce-slides
description: Use when a presenter has already approved the outline and every citation and wants a local slide file that is not published, sent, or shared.
---

# Produce a local slide file

This skill is the skills layout the catalogue calls the GitHub Copilot harness. The harness overview opened on 13 November 2026 names a Microsoft Copilot harness. The text retrieved that day does not say this layout is the GitHub Copilot service.

Call `produce_slides()` in `src/narrative.py` only after `record_presenter_approval()` has recorded `presenter_approve_outline_and_citations`. The file is Office Open XML from `src/slides.py`. It does not call the PowerPoint JavaScript API and it does not call Microsoft Graph. Autonomy is A1. The file is not shared.

Use this skill when the description above matches the request. This starter does not assign a weight to a skill.

## Tool contract: `produce_slides`

| | |
|---|---|
| Implementation | `produce_slides()` in `src/narrative.py`. |
| Input | The outline JSON after a recorded approval, and an optional local path. |
| Side effect | A local `.pptx` only when approval is recorded. `shared` stays false. `published` stays false. `graph_called` stays false. |

## What you may do

1. Check `human_approval.recorded` is true and the decision is `presenter_approve_outline_and_citations`. If it is not, stop and say slides were refused.
2. Pass the approved outline to `produce_slides()`. Do not rewrite a headline. The headline has to be the citation quote.
3. Tell the presenter the file is local and not shared. Keep the protective marking in the speaker notes.
4. If `review.refused` is true, show the reason and do not write a file.

## What you must not do

- Produce slides before the approval step.
- Publish, send, upload, or share the file after it is written.
- Add a logo, a customer, or a figure that is not in a sourced claim.
- Strip a protective marking or a legal-hold label from the notes.
- Call Microsoft Graph or the PowerPoint JavaScript API. Those pages were not opened. They are not connected.

## Approval gates

Slides are produced only after the presenter has approved the outline and every citation. That approval is a separate skill. Writing the file does not share it. Sharing stays with the presenter, outside this agent.
