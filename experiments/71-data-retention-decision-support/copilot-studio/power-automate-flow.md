# Flow note

This is not a solution package and it does not call a live records store.

1. Trigger when a records owner submits a synthetic series id and a question date.
2. Run `advise_retention()` with the pinned files. Pass the question date as `as_of`. Do not pass `human_approval`.
3. Show the JSON. Stop.
4. A second flow, started by the owner and not by the note, calls `record_advice_seen()` with the seen object and the advice hash.
5. There is no action for delete, move, relabel, archive, transfer, dispose, or send.

If the flow is connected to a SharePoint library later, that connection is a different system. This starter does not include it. A connector that can delete a file would breach the autonomy level.
