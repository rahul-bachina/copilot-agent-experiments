---
name: record-lawyer-seen
description: Record that a directory lawyer has seen this contract hash and this deviations hash. Use when the lawyer has the comparison in front of them and is recording the seen step. Do not accept terms, sign, or send.
---

# Record that the lawyer has seen the comparison

This skill calls `record_lawyer_seen()` in `src/review.py`. It does not decide that a term is enforceable.

The `name` and `description` above are the skill fields. This file does not list phrases for selection, and it does not assign weights.

## When to use this skill

Use it when a directory lawyer is recording that they have seen one comparison. The item is `clause-review`, or `distress-seen`, or `grievance-seen`. A guest cannot record it. A string is not a substitute for the boolean `true`.

## Tool contract: `record_lawyer_seen`

| | |
|---|---|
| Implementation | `record_lawyer_seen()` in `src/review.py`. |
| Input | The comparison JSON, the directory JSON, and a seen object. |
| Output | The comparison with `human_approval` set only when the checks pass. |
| Side effect | None outside the returned JSON. `terms_accepted`, `signed`, and `sent` stay false. |
| Approval | This call is the approval record. It is not acceptance of terms. |

The seen object must include `approver_ref`, `item`, `decision` with the value `seen`, `contract_hash`, and `deviations_hash`. Those hashes are the ones on the comparison. A hash from another run is a mismatch.

If the playbook is stale, not yet in force, or unreadable, `playbook_seen` must be the boolean `true`. If a statute pin is unconfirmed, `pins_seen` must be the boolean `true`. `"true"` is not accepted.

Do not pass a decision of accept, reject, sign, or send.

If the cue is distress or a grievance, record that route before `clause-review`. A clause-review record does not close the route.

## Approval gates

| Act | Who |
|---|---|
| See the route | The directory lawyer |
| See this comparison | The directory lawyer, for these hashes |
| Accept, sign, or send | Not this agent |
