# Power Automate note

Catalogue row O007 names Power Platform. This file is guidance for a maker. It is not an importable solution, and this repository does not create a flow.

A flow that sends the draft to the named approver would:

1. Call the same assemble step this starter uses, with the synthetic request and the question date.
2. Stop if the outcome is `route_to_human` until `record_route_seen` has been called for the current hash.
3. Use an Approvals action whose title includes the content hash, and whose body is the cover note. The approver is the directory person the draft named, not an address taken from the request text.
4. On the approver's response, call `record_approver_decision` with that same hash and the decision approve, reject, or return. Do not add a send, a payment, or a signature step.
5. If the request changes after the approval starts, cancel the approval. Do not record the old decision against the new hash.

The Approvals connector and its tenant settings were not opened on 26 November 2026. Treat connector behaviour as unverified. A human can always stop the flow and handle the request outside it.

No mailbox, SharePoint library, or finance system is connected by this starter.
