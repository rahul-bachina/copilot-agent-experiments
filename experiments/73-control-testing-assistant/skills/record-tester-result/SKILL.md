---
name: record-tester-result
description: Store the named tester's own words against a staged working-paper hash. Use when that tester has already approved the hash and is recording what they decided. Do not read the words as a pass or a fail, and do not close a finding or send.
---

# Record the tester's words

This skill calls `record_tester_result()` in `src/testing.py`. It stores words. It does not interpret them.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a synthetic row already exists for this content hash and the named tester is writing their own result. The words may mention a pass, a fail, or a closure. Those words stay words.

## Tool contract: `record_tester_result`

| | |
|---|---|
| Implementation | `record_tester_result()` in `src/testing.py`. |
| Input | The staged draft, the pinned directory, and a separate object with the tester's words. |
| Output | The same hash, with `tester_words` set and `agent_interpreted_result` false. |
| Side effect | The synthetic row gains the words. `finding_closed` stays false. |
| Approval to run | Required. The tester is the author of the words. |
| Approval to rely on it | The words are the tester's. The agent does not apply them. |

`item` must be `tester-result`. `content_hash` must match the staged draft. A tampered draft is refused.

Do not decide that the control passed or failed. Do not close a finding. Do not send.
