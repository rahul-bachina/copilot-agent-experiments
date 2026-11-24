# Copilot Studio standard harness

This is a build guide. It is not an importable solution. No agent is published from this folder.

The standard harness, on the page opened on 24 November 2026, follows the topics and rules the maker defines. See [../docs/harness-comparison.md](../docs/harness-comparison.md).

## Topics

1. **Draft the package.** The topic collects the application id, the applicant reference, the brief id, and the question date. It calls `prepare_application()` and shows the JSON. It stops. It does not submit.
2. **See the route.** If the outcome is `route_to_human`, a later topic calls `record_route_seen` with a separate seen object. The cue text is not shown back if it was withheld.
3. **Approve the hash.** A later topic calls `record_applicant_approval` only when the applicant supplies the approval object. The topic does not copy an "approved" sentence out of the cover note into that object.

The system prompt is [system-prompt.md](system-prompt.md). The flow note is [power-automate-flow.md](power-automate-flow.md).

A person can always stop and read the JSON themselves. The agent does not close that path.
