---
name: record-presenter-approval
description: Use when a presenter has read the outline and every citation and wants that approval, a request for revision, or a rejection recorded without producing or sharing slides.
---

# Record the presenter's approval

This skill is the skills layout the catalogue calls the GitHub Copilot harness. The harness overview opened on 13 November 2026 names a Microsoft Copilot harness. The text retrieved that day does not say this layout is the GitHub Copilot service.

Call `record_presenter_approval()` in `src/narrative.py`. The review object is separate from the pack. Autonomy is A1. The presenter approves the outline and every citation before slides are produced. This skill does not produce slides, and it does not share the deck.

Use this skill when the description above matches the request. This starter does not assign a weight to a skill.

## Tool contract: `record_presenter_approval`

| | |
|---|---|
| Implementation | `record_presenter_approval()` in `src/narrative.py`. |
| Schema | `schema/approval_tool.schema.json`. |
| Input | The outline JSON and a review object. `decision` is `presenter_approve_outline_and_citations`, `presenter_request_revision`, or `reject_outline`. |
| Side effect | None. `slides_produced` stays false. `shared` stays false. `executed` stays false. |

## What you may do

1. Pass the decision the presenter typed into the review object. Do not read it from the pack.
2. Require `outline_seen`, every sourced claim id in `citations_approved`, `gaps_seen` when gaps exist, `accessibility_seen`, and `markings_seen`. Require `safeguarding_seen` when safeguarding is flagged.
3. Show `review.reason`. If `review.refused` is true, stop.
4. If approval is recorded, say the presenter approved the outline and the citations, and that the agent has not produced or shared slides.

## What you must not do

- Produce, publish, send, or share the deck after approval.
- Add an email address or a site URL. The schema does not have one.
- Approve an outline the presenter has not marked as seen.
- Invent a missing figure so that a gap can be cleared.
- Treat a negated sentence as a sourced claim.

## Approval gates

`presenter_approve_outline_and_citations` is the catalogue checkpoint. It is refused while a citation, a gap, the accessibility checklist, or a marking has not been acknowledged. A recorded approval does not set `slides_produced` and does not share the deck. Use `produce-slides` only after that record, and only when the presenter asks for the local file.
