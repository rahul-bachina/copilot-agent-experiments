# Dynamics 365 Customer Service

The starter does not connect to Dynamics 365. The handler pastes the complaint. That is deliberate. A connector is the point at which the agent could create, update, resolve, or email, and those actions are out of scope at autonomy A1.

If a firm adds a connector later, this is the boundary to build to. Update `agent-manifest.yaml` in the same change. Do not add the connector and leave the manifest saying there is none.

## Default: no connector

Copilot Studio shows the draft in the chat. The handler copies what they accept into the case, using their own Dynamics 365 security role. The agent identity has no Dataverse role at all.

That matches the manifest: production Dynamics 365 is on the never-access list, and writes are disabled.

## If a read is required

Read only the case the handler already has open.

| Privilege | Incident | Email | Contact | A custom draft table |
|---|---|---|---|---|
| Read | Yes, user-owned or the one whose id the handler passed | No | No, unless the handler's screen already shows it and the firm accepts the extra data | Yes, drafts this agent created |
| Create | No | No | No | Only if the firm chooses the draft table below |
| Write | No | No | No | No. A correction is a new draft, or the handler edits it in the app |
| Append / append to | No | No | No | No customer-visible activity |
| Assign, share | No | No | No | No |
| Delete | No | No | No | No |

Pass the incident id from the session the handler started. Do not search incidents by customer name. Do not read the timeline, the audit history, or other cases on the same customer. Those are not needed to draft an acknowledgement of the text in front of the handler.

A read of the description can still contain special-category data. The UK GDPR notes in the manifest apply. The agent still must not write a vulnerability marker onto the contact.

## If the draft must be stored

Store it somewhere the customer cannot see and the agent cannot send.

One pattern that stays inside "draft only":

- A custom table, for example `nb_intake_draft`, not the email table and not the incident.
- Columns: incident lookup, draft text, clock JSON, model deployment name, created by, created on.
- The agent's application user can create a row. It cannot write the incident, cannot create an email, and has no send privilege on any mailbox.
- The row is not an activity. It does not appear on the customer timeline.
- A handler opens the row, edits the text in the case form they already use, and sends from their own mailbox. Sending remains a human action in Dynamics, not a tool call.

Do not use "create email in draft status" unless the security role also cannot send, and a second control stops a later flow from sending drafts automatically. A draft email is one status change away from a regulated communication. The custom table is the smaller privilege.

## Status reasons the agent must not set

Resolved, cancelled, or any firm-specific "upheld" or "rejected" status. Closure and outcome are decisions under the firm's DISP procedure. They are not intake.

## Power Automate

A flow that creates or updates an incident, sends an email, or posts to a queue is a write or a send. Do not add one "just to file the draft". If a flow calls the clock, it may return JSON to Copilot Studio and stop there. See the Copilot Studio guide.
