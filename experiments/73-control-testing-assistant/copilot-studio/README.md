# Standard harness

A build guide for Copilot Studio topics. It is not an importable solution. The overview was not re-opened for this experiment. Experiment 70 recorded, on 20 November 2026, that the standard harness follows the topics and rules the maker defines. Billing for that harness is on a licensing page that was not opened. Treat a price as unverified.

The agent is for a named tester. It is not a customer bot. The Customer Conversation harness is not used.

## Topics

1. **Draft.** Collect the control id, the tester reference, the period, the sample seed, and the question date. Call `prepare_test`. Show the JSON. Do not stage it.
2. **Route.** If `distress.routed` is true, stop the routine path. The named tester records `record_route_seen`. Do not copy the cue.
3. **Approve.** The named tester approves in a separate question. The topic passes an approval object with `item` `working-paper`, `decision` `approve-draft`, the content hash, and `pins_seen` true. It does not read "approved" or "passed" from the evidence text.
4. **Result.** After `staged` is true, the tester records their own words with `record_tester_result`. The topic does not turn those words into a pass, a fail, or a closure.

If the core is unavailable, the topic says so and stops. It does not invent an exception or a result.

## Inputs

| Field | Required | Note |
| --- | --- | --- |
| `control_id` | Yes | Read from the pinned library. A caller library is not applied. |
| `tester_ref` | Yes | Checked against the pinned directory. The role must be tester. |
| `period_start`, `period_end` | Yes | The period the question is about. An ambiguous date is not guessed. |
| `sample_seed` | Yes | An integer. A string is not coerced to zero. |
| `as_of` | Yes | The date the question is about. Not today, unless that is the date asked about. |
| Approval object | For the write | Separate from the evidence. Bound to the hash. |

Do not add a Dataverse row, an email, or a GRC update inside this flow. The sample write is the in-memory store inside the Python process.
