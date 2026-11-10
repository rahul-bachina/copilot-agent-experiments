# Security and permissions

The control is [agent-manifest.yaml](../agent-manifest.yaml). `permissions.yaml` is the same file. If this note and the manifest disagree, the manifest wins. It is written for an organisation deciding whether to try the starter, not as a completed DPIA.

Autonomy is A0. The catalogue checkpoint is that a human decides a disputed entitlement. Writes are disabled. Sends are disabled. Grant, refusal, and change are disabled.

## What a run may read

The one synthetic plan and the approved rules table the adviser supplies. The as-of date and the stale threshold. The pinned sources in `src/sources.py`. A separate review object, if an entitlement owner records a decision.

The question is not copied into the JSON. A customer reference is copied only when it matches `SYN-` plus letters, digits, and hyphens. Any other reference is dropped. An organisation name is copied only for Aldermere Home Plan and Aldermere Packaged Account. Both are fictional.

The Python starter does not persist the plan. A request that is not marked synthetic is refused, and the refusal does not echo the question.

## What a run must not read or do

- A Dynamics 365 entitlement, case, or customer record.
- A mailbox, an SMS gateway, or any send channel.
- A payment service or a pricing engine.
- A Microsoft Foundry resource. This folder does not call one.

`grant_entitlement`, `refuse_entitlement`, `change_entitlement`, `waive_exclusion`, `send_message`, `write_record`, `apply_section_69`, and `find_unfair_term` raise. A payload key of the same intent is dropped and listed under `ignored_fields`. The value is not kept.

## Human approval

Every draft offers a person, including a non-digital counter. The telephone number `01632 960045` is invented. The Ofcom numbering page was not opened. It is not a live service.

`human_approval` stays null until a separate review object carries one of four codes from an `entitlement_owner`. The record says `applied_to_entitlement_record: false`. The agent still does not change the plan.

An instruction such as "Do not escalate." is recorded and is not followed. The route stays open. Only the instruction span is removed from matching. The rest of the question stays, so a real question is not dropped. "The plan does not include accidental damage." is not treated as an instruction.

## UK GDPR

Article 5 and Article 12 were read on 10 November 2026. Article 5(1)(a) and Article 12(1) are why the draft says it was prepared by an automated assistant and uses plain language. Article 5(1)(c) is why the question is not copied out. Article 5(1)(d) is why a stale rule is not stated as current. Article 5(3) says compatibility with the original purpose is not, by itself, a lawful basis. Article 6 was not opened. No lawful basis is asserted. Articles 13 and 14 were not opened.

Article 22A was read the same day. A decision is based solely on automated processing if there is no meaningful human involvement, and it is significant if it produces a legal effect or a similarly significant effect. This starter does not take that decision and does not certify meaningful human involvement. The Article 22A page records substitution by the Data (Use and Access) Act 2025, section 80(1). That section was not opened. Article 22 was not re-opened.

## Controls named, and not opened, on 10 November 2026

These names are the ones a deployment is often asked about. The product pages were not opened for this revision. Treat the current label, the licence, and the region as unverified.

| Control | What this starter can say |
|---|---|
| Microsoft Entra Agent ID | Not registered. The page was not opened. Unverified. |
| Conditional Access | Not configured. The page was not opened. Unverified. |
| Power Platform DLP | No mail, payment, or entitlement-write connector is in this starter. A DLP policy page was not opened. Unverified. |
| Microsoft Foundry prompt shields | This starter does not call a model, so it does not enable a shield. The control name in the portal was not checked. Unverified. |
| Key Vault | No secret is stored. The page was not opened. Unverified. |
| Microsoft Purview | No sensitivity label is applied. The page was not opened. Unverified. |
| Application Insights | This starter writes no log. The page was not opened. Unverified. |

## Logging

This starter writes no log. Before live use, log the request id, the rule ids, the clause reference, the outcome, whether an instruction was detected, and whether a source or a rule was stale. Do not log the question.

## Risk

Assessed 10 November 2026 for this starter rather than a named organisation. Residual risk is not all Low. The rows match the manifest. The residual risk that a later host stores the question, or adds a tool this folder does not have, is Medium.

## ATRS

There is no ATRS mapping that this starter completes. ATRS is a public-sector standard. A firm does not complete an ATRS record by using this starter. Experiment 03 can draft an assurance pack. This experiment does not. The scope policy was not re-opened.
