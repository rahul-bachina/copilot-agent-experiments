# Copilot Studio standard harness

The maker defines three topics. Each topic calls the Python core. None of them sends.

1. **Propose.** Input is the synthetic request and `as_of`. Output is the proposal JSON. The topic stops. It does not look for the word approved in the note.
2. **Approve one change.** Input is the proposal and a separate approval object from the compliance owner. The topic calls `stage_approved_change`. A mismatch returns `blocked_reason` and writes nothing.
3. **Route seen.** Input is a route result and a separate seen object. The topic calls `record_route_seen`. It does not stage.

Power Automate, in `power-automate-flow.md`, is a note of that sequence. It is not an importable solution. No Dataverse environment is connected. The table design is `docs/dataverse.md`.

The system prompt in `system-prompt.md` tells the topic not to decide applicability, not to assign accountability, and not to send.
