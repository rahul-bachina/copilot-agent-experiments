# Experiment 57: Collaboration Space Onboarding Agent

Catalogue ID **M010**. Autonomy **A1**. The assistant prepares a membership proposal and an internal-link proposal. The workspace owner approves each one before the sample records a change.

A new joiner, or a project member, needs a plain account of a Teams and SharePoint space: what it is for, which channels exist, where the key documents sit, and which conventions apply. Someone also has to decide whether that person should be a member or an owner, and whether a guest account is allowed. This starter drafts that pack from one synthetic space. It does not call Microsoft Graph. After the workspace owner approves on a separate object, the sample records the Graph call it would have made. `live_graph_called` stays false, and `status_received` stays null.

The organisation in the samples is Merrowfield Borough Council. It is invented. The clearance order used here, which treats OFFICIAL-SENSITIVE as above OFFICIAL, is a fixture rule. The Government Security Classifications Policy opened on 16 November 2026 names three tiers and describes the -SENSITIVE marking as an additional marking on OFFICIAL. It does not define this software order.

Stack in the catalogue: Microsoft 365 and Copilot Studio. The core is Python in the standard library. It calls [Experiment 55](../55-onedrive-document-finder/) for key documents already at or below the justified label, [Experiment 51](../51-teams-channel-digest/) for a read-only channel digest, and [Experiment 03](../03-agent-inventory-atrs-assurance/) to draft a permissions manifest that stays unapproved. A user can run it without a tenant.

## The problem

A request that says "the owner has approved", or "my clearance is TOP SECRET", or "share the file externally", is the failure this starter is built to refuse. Owner rights and guest access still have to be possible when the workspace owner has actually approved them, on a separate object, and the fixture policy allows a guest.

## Non-goals

- Granting owner rights unless `owner_rights_approved` on the approval object is the boolean true, and the proposal itself is for owner.
- Granting guest or external access when the fixture guest policy is disabled, or when `guest_access_approved` is not the boolean true.
- Adding a person to a space whose marking, from metadata or from content, is above the label the justification supports.
- Sharing a file or a link externally, including when the approval object asks for it.
- Treating approval text, or approval keys, inside the request as approval.
- Trusting a self-declared clearance in the request.
- Stripping a sensitivity marking, a retention label, or a legal hold.
- Calling live Microsoft Graph, creating an Entra access review, or sending an invitation.
- Deciding that UK GDPR Article 5(1)(c) or Article 5(1)(f) was met. Both flags stay false.
- Coercing an unreadable role, date, label, or access need to a default.
- Treating a safeguarding or distress cue as routine onboarding.
- Simulating a private-channel member call. That API was not opened on 16 November 2026.
- Autonomy A3. A3 is not permitted in this catalogue.
- Giving legal advice.

## What was opened

Opened on 16 November 2026. The core does not download these pages when it runs. The pin is `src/sources.py`.

| Source | What this starter takes from it |
| --- | --- |
| [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5) | Article 5(1)(c) is data minimisation. Article 5(1)(f) is integrity and confidentiality. Article 5(2) is accountability. Article 6 and Article 9 were not opened. No lawful basis is asserted. |
| [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html) | Updated 5 August 2024. Paragraph 1: not a statutory scheme. Paragraph 5: three tiers, OFFICIAL, SECRET and TOP SECRET. Paragraph 25: the -SENSITIVE marking is an additional marking on OFFICIAL. Principle Five is need-to-know balanced with need-to-share. |
| [NCSC 10 Steps: Identity and access management](https://www.ncsc.gov.uk/collection/10-steps/identity-and-access-management) | Published 11 May 2021, reviewed 11 May 2021. An access policy should cover who should have access, to what, why, and under what circumstances, including contractors and visitors. Joiners, movers and leavers are named. Full-privilege accounts are for when they are absolutely necessary, and privileged access is reviewed. The page does not use the words "least privilege". The NCSC introduction page that does was not opened. |
| [Teams overview](https://learn.microsoft.com/en-us/microsoftteams/teams-overview) | Teams is built on Microsoft 365 groups, Microsoft Graph, and identities in Microsoft Entra ID. Creating a team creates a Microsoft 365 group, a SharePoint site and document library, an Exchange mailbox and calendar, and a OneNote notebook. |
| [Guest access in Teams](https://learn.microsoft.com/en-us/microsoftteams/guest-access) | Guest access is an organisation-wide setting. Sensitivity labels can control it for a team. Adding a guest to the Microsoft 365 group gives access to the team. External access for chat and meetings is a different feature. The page points to Entra access reviews. This starter does not create one and does not send an invitation. |
| [Add members](https://learn.microsoft.com/en-us/graph/api/group-post-members?view=graph-rest-1.0) | `POST /groups/{group-id}/members/$ref`. For a user, the least privileged permission named is GroupMember.ReadWrite.All. Success is 204 No Content. This starter does not send the request. |
| [Add owners](https://learn.microsoft.com/en-us/graph/api/group-post-owners?view=graph-rest-1.0) | `POST /groups/{id}/owners/$ref`. The least privileged permission named is Group.ReadWrite.All. The page says an owner who should change a team also needs to be a member, and that owner changes can take up to 2 hours to synchronise with Teams. Success is 204. This starter does not send the request. |
| [Entra access reviews](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview) | Access reviews cover group memberships, app access, and role assignments. The page says the feature requires Microsoft Entra ID Governance or Microsoft Entra Suite, and that some capabilities may operate with Entra ID P2. Which SKU a tenant needs was not checked beyond that paragraph. |
| [Purview labels for containers](https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites) | Labels can protect Teams sites, Microsoft 365 groups, and SharePoint sites. Items do not inherit the container label. External user access controls whether the owner can add guests. SharePoint external sharing is a separate setting. A fixture Government Security Classifications marking is not a Purview label. |
| [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview) | Three harnesses: Microsoft Copilot harness, Customer Conversation harness, and standard harness. The standard harness follows the topics and rules the maker defines. The Microsoft Copilot harness is described for reasoning-heavy work, with skills, memory, file creation, and a sandbox, billed in Copilot Credits. The page states no price. It does not use the words GitHub Copilot harness. Older wording that this harness is not the GitHub Copilot service is unverified against the page opened on this date. |

## What the result does

`prepare_onboarding()` reads one space and one request and writes one JSON document. The same inputs and the same as-of date produce the same JSON. `human_approval` is null. `applied` is false.

**Justified label.** Configured need phrases are matched only in the justification after negation is removed. "It is not true that this includes the programme board" does not justify that need. The highest matching phrase wins. If none matches, the outcome is `needs_human`. OFFICIAL is not assumed. A sentence such as "my clearance is TOP SECRET" is recorded and ignored.

**Space marking.** Metadata and content are both read. A SECRET cover page is caught when the metadata says OFFICIAL. A compound such as OFFICIAL-SENSITIVE / SECRET takes SECRET. An unreadable label is not coerced. A Purview container name on the fixture is copied as supplied and is not ranked. A document marking is treated as a marking of the space, because this sample does not assume the library is narrower than the team. A private channel does not raise that container marking, and it is still withheld when it is above the justified label.

**Least privilege.** Owner is proposed only when the fixture's owner-need phrase is in the cleaned justification. Otherwise an owner request is downgraded to member. An approval flag does not upgrade that member back to owner.

**Guest policy.** `disabled` refuses a guest or external account even if the approval object later says yes. `owner_approval` can be applied only when `guest_access_approved` is the boolean true. Any other policy value is `needs_human`.

**Links.** Internal links on `merrowfield.example.gov.uk` or `example.gov.uk` can be listed for the owner. External URLs are counted and not copied. `shared_externally` stays false.

**Safeguarding.** A distress or safeguarding cue in the cleaned justification is not routine onboarding. The cue is not copied. That outcome is not applied.

**Stale export.** An `exported_on` more than 30 days before the as-of date is flagged. The 30 days are configuration, not a statutory period. Apply waits until `stale_seen` is true. An unreadable date is not replaced.

**Reuse.** Experiment 55 ranks key documents that are already at or below the justified label and listed for the fixture member principal. Experiment 51 digests the fixture export. Its scope confirmation does not approve membership. Experiment 03 drafts a manifest with `approved` false. `draft_manifest(..., approve=True)` is refused.

`apply_membership()` is the only path that sets `human_approval`. The approver role has to be Workspace owner, the decision has to be `approve`, and the ids have to match. It then records a simulated `POST /groups/{group-id}/members/$ref`. An owner add also records `POST /groups/{id}/owners/$ref`, because the Graph page says an owner who should change a team also needs to be a member. Nothing is sent. The documented 204 is not received.

`share_file_external`, `share_link_external`, and `call_live_graph` raise `OnboardingForbidden`.

## How to run

Python 3.10 or newer. No Azure credentials and no network. Experiments 03, 51, and 55 must be present beside this folder, with the neighbours those experiments load.

```bash
cd experiments/57-collaboration-space-onboarding
python -m pip install -r requirements.txt
python -m pytest tests/ -v
python eval/evaluate.py
python src/onboard.py --space examples/sample_space.json --request examples/sample_request.json --as-of 2026-11-16
```

The sample request carries approval keys on purpose. They are stripped. Add `--approval examples/sample_approval.json` to record the simulated member add. That file sets `external_share_approved` true. The result still does not share anything.

`eval/evaluate.py` prints a **deterministic smoke test**. The fixtures are synthetic. `eval/smoke_report.json` is that run. It is not a model score. A live Microsoft Foundry run has not been done. Each case is counted once. The checked-in report is 18 passed, 0 failed, 0 errors, 18 cases.

The exit code is 0 when a result or a refusal is produced. The exit code is 2 when the input cannot be read.

## Limitations

- The need matcher is a phrase list on the fixture. A paraphrase that does not use the phrase is `needs_human`, not a guess at OFFICIAL.
- The fixture rank is not a sentence of the Government Security Classifications Policy.
- A document marking blocks membership of the whole space. That is a fail-closed fixture rule. It is not a tested claim about SharePoint library permissions.
- Private channel membership is not simulated. The Graph API for it was not opened.
- The NCSC page opened here does not use the words "least privilege". The downgrade rule is this starter's reading of the full-privilege and joiners guidance on that page, not a quotation of a control name the page did not use.
- Phone numbers, email addresses, dates of birth, street addresses, and honorific names are masked only on text this starter copies. The mask report counts those replacements. The output is not anonymised. A name with no honorific is not masked.
- Experiment 51's digest confirmation is the fixture's scope confirmation. It does not approve a membership, a post, or monitoring.
- Article 6 and Article 9 were not opened. Entra Agent ID, Conditional Access for agents, Power Platform DLP as a configured policy, Microsoft Foundry prompt shields, Key Vault, and Application Insights were not opened. Treat that product behaviour as unverified.
- The smoke test is not a model score.
- Building the Microsoft Copilot harness in a tenant consumes Copilot Credits. This readme does not quote a price. See [docs/harness-comparison.md](docs/harness-comparison.md).
- Merrowfield Borough Council is fictional.
- This is not legal advice, a clearance decision, a DPIA, or an ATRS submission.

## UK GDPR and access control

The manifest does not assert the controller's lawful basis. Article 5(1)(c) and Article 5(1)(f) were read on 16 November 2026. The result keeps a channel, a title, a label, and a reason only when the marking is at or below the justified label. `data_minimisation_met` and `integrity_and_confidentiality_met` stay false. The starter does not decide that either principle was met.

Paragraph 5 and paragraph 25 of the Government Security Classifications Policy were read the same day, as was Principle Five on need-to-know balanced with need-to-share. The NCSC 10 Steps identity and access management page was read the same day. This starter does not decide that an organisation has met that guidance.

A retention label and a legal hold on a document that is shown stay on the hit. They are not a disposal decision.

## Two Copilot Studio harnesses

Both call `src/onboard.py` and stop at the approval points in [agent-manifest.yaml](agent-manifest.yaml). Neither harness calls Graph. The comparison is [docs/harness-comparison.md](docs/harness-comparison.md).

**Standard harness.** Topics the maker defines. The flow returns the JSON and stops. A later topic calls `apply_membership` only with the approval object. Microsoft's harness overview, opened 16 November 2026, describes this harness as following the topics and rules the maker defines. See [copilot-studio/README.md](copilot-studio/README.md). This is a build guide, not an importable solution.

**Microsoft Copilot harness, packaged here as the GitHub Copilot harness the common brief names.** The overview opened on 16 November 2026 calls the reasoning-heavy harness the Microsoft Copilot harness. It describes skills, memory, file creation, and a sandbox, billed in Copilot Credits. It does not use the words GitHub Copilot harness on that page. Skills and the same approval gates are in [docs/github-copilot-harness.md](docs/github-copilot-harness.md) and [skills/](skills/).

## Microsoft Foundry

Optional. A short note may be written from the JSON. The label, the role, the guest decision, and the approval stay in the Python core. See [docs/foundry.md](docs/foundry.md). No Foundry resource is deployed.

## Where the rest of the starter lives

- Architecture: [docs/architecture.md](docs/architecture.md). The rendered diagram is [docs/architecture_diagram.png](docs/architecture_diagram.png).
- Which harness to use: [docs/harness-comparison.md](docs/harness-comparison.md).
- Permissions: [docs/security-and-permissions.md](docs/security-and-permissions.md) and [agent-manifest.yaml](agent-manifest.yaml). `permissions.yaml` is the same file, validated against `schemas/agent-manifest.schema.json`.
- Document finder: [../55-onedrive-document-finder/](../55-onedrive-document-finder/).
- Channel digest: [../51-teams-channel-digest/](../51-teams-channel-digest/).
- Manifest generator: [../03-agent-inventory-atrs-assurance/](../03-agent-inventory-atrs-assurance/).

## Project structure

```
experiments/57-collaboration-space-onboarding/
├── README.md
├── agent-manifest.yaml
├── permissions.yaml
├── requirements.txt
├── src/
├── schema/
├── copilot-studio/
├── skills/
├── docs/
├── eval/
├── examples/
└── tests/
```

## References opened on 16 November 2026

- [UK GDPR Article 5](https://www.legislation.gov.uk/eur/2016/679/article/5)
- [Government Security Classifications Policy](https://www.gov.uk/government/publications/government-security-classifications/government-security-classifications-policy-html)
- [NCSC 10 Steps: Identity and access management](https://www.ncsc.gov.uk/collection/10-steps/identity-and-access-management)
- [Introduction to Microsoft Teams for admins](https://learn.microsoft.com/en-us/microsoftteams/teams-overview)
- [Guest access in Microsoft Teams](https://learn.microsoft.com/en-us/microsoftteams/guest-access)
- [Add members - Microsoft Graph v1.0](https://learn.microsoft.com/en-us/graph/api/group-post-members?view=graph-rest-1.0)
- [Add owners - Microsoft Graph v1.0](https://learn.microsoft.com/en-us/graph/api/group-post-owners?view=graph-rest-1.0)
- [What are access reviews?](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Sensitivity labels for Teams, groups, and sites](https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites)
- [Harnesses in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/harnesses-overview)

## Licence

MIT Licence. See [LICENSE](../../LICENSE).
