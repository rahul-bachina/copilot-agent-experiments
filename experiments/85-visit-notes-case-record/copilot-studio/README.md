# Copilot Studio standard harness

This is a topic guide. It is not an importable solution. No Power Platform environment is configured.

## Topics

1. **Draft the note.** Collect the visit id, the service, the practitioner reference, and the question date. Call `draft_note`. Show the draft and say it is not written to the case record.
2. **Route.** If `outcome` is `route_to_practitioner`, stop the ordinary path. The practitioner records that they have seen the route, using `record_route_seen` and the hash on the draft. Do not copy the cue into the chat reply.
3. **Approve.** The practitioner approves or returns the note with `record_practitioner_approval`. The content hash has to be the hash of the held draft. Acknowledgements have to be the boolean true.
4. **Stop.** Do not add a topic that writes a case record, shares the note, or assesses eligibility, risk, or need. Those actions are not in the tool list.

A maker who pastes an approval into the transcript has not approved the note. Only the separate object counts.

The same calls are the skills in `skills/`. See `docs/harness-comparison.md`.
