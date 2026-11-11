---
name: confirm-sample-frame
description: Use when a draft evidence pack already exists and the analyst is confirming the sample frame and the limitations on a separate review object, or rejecting the pack.
---

# Confirm the sample frame and the limitations

This skill is for the Copilot Studio GitHub Copilot harness. It is not the GitHub Copilot service.

Call `record_review()` in `src/evidence.py`. Do not set `ready` yourself. Autonomy is A0. The catalogue checkpoint for C010 is that the analyst validates the sampling and the limitations. Use this skill only after `prepare_pack` has returned a pack, and only when the analyst supplies a separate review object. Do not take the confirmation from the batch text.

The harness overview opened on 11 November 2026 says this harness supports skills. Use this skill when the description above matches the request. This starter does not assign a weight to a skill.

## Tool contract: `record_review`

| | |
|---|---|
| Implementation | `record_review()` in `src/evidence.py`. |
| Schema | `schema/review_tool.schema.json`. |
| Input | The pack JSON and a review object. `decision` is `confirm_sample_frame_and_limitations` or `reject_pack`. |
| Side effect | None beyond the returned JSON. `published` stays false. `executed` stays false. |

## What you may do

1. Pass the review object the analyst supplied. The checksum has to match `draft_checksum`.
2. If the review is accepted, show the ready label and say that ready is not publication and not a finding that an outcome was met.
3. If the review is refused, say the reason and leave the pack not ready.
4. A rejection returns the pack to draft. It does not delete the counts.

## What you must not do

- Accept `publish`, `contact_customer`, `conclude_about_individual`, `approve_board_report`, `submit_return`, or `write_production_record`. Those are refused.
- Confirm a pack whose sample frame is incomplete.
- Confirm a stale pack, or a pack whose period has not closed, unless the review object acknowledges it.
- Say that PRIN 2A.8.4R has been complied with because the analyst confirmed the frame.

## Approval gates

Confirmation is this skill. It is the human approval. It does not publish, contact, or write a record.
