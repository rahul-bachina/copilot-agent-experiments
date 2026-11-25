# Flow note

No flow is deployed from this folder.

A flow that called this starter would:

1. Pass the synthetic request and the question date to `prepare_comparison()`.
2. Show the JSON to the named reader.
3. If the outcome is `route_to_human`, wait for a separate seen object and call `record_route_seen`.
4. Wait for a separate confirmation object and call `confirm_versions`. Reject the call when the content hash or either document hash does not match the held copy.
5. Wait for a separate interpretation acknowledgement and call `record_interpretation_seen`.
6. Stop. Do not edit the document, do not write it back, and do not send it.

The in-memory confirmation is not a document write. `writes` and `sends` stay disabled in the manifest.
