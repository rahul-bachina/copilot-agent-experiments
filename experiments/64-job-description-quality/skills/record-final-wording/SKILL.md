---
name: record-final-wording
description: Store the final wording the directory recruiter wrote, bound to the hash of that exact text. Use when every suggestion has a decision and the recruiter has written the words. Do not publish, post, or send.
---

# Record the recruiter's wording

This skill calls `record_final_wording()` in `src/review.py`. The agent does not compose the advert.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when the directory recruiter has accepted or rejected every suggestion and has written the final wording themselves. A distress route cannot reach this skill. An HR route has to have been seen first.

## Tool contract: `record_final_wording`

| | |
|---|---|
| Implementation | `record_final_wording()` in `src/review.py`. |
| Input | The review JSON, the directory JSON, and one wording object. |
| Output | The review JSON with `human_approval` set, or a blocked reason and no wording stored. |
| Side effect | None. `published`, `posted`, and `sent` stay false. |
| Approval | The object is the approval. `wording_hash` has to be the SHA-256 of `wording`. `draft_hash` has to match the review. |

A stale guide, an unconfirmed pin, or a conflicting question date needs the boolean `true` on the matching seen field. The string "true" does not count.

If the draft contained a mandated statement, the wording has to still contain it. A legal hold and every retention label stay on the record even if the wording does not repeat them.

Do not publish. Do not post. Do not send. Do not score anyone. Recording the wording is not an advert.
