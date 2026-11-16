# Security and permissions

Manifest `exp-57-collaboration-space-onboarding`, version 0.1.0. Autonomy **A1**. Writes disabled. Sends disabled. `permissions.yaml` is the same file as `agent-manifest.yaml` and validates against `schemas/agent-manifest.schema.json`.

The workspace owner is the approver. `apply_membership()` is the only function that sets `human_approval`. It reads a separate object. Approval keys on the request are stripped. Approval sentences are recorded with `followed` false.

## What the sample can record

After a matching approval, the result contains a simulated `POST /groups/{group-id}/members/$ref`. The Graph v1.0 page opened on 16 November 2026 names GroupMember.ReadWrite.All as the least privileged permission for adding a user, and 204 No Content as success. An owner add also records `POST /groups/{id}/owners/$ref`. That page names Group.ReadWrite.All, says the owner also needs to be a member to change a team, and says synchronisation to Teams can take up to 2 hours. `live_graph_called` is false. `status_received` is null. The sample did not receive 204.

## What it cannot do

- Share a file or a link externally. `share_file_external` and `share_link_external` raise `OnboardingForbidden`.
- Call live Graph. `call_live_graph` raises.
- Grant owner rights because a request says so, or because `owner_rights_approved` is true on a proposal that was downgraded to member.
- Grant guest access when `guest_policy` is `disabled`.
- Copy a title above the justified label, or a self-declared clearance into the rank.
- Strip a retention label or a legal hold from a document that is shown.
- Mark the Experiment 03 manifest approved.

## Products named, and what was not opened

Teams, Microsoft 365 groups, Graph member and owner add, Entra access reviews, and Purview container labels were opened on 16 November 2026. The descriptions in the readme stay inside those pages.

These were not opened on that date. Treat the product behaviour as unverified:

- Entra Agent ID
- Conditional Access for agents
- Power Platform DLP as a configured policy
- Microsoft Foundry prompt shields
- Key Vault
- Application Insights

A production deployment that adds a Graph connector would need a new manifest, a new approval test, and a review. This starter does not add that connector.

The private-channel member API was not opened. `private_channel_api_opened` stays false, and the sample does not invent that call.

Contact addresses on `merrowfield.example.gov.uk` are placeholders. Merrowfield Borough Council is invented.
