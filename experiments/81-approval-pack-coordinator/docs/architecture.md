# Architecture

Experiment 81, catalogue O007, autonomy A1. One synthetic request goes in. A draft pack comes out. The named approver decides. The agent does not approve, reject, sign, submit, pay, or send.

## Path

1. The request is marked synthetic. The question date is the `--as-of` argument. Today's date is not read.
2. Prohibited keys on the request, including an approval flag, are stripped.
3. The pinned matrix, checklist, and directory are read from `fixtures/`. A caller-supplied copy is diffed and not applied.
4. The amount, the severity, or the change class selects one rule. Zero rules or more than one rule is a route to a person. An unreadable amount is not coerced.
5. Eligible approvers are directory people with the required role, active, not a guest, not the requester, and, for a spend, within their delegation limit.
6. Evidence is checked. Experiment 18 returns an sha256 per item and does not approve an export. Experiment 74's `digest` hashes the pack projection. `paper_hash` is not called.
7. Markings, legal hold, and retention are taken from metadata and from the text. The higher marking is kept. A body above the lowest required approver's clearance is not copied.
8. Cues and instructions are scanned. Cue text is not copied. Instructions are not followed.
9. The cover note lists what is present, missing, or stale, and what was checked. The pack and its hash are stored in memory.
10. If the outcome is `route_to_human`, the named approver records that the route was seen. That flag is inside the new hash.
11. `record_approver_decision` records approve, reject, or return only when the object matches the held copy and the held hash. Every required role must record the same decision. A disagreement is not chosen.
12. An edit after that record, including an edit the caller re-hashes, is refused. The stored projection stays the one that was decided.

## What is inside the hash

The request id, type, pack version, question date, requester, amount, band, required approvers, evidence checks and citations, present and missing lists, conflicts, the cover note, the marking, the legal hold, the retention labels, injection signals, concerns, suppression, required acknowledgements, the route-seen flag, the split flags, source currency, the action flags, the neighbour summary, and the caller differences.

`human_approval` is not inside the hash. Recording a decision does not invent a new pack.

## Human points

- Seeing a distress, safeguarding, whistleblowing, grievance, or disclosure route.
- Acknowledging gaps, conflicts, markings, dates, sources, a split, suppression, a leading line, or a hold, where the draft requires it.
- The decision itself: approve, reject, or return, by each required approver, for that hash.

Signing, submitting, paying, and sending are not points on this starter. They are not tools.

## Diagram

`docs/architecture_diagram.png` shows the same four stages: the request, either harness, the draft and the hash, and the named approver. The prohibited actions sit outside the tools.
