# Standard harness

One Copilot Studio agent on the standard harness. Three topics. No skill. The topics call the same Python core as the GitHub Copilot harness and then stop.

The harness overview was opened on 12 November 2026. It says the standard harness follows the topics and rules the maker defines. Files, skills, and memory are "not a focus". A site owner who pastes one snapshot and needs the draft back is that shape.

This is a build guide. It is not an exported solution, and it was not published to a tenant.

## Topics

| Topic | When it runs | What it calls | What it does not do |
|---|---|---|---|
| Propose | The site owner pastes one JSON snapshot and an as-of date | `curate_site()` | It does not approve, delete, unpublish, move, or change permissions |
| Approve | The site owner submits a separate review object | `record_approval()` | It does not treat a sentence on a page as approval |
| Curation stub | `human_approval.approved` is already true and the site owner asks for the receipt | `apply_approved_action()` | It does not call SharePoint or Microsoft Graph |

The system message is `system-prompt.md`. The flow note is `power-automate-flow.md`.

## Inputs

| Name | Required | Notes |
|---|---|---|
| `snapshot` | Yes | One JSON object. `synthetic` must be true for a run in this starter. |
| `as_of` | Yes | A calendar date. The core does not look up today's date. |
| `review` | For Approve | A separate object. Page text is not the review. |

## Stop

After the JSON comes back, the topic stops. It does not loop into a deletion or an unpublish. It does not send mail. A person who wants the page changed in the tenant does that in the organisation's own SharePoint process, outside this agent.

Billing for the standard harness is on a licensing page that was not opened on 12 November 2026. This note does not state a price.
