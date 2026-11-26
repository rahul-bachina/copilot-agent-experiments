# Copilot Studio standard harness

This is a build guide. It is not an importable solution. No agent is published from this folder.

The standard harness, on the page opened on 26 November 2026, follows the topics and rules the maker defines. See [../docs/harness-comparison.md](../docs/harness-comparison.md).

## Topics

1. **Read the runs.** The topic collects the diagnosis id, the process id, and the question date. It calls `diagnose()` and shows the JSON. It stops. It does not retry a flow.
2. **See the route.** If the outcome is `route_to_human`, a later topic calls `record_route_seen` with a separate seen object. The cue text is not shown back.
3. **Choose the action.** A later topic calls `record_owner_decision` only when the owner supplies the decision object for this hash. The topic does not copy an "approved" sentence out of the payload into that object. The recorded choice does not call Power Automate.

The system prompt is [system-prompt.md](system-prompt.md). The flow note is [power-automate-flow.md](power-automate-flow.md).

A person can always stop and read the JSON themselves. The agent does not close that path.
