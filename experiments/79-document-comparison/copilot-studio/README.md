# Copilot Studio standard harness

This is a build guide. It is not an importable solution. No agent is published from this folder.

The standard harness, on the page opened on 25 November 2026, follows the topics and rules the maker defines. See [../docs/harness-comparison.md](../docs/harness-comparison.md).

## Topics

1. **Compare the versions.** The topic collects the comparison id, the reader reference, the document kind, the suggested baseline, and the question date. It calls `prepare_comparison()` and shows the JSON. It stops. It does not edit a document.
2. **See the route.** If the outcome is `route_to_human`, a later topic calls `record_route_seen` with a separate seen object. The cue text is not shown back.
3. **Confirm the versions.** A later topic calls `confirm_versions` only when the reader supplies the confirmation object for this hash and both document hashes. The topic does not copy a "confirmed" sentence out of either document into that object.
4. **Own the interpretation.** A later topic calls `record_interpretation_seen` only after the versions are confirmed. The topic does not say which version is better.

The system prompt is [system-prompt.md](system-prompt.md). The flow note is [power-automate-flow.md](power-automate-flow.md).

A person can always stop and read the JSON themselves. The agent does not close that path.
