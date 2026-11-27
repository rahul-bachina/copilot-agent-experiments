# Power Automate

Catalogue row UK13 names Power Platform. This folder does not import a flow.

A flow, if someone builds one later, may call `draft_note` and show the JSON to the practitioner. It must not write a case-management row, send the note, or call an assessment API. The approval stays the Python step `record_practitioner_approval`, bound to the held hash.

No connector in this starter has a write privilege. `tools.writes.enabled` is false. `tools.sends.enabled` is false.
