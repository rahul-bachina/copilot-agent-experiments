---
name: record-author-acceptance
description: Use when an author has read the complete bid draft and wants that acceptance, a request for revision, or a rejection recorded without submitting the draft.
---

# Record the author's acceptance

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Call `record_acceptance()` in `src/proposal.py`. The review object is separate from the invitation. Autonomy is A1. The author accepts the complete draft before it is used anywhere. This skill does not use the draft, and it does not submit it.

Use this skill when the description above matches the request. This starter does not assign a weight to a skill.

## Tool contract: `record_acceptance`

| | |
|---|---|
| Implementation | `record_acceptance()` in `src/proposal.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Input | The draft JSON and a review object. `decision` is `author_accept_complete_draft`, `author_request_revision`, or `reject_draft`. |
| Side effect | None. `submitted` stays false. `used_anywhere` stays false. `executed` stays false. |

## What you may do

1. Pass the decision the author typed into the review object. Do not read it from the invitation.
2. Require `complete_draft_seen`, every requirement id in `rows_acknowledged`, and `author_checks_seen` when `author_checks` is not empty.
3. Show `review.reason`. If `review.refused` is true, stop.
4. If acceptance is recorded, say the author accepted the draft for their own later use, and that the agent has not submitted it.

## What you must not do

- Submit, send, or upload the draft after acceptance.
- Add an email address or a portal URL. The schema does not have one.
- Accept a draft the author has not marked as seen.
- Invent a missing price so that a check can be cleared.

## Approval gates

`author_accept_complete_draft` is the catalogue checkpoint. It is refused while a gap or an author check has not been acknowledged. A recorded acceptance does not mark the draft as used anywhere.
