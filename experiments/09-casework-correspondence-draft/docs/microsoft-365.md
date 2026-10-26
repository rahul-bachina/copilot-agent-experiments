# Microsoft 365

The catalogue stack for this agent is Microsoft 365 and Copilot Studio. This starter does not connect to a tenant.

## What would live in Microsoft 365

A correspondence unit already keeps lines to take in SharePoint or in a shared library. The agents overview retrieved on 26 October 2026 lists SharePoint as a supported knowledge source on both the standard harness and the GitHub Copilot harness.

That is not how this starter cites a line. A knowledge answer can paraphrase. The drafter pastes a line from `fixtures/lines_to_take.json` and refuses a line that is withdrawn, overdue, or not yet in force. If a unit later points the matcher at an export of its own library, the file still has to carry `status`, `effective_on`, and `review_due_on`. A SharePoint search result without those fields is not a citable line.

A read of one exported file would be a deployment change. The manifest does not allow it yet. A write back to SharePoint, a mailbox read, or a send through Outlook is a different change again, and sends stay off.

## What the author does in the tools they already have

The author pastes the letter, reads the draft, approves the recipient and the text, and sends from the unit's own mailbox under their own account. The agent is not a second mailbox.

Sensitivity labels and retention on that mailbox are the organisation's Purview configuration. This starter does not set a label. See [security-and-permissions.md](security-and-permissions.md). Whether a Copilot Studio session inherits the mailbox's label was not verified.

## What not to connect

- Outlook, or any "send an email" action.
- A case-management connector that creates or updates a record.
- A people search that resolves an MP or a constituent to a directory object. The fixtures use fictional names on purpose.
- The organisation's real lines file, until it has been reviewed and the manifest lists that read.
