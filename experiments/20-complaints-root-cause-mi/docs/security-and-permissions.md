# Security and permissions

Complaints root-cause and regulatory MI, Experiment 20. Catalogue ID UK04.

This note matches `agent-manifest.yaml`. If the two disagree, the manifest is the control. It is written for an organisation deciding whether to try the starter, not as a completed data protection impact assessment and not as a regulatory return.

## Purpose

The agent reads one synthetic complaint batch and returns draft management information. It groups in-period records into themes and drafts sentences whose numbers are figure values. Financial-services narratives are passed to Experiment 02 `analyse()`. Every free-text field is passed to Experiment 08 `propose()`. Autonomy is A0. The complaints owner validates the clusters and the narrative. The agent cannot execute either step, and it cannot confirm compliance or submit a return.

## What the agent cannot do

These are disabled in the manifest, not merely discouraged in the prompt.

- Validate clusters or a narrative.
- Present the draft as a final regulatory return.
- Confirm that a firm is complying with the Consumer Duty. `complying_with_consumer_duty` stays null.
- Confirm that a landlord complies with the Complaint Handling Code. `code_compliant` stays null. Every code prompt has `comply` null.
- Confirm that an Ofgem return is complete, or send one. `ofgem_return_complete` stays null.
- Publish the report, or send it to the FCA, the Housing Ombudsman, Ofgem, a governing body, or a resident.
- Write a production complaints record.
- Offer redress, uphold or reject a complaint, or label a customer vulnerable.
- Calculate whether a complaint was resolved by the end of the first working day.
- Release redacted text, or describe the Experiment 08 output as anonymised.
- Re-implement Experiment 02 or Experiment 08.

There is no tool whose side effect is any of the above. `record_external_attestation` updates a copy of the JSON in memory and still does not validate the draft. The skills say the agent must not call it. `approve_clusters`, `approve_narrative`, `submit_regulatory_return`, `publish_report`, `send_report`, and `write_production_record` raise `ReportForbidden`. `tests/test_safety.py` checks that an instruction inside a narrative does not become an action.

## Data

**Read, in this starter.** The one batch the complaints owner supplies. The as-of date, typed by that person. The static quotations in `src/sources.py`. Experiment 02 `analyse()`, called in-process for a financial-services batch. Experiment 08 `propose()`, called in-process.

**Not read.** A live complaints system, the FCA, Housing Ombudsman, or Ofgem inboxes, mailboxes, and the Experiment 08 reversible token vault. An `as_of` field inside the batch is stripped. It does not replace the date the person typed.

Narratives may contain UK identifiers. The manifest does **not** assert a UK GDPR lawful basis and does **not** assert an Article 9 condition. The caller confirms both before production use. The draft may describe complaints about health or other special category matters. No Article 9 condition is asserted.

The Python starter does not persist the text. The draft stores hashes, closed-list phrases, matched lexicon phrases, and redacted copies of organisation names, service-improvement strings, and supplied Ombudsman titles. It does not store the full complaint narrative. It does not store raw identifier values. A batch that is not marked synthetic is refused, and the refusal does not echo the body. Production inference, if used, should run in Microsoft Foundry in UK South or UK West. Confirm the data-use terms at deployment.

Samples use the non-allocatable National Insurance fixture documented in Experiment 08. Northbridge Mutual, Harbourside Housing, and Lantern Energy are fictional.

## Prompt injection and stale sources

Fixtures include instructions hidden in an HTML comment, after a form feed, after blank lines, and between zero-width characters, including instructions to submit a return, publish the report, validate the clusters, or clear a stale flag. The checker records them and does not follow them. `followed` is false. The phrase is removed before classification and before a copied string. It remains in `prompt_injection.signals`.

The source pin of 29 October 2026 is stale when the as-of date is more than 90 days later. A sentence in a record does not clear the flag. The 90-day window is not a review period in PRIN 2A, the Complaint Handling Code, or the Ofgem guidance.

## Human approval

| Decision | Who |
| --- | --- |
| Validate the clusters | Complaints owner |
| Validate the narrative before it is used | Complaints owner |
| Decide compliance or return completeness, and submit or publish if they decide to | Complaints owner. This agent cannot submit or publish. |
| Rely on the draft after the pinned sources are marked stale | Complaints owner |
| Treat an Experiment 02 suggestion, or a lexicon label, as the confirmed root cause | Complaints owner |

Viewing a draft and re-running it do not need a separate approval.

## Risk register

Assessed 29 October 2026 for this starter, not for a named organisation. Residual risk is not all Low. The manifest holds the full rows. The residual risk that a later model treats the draft as anonymised is High, because Experiment 08 does not redact names, email addresses, or telephone numbers, and this draft must not be described as cleaned. The residual risk that a draft is filed as a return is also recorded. The functions that would file it raise `ReportForbidden`.

## Logging and the kill switch

This starter writes no log. Before live use, log who ran it, the batch id, the checksum, whether injection or a stale pin was flagged, and the later human decision. Do not log raw narratives or raw identifiers.

Turn the Copilot Studio agent off. Stop calling `draft_report()`. Remove any Foundry access. Block a later connector in a Power Platform DLP policy.

## Tenant controls named and not configured here

Entra Agent ID, Conditional Access, Power Platform DLP, Microsoft Foundry prompt shields, Key Vault, Purview, and Application Insights. The product pages for those controls were not opened on 29 October 2026, except the Copilot Studio harness overview. Dynamic Permissions, Dynamic Agent Risk, and Dynamic Conditional Access are recorded in Experiment 01 as announced, with availability unverified. This folder did not re-check that announcement.

## Review

29 October 2026. Next review 29 April 2027, and sooner if PRIN 2A.8, PRIN 2A.9, the Complaint Handling Code, the Ofgem complaints guidance, or regulations 2 and 11 of the 2008 complaints-handling standards change.

There is no ATRS submission. A public body that used this pattern would consider the Algorithmic Transparency Recording Standard separately. This starter does not submit a record, and it does not submit a regulatory return.
