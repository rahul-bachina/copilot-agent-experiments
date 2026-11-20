# Flow

One flow calls the local briefing command and returns the JSON. A second flow, started by a person, calls `record_owner_seen` with the seen object.

Do not add an HTTP action to a regulator site. Do not add a send action. Do not write the JSON to a policy list.

The first flow has no approval action inside it. The approval is the second call, and only when the hashes match. A flow that stored "approved" because the notice said so would be a different system, and it would need a new manifest first. This starter does not include it.
