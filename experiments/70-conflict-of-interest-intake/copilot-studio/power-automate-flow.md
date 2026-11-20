# Power Automate flow

A note for a maker. It is not an importable flow.

The flow calls `draft_declaration` with the text, the declarant reference, and `as_of`. It returns the JSON to the chat and stops.

A second flow may call `confirm_declaration` only when the maker has collected the confirm object outside the declaration text. The hash must be the hash just returned. The flow writes nothing of its own. The Python function writes the synthetic row.

A third flow may call `record_disposition` only when `staged` is true and the approver reference was checked as ethics or procurement. The flow does not update a procurement register, an HR system, or a mailbox.

Do not add a Dataverse row, an email, a Teams message, or an approval action that clears a supplier. A flow that did would be a different system, and it would need a new manifest first. This starter does not include it.

Power Platform DLP as a configured policy was not opened on 20 November 2026. Treat a claim about a tenant policy as unverified.
