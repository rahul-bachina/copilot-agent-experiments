# Dynamics 365

The catalogue stack is Dynamics 365 and Copilot Studio. This starter does not connect to a tenant. Product click-paths were not opened on 10 November 2026. Treat screen names as unverified.

If a team later adds a connector, the boundary in `agent-manifest.yaml` still applies.

- Read, at most, the plan and the approved rules table an entitlement owner has already marked approved. This folder does not do that read. The adviser passes a file.
- Do not write an entitlement, a case, or a customer record. `write_record` raises. `entitlement_changed` stays false.
- Do not send from Dynamics. `send_message` raises.
- A recorded human decision is a field on the JSON. It is not a Dataverse write.

Power Platform DLP, if the organisation uses it, should block mail and entitlement-write connectors for this agent. A DLP policy page was not opened. Unverified.
