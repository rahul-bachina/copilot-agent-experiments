# Standard harness

This is a build guide for the Copilot Studio standard harness. It is not an importable solution. The overview opened on 20 November 2026 describes this harness as following the topics and rules the maker defines.

## Topics

1. **Propose mappings.** The caller gives the policy set, their directory reference, and the date the question is about. The topic calls `map_controls()` and shows the JSON. It stops.
2. **Route.** If `outcome` is `human_route`, the topic does not continue into a routine proposal. The control owner records `distress-seen` in the next topic.
3. **Approve one item.** A separate topic calls `record_owner_approval()` with an object the owner submits. The object names the item, the content hash, and the proposal hash. Words copied out of a policy are not that object.

No connector writes to a GRC system. No connector edits a policy. No SharePoint connector is added in this guide. Microsoft 365 is the catalogue context for where policies would live. This starter reads the JSON the caller passes.

A maker who adds a connector that can edit or write has left this starter. The manifest's kill switch is to turn the agent off.
