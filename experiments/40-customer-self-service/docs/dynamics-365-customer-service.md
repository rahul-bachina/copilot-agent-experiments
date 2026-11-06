# Dynamics 365 Customer Service

The starter does not connect to Dynamics 365. The customer or the handler pastes the enquiry. That is deliberate. A connector is the point at which the agent could update a contact, resolve a case, take a payment, or send an email, and those actions are out of scope at autonomy A1.

The product behaviour of Copilot in Dynamics 365 Customer Service was not opened on 6 November 2026. Treat click-paths, security-role names, and Copilot features in that product as unverified in this folder. The table below is a permission boundary for a later connector, in the same shape as Experiment 02. It is not a description of a tenant that exists.

If an organisation adds a connector later, this is the boundary to build to. Update `agent-manifest.yaml` in the same change. Do not add the connector and leave the manifest saying there is none.

## Default: no connector

Copilot Studio shows the draft in the chat. The handler copies what they accept into the case, using their own Dynamics 365 security role. The agent identity has no Dataverse role at all.

That matches the manifest: production Dynamics 365 is on the never-access list, and writes are disabled.

## If a read is required

Read only the case or the account the handler already has open.

| Privilege | Case or incident | Email | Contact or account | A custom draft table |
| --- | --- | --- | --- | --- |
| Read | Yes, the one whose id the handler passed | No | No, unless the handler's screen already shows it and the organisation accepts the extra data | Yes, drafts this agent created |
| Create | No | No | No | Only if the organisation chooses the draft table below |
| Write | No | No | No | No. A correction is a new draft, or the handler edits it in the app |
| Append / append to | No | No | No | No customer-visible activity |
| Assign, share | No | No | No | No |
| Delete | No | No | No | No |

Pass the record id from the session the handler started. Do not search customers by name. Do not read the timeline, the audit history, or other cases on the same customer.

A read of the description can still contain special-category data. The UK GDPR notes in the manifest apply. The agent still must not write a vulnerability marker onto the contact.

## If the draft must be stored

Store it somewhere the customer cannot see and the agent cannot send.

One pattern that stays inside "draft only":

- A custom table, for example `mf_service_draft`, not the email table and not the incident.
- Columns: case lookup, draft text, model deployment name if any, created by, created on.
- The agent's application user can create a row. It cannot write the incident, cannot update the customer's address, cannot create an email, and has no send privilege on any mailbox.
- The row is not an activity. It does not appear on the customer timeline.
- A handler opens the row, edits the text in the case form they already use, and sends from their own mailbox if they decide to. Sending remains a human action in Dynamics, not a tool call.

Do not use "create email in draft status" unless the security role also cannot send, and a second control stops a later flow from sending drafts automatically. A draft email is one status change away from a customer message. The custom table is the smaller privilege.

## Status reasons the agent must not set

Resolved, cancelled, or any organisation-specific "upheld" or "rejected" status. Closure and outcome are decisions for a person. They are not self-service.

The agent must not write a new address, a tariff, a contract end date, or an appointment onto the account. A confirmed draft in this starter is still not that write.

## Power Automate

A flow that creates or updates a case, sends an email, takes a payment, or posts to a queue is a write or a send. Do not add one "just to file the draft". If a flow calls the Python core, it may return JSON to Copilot Studio and stop there. See the Copilot Studio guide.
