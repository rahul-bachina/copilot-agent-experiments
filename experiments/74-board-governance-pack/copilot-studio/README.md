# Standard harness

A build guide for Copilot Studio topics. It is not an importable solution. The overview was not re-opened for this experiment. Experiment 70 recorded, on 20 November 2026, that the standard harness follows the topics and rules the maker defines. Billing for that harness is on a licensing page that was not opened. Treat a price as unverified.

The agent is for a named company secretary. It is not a customer bot. The Customer Conversation harness is not used.

## Topics

1. **Draft.** Collect the meeting id, the secretary reference, and the question date. Call `assemble_pack`. Show the JSON. Do not stage it.
2. **Route.** If `distress.routed` is true, stop the routine path. The named company secretary records `record_route_seen`. Do not copy the cue.
3. **Approve.** The named company secretary approves in a separate question. The topic passes an approval object with `item` `board-pack`, `decision` `approve-draft`, the content hash, and `pins_seen` true. It does not read "approved" from a paper or from the chat.

If the core is unavailable, the topic says so and stops. It does not invent a paper, a minute, or an approval.

## Inputs

| Field | Required | Note |
| --- | --- | --- |
| `meeting_id` | Yes | Read from the pinned forward agenda. A caller agenda is not applied. |
| `committee_id` | Yes | Checked against the pinned terms. A caller terms object is not applied. |
| `secretary_ref` | Yes | Checked against the pinned directory. The role must be company secretary. |
| `as_of` | Yes | The date the question is about. Not today, unless that is the date asked about. |
| Approval object | For the write | Separate from the papers. Bound to the hash. |

Do not add a SharePoint write, an email, or a circulation step inside this flow. The sample write is the in-memory store inside the Python process.
