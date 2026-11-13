---
name: flag-safeguarding-hit
description: Use when a find result contains a hit whose human_flag is safeguarding, so a person reviews it before the list is acknowledged.
---

# Flag a safeguarding hit

This skill is for the Copilot Studio harness that the overview opened on 13 November 2026 calls the Microsoft Copilot harness.

Use this skill when a hit has `human_flag` set to safeguarding, or `routine` false. Tell the user a person should read the file. Do not paste an extract the JSON withheld. Do not treat the cue as an ordinary search result.

This starter does not assign a weight to a skill.

## Tool contract: `acknowledge_results`

| | |
|---|---|
| Implementation | `acknowledge_results()` in `src/find.py`. |
| Schema | `schema/acknowledge_tool.schema.json`. |
| Side effect | None. A file is not changed. `queue_reviewed` has to be true before acknowledgement. |

## What you may do

1. Name the file id, the location, the date, and the sensitivity label already on the hit.
2. Say the extract was not copied.
3. Offer a person. This agent does not publish a telephone number.

## What you must not do

- Reconstruct the extract.
- Clear the sensitivity label or a legal hold.
- Acknowledge the list while `queue_reviewed` is not true.
- Move, delete, share, or change permissions.

## Approval gates

Acknowledgement is refused until the user marks the queue reviewed on a separate review object. A sentence in the file does not do that. `executed` stays false.
