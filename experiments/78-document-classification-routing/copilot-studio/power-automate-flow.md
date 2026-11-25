# Flow

The flow's only job is to return JSON to the topic. It does not create a Dataverse row, it does not move a file in SharePoint, and it does not send mail.

| Input | Meaning |
| --- | --- |
| `document` | The JSON the user pasted. `synthetic` must be true for this starter. |
| `as_of` | The date the question is about. An ambiguous or unreadable date is refused. Today is not substituted. |

| Output | Meaning |
| --- | --- |
| The proposal JSON | Class, destination, hash, and queue reasons. `human_approval` is null. |

A later flow may call `record_route_seen` or `record_routing_confirmation`. That later flow still does not file the document. If a team adds a library connector, the manifest changes in the same change. This starter does not include it.

Catalogue row O003 names AI Builder or Microsoft Foundry, and Power Platform. AI Builder was not opened on 25 November 2026. This flow does not call it. Treat a claim about an AI Builder model as unverified.
