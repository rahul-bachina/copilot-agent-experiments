# Flow

This is the shape of the flow. It is not an exported Power Automate solution.

1. Receive the synthetic space, the request, and the as-of date.
2. Run `prepare_onboarding`. Do not read `human_approval` from the request.
3. If the outcome is not `proposal_ready`, stop and show the statement. A person can take the request outside the agent.
4. If a safeguarding cue was flagged on a proposal that is otherwise ready, wait until `safeguarding_reviewed` is true on the approval object.
5. If the export is stale, wait until `stale_seen` is true.
6. Show the proposal to the workspace owner. The owner chooses approve, defer, or refuse on a separate object.
7. For an owner proposal, the owner also sets `owner_rights_approved`. For a guest, the owner also sets `guest_access_approved`. Internal links are a separate boolean.
8. Run `apply_membership`. Show the simulated path and `live_graph_called: false`.
9. Do not add a Graph connector, a mail connector, or an external share action to this flow.

The 204 status on the Graph pages is the documented success of a live call. This flow does not receive it.
