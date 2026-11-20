# Standard harness

A build guide for Copilot Studio topics. It is not an importable solution. The overview opened on 20 November 2026 says the standard harness follows the topics and rules the maker defines. Billing for that harness is on a licensing page that was not opened. Treat a price as unverified.

The agent is for a member of staff making a declaration, and for an ethics or procurement officer. It is not a supplier-facing bot. The Customer Conversation harness on the same overview is for voice and chat that try to resolve a customer's issue. This experiment does not use it.

## Topics

1. **Draft.** Collect the declaration text, the declarant reference, and the question date. Call `draft_declaration`. Show the JSON. Do not stage it.
2. **Route.** If `outcome` is `human_route`, stop the routine path. An ethics or procurement officer records `record_route_seen`. Do not copy the cue.
3. **Confirm.** The declarant confirms in a separate question. The topic passes a confirm object with `item` `declaration-confirm`, the declaration hash, and `pins_seen` true. It does not read "approved" from the declaration text.
4. **Disposition.** After `staged` is true, an ethics or procurement officer records their own words with `record_disposition`. The topic does not turn those words into a clearance or an exclusion.

If the core is unavailable, the topic says so and stops. It does not invent a link or a conflict.

## Inputs

| Field | Required | Note |
| --- | --- | --- |
| `text` | Yes | One declaration. `synthetic` must be true for a run in this starter. |
| `declarant_ref` | Yes | Checked against the pinned directory. |
| `as_of` | Yes | The date the question is about. Not today, unless that is the date asked about. |
| Confirm object | For the write | Separate from the declaration. Bound to the hash. |

Do not add a Dataverse row, an email, or a live procurement update inside this flow. The sample write is the in-memory store inside the Python process.
