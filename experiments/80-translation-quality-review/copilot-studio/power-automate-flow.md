# Flow note

No flow is deployed from this folder.

A flow that called this starter would:

1. Pass the synthetic request and the question date to `prepare_review()`.
2. Show the JSON to the named bilingual reviewer.
3. If the outcome is `route_to_human`, wait for a separate seen object and call `record_route_seen`.
4. If high-risk segments are present, wait for a separate validation object and call `record_high_risk_validated`. Reject the call when the content hash or either document hash does not match the held copy.
5. Wait for a separate ownership object and call `record_translation_owned`.
6. Stop. Do not publish the translation, do not send it, and do not overwrite the document.

The in-memory ownership is not a document write. `writes` and `sends` stay disabled in the manifest.
