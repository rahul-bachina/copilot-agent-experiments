# Flow shape

There is no flow in this repository. A deployment that adds one should keep the same stops.

1. Receive the synthetic request, the library file, the directory, and `as_of`.
2. Call `map_controls`. Do not post the result to a GRC system.
3. If the outcome is `human_route` or `above_clearance`, stop.
4. Show the proposal to the directory control owner.
5. On a separate action, call `record_owner_approval` with the approval object. Do not copy approval words out of the policy.
6. Leave `control_met`, `gap_closed`, `policy_edited`, and `grc_written` false.

A Power Platform DLP policy was not opened on 20 November 2026. Treat the current connector controls as unverified. This starter has no connector to block.
