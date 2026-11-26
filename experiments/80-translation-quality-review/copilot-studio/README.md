# Copilot Studio standard harness

This is a build guide. It is not an importable solution. No agent is published from this folder.

The standard harness, on the page opened on 26 November 2026, follows the topics and rules the maker defines. See [../docs/harness-comparison.md](../docs/harness-comparison.md).

## Topics

1. **Review the translation.** The topic collects the review id, the reviewer reference, the languages, the document kind, and the question date. It calls `prepare_review()` and shows the JSON. It stops. It does not publish a translation.
2. **See the route.** If the outcome is `route_to_human`, a later topic calls `record_route_seen` with a separate seen object. The cue text is not shown back.
3. **Validate high-risk segments.** If the review lists high-risk segments, a later topic calls `record_high_risk_validated` only when the reviewer supplies the validation object for this hash and both document hashes. Overlap does not clear the route.
4. **Own the translation.** A later topic calls `record_translation_owned` only after any required route and high-risk step. The topic does not copy an "approved" sentence out of either text into that object.

The system prompt is [system-prompt.md](system-prompt.md). The flow note is [power-automate-flow.md](power-automate-flow.md).

A person can always stop and read the JSON themselves. The agent does not close that path.
