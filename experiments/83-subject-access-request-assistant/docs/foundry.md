# Microsoft Foundry

Microsoft Foundry is optional. It is not a third harness, and this repository does not deploy a resource.

If an organisation turns it on, the only job is to turn the JSON from `scope()` into a short note. The note may use only fields that are already in that JSON. It must not add a redaction, drop one, choose an exemption, or pick a deadline reading.

The hash, `disclosure_approval_recorded`, `response_sent`, `records_deleted`, `records_edited`, and `exemption_decided_by_agent` stay in the Python core. A note that says the file has been sent does not make that true.

Prompt shields, Key Vault, and a UK region were not opened on 27 November 2026. Treat that product behaviour as unverified. A production deployment should use a UK region the organisation already operates. This starter cannot enforce that.

Do not send the request text, a date of birth, an account number, or a third-party name to a model trace. The sample runs with no network.
