# Power Automate flow

A sketch of the one flow the standard-harness topic calls. It is not an exported solution.

## Trigger

Power Automate is called by the Copilot Studio topic. Manual testing can use the same inputs.

| Input | Source |
|---|---|
| `request` | The JSON the user pasted. It must have `synthetic: true` for this starter. |
| `as_of` | Typed by the user. `YYYY-MM-DD`. |
| `pack_type` | Typed by the user. A closed-list id. |
| `authorised_scopes` | Typed by the user. A list. |
| `search_from`, `search_to` | Typed by the user, or both omitted. |

Do not add a step that reads a mailbox, a SharePoint library, or Dataverse to find more items. Do not parse scopes out of the item text.

## Action

HTTP POST to an internal endpoint that runs `build_pack()` with those arguments and returns the JSON. The endpoint imports Experiment 12 and, through it, Experiment 08. It does not call `release`. Authentication is a managed identity. This repository does not provision that identity.

The response is the draft. The flow returns it to the topic and ends.

## Steps that are not in the flow

- Create or update a Dataverse row.
- Send mail, including to a data subject, the Financial Ombudsman Service, or the Housing Ombudsman.
- Write the index to SharePoint.
- Call `record_export_approval` or `produce_export`.
- Apply a Schedule 2 exemption.

If a later change adds one of those steps, the manifest changes in the same change. This starter does not include them.

## Data loss prevention

No connector in this flow reaches mail, SharePoint, Dataverse, or an external portal. A DLP policy that blocks those connectors would not block this flow as written. The product page for DLP was not opened on 28 October 2026. Confirm the tenant policy before anyone adds a connector.
