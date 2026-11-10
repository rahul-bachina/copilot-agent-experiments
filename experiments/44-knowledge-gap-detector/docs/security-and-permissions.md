# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

Autonomy **A0**. The knowledge manager confirms gaps. Writes are disabled. Sends are disabled. Approve or reject, regulated decision, production record change, external send, and spending are disabled. So are publishing an article, editing or deleting one, and choosing the winning side of a conflict.

## What a run may read

The one pack the knowledge manager supplies, the approved articles, the pinned citations in `src/sources.py`, and Experiments 08, 21, and 40 by calling them. The Python starter does not persist the pack. A call that is not marked synthetic is refused, and the text is not copied out.

Experiment 08 `propose()` counts UK identifiers. The redacted text is not copied out. `release()` is not called. `output_is_anonymised` stays false. Experiment 08 does not redact names, email addresses, or telephone numbers.

Experiment 21 `is_stale()` is the window on `last_reviewed`. `match_articles()` runs for an `it_service` pack and returns ids. Experiment 40 `match_articles()` runs for public-service, financial-services, energy, and telecoms packs and returns ids. Bodies are not copied.

## What a run must not do

- Publish, edit, or delete a knowledge article, including after the manager confirms a gap.
- Write a Dynamics 365 record or a Microsoft Fabric table.
- Send an email, an SMS, a letter, or a chat reply.
- Treat pack text as confirmation. The confirmation object is separate and it has no publish field.
- Copy a query, a case note, a search string, or an article body into the output.
- Decide that PRIN 2A.5, Article 5(1)(c), or Equality Act section 20 has been met.
- Choose which conflicting article is right.

## Data minimisation

UK GDPR Article 5(1)(c) was read on 10 November 2026. The review keeps ids, hashes, and counts. `data_minimisation_met` stays false. Article 6 was not opened. No lawful basis is asserted.

## Platform controls this starter does not configure

These product pages were not opened on 10 November 2026. Treat the names as unverified here. None of these objects is created in this folder.

**Microsoft Entra Agent ID.** Not opened. This starter does not register an agent identity. A deployment that needs one would use a dedicated identity with no publish role and no Dynamics 365 write role. That design was not verified here.

**Conditional Access.** Not opened. This starter does not describe a Conditional Access policy for agents. Confirm the tenant before relying on one.

**Power Platform DLP.** Not opened as a configured policy. The manifest says a later publishing, Dynamics 365 write, Fabric write, or mail connector should be blocked. This folder does not create that policy.

**Microsoft Foundry prompt shields.** Not opened. The core does not call a model. The injection tests in this folder are the control on the stand-in. A filter is not a substitute for having no publish tool. The portal label is unverified here.

**Key Vault.** Not opened. This starter has no secret to store. A later Foundry key, if one is added, belongs in a vault the organisation already operates. That wiring is unverified here.

**Microsoft Purview.** Not opened. This starter does not set a sensitivity label and does not claim a Copilot Studio audit schema. An organisation that already uses Purview decides whether prompts and reviews are in scope.

**Application Insights.** Not opened. This starter writes no telemetry. Do not put the pack text in an application trace.

Dynamics 365 knowledge-article pages and Microsoft Fabric pages were not opened. See [dynamics-365-and-fabric.md](dynamics-365-and-fabric.md).
